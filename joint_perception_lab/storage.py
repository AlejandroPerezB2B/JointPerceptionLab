"""Crash-resistant append-only CSV and session metadata."""
import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

FIELDS = ['session_id','participant_id','condition','phase','trial','filename','signal_present',
          'noise','direction','position','repetition','block','block_trial','response','response_walker','correct',
          'hit','false_alarm','miss','correct_rejection','rt_s','fixation_onset_s',
          'video_onset_s','video_end_s','video_frames','video_late_frames','response_cue_onset_s',
          'timestamp_utc',
          'video_source_fps','video_width_px','video_height_px',
          'video_expected_duration_s','video_actual_duration_s','video_duration_error_ms',
          'video_duration_within_one_frame','video_flip_interval_mean_ms',
          'video_flip_interval_p95_ms','video_flip_interval_max_ms',
          'video_first_to_last_frame_ms','video_last_frame_to_cue_ms',
          'video_long_update_gaps','video_frame_repeats','video_frame_skips',
          'video_refresh_estimate_ms','peer_response','peer_rt_s','peer_response_received_s',
          'network_role','network_session_label']


def safe_id(value):
    value = value.strip()
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,60}', value):
        raise ValueError('Participant ID must contain 1–60 letters, digits, hyphens or underscores.')
    return value


def create_session(base, participant, condition, config, main_trials, practice_trials):
    participant = safe_id(participant)
    now = datetime.now(timezone.utc)
    stamp = now.strftime('%Y%m%dT%H%M%S%fZ')
    session_id = f'{participant}_{condition}_{stamp}'
    folder = Path(base) / session_id
    folder.mkdir(parents=True, exist_ok=False)
    metadata = {'session_id':session_id, 'participant_id':participant, 'condition':condition,
                'created_utc':now.isoformat(), 'config':config,
                'main_trial_count':len(main_trials), 'practice_trial_count':len(practice_trials)}
    (folder/'session.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    from .stimuli import write_trials
    write_trials(folder/'main_order.csv', main_trials)
    write_trials(folder/'practice_order.csv', practice_trials)
    return folder, session_id


def append_row(path, row):
    path = Path(path)
    new_file = not path.exists()
    with path.open('a', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction='ignore')
        if new_file:
            writer.writeheader()
        writer.writerow({field: row.get(field, '') for field in FIELDS})
        handle.flush()
        os.fsync(handle.fileno())


def score_row(stimulus, response):
    signal = int(stimulus['signal_present'])
    yes = int(response == 'yes')
    return {'response_walker':yes, 'correct':int(signal == yes),
            'hit':int(signal == 1 and yes == 1),
            'false_alarm':int(signal == 0 and yes == 1),
            'miss':int(signal == 1 and yes == 0),
            'correct_rejection':int(signal == 0 and yes == 0)}
