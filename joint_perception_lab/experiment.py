"""Full-screen individual and TCP-coordinated dyadic biological-motion experiments.

Not yet validated for research-grade display timing or inter-computer synchrony.
"""
from datetime import datetime, timezone
import json
import time

from .storage import append_row, score_row
from .timing import assess_timing, analyse_frame_log, write_timing_report
from .video_render import bgr_to_psychopy, display_size, decode_video
from .networking import Peer, order_digest


def run_biological_motion(participant_id, session_id, folder, main_trials, practice_trials,
                          fixation_s=.5, feedback_s=.8, fullscreen=True,
                          role='individual', peer_address='127.0.0.1', session_label='session01'):
    import numpy as np
    from psychopy import visual, core, event
    peer = None
    if role in ('host','client'):
        peer = Peer.connect(role, peer_address)
        try:
            peer.handshake(order_digest(practice_trials, main_trials), session_label)
        except BaseException:
            peer.close()
            raise
    win = None
    try:
        win = visual.Window(fullscr=fullscreen, units='pix', color=(-1,-1,-1),
                            allowGUI=False, waitBlanking=True)
        clock=core.Clock()
        text=visual.TextStim(win,text='',color='white',height=27,wrapWidth=950)
        fixation=visual.TextStim(win,text='+',color='white',height=55)
        image=visual.ImageStim(win,image=np.zeros((32,32,3),dtype=np.float32)-1,
                               units='pix',size=(32,32),interpolate=True)
        # Estimate refresh from flip intervals; estimate only, never assume 60 Hz.
        win.recordFrameIntervals = True
        for _ in range(45):
            win.flip()
        measured = [v for v in win.frameIntervals if .004 < v < .1]
        refresh_s = float(np.median(measured)) if measured else None
        win.frameIntervals.clear()
        def screen(message):
            text.text=message
            text.draw()
            win.flip(clearBuffer=True)
            return clock.getTime()
        def keys(allowed):
            event.clearEvents(eventType='keyboard')
            while True:
                for key, t in event.getKeys(timeStamped=clock):
                    if key=='escape':
                        raise KeyboardInterrupt('Escape pressed')
                    if key in allowed:
                        return key,t
                core.wait(.005)
        def play(path):
            frames_bgr,fps=decode_video(path)
            height,width=frames_bgr[0].shape[:2]
            image.size=display_size(width,height,*map(int,win.size),mode='native')
            frames=[bgr_to_psychopy(frame) for frame in frames_bgr]
            duration=len(frames)/fps
            times=[]
            indices=[]
            late=0
            onset=None
            for i,frame in enumerate(frames):
                if event.getKeys(keyList=['escape']):
                    raise KeyboardInterrupt('Escape pressed')
                if onset is not None:
                    target=onset+i/fps
                    while clock.getTime() < target-.003:
                        core.wait(.001)
                    if clock.getTime()>target+.5/fps:
                        late+=1
                image.image=frame
                image.draw()
                win.flip(clearBuffer=True)
                t=clock.getTime()
                times.append(t)
                indices.append(i)
                if onset is None:
                    onset=t
            while clock.getTime()<onset+duration-.003:
                if event.getKeys(keyList=['escape']):
                    raise KeyboardInterrupt('Escape pressed')
                core.wait(.001)
            return dict(onset=onset, last_frame_flip=times[-1], flip_times=times,
                        indices=indices, frames=len(frames),fps=fps,
                        expected_duration=duration,late_frames=late,width=width,height=height)
        def block(trials,phase):
            for stim in trials:
                if phase == 'main' and stim.get('block') == 2 and stim.get('block_trial') == 1:
                    screen('Block 1 complete. Take a break.\n\nPress SPACE when ready for Block 2.')
                    keys(['space'])
                    if peer:
                        screen('Waiting for partner to start Block 2...')
                        peer.barrier('main', 81, 'block2_start')
                if peer:
                    screen(f'Waiting for both participants — {phase} trial {stim["trial"]}')
                    peer.barrier(phase,stim['trial'],'pre_fixation')
                fixation.draw()
                win.flip(clearBuffer=True)
                fixation_onset=clock.getTime()
                core.wait(fixation_s)
                playback=play(stim['path'])
                cue_onset=screen('Did you see a human walker?\n\nY = Yes       N = No')
                observed=cue_onset-playback['onset']
                qc=assess_timing(playback['expected_duration'],observed,
                                 [b-a for a,b in zip(playback['flip_times'],playback['flip_times'][1:])],
                                 playback['fps'])
                frames_qc=analyse_frame_log(playback['flip_times'],playback['indices'],
                                            playback['fps'],refresh_s)
                # Save per-frame presentation events BEFORE waiting for a response.
                with (folder/'frame_events.jsonl').open('a',encoding='utf-8') as f:
                    f.write(json.dumps({'phase':phase,'trial':stim['trial'],
                        'filename':stim['filename'],'source_fps':playback['fps'],
                        'frame_indices':playback['indices'],
                        'flip_return_times_s':playback['flip_times'],
                        'video_first_flip_s':playback['onset'],
                        'video_last_frame_flip_s':playback['last_frame_flip'],
                        'response_cue_flip_s':cue_onset})+'\n')
                key, response_t=keys(['y','n'])
                response='yes' if key=='y' else 'no'
                peer_data={}
                if peer:
                    screen('Response recorded. Waiting for your partner...')
                    other=peer.exchange_response(phase,stim['trial'],response,response_t-cue_onset)
                    peer_data={'peer_response':other['response'],'peer_rt_s':other['rt_s'],
                               'peer_response_received_s':clock.getTime()}
                row={**stim,**score_row(stim,response),
                     'session_id':session_id,'participant_id':participant_id,
                     'block':stim.get('block',''),'block_trial':stim.get('block_trial',''),
                     'condition':'shared' if peer else 'individual','phase':phase,'response':response,
                     'rt_s':round(response_t-cue_onset,6),'fixation_onset_s':fixation_onset,
                     'video_onset_s':playback['onset'],'video_end_s':cue_onset,
                     'video_frames':playback['frames'],'video_late_frames':playback['late_frames'],
                     'video_source_fps':round(playback['fps'],6),
                     'video_width_px':playback['width'],'video_height_px':playback['height'],
                     'video_expected_duration_s':qc['expected_duration_s'],
                     'video_actual_duration_s':qc['observed_duration_s'],
                     'video_duration_error_ms':qc['duration_error_ms'],
                     'video_duration_within_one_frame':int(qc['duration_within_one_source_frame']),
                     'video_flip_interval_mean_ms':qc['flip_interval_mean_ms'],
                     'video_flip_interval_p95_ms':qc['flip_interval_p95_ms'],
                     'video_flip_interval_max_ms':qc['flip_interval_max_ms'],
                     'video_first_to_last_frame_ms':round((playback['last_frame_flip']-playback['onset'])*1000,3),
                     'video_last_frame_to_cue_ms':round((cue_onset-playback['last_frame_flip'])*1000,3),
                     'video_long_update_gaps':frames_qc['intervals_over_1_5_source_frames'],
                     'video_frame_repeats':frames_qc['source_frame_repeats'],
                     'video_frame_skips':frames_qc['source_frame_skips'],
                     'video_refresh_estimate_ms':frames_qc['refresh_estimate_ms'],
                     'response_cue_onset_s':cue_onset,
                     'network_role':role,'network_session_label':session_label if peer else '',
                     'timestamp_utc':datetime.now(timezone.utc).isoformat(),**peer_data}
                append_row(folder/'trials.csv',row)
                if phase=='practice':
                    screen('Correct' if row['correct'] else 'Incorrect')
                    core.wait(feedback_s)
                else:
                    win.flip(clearBuffer=True)
                    core.wait(.3+(stim['trial']%5)*.05)
        screen('BIOLOGICAL MOTION DETECTION\n\nY = walker present; N = absent.\n\nPress SPACE to begin.')
        keys(['space'])
        if peer:
            screen('Waiting for partner to begin practice...')
            peer.barrier('practice',0,'start')
        block(practice_trials,'practice')
        screen('Practice finished. Press SPACE to start the main task.')
        keys(['space'])
        if peer:
            screen('Waiting for partner to begin main task...')
            peer.barrier('main',0,'start')
        block(main_trials,'main')
        screen('Finished. Thank you. Press SPACE to close.')
        keys(['space'])
    except BaseException:
        if peer:
            try:
                peer.send({'type':'ABORT'})
            except Exception:
                pass
        raise
    finally:
        if win is not None:
            win.close()
        if peer:
            peer.close()
        write_timing_report(folder)
