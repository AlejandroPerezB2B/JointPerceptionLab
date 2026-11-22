# Joint Perception Lab v0.3 — Timing QC

## What has changed

Version 0.3 retains the **v0.2 corrected floating-point RGB rendering**, native 1024 × 768 video size, and full-screen presentation. It adds per-trial software timing observations and a session summary. It does **not** implement shared mode or line bisection yet.

Each trial records `video_expected_duration_s` (decoded frame count / source FPS), `video_actual_duration_s` (time between first video flip return and response-cue flip return), and `video_duration_error_ms` (actual minus expected). It also records decoded FPS, width/height, frame count, late-frame scheduling counts, and the mean/95th-percentile/maximum intervals between video-frame flips. Values are in `data/<session>/trials.csv`.

At the end of a completed or interrupted session, `data/<session>/timing_report.json` summarises completed practice and main trials separately, including trials with absolute duration errors exceeding **one source-video frame** (~33.3 ms for 30 fps). This is a *diagnostic flag*, not proof of adequate timing. A small total duration error does not guarantee correct per-frame presentation.

## Quick QC without completing 160 trials

1. Back up the current v0.2 project. Extract this ZIP into a **new** folder, e.g. `C:\JointPerceptionLab_v03`.
2. Copy the existing `stimuli/biological_motion` videos into the new folder's matching directory. The included `S24L0.mp4` is a diagnostic sample only; the full experiment requires the full stimulus set.
3. If you have already installed the project dependencies, either run `setup_windows.bat` in the new folder or copy the existing `.venv` directory (copying a venv between paths can break it; fresh setup is preferred).
4. Launch `run_windows.bat`, enter a test participant ID, validate stimuli, and start the individual biological-motion task.
5. Complete just a few practice trials and press **Esc** to stop. Partial `trials.csv` and `timing_report.json` are written under `data/<session>/`.
6. Open `timing_report.json` in Notepad and inspect `practice.completed_trials`, `practice.max_absolute_duration_error_ms`, and `practice.trials_exceeding_one_source_frame`.

## Interpretation and limitations

- Nominal duration is `decoded_frame_count / reported_fps`. It is not a direct measurement of the MP4 container timeline; variable-frame-rate material may require separate PTS-based checks.
- Actual duration is measured using the PsychoPy clock immediately after `Window.flip()` returns. The final video frame is replaced by the response cue at the next flip.
- A typical 60-Hz display cannot represent arbitrary 30-fps onset times without quantization to 16.7-ms refresh boundaries. Monitor settings, dropped refreshes, video decoding and operating-system scheduling can affect the results.
- The flip-interval statistics describe source-frame update timing; they are **not** monitor-refresh interval measurements.
- `video_late_frames` is a heuristic scheduling count, **not** a confirmed dropped-frame count.
- These measurements are software-side estimates. A photodiode or high-speed camera is required to validate the actual luminance onset and offset on the research display.
- **Do not interpret a clean timing report as full experimental validation.**

## Outputs

- `session.json` — session configuration
- `main_order.csv`, `practice_order.csv` — deterministic trial sequences
- `trials.csv` — responses, timestamps and per-trial video QC
- `timing_report.json` — QC summary, including partial sessions
- `error.log` — only if the session exits with an error
