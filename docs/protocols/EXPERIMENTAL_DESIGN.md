# Experimental design and presentation order (v0.6)

**Source of truth:** `joint_perception_lab/stimuli.py`, `experiment.py`, `bisection.py`, `gui.py` and `networking.py`. This describes *implemented software behaviour*, not a validated or approved experimental protocol.

## Modes

Each task supports **individual**, **shared host** and **shared client**. In shared mode, both participants view their own screen, respond privately, and exchange response records over TCP. Readiness barriers coordinate trial progression but do not guarantee simultaneous visual stimulus onset.

## Biological motion — main design

| Factor | Values |
|---|---|
| Signal | `U` intact walker (signal present = 1); `S` scrambled (signal absent = 0) |
| Noise | 24, 48, 96, 192 |
| Direction | `L`, `R` |
| Position | −20, −10, 0, +10, +20 |

2 × 4 × 2 × 5 = **80 unique main stimuli**. Every stimulus appears once in **Block 1** and once in **Block 2**: **160 main trials**. Each block has 40 present/40 absent trials, 20 trials per noise level and 10 per signal × noise combination. Block 2 starts after a participant-initiated break following Block 1.

**Order constraint:** Within each block, a randomised Eulerian circuit constructs an 80-item binary signal order with exactly 20 occurrences of each cyclic adjacent pair `00`, `01`, `10`, `11`. Since the actual block is linear, only 79 transitions are experienced; exactly one pair occurs 19 times and the other three occur 20 times. The final-to-first cyclic pair is a mathematical balancing device, **not a presented transition**. The transition across the block break is not balanced. The individual stimulus filenames are shuffled independently within each signal class and assigned to signal slots. Thus noise, direction and position have balanced marginal counts per block but **not controlled sequential transitions**. There is no same-video repeat within a block; the last video of Block 1 could equal the first of Block 2. This is constrained pseudorandomisation, **not** a full de Bruijn sequence.

**Practice:** 10 trials, five `U` and five `S`, selected with fixed seed `20260608`. The selection preferentially uses noise-12 files, falling back to noise-12 and noise-24 files if fewer than 10 noise-12 files are found. The practice sequence is fixed only if the stimulus folder contents and filenames are unchanged.

**Main seed:** Individual mode uses a new random 64-bit seed per session; shared mode derives the same 64-bit seed on both computers from the stripped session label using the first eight bytes of SHA-256(`JPL-v0.5-main:` + label), interpreted as an unsigned big-endian integer. Reusing a label reproduces the order. Each computer verifies a digest of the ordered practice/main filenames during handshake. The digest does not verify file bytes.

## Biological motion — one trial

1. Shared mode: pre-fixation TCP readiness barrier; individual mode does not use the barrier.
2. Fixation cross for approximately **500 ms** (`fixation_s=.5`).
3. Play all decoded source-video frames via OpenCV and PsychoPy ImageStim at native pixel dimensions (when screen fits), preserving aspect ratio; frame presentation scheduled from source FPS. The example reference video has 61 frames at ~30 fps (~2.033 s), but the actual file metadata are used per clip.
4. Display the question **“Did you see a human walker?”**, response **Y** (yes) or **N** (no), without a programmed response deadline. RT is calculated relative to the response-cue software timestamp, **not video onset**.
5. In shared mode, exchange responses and wait for the partner. During practice, show Correct/Incorrect feedback for ~800 ms. In main trials, show a black intertrial interval of **300, 350, 400, 450 or 500 ms** based on trial number modulo five (deterministic). The code does not impose an explicit post-response barrier for main biological-motion trials beyond the next trial's pre-fixation barrier.
6. After main trial 80, present a break screen; each participant presses Space and shared participants meet at the block-2 barrier.

**Timing caveat:** recorded PsychoPy flip-return timestamps approximate software presentation events; they are not photodiode-verified photon times. Frame intervals and video offset can differ from source-video duration.

## Line bisection — main design

73 marker targets `−900, −875, …, 875, 900` (step 25). Each target occurs **twice**, yielding **146 main trials** in a single continuous sequence. The target order is shuffled using fixed seed **20260427** for all individual and shared sessions; **no two-block organisation or transition balancing** is implemented for bisection. The main order is independently reproduced on both shared computers and checked via a digest.

Practice consists of three fixed targets **−750, 0, +750**; this is provisional and not verified against the historical MATLAB/Psychtoolbox procedure.

The horizontal line is labelled −1000 and +1000; a vertical marker appears at a linearly mapped target position. On sufficiently wide screens the line is 1000 screen pixels long, centred on a black background. No fixation cross is programmed. Participant enters a signed integer from −1000 to +1000 and presses Enter; invalid entries are rejected. The screen remains until a valid response. RT is measured from the first target display flip to Enter; typed updates redraw the target and do not reset the original RT onset.

Individual: Space before each trial. Shared: readiness barrier, independent numeric answers, response exchange, post-response barrier, 300–500 ms locally random black ITI, then either participant can press Space to trigger advancement to the next trial. These ITIs are not explicitly synchronised across computers. No 80-trial break is programmed for bisection.

**Caution:** This is a number-line marker localisation implementation, not yet a confirmed pixel-perfect replication of the original line-bisection experiment. Confirm geometry, labels, visual angle, trial timing and practice against the approved study protocol.
