"""Audit main trial orders without launching the GUI.

Usage: python tools/audit_orders.py --stimuli stimuli/biological_motion --seed 20260607
"""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from joint_perception_lab.stimuli import discover, make_main_trials, order_quality_report
from joint_perception_lab.bisection import make_order

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--stimuli',default=None)
    p.add_argument('--seed',type=int,default=20260607)
    a=p.parse_args()
    print('Bisection:',len(make_order(20260427)),'trials, 73 positions twice')
    if a.stimuli:
        order=make_main_trials(discover(a.stimuli),seed=a.seed)
        print(json.dumps(order_quality_report(order),indent=2))
    else:
        print('Specify --stimuli to audit biological-motion order.')
if __name__=='__main__': main()
