# Reproducibility and trial-order audit

## Seeds

- Biological-motion practice: fixed `20260608` (same order for same stimulus folder).
- Biological-motion individual main: a new 64-bit seed generated with `secrets.randbits(64)` for each session.
- Biological-motion shared main: SHA-256 of `JPL-v0.5-main:` plus the stripped shared session label, first eight bytes as unsigned big-endian integer. Identical labels produce identical seeds.
- Bisection main: fixed `20260427` for all sessions, including shared. The `shared_seed()` helper in `bisection.py` exists but is **not used by the v0.6 GUI**.

## Auditable outputs

Each session writes `session.json` and `main_order.csv`; biological motion also writes `practice_order.csv`, `trials.csv`, `frame_events.jsonl` and `timing_report.json`. Bisection writes `practice_order.csv` and `bisection_trials.csv`. Biological-motion session metadata includes `order_quality` transition counts and maximum signal run per block.

## Exact transition-balancing algorithm

The algorithm creates a directed multigraph with two vertices (0 absent, 1 present), 20 copies of each directed edge (00, 01, 10, 11), randomises outgoing-edge order, and constructs an Eulerian circuit. Removing the duplicated closing vertex gives 80 signal labels. Every cyclic bigram occurs 20 times; exactly one linear bigram occurs 19 times. Within each signal group, the 40 unique filenames are independently shuffled and assigned to the 40 slots. This is **first-order signal transition balancing**, not higher-order de Bruijn balancing.

## Integrity caveats

Shared biological-motion handshakes hash ordered filenames, **not video contents**. Preserve exact authorised video assets across machines and consider a file SHA-256 manifest for future releases. Shared bisection uses a digest of practice and main target order. Session label reuse reuses biological-motion main order.

## Tests

From the project directory with the virtual environment active:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Do not treat passing unit tests as hardware display validation.
