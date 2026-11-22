"""Biological-motion stimulus discovery and reproducible trial scheduling."""
import csv
import random
import re
from pathlib import Path

PATTERN = re.compile(r'^(?P<signal>[SU])(?P<noise>12|24|48|96|192)(?P<direction>[LR])(?P<position>-20|-10|0|10|20)\.(?:mp4|avi)$', re.I)
MAIN_NOISE = {24, 48, 96, 192}


def discover(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise ValueError(f'Stimulus folder not found: {folder}')
    stimuli = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in ('.mp4', '.avi'):
            continue
        match = PATTERN.fullmatch(path.name)
        if not match:
            raise ValueError(f'Unexpected video filename: {path.name}')
        fields = match.groupdict()
        stimuli.append({'filename': path.name, 'path': str(path.resolve()),
                        'signal_present': int(fields['signal'].upper() == 'U'),
                        'noise': int(fields['noise']), 'direction': fields['direction'].upper(),
                        'position': int(fields['position'])})
    if not stimuli:
        raise ValueError(f'No matching videos found in {folder}')
    # Avoid accidentally mixing two encodings of the same stimulus.
    stems = [Path(s['filename']).stem.lower() for s in stimuli]
    if len(stems) != len(set(stems)):
        raise ValueError('Duplicate stimulus stems detected (e.g. both AVI and MP4). Use one format.')
    return stimuli


def seed_from_session_label(label):
    """Stable cross-machine seed; use a NEW label for each dyad/session."""
    import hashlib
    label = label.strip()
    if not label:
        raise ValueError('Shared session label must not be empty.')
    return int.from_bytes(hashlib.sha256(('JPL-v0.5-main:'+label).encode('utf-8')).digest()[:8], 'big')


def transition_counts(sequence, cyclic=False):
    """Counts of consecutive binary signal transitions."""
    signals = [int(t['signal_present']) if isinstance(t, dict) else int(t) for t in sequence]
    counts = {f'{a}{b}': 0 for a in (0, 1) for b in (0, 1)}
    for a, b in zip(signals, signals[1:]):
        counts[f'{a}{b}'] += 1
    if cyclic and len(signals) > 1:
        counts[f'{signals[-1]}{signals[0]}'] += 1
    return counts


def _balanced_binary_order(rng, n_per_signal=40, transitions_per_pair=20):
    """Random Eulerian circuit over two symbols with exactly balanced cyclic bigrams.

    For each 80-trial block: 20 each of 00, 01, 10, 11 cyclic transitions.
    Linear transition counts differ by at most one due to the omitted wrap edge.
    """
    edges = {0: [0]*transitions_per_pair + [1]*transitions_per_pair,
             1: [0]*transitions_per_pair + [1]*transitions_per_pair}
    for values in edges.values():
        rng.shuffle(values)
    start = rng.randrange(2)
    stack = [start]
    circuit = []
    while stack:
        current = stack[-1]
        if edges[current]:
            stack.append(edges[current].pop())
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    result = circuit[:-1]
    assert len(result) == n_per_signal * 2
    assert result.count(0) == result.count(1) == n_per_signal
    assert all(v == transitions_per_pair for v in transition_counts(result, cyclic=True).values())
    return result


def make_main_trials(stimuli, seed=20260607, repeats=2, strict=True):
    """Two 80-trial blocks, each stimulus once; exactly balanced cyclic U/S transitions.

    Reproducible for a given seed and stimulus set. Other factors are shuffled
    within each signal category; their transitions are NOT explicitly balanced.
    """
    if repeats != 2:
        raise ValueError('v0.5 design requires exactly two repetitions/blocks.')
    main = [s for s in stimuli if s['noise'] in MAIN_NOISE]
    keys = [(s['signal_present'], s['noise'], s['direction'], s['position']) for s in main]
    if strict and (len(main) != 80 or len(set(keys)) != 80):
        raise ValueError(f'Expected 80 unique main stimuli; found {len(main)}. Check the stimulus folder.')
    if len(main) != 80 or len(set(keys)) != 80 or sum(s['signal_present'] for s in main) != 40:
        raise ValueError('Two-block transition balancing requires 40 unique stimuli per signal category.')
    rng = random.Random(seed)
    result = []
    # Sorting makes sequence independent of filesystem enumeration order.
    main.sort(key=lambda s: (s['signal_present'], s['noise'], s['direction'], s['position'], s['filename']))
    for block in (1, 2):
        pools = {signal: [dict(s) for s in main if s['signal_present'] == signal] for signal in (0, 1)}
        for pool in pools.values():
            rng.shuffle(pool)
        sequence = _balanced_binary_order(rng)
        for within_block, signal in enumerate(sequence, 1):
            stim = pools[signal].pop()
            result.append({**stim, 'repetition': block, 'block': block,
                           'block_trial': within_block, 'trial': len(result) + 1})
        assert not pools[0] and not pools[1]
    return result


def order_quality_report(trials):
    """Persist interpretable order checks, including block boundaries."""
    report = {'total_trials': len(trials), 'blocks': []}
    for block in (1, 2):
        subset = [t for t in trials if t.get('block') == block]
        report['blocks'].append({
            'block': block, 'trials': len(subset),
            'signal_present': sum(t['signal_present'] for t in subset),
            'signal_absent': len(subset)-sum(t['signal_present'] for t in subset),
            'unique_stimuli': len({t['filename'] for t in subset}),
            'transitions_linear': transition_counts(subset),
            'transitions_cyclic': transition_counts(subset, cyclic=True),
            'max_signal_run': max((len(list(g)) for _, g in __import__('itertools').groupby(t['signal_present'] for t in subset)), default=0),
        })
    return report

def make_practice_trials(stimuli, seed=20260608, count=10):
    # Prefer separate 12-dot videos, but fall back to main stimuli when unavailable.
    pool = [s for s in stimuli if s['noise'] == 12]
    if len(pool) < count:
        pool = [s for s in stimuli if s['noise'] in (12, 24)]
    rng = random.Random(seed)
    present = [s for s in pool if s['signal_present'] == 1]
    absent = [s for s in pool if s['signal_present'] == 0]
    if len(present) < count // 2 or len(absent) < count - count // 2:
        raise ValueError('Not enough balanced practice stimuli (need 5 intact and 5 scrambled).')
    chosen = rng.sample(present, count // 2) + rng.sample(absent, count - count // 2)
    rng.shuffle(chosen)
    return [{**s, 'trial': i + 1} for i, s in enumerate(chosen)]


def write_trials(path, trials):
    keys = ['trial', 'block', 'block_trial', 'filename', 'signal_present', 'noise', 'direction', 'position', 'repetition']
    with open(path, 'w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows([{key: row.get(key, '') for key in keys} for row in trials])
