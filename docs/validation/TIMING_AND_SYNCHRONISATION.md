# Timing and synchronisation — interpretation and limitations

**Source:** `experiment.py`, `timing.py`, `networking.py` (v0.6).

Biological-motion videos are decoded with OpenCV and displayed through PsychoPy `ImageStim`, using RGB floating-point arrays and native pixel dimensions where supported. Frames are scheduled using the decoded source FPS, and PsychoPy flip-return timestamps are recorded.

Recorded metrics include first and last source-frame flip timestamps, response-cue flip, source-frame indices, source FPS, expected duration, observed onset-to-cue duration, duration error, intervals between frame updates, counts of long intervals, and refresh estimates. The response-cue transition can introduce an additional refresh-grid interval; a duration discrepancy is not by itself proof of missed source frames.

**Important:** Software timestamps are not photon onset measurements. No shared hardware clock is used. TCP barriers coordinate readiness and order, not synchronous monitor flips. Different PCs' local clock values must not be subtracted as though they share a common epoch. No formal network clock-offset estimator is implemented in v0.6.

### Minimum future hardware validation

- Confirm monitor refresh rates and disable variable-refresh/image-processing modes where appropriate.
- Use a photodiode or high-speed camera to measure stimulus first-photon onset and offset.
- Check all 61 source frames (where applicable) and their displayed durations; quantify skipped/repeated/held frames.
- Measure host/client physical onset difference across many trials and under network load.
- Save hardware/OS/GPU/monitor specifications and software package versions.
- Establish preregistered tolerances and document exclusions.

The present version is a **prototype for pilot work**, not a validated synchronised-display platform.
