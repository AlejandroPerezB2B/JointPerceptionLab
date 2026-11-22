# Joint Perception Lab v0.4 — timing QC and experimental shared mode

## Install and run (Windows)
1. Extract the entire ZIP to a **new** folder. Keep v0.3 intact.
2. Copy all biological-motion MP4 files into `stimuli\biological_motion` (the single example is not enough for the full experiment).
3. Double-click `setup_windows.bat` (Python **3.11** required). Wait until it reports success.
4. Double-click `run_windows.bat`.
5. Select **Biological motion detection**, enter a unique participant ID, and choose the stimulus folder. Click **Validate stimuli** before **Start experiment**.
6. To stop a test, press **Escape**. Completed trials remain in `data\<session_id>\`.

## Individual
Choose **Individual**. The experiment uses the visually corrected floating-point RGB frames at native resolution.

## Shared — experimental, not synchronized/validated
- Use two Windows PCs on the same private wired LAN; Windows firewall must permit inbound TCP **48321** on the host.
- Both computers need **the same stimulus files**, and the same session label. Participant IDs must be different.
- Find the host IPv4 address using `ipconfig` in Command Prompt.
- On the host, choose **Shared — Host** and click Start. The host waits for a client (up to 120 seconds).
- On the other computer, choose **Shared — Client**, enter the host IPv4 address, and click Start.
- Both participants press SPACE to start each block. The software coordinates each trial before fixation, records independent responses, and does not advance until both responses are received.
- Both computers save separate local CSV, JSONL and session files. Preserve both.
- **Important:** TCP barriers do not establish simultaneous display onset. No network-clock offset estimation or hardware sync has been implemented. Do not collect research data with shared mode yet.

## Timing diagnostics
- `trials.csv`: per-trial source duration, software-estimated duration, first-to-last-frame interval, final-frame-to-response-cue interval, estimated refresh interval, gap flags, peer response (shared only).
- `frame_events.jsonl`: one JSON object per completed video with every source-frame index and local PsychoPy flip-return timestamp. Can include videos without a completed response if a session was interrupted.
- `timing_report.json`: summary for completed trials.
- **Important:** A 61-frame, 30-fps video has nominal duration 61/30 = 2.0333 s. The first-to-last frame flip interval is nominally 60/30 = 2.000 s, not 2.0333 s. The response-cue flip is an *estimate* of video offset and can occur on a later refresh. These values are intentionally reported separately.
- Frame-index repeat/skip counters only assess the submitted source-frame sequence, **not** the number of physical display refreshes or GPU dropped frames. Gaps indicate scheduling irregularity, not necessarily missing stimulus content.
- Use a photodiode or high-speed camera for actual light onset/offset and cross-monitor synchronization testing.

## Known limitations
- Shared mode is an **experimental prototype**; networking has not been exercised on two physical PCs here. Blocking network operations may cause a non-responsive window until timeout if a peer disconnects. No reconnect/resume functionality.
- Refresh estimation and video timing are software estimates. A 30-fps movie on a 60-Hz screen usually spans about two monitor refreshes per source frame.
- Line bisection remains unimplemented.
- Windows `.exe` is **not included**; `build_windows.bat` is a candidate build script, requiring packaging and testing on Windows.
- Do not use for definitive research data collection before hardware and network validation.
