"""
AUDIT SCRIPT 3 -- where does the user's scheme actually become bounded, and when
exactly does it reach non-finite values?

The claim under test (C6, second half): "For dt greater than 2/lambda ~ 0.119 s the
modulus is bounded but the solution sign-oscillates and collapses."

Implicit-Euler update operator M(dt) = (I - dt*A)^-1 has eigenvalues
1/(1 - dt*lambda).  |1/(1-dt*l)| >= 1 for every l<0 and for l in (0, 2/dt).
Hence the scheme is bounded for a given dt iff 2/dt <= min{lambda > 0} =: l_min^+,
i.e. iff dt >= dt* = 2/l_min^+.

Run:  python src/audit_dtstar.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import T0K, make_env, run  # noqa: E402
from audit_eigs_dt import operators            # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))

if __name__ == "__main__":
    M = 200
    Au = operators(M)[1]
    lam = np.linalg.eigvals(Au).real
    pos = np.sort(lam[lam > 0])
    neg = lam[lam < 0]
    print(f"M={M}: {len(pos)} positive eigenvalues, {len(neg)} negative")
    print(f"  lambda_max      = {lam.max():.8f}")
    print(f"  lambda_min^+    = {pos[0]:.8f}   (smallest positive eigenvalue)")
    print(f"  lambda_min      = {lam.min():.8f}")
    dt_star = 2.0 / pos[0]
    print(f"  => bounded only for dt >= 2/lambda_min^+ = {dt_star:.4f} s")
    print(f"  (the claim says 'bounded for dt > 2/lambda_max = {2/lam.max():.4f} s')")

    print("\n  max_lambda |1/(1-dt*lambda)| over a fine dt grid:")
    print(f"  {'dt[s]':>10} {'g_max':>14} {'argmax lambda':>16} {'bounded?':>9}")
    for dt in (0.1, 0.119, 0.12, 0.5, 1.0, 2.0, 4.0, 6.0, 7.0, 7.4, 7.49, 7.5, 7.55, 8.0, 10.0):
        g = 1.0 / np.abs(1.0 - dt * lam)
        print(f"  {dt:>10.4f} {g.max():>14.6e} {lam[np.argmax(g)]:>16.8f} {str(bool(g.max()<=1.0)):>9}")

    # exact numerical blow-up time (true Inf/NaN), M=200, t_end=200 s
    hr("Exact non-finite time of the user's scheme (no artificial tolerance)")
    fT, fC = make_env("pchip")
    for dt in (0.1, 0.0005, 0.05, 0.5, 1.0, 5.0, 7.5, 10.0, 20.0):
        with np.errstate(over="ignore", invalid="ignore"):
            r = run(M, dt, 200.0, fT, fC, Tdiag="user", moisture=False, blow_tol=1e300)
        T = r["T"]
        finite = np.isfinite(T)
        print(f"  dt={dt:>8.5g}: ok={r['ok']}  t_blow={r['t_blow']}  "
              f"all-finite-at-end={bool(finite.all())}  "
              f"T_end range=[{np.nanmin(T):.4f}, {np.nanmax(T):.4f}] K")
    hr("Bounded tail check: dt >= dt*, user's scheme, does it collapse to 0 K?")
    for dt in (7.5, 10.0, 20.0):
        for t_end in (60.0, 600.0, 3600.0):
            with np.errstate(over="ignore", invalid="ignore"):
                r = run(M, dt, t_end, fT, fC, Tdiag="user", moisture=False, blow_tol=1e300)
            T = r["T"]
            print(f"  dt={dt:>6.1f} t={t_end:>7.0f}s: T in [{np.nanmin(T):+.6e}, {np.nanmax(T):+.6e}] K  "
                  f"max|T|={np.nanmax(np.abs(T)):.4e}  (physical range is [301.15, 301.68] K)")
