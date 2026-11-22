# Software architecture (v0.6)

| Module | Responsibility |
|---|---|
| `gui.py` | PySide6 experimenter configuration and task dispatch |
| `experiment.py` | biological-motion presentation, responses and timing logs |
| `stimuli.py` | video discovery, factorial validation and constrained trial order |
| `video_render.py` | OpenCV decode and PsychoPy-compatible RGB frame conversion |
| `bisection.py` | number-line stimulus, order, numeric responses, CSV logging |
| `networking.py` | TCP handshake, barriers, peer response exchange, port 48321 |
| `timing.py` | software-side timing QC and reporting |
| `storage.py` | session directories, append-only CSV and correctness coding |
| `sdt.py` | signal detection summary |
| `launcher.py` | application startup |

Design limitation: visual and network operations are not hardware synchronised; the GUI launches the full-screen PsychoPy task in-process. Future releases should separate experiment engine and GUI processes and add hardware timing verification.
