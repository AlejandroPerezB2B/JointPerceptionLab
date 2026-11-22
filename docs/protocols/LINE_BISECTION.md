# Numerical line-bisection protocol — v0.6 prototype

This implementation asks participants to estimate the numerical location of a marker on a horizontal number line. It should not be described as the validated historical line-bisection task until the original protocol has been reconciled.

**Stimulus:** black background, white horizontal line labelled −1000 and +1000; white vertical marker at a target from −900 to +900 in steps of 25 (73 levels). Line length is 1000 px on sufficiently wide displays, adjusted on narrower screens. Marker is positioned by a linear mapping from the numerical range to horizontal screen coordinates.

**Trials:** fixed practice −750, 0, +750; main 73 targets × two repetitions = 146 trials, fully shuffled with seed 20260427. The entire main sequence is the same for all sessions. No explicit break or blocked presentation.

**Response:** type signed integer −1000 to +1000, press Enter. Invalid entries prompt retry. RT from target flip to Enter. Outputs include response, signed error (response minus target) and absolute error. No feedback is given for valid responses.

**Shared:** host/client display same target sequence, respond privately; both responses are exchanged before the next trial. Either participant's Space advances both after the response barrier and locally sampled ITI. Synchronisation is TCP-based and unvalidated at the display hardware.

**Pending scientific decisions:** intended viewing distance, stimulus physical dimensions, endpoint labels, fixation, exact practice instructions, response mapping, timing and randomisation policy.
