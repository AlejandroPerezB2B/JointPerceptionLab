"""Number-line marker localisation, individual or shared, v0.6 prototype.

This is the 73-position, typed-estimate task specified for Joint Perception Lab.
Screen geometry is explicit and should be calibrated against the original protocol.
"""
import csv
import hashlib
import json
import os
import random
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

POSITIONS = tuple(range(-900, 901, 25))
PRACTICE_POSITIONS = (-750, 0, 750)
LINE_ENDS = (-1000, 1000)
FIELDS = ('session_id','participant_id','condition','network_role','session_label',
          'phase','trial','target_position','response_integer','signed_error','absolute_error',
          'response_rt_s','stimulus_flip_s','response_enter_s','peer_response_integer',
          'peer_rt_s','iti_s','timestamp_utc')


def make_order(seed):
    """Each of 73 positions occurs twice; deterministic for an explicit seed."""
    rng = random.Random(seed)
    positions = list(POSITIONS) * 2
    rng.shuffle(positions)
    return [{'trial': i + 1, 'target_position': p} for i, p in enumerate(positions)]


def order_digest(order, practice):
    payload = {'task':'line_bisection_v06', 'practice':practice,
               'main':[(t['trial'],t['target_position']) for t in order]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def shared_seed(label):
    label = label.strip()
    if not label:
        raise ValueError('Shared session label must not be empty')
    return int.from_bytes(hashlib.sha256(('JPL-v0.6-bisection:'+label).encode()).digest()[:8], 'big')


def write_order(folder, order, practice):
    for filename, rows in [('main_order.csv',order),
                           ('practice_order.csv',[{'trial':i+1,'target_position':p} for i,p in enumerate(practice)])]:
        with (folder/filename).open('w',newline='',encoding='utf-8') as handle:
            writer=csv.DictWriter(handle,fieldnames=('trial','target_position'))
            writer.writeheader(); writer.writerows(rows)


def save_trial(path, row):
    new = not path.exists()
    with path.open('a',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=FIELDS)
        if new: writer.writeheader()
        writer.writerow({field:row.get(field,'') for field in FIELDS})
        handle.flush(); os.fsync(handle.fileno())


def run_line_bisection(participant_id, session_id, folder, main_order, practice_positions=PRACTICE_POSITIONS,
                       fullscreen=True, role='individual', peer_address='192.168.1.211',session_label='session01'):
    from psychopy import visual, core, event
    from .networking import Peer
    peer=None
    if role in ('host','client'):
        peer=Peer.connect(role,peer_address)
        try:
            peer.handshake(order_digest(main_order,practice_positions),session_label)
        except BaseException:
            peer.close(); raise
    win=None
    try:
        win=visual.Window(fullscr=fullscreen,units='pix',color=(-1,-1,-1),allowGUI=False,waitBlanking=True)
        clock=core.Clock()
        width,height=map(int,win.size)
        # 1000 px is the target length; fit smaller windows without clipping labels.
        line_length=min(1000,max(300,width-300))
        x_left=-line_length/2
        line=visual.Line(win,start=(x_left,0),end=(-x_left,0),lineColor='white',lineWidth=4)
        marker=visual.Line(win,start=(0,-13),end=(0,13),lineColor='white',lineWidth=5)
        left_label=visual.TextStim(win,text='-1000',pos=(x_left-35,-48),height=24,color='white')
        right_label=visual.TextStim(win,text='+1000',pos=(-x_left+35,-48),height=24,color='white')
        text=visual.TextStim(win,text='',height=25,color='white',wrapWidth=max(400,width-160))
        entry=visual.TextStim(win,text='',pos=(0,-160),height=30,color='white')
        hint=visual.TextStim(win,text='Type a number from -1000 to +1000, then press ENTER. Backspace edits.',
                             pos=(0,-105),height=20,color='white')
        def screen(message):
            text.text=message; text.draw(); win.flip(clearBuffer=True)
        def wait_space():
            event.clearEvents(eventType='keyboard')
            while True:
                for key in event.getKeys():
                    if key=='escape': raise KeyboardInterrupt('Escape pressed')
                    if key=='space': return
                core.wait(.005)
        def show_target(target, response=''):
            marker_x=target/1000*(line_length/2)
            marker.start=(marker_x,-13); marker.end=(marker_x,13)
            line.draw();marker.draw();left_label.draw();right_label.draw();hint.draw()
            entry.text=response if response else '_'
            entry.draw()
            win.flip(clearBuffer=True)
            return clock.getTime()
        def get_integer(target):
            typed=''; onset=show_target(target)
            event.clearEvents(eventType='keyboard')
            while True:
                changed=False
                for key, t in event.getKeys(timeStamped=clock):
                    if key=='escape': raise KeyboardInterrupt('Escape pressed')
                    if key in ('backspace','delete'):
                        typed=typed[:-1]; changed=True
                    elif key in ('minus','subtract','num_subtract') and not typed:
                        typed='-';changed=True
                    elif key in ('plus','add','num_add') and not typed:
                        typed='+';changed=True
                    elif key in ('return','enter','num_enter'):
                        try: value=int(typed)
                        except ValueError: value=None
                        if value is not None and -1000<=value<=1000:
                            return value, t-onset, onset, t
                        screen('Invalid response. Enter an integer from -1000 to +1000.\n\nPress SPACE to retry.')
                        wait_space(); typed='';changed=True
                    else:
                        digit = key if len(key)==1 and key.isdigit() else (key[4:] if key.startswith('num_') and len(key)==5 and key[-1].isdigit() else None)
                        if digit is not None and len(typed)<5:
                            typed+=digit;changed=True
                if changed: show_target(target,typed)  # Keep the original onset timestamp for RT.
                core.wait(.005)
        def shared_next(phase,trial):
            """Either participant presses Space; both exchange NEXT tokens before continuing."""
            import threading
            received=threading.Event(); failure=[]
            def reader():
                try:
                    msg=peer.receive('NEXT')
                    if msg.get('phase')!=phase or msg.get('trial')!=trial:
                        raise RuntimeError('NEXT trial mismatch')
                except BaseException as exc: failure.append(exc)
                finally: received.set()
            worker=threading.Thread(target=reader,daemon=True);worker.start()
            sent=False
            event.clearEvents(eventType='keyboard')
            while not received.is_set():
                for key in event.getKeys():
                    if key=='escape':
                        peer.send({'type':'ABORT'});raise KeyboardInterrupt('Escape pressed')
                    if key=='space' and not sent:
                        peer.send({'type':'NEXT','phase':phase,'trial':trial});sent=True
                core.wait(.005)
            if failure: raise failure[0]
            if not sent:
                peer.send({'type':'NEXT','phase':phase,'trial':trial})
            worker.join(timeout=1)
        def run_phase(phase, targets):
            for index,target in enumerate(targets,1):
                if peer:
                    screen(f'Waiting for partner — {phase} trial {index}...')
                    peer.barrier(phase,index,'ready')
                else:
                    screen(f'{phase.title()} trial {index}/{len(targets)}\n\nPress SPACE to show the line.')
                    wait_space()
                value,rt,onset,entered=get_integer(target)
                other={}
                if peer:
                    screen('Response recorded. Waiting for partner...')
                    other=peer.exchange_response(phase,index,value,rt)
                    peer.barrier(phase,index,'both_responses')
                iti=random.uniform(.3,.5)
                row={'session_id':session_id,'participant_id':participant_id,
                     'condition':'shared' if peer else 'individual','network_role':role,
                     'session_label':session_label if peer else '',
                     'phase':phase,'trial':index,'target_position':target,
                     'response_integer':value,'signed_error':value-target,'absolute_error':abs(value-target),
                     'response_rt_s':round(rt,6),'stimulus_flip_s':onset,'response_enter_s':entered,
                     'peer_response_integer':other.get('response',''), 'peer_rt_s':other.get('rt_s',''),
                     'iti_s':round(iti,4),'timestamp_utc':datetime.now(timezone.utc).isoformat()}
                save_trial(folder/'bisection_trials.csv',row)
                win.flip(clearBuffer=True)
                core.wait(iti)
                if peer and index<len(targets):
                    screen('Both responses recorded.\n\nEither participant: press SPACE for next trial.')
                    shared_next(phase,index)
        screen('NUMBER-LINE TASK\n\nEstimate the numerical position of the vertical marker.\nType your answer and press ENTER.\n\nPress SPACE to begin practice.')
        wait_space()
        if peer:
            screen('Waiting for partner to begin practice...')
            peer.barrier('practice',0,'start')
        run_phase('practice',practice_positions)
        screen('Practice finished. Press SPACE to start the main experiment.')
        wait_space()
        if peer:
            screen('Waiting for partner to begin main experiment...')
            peer.barrier('main',0,'start')
        run_phase('main',[t['target_position'] for t in main_order])
        screen('Finished. Thank you. Press SPACE to close.')
        wait_space()
    except BaseException:
        if peer:
            try: peer.send({'type':'ABORT'})
            except Exception: pass
        raise
    finally:
        if win is not None:win.close()
        if peer:peer.close()
