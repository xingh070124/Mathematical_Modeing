# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 9: is the V5 temperature agreement a SURFACE-only number
registered under the label "maximum temperature difference"?  And what is the
true domain-max temperature difference between the two formulations?
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q4_verify import compare_formulations

print("=" * 76)
print("AUDIT PROBE 9: V5 temperature metric")
print("=" * 76)
for app, rmo, app3, lab in (("app3", "const", True, "app3 + frozen shrink"),
                            ("app4", "data", False, "app4 + shrink (prod)")):
    for M in (100, 200, 400):
        c = compare_formulations(M=M, t_end=21600.0, app=app, rad_mode=rmo,
                                 app3=app3)
        surf = abs(c["Tsurf_m"] - c["Tsurf_f"])
        print(f"  {lab:24s} M={M:3d}: registered 'max' dT = {surf:.4e} K "
              f"(surface pair);  true domain max|dT| = {c['max_dT']:.4e} K;  "
              f"mean|dT| = {c['mean_dT']:.4e} K")
print()
print("  registry key V5_dT_* is labelled '最大温度差' but stores the SURFACE")
print("  pair difference; the domain maximum is a different (larger) number.")
