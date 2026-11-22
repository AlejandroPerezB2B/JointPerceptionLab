# Numerical line-bisection protocol — v0.6 prototype

This implementation asks participants to estimate the numerical location of a marker on a horizontal number line. It should not be described as the validated historical line-bisection task until the original protocol has been reconciled.

**Stimulus:** black background, white horizontal line labelled −1000 and +1000; white vertical marker at a target from −900 to +900 in steps of 25 (73 levels). Line length is 1000 px on sufficiently wide displays, adjusted on narrower screens. Marker is positioned by a linear mapping from the numerical range to horizontal screen coordinates.

**Trials:** fixed practice −750, 0, +750; main 73 targets × two repetitions = 146 trials, fully shuffled with seed 20260427. The entire main sequence is the same for all sessions. No explicit break or blocked presentation.

**Response:** type signed integer −1000 to +1000, press Enter. Invalid entries prompt retry. RT from target flip to Enter. Outputs include response, signed error (response minus target) and absolute error. No feedback is given for valid responses.

**Shared:** host/client display same target sequence, respond privately; both responses are exchanged before the next trial. Either participant's Space advances both after the response barrier and locally sampled ITI. Synchronisation is TCP-based and unvalidated at the display hardware.

**Pending scientific decisions:** intended viewing distance, stimulus physical dimensions, endpoint labels, fixation, exact practice instructions, response mapping, timing and randomisation policy.

# Line Bisection Task

## Overview

Implementation of a computerized line bisection experiment designed to investigate whether performing a perceptual task alone or in the simultaneous presence of another person alters perceptual processing.

The experiment includes two experimental conditions:

1. **Individual condition**  
   Participants perform the task alone inside an isolated laboratory cubicle.

2. **Shared condition**  
   Two participants perform the exact same task simultaneously while seated side by side using interconnected laptops.

The perceptual task itself is identical across conditions. The critical manipulation concerns whether the task is performed:
- in isolation,
- or in a shared perceptual environment.

The experiment was designed to explore how commonly perceived environments may influence:
- spatial attention,
- perceptual organization,
- and potentially low-level perceptual processing.

---

# Stimuli

Participants are presented with:
- a horizontal white line,
- displayed centrally on a black background,
- intersected by a short vertical tick mark.

Participants must estimate where the tick is located along the line.

The response scale is:

```text
-1000 -------------------- 0 -------------------- +1000
```

where:
- `-1000` corresponds to the far-left end of the line,
- `0` corresponds to the exact center,
- `+1000` corresponds to the far-right end.

Participants type their estimate directly using the keyboard and confirm the response by pressing `ENTER`.

Example valid responses:

```text
-350
+420
+0
```

---

# Trial Structure

- 73 equally spaced tick positions
- ranging from `-900` to `+900`
- each repeated twice
- total: 146 trials

Two fixed pseudorandom trial orders are generated:
- one for the individual condition,
- one for the shared condition.

All participants receive exactly the same order within each condition.

---

# Timing

The task is self-paced.

Before each trial participants see:

```text
Press SPACE to start
```

Only the spacebar initiates the next trial.

After a valid response:
- a black screen appears,
- with a random inter-trial interval between 300–500 ms.

---

Participants:
- perform the same task,
- share the same temporal structure,
- but remain perceptually and behaviorally independent regarding their responses.

