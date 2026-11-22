# Video trails diagnostic — Joint Perception Lab v0.1

This is a **diagnostic update**, not a validated experimental release. The original video files are not changed.

## Install

1. Close Joint Perception Lab.
2. Extract this ZIP to a **new** folder, or copy `joint_perception_lab/experiment.py` and `diagnose_video.py` into your existing project (preserve your `.venv`, `stimuli`, and `data` folders).
3. If using the existing project, do **not** replace your `.venv` folder or participant data.

## Compare

1. Open one of your MP4s in a multimedia player **full-screen on the same monitor**. Check whether it leaves trails.
2. Open the project folder in File Explorer, click the address bar, type `cmd`, and press Enter.
3. Run this command (replace the filename with a real video):

   `.venv\Scripts\python.exe diagnose_video.py "stimuli\biological_motion\U24L10.mp4"`

4. The program shows one **still frame for 4 seconds**, then plays the video. Press Escape to exit.
5. If the still dots have trails, suspect graphics scaling/display processing. If only moving dots trail in both the multimedia player and this test, suspect monitor response/overdrive. If the multimedia player is clean but the diagnostic trails, suspect the PsychoPy rendering path or timing.
6. For a stronger test, record a short slow-motion phone video of both applications running on the same screen; do not confuse camera artifacts with display artifacts.

The experiment file now explicitly disables texture interpolation and clears the back buffer on every video frame. This is a targeted test, **not a guaranteed fix**.

Do not collect research data until the visual problem and frame timing have been validated.
