# Data dictionary — v0.6

## Shared session files

`session.json`: participant ID, session ID, task, mode, network role, shared label, software version, random seed and configuration. `main_order.csv` and `practice_order.csv`: planned trial order. These are created before the task begins; a planned trial does not imply completion.

## Biological-motion `trials.csv`

| Field | Meaning |
|---|---|
| `phase`, `trial`, `block`, `block_trial`, `repetition` | trial identifiers; practice has no block |
| `filename`, `signal_present`, `noise`, `direction`, `position` | stimulus identity and factors |
| `response`, `response_walker`, `correct` | yes/no, binary yes, accuracy |
| `hit`, `false_alarm`, `miss`, `correct_rejection` | binary SDT outcome flags |
| `rt_s` | seconds from response-cue software flip to key response |
| `fixation_onset_s`, `video_onset_s`, `video_end_s`, `response_cue_onset_s` | software timestamps in local PsychoPy clock, not shared wall time |
| `video_frames`, `video_source_fps`, `video_width_px`, `video_height_px` | decoded video properties |
| `video_expected_duration_s`, `video_actual_duration_s`, `video_duration_error_ms` | expected from source frames/FPS, observed onset-to-cue, difference |
| `video_first_to_last_frame_ms`, `video_last_frame_to_cue_ms` | separation of source-frame and cue-transition intervals |
| `video_flip_interval_mean_ms`, `video_flip_interval_p95_ms`, `video_flip_interval_max_ms` | frame-update interval QC |
| `video_late_frames`, `video_long_update_gaps`, `video_frame_repeats`, `video_frame_skips` | software QC counters |
| `video_refresh_estimate_ms` | approximate monitor refresh interval |
| `peer_response`, `peer_rt_s`, `peer_response_received_s` | shared peer audit values, not presented to participant |
| `timestamp_utc`, `session_id`, `participant_id`, `condition`, `network_role`, `network_session_label` | metadata |

`frame_events.jsonl`: one JSON object per presented trial containing source-frame indices and flip-return times. `timing_report.json`: aggregated software QC by phase.

## Bisection `bisection_trials.csv`

| Field | Meaning |
|---|---|
| `phase`, `trial`, `target_position` | trial phase/index and target on −1000…1000 scale |
| `response_integer` | participant's signed integer estimate |
| `signed_error` | response − target |
| `absolute_error` | abs(response − target) |
| `response_rt_s` | seconds from first marker flip to Enter |
| `stimulus_flip_s`, `response_enter_s` | local software clock times |
| `peer_response_integer`, `peer_rt_s` | peer response audit fields in shared mode |
| `iti_s` | locally sampled intertrial interval |
| `session_id`, `participant_id`, `condition`, `network_role`, `session_label`, `timestamp_utc` | metadata |

**Interpretation:** no output field is a direct measure of photon onset or absolute synchrony between displays. Do not merge dyad timing on uncorrected local clocks.
