# Joint Perception Lab v0.6 — biological motion + number-line task

## Installation

Keep v0.5 as a backup. Extract v0.6 into a new folder. Copy all biological-motion MP4 stimuli into `stimuli/biological_motion`. On Windows with Python **3.11**, run `setup_windows.bat` once and then `run_windows.bat`. The Python source is included; `build_windows.bat` is a build helper, **not** a prebuilt executable. The Windows executable has not been built or tested.

## Starting a shared experiment — ORDER MATTERS

1. On **HOST** computer (IPv4 **192.168.1.211**), launch the app, select the task and **Shared — Host**, enter its participant ID and the shared session label, then click **Start experiment**. **Wait for the host to listen for the connection.**
2. Only **after the host is waiting**, on **CLIENT** launch the app, choose the **same task**, select **Shared — Client**, enter a different participant ID and the **same session label**. The Host IP field defaults to **192.168.1.211**. Click **Start experiment**.
3. Both participants press Space at the instructions. Both answer privately. In number-line mode, once both valid answers are received, **either** participant may press Space to start the next trial.
4. Use Escape to stop. Data already written to disk remain in `data/<session_id>/`.

The host address is a default only; verify it is still assigned to the host computer. TCP port 48321 must be accessible on the trusted local network.

## Biological motion

Unchanged from v0.5: 10 fixed practice trials, two main blocks of 80, one instance of each of 80 videos per block, balanced cyclic U/S transitions, and v0.2 corrected rendering. The software timing diagnostics are not hardware validation.

## Number-line / line-bisection task (new prototype)

- White horizontal number line on black background, anchored **−1000** (left) and **+1000** (right), with a vertical white marker.
- **73 target positions** −900 through +900 in steps of 25, each **twice** = **146 main trials**.
- One **fixed pseudorandom order** across sessions, seed **20260427**, identical for host and client. Saved in `main_order.csv`; digest checked during the network handshake.
- **Three preliminary practice targets** −750, 0, +750. These are provisional operator familiarisation trials, **not a validated replication of an original practice procedure**.
- **No fixation cross.** Participants type a signed integer from −1000 to +1000 and press Enter. Backspace edits. Escape aborts. The display stays until a valid response. Invalid input produces an error and a retry prompt.
- **Individual:** press Space to start each trial. **Shared:** identical target on both computers; private responses; after both valid responses, Space on **either** computer unlocks the next trial. A 300–500 ms black ITI is applied on each computer.
- Responses, signed/absolute error, RT, software stimulus flip timestamps, peer response and RT (for audit, **not displayed to participant**) are written immediately to `bisection_trials.csv`.
- The line is 1000 screen pixels on a sufficiently wide display, with proportional target placement. This is a **first Python implementation**, not yet a pixel-perfect reproduction of the historical MATLAB/PTB task. The previous PTB program used different layout details; confirm geometry, viewing distance and instructions against the approved experimental protocol before research collection.

## Quality and limitations

Automated tests check order generation, counts, reproducibility and CSV writing. PsychoPy GUI rendering and actual two-PC operation cannot be tested in this environment. Shared barriers do **not** guarantee synchronised physical stimulus onset. The individual and shared number-line task should be pilot-tested before data collection. Practice targets and screen geometry should be confirmed with the research team.
