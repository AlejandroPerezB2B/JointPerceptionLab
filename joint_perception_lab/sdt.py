"""Hautus-corrected SDT without SciPy dependency."""
import csv
from pathlib import Path
from statistics import NormalDist


def summarize(rows):
    result = []
    groups = [('overall', rows)] + [(str(n), [r for r in rows if int(r['noise']) == n])
                                    for n in sorted({int(r['noise']) for r in rows})]
    for label, subset in groups:
        ns = sum(int(r['signal_present']) for r in subset)
        nn = len(subset) - ns
        if ns == 0 or nn == 0:
            continue
        hits = sum(int(r['hit']) for r in subset)
        fas = sum(int(r['false_alarm']) for r in subset)
        hr = (hits + .5) / (ns + 1)
        far = (fas + .5) / (nn + 1)
        zhit = NormalDist().inv_cdf(hr)
        zfa = NormalDist().inv_cdf(far)
        rts = [float(r['rt_s']) for r in subset if r.get('rt_s') not in ('', None)]
        result.append({'noise':label, 'n_signal':ns, 'n_noise':nn, 'hits':hits,
                       'false_alarms':fas, 'hit_rate':hr, 'false_alarm_rate':far,
                       'dprime':zhit-zfa, 'criterion_c':-.5*(zhit+zfa),
                       'accuracy':sum(int(r['correct']) for r in subset)/len(subset),
                       'mean_rt_s':sum(rts)/len(rts) if rts else ''})
    return result


def analyze_csv(csv_path):
    csv_path = Path(csv_path)
    with csv_path.open(newline='', encoding='utf-8') as f:
        rows = [r for r in csv.DictReader(f) if r['phase'] == 'main']
    results = summarize(rows)
    if results:
        dest = csv_path.with_name(csv_path.stem + '_sdt.csv')
        with dest.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=list(results[0]))
            writer.writeheader()
            writer.writerows(results)
        return dest
    raise ValueError('No valid main trials with both signal and noise conditions.')
