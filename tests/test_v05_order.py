import unittest
from collections import Counter
from joint_perception_lab.stimuli import make_main_trials, seed_from_session_label, order_quality_report, transition_counts


def stimuli():
    return [{'filename': f'{s}{n}{d}{p}.mp4', 'signal_present': int(s=='U'),
             'noise': n, 'direction': d, 'position': p, 'path': f'fake/{s}{n}{d}{p}.mp4'}
            for s in 'SU' for n in (24,48,96,192) for d in 'LR'
            for p in (-20,-10,0,10,20)]


class TestOrderV05(unittest.TestCase):
    def test_balancing_and_uniqueness_many_seeds(self):
        source=stimuli()
        for seed in (0,1,2,3,12345,20260607,2**64-1):
            trials=make_main_trials(source, seed=seed)
            self.assertEqual(len(trials),160)
            self.assertEqual([t['trial'] for t in trials],list(range(1,161)))
            for block in (1,2):
                subset=trials[(block-1)*80:block*80]
                self.assertEqual({t['block'] for t in subset},{block})
                self.assertEqual([t['block_trial'] for t in subset],list(range(1,81)))
                self.assertEqual({t['filename'] for t in subset},{s['filename'] for s in source})
                self.assertEqual(Counter(t['signal_present'] for t in subset),{0:40,1:40})
                self.assertEqual(set(transition_counts(subset,cyclic=True).values()),{20})
                self.assertEqual(sorted(transition_counts(subset).values()),[19,20,20,20])
            self.assertEqual(order_quality_report(trials)['total_trials'],160)

    def test_reproducibility_and_different_sessions(self):
        source=stimuli()
        seed=seed_from_session_label('dyad001')
        self.assertEqual(make_main_trials(source,seed),make_main_trials(list(reversed(source)),seed))
        self.assertNotEqual(seed,seed_from_session_label('dyad002'))
        self.assertNotEqual([t['filename'] for t in make_main_trials(source,seed)],
                            [t['filename'] for t in make_main_trials(source,seed+1)])

    def test_missing_stimulus_fails(self):
        with self.assertRaises(ValueError):
            make_main_trials(stimuli()[:-1])


if __name__=='__main__':
    unittest.main()
