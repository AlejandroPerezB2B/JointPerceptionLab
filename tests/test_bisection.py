from collections import Counter
from pathlib import Path
import tempfile
import unittest
from joint_perception_lab.bisection import POSITIONS, make_order, order_digest, PRACTICE_POSITIONS, write_order, save_trial

class BisectionTests(unittest.TestCase):
    def test_positions(self):
        self.assertEqual(len(POSITIONS),73)
        self.assertEqual((POSITIONS[0],POSITIONS[-1]),(-900,900))
    def test_order(self):
        a=make_order(20260427)
        self.assertEqual(len(a),146)
        self.assertTrue(all(v==2 for v in Counter(x['target_position'] for x in a).values()))
        self.assertEqual(a,make_order(20260427))
        self.assertNotEqual(a,make_order(20260428))
    def test_digest(self):
        self.assertEqual(order_digest(make_order(20260427),PRACTICE_POSITIONS),order_digest(make_order(20260427),PRACTICE_POSITIONS))
    def test_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);write_order(path,make_order(20260427),PRACTICE_POSITIONS)
            self.assertEqual(len((path/'main_order.csv').read_text().splitlines()),147)
            save_trial(path/'bisection_trials.csv',{'trial':1,'response_integer':-100})
            self.assertIn('-100',(path/'bisection_trials.csv').read_text())
if __name__=='__main__':unittest.main()
