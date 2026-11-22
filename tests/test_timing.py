import csv
import json
from joint_perception_lab.timing import assess_timing, write_timing_report


def test_timing_exact():
    r = assess_timing(61/30, 61/30, [1/30]*60, 30)
    assert r['duration_within_one_source_frame']
    assert r['duration_error_ms'] == 0


def test_timing_flags_deviation():
    r = assess_timing(2, 2.1, [.033]*59, 30)
    assert not r['duration_within_one_source_frame']
    assert r['duration_error_ms'] == 100


def test_partial_report(tmp_path):
    with (tmp_path/'trials.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['phase','trial','video_expected_duration_s',
                'video_actual_duration_s','video_duration_error_ms','video_duration_within_one_frame'])
        writer.writeheader()
        writer.writerow(dict(phase='practice', trial=1, video_expected_duration_s=2,
                             video_actual_duration_s=2.1, video_duration_error_ms=100,
                             video_duration_within_one_frame=0))
    report = write_timing_report(tmp_path)
    assert report['phases']['practice']['trials_exceeding_one_source_frame'] == 1
    assert (tmp_path/'timing_report.json').exists()
