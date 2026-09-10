"""
AUDIT SCRIPT 7 -- extra: the user's MOISTURE discretisation is unstable on its own.

The temperature is always solved with the repaired diagonal, so any blow-up here
comes from the moisture scheme (wrong b_i diagonal and/or nodal D used on both
faces).  Run:  python src/audit_moist_stab.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import Dfun, make_env, run  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

if __name__ == "__main__":
    fT, fC = make_env("pchip")
    print("moisture-only variants, M=200, t_end=1800 s, temperature repaired throughout")
    print(f"{'dt':>8} {'Cdiag':>6} {'Dface':>6} {'t_blow':>8} {'C_min':>14} {'C_max':>14}")
    for dt in (0.1, 0.05, 0.01, 0.001):
        for Cdiag, Dface in (("fixed", "fixed"), ("fixed", "node"),
                             ("user", "fixed"), ("user", "node")):
            r = run(200, dt, 1800.0, fT, fC, Tdiag="fixed", Cdiag=Cdiag, Dface=Dface,
                    blow_tol=1e120)
            print(f"{dt:>8} {Cdiag:>6} {Dface:>6} {str(r['t_blow']):>8} "
                  f"{r['C'].min():>14.6e} {r['C'].max():>14.6e}")
    print()
    print("theoretical growth rates of the moisture operator at M=200, C=C0:")
    D0v = float(Dfun(2.55))
    dr = 0.02 / 200
    print(f"  D(C0) = {D0v:.6e} m^2/s ; D/dr^2 = {D0v/dr**2:.6f} 1/s")
    print(f"  user's moisture diagonal deficit is the same |a_i|, largest ~ D/dr^2 = {D0v/dr**2:.4f} 1/s")
    print(f"  => at dt=0.1 s the moisture amplification per step is ~1/(1-dt*lambda) with "
          f"dt*lambda_max={0.1*D0v/dr**2:.5f}")

