# User Manual — Joint Perception Lab v0.6

1. Turn on the Windows computer, sign in and open the `JointPerceptionLab` folder.
2. Double-click `run_windows.bat`. (If the program has never been installed on this computer, run `setup_windows.bat` once first; Python 3.11 required.)
3. Choose **Biological motion detection** or **Line bisection**.
4. Choose **Individual**, **Shared — Host** or **Shared — Client**. Enter a unique participant ID.
5. Biological motion only: ensure the MP4 folder is correct; click **Validate stimuli**. Line bisection needs no video files.
6. For **individual**, click **Start experiment**, follow the full-screen instructions, and let the participant respond.
7. For **shared**, enter the same session label on both computers. **On HOST, click Start experiment FIRST and wait for the connection. Only then on CLIENT, check Host IP (default `192.168.1.211`) and click Start experiment.** Both participants press Space when instructed.
8. Biological motion: respond **Y** for walker, **N** for absent. Line bisection: type an integer and press **Enter**. For shared line bisection, after both respond, **either participant presses Space** to continue.
9. At the end, inspect `data/<session_id>/` and verify `trials.csv` (biological motion) or `bisection_trials.csv` (bisection). `main_order.csv` and `session.json` document the planned order. Pressing Escape can interrupt a session; inspect partial records and `error.log` if present.

**Do not use the software for definitive data collection until the study protocol and timing are validated.**
