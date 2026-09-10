"""
AUDIT SCRIPT 6 -- clean spatial orders for the surface-node variants, and the time
accuracy of the moisture field at the user's recommended dt.

(A) with dt small enough that the implicit-Euler temporal plateau sits well below
    every spatial error, measure the observed order of:
      halfcv   -- exact node-centred half control volume [R-dr/2, R]
      user     -- the coefficients as the user wrote them (the M->inf limit)
    against the analytic Robin-cylinder series (const T_inf = 50 C).

(B) face-averaged (conservative) moisture scheme, M fixed: error at the five output
    radii as a function of dt, to see whether dt = 0.1 s (user) / 0.125 s (repo
    production) resolves 4 decimals in C.

Run:  python src/audit_orders.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (ALPHA, R0, T0K, make_env, run)          # noqa: E402
from audit_extra import BI, T_CONST, run_T, series_eigs, theta_series  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))


def partA():
    hr("(A) spatial convergence of the surface-node variants, dt=0.002 s (t=300 s)")
    lam, Cn = series_eigs(BI, 400)
    t_chk, dt = 300.0, 0.002
    Fo = ALPHA * t_chk / R0 ** 2
    fT = lambda tt: T_CONST
    Ms = (25, 50, 100, 200, 400, 800)
    errs = {"halfcv": [], "user": []}
    for M in Ms:
        for s in ("halfcv", "user"):
            r, T = run_T(M, dt, t_chk, fT, surface=s)
            e = np.max(np.abs(T - (T_CONST + (T0K - T_CONST) * theta_series(r / R0, Fo, lam, Cn))))
            errs[s].append(e)
        print(f"  M={M:>4}: halfcv={errs['halfcv'][-1]:.6e}  user={errs['user'][-1]:.6e}  "
              f"ratio={errs['user'][-1]/errs['halfcv'][-1]:.1f}")
    for s in ("halfcv", "user"):
        e = errs[s]
        print(f"  observed order {s:>7}: " + " ".join(f"{np.log2(e[i]/e[i+1]):.3f}" for i in range(len(e)-1)))
    print("  (dt=0.002 s gives an implicit-Euler plateau of ~1e-5 K at all M; the 'user' variant's")
    print("   errors are 1e-2..1e-3 K, so its order is not contaminated)")


def partB():
    hr("(B) time accuracy of the moisture field at dt=0.1/0.125 s (face-averaged D, conservative)")
    fT, fC = make_env("pchip")
    pr = np.array([0.0, 0.005, 0.01, 0.015, 0.02])
    t_end = 1800.0
    for M in (400,):
        ref = run(M, 0.004, t_end, fT, fC, Tdiag="fixed", Cdiag="fixed", Dface="fixed")
        Cref = np.interp(pr, ref["r"], ref["C"])
        Tref = np.interp(pr, ref["r"], ref["T"])
        print(f"  M={M}; reference dt=0.004 s")
        print(f"  reference C = " + " ".join(f"{v:.6f}" for v in Cref))
        print(f"  {'dt[s]':>8} {'max|dC| [kg/kg]':>17} {'max|dT| [K]':>12} "
              f"{'order(C)':>9}   C at 0/0.5/1/1.5/2 cm")
        prev = None
        for dt in (1.0, 0.5, 0.25, 0.125, 0.1, 0.05, 0.02, 0.01):
            o = run(M, dt, t_end, fT, fC)
            Cm = np.interp(pr, o["r"], o["C"])
            Tm = np.interp(pr, o["r"], o["T"])
            eC = np.max(np.abs(Cm - Cref))
            eT = np.max(np.abs(Tm - Tref))
            oC = "" if prev is None else f"{np.log2(prev/eC):.3f}"
            prev = eC
            print(f"  {dt:>8.4f} {eC:>17.6e} {eT:>12.3e} {oC:>9}   "
                  + " ".join(f"{v:.6f}" for v in Cm))


if __name__ == "__main__":
    partA()
    partB()
