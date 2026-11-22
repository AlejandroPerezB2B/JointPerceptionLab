"""Software-side stimulus timing QC; never a substitute for photodiode validation."""
import csv
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


def assess_timing(expected_s, observed_s, flip_intervals_s, source_fps):
    if expected_s <= 0 or source_fps <= 0:
        raise ValueError('Expected duration and FPS must be positive')
    error_ms = (observed_s - expected_s) * 1000
    intervals = [v*1000 for v in flip_intervals_s]
    tolerance = 1000/source_fps
    return dict(expected_duration_s=round(expected_s,6), observed_duration_s=round(observed_s,6),
                duration_error_ms=round(error_ms,3), duration_error_abs_ms=round(abs(error_ms),3),
                duration_within_one_source_frame=abs(error_ms)<=tolerance,
                flip_interval_mean_ms=round(statistics.mean(intervals),3) if intervals else None,
                flip_interval_max_ms=round(max(intervals),3) if intervals else None,
                flip_interval_p95_ms=round(sorted(intervals)[math.ceil(.95*len(intervals))-1],3) if intervals else None,
                source_frame_period_ms=round(tolerance,3))


def analyse_frame_log(times, indices, source_fps, refresh_s=None):
    """Assess source-frame scheduling; a displayed frame can span several refreshes."""
    intervals = [b-a for a,b in zip(times,times[1:])]
    repeats = sum(b==a for a,b in zip(indices,indices[1:]))
    skips = sum(max(0,b-a-1) for a,b in zip(indices,indices[1:]))
    long_gaps = sum(dt > 1.5/source_fps for dt in intervals)
    return {'source_frame_updates':len(indices), 'source_frame_repeats':repeats,
            'source_frame_skips':skips, 'intervals_over_1_5_source_frames':long_gaps,
            'max_update_gap_ms':round(max(intervals)*1000,3) if intervals else None,
            'refresh_estimate_ms':round(refresh_s*1000,3) if refresh_s else None}


def write_timing_report(session_folder):
    folder=Path(session_folder)
    path=folder/'trials.csv'
    if not path.exists():
        return None
    with path.open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    phases={}
    for phase in ('practice','main'):
        subset=[r for r in rows if r.get('phase')==phase and r.get('video_duration_error_ms')]
        errors=[float(r['video_duration_error_ms']) for r in subset]
        flags=[r.get('trial') for r in subset if r.get('video_duration_within_one_frame')=='0']
        gaps=[int(r['video_long_update_gaps']) for r in subset if r.get('video_long_update_gaps')]
        phases[phase]={'completed_trials':len(subset),
                       'mean_duration_error_ms':round(statistics.mean(errors),3) if errors else None,
                       'max_absolute_duration_error_ms':round(max(map(abs,errors)),3) if errors else None,
                       'trials_exceeding_one_source_frame':len(flags), 'flagged_trial_numbers':flags,
                       'trials_with_long_frame_update_gaps':sum(g>0 for g in gaps)}
    report={'generated_utc':datetime.now(timezone.utc).isoformat(), 'software_version':'0.4',
            'status':'SOFTWARE TIMING QC ONLY — NOT DISPLAY-HARDWARE VALIDATION',
            'method':'Flip-return timestamps from PsychoPy, source-frame indices logged separately; cue flip estimates video offset',
            'limitations':['Flip return does not measure light output.',
                           'Onset/offset timing includes scheduling and refresh-grid quantisation.',
                           'Source-frame updates do not prove unique physical refreshes.',
                           'TCP barriers do not synchronize host and client monitor onset.',
                           'Use photodiode/high-speed camera for display validation.'], 'phases':phases}
    (folder/'timing_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report
