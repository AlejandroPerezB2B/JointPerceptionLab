import tempfile
import unittest
from pathlib import Path
from joint_perception_lab.stimuli import discover, make_main_trials, make_practice_trials
from joint_perception_lab.storage import score_row
from joint_perception_lab.sdt import summarize


class CoreTests(unittest.TestCase):
    def test_trials(self):
        with tempfile.TemporaryDirectory() as tmp:
            for signal in ('S','U'):
                for noise in (12,24,48,96,192):
                    for direction in ('L','R'):
                        for position in (-20,-10,0,10,20):
                            Path(tmp, f'{signal}{noise}{direction}{position}.mp4').touch()
            items = discover(tmp)
            main = make_main_trials(items)
            self.assertEqual(len(main), 160)
            self.assertEqual(main, make_main_trials(items))
            practice = make_practice_trials(items)
            self.assertEqual(len(practice), 10)
            self.assertEqual(sum(x['signal_present'] for x in practice), 5)

    def test_sdt(self):
        rows = []
        for signal, response in ((1,'yes'),(1,'no'),(0,'yes'),(0,'no')):
            rows.append({'signal_present':signal, 'noise':24,
                         **score_row({'signal_present':signal}, response), 'rt_s':.5})
        summary = summarize(rows)
        self.assertEqual(summary[0]['dprime'], 0)


if __name__ == '__main__':
    unittest.main()
