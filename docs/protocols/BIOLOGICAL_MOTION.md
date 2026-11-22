# Biological-motion detection protocol

See [experimental design](EXPERIMENTAL_DESIGN.md) for complete factor levels, block composition, transition balancing and exact trial flow.

**Filename encoding:** `U`/`S` + noise level + `L`/`R` + signed position, e.g. `S24L0.mp4`. `U` = intact/present, `S` = scrambled/absent. Noise 12 is preferentially used for practice; 24, 48, 96 and 192 are main conditions.

**Presentation:** fixation 0.5 s → decoded video at native pixel size with frame scheduling from source FPS → yes/no response screen, Y/N unlimited → practice feedback 0.8 s or main ITI 0.30–0.50 s. The source videos themselves are not part of the public template.

**Design:** 80 distinct main-condition files, twice each, separated into two complete 80-trial blocks; binary walker presence/absence transitions cyclically balanced 20 per pair per block, with 79 linear transitions. Main order session-specific for individual participants, session-label deterministic for dyads. Practice uses a fixed seed and balanced five present/five absent selection.

**Dependent measures:** response, accuracy, hit/miss/false alarm/correct rejection, response-cue-locked RT, and timing QC. The SDT helper computes sensitivity and criterion; consult `sdt.py` for correction and aggregation details.

**Validation needed:** display-onset timing, frame pacing, cross-machine onset alignment, stimulus-file hashes, participant instruction approval and stimulus redistribution rights.

# Biological Motion Detection Task

This biological motion detection task is inspired by Szymanek, Senderecka, & Hohol (2026), *I see moving people: Expectations drive detection of biological motion in noisy point-light displays*, Psychonomic Bulletin & Review. The stimuli are based on the point-light biological motion displays originally used by van Elk (2013) and later used in that task.

The implementation includes two conditions:

1. **Individual condition**: one participant performs the task alone.
2. **Shared condition**: two participants perform the same task simultaneously on two interconnected laptops.

## Stimulus naming convention

Example:

```text
U48R-10.mp4
```

| Component | Meaning |
|---|---|
| `U` | unscrambled / intact walker / signal present |
| `S` | scrambled / no walker / signal absent |
| `24, 48, 96, 192` | number of distractor dots |
| `L` | leftward movement |
| `R` | rightward movement |
| `-20, -10, 0, 10, 20` | horizontal position |

## References

Hautus, M. J. (1995). Corrections for extreme proportions and their biasing effects on estimated values of d′. *Behavior Research Methods, Instruments, & Computers*, 27, 46–51.

Szymanek, A., Senderecka, M., & Hohol, M. (2026). *I see moving people: Expectations drive detection of biological motion in noisy point-light displays*. *Psychonomic Bulletin & Review*.

van Elk, M. (2013). Biological motion point-light display stimuli used as the basis for the task.

