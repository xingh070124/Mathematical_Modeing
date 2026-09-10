"""
AUDIT SCRIPT 8 -- reconciliation of the repo's E4 / E5 numbers against my own.

E4 (registry rows E30/E31/E32) reports the "cell" surface variant error vs the
analytic series.  My own re-implementation gets numbers ~10x smaller.  One of the
two implementations is wrong; this script decides which by running both side by
side through the same reference series.

E5 (rows E40/E41/E42) reports the moisture blow-up time.  Their criterion is "first
non-finite value"; mine was "first value above 1e120".  Both are computed here.

Run:  python src/audit_reconcile_e4.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q1_energy_check as qec                       # noqa: E402
from audit_common import (ALPHA, CP, HCONV, KCOND, RHO, R0, T0K, make_env,  # noqa: E402
                          run)
from audit_extra import BI, T_CONST, series_eigs, theta_series  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))
T_CHK = 300.0
FO = ALPHA * T_CHK / R0 ** 2


def errs_for(M, dt, variant):
    """My own solver, my own analytic series."""
    lam, Cn = series_eigs(BI, 400)
    from audit_extra import run_T
    r, T = run_T(M, dt, T_CHK, lambda tt: T_CONST, surface=variant)
    Tan = T_CONST + (T0K - T_CONST) * theta_series(r / R0, FO, lam, Cn)
    return float(np.max(np.abs(T - Tan)))


def errs_repo(M, dt, variant):
    """The repo's own function, evaluated against MY analytic series."""
    lam, Cn = series_eigs(BI, 400)
    r, T = qec.solve_surface_variant(M, dt, T_CHK, T_CONST, variant)
    Tan = T_CONST + (T0K - T_CONST) * theta_series(r / R0, FO, lam, Cn)
    return float(np.max(np.abs(T - Tan)))


def errs_repo_vs_repo_series(M, dt, variant):
    """The repo's function against the repo's analytic series (their exact E4)."""
    lam, Cn = qec.robin_cylinder_eigen(BI, n_modes=400)
    r, T = qec.solve_surface_variant(M, dt, T_CHK, T_CONST, variant)
    Tan = T_CONST + (T0K - T_CONST) * qec.robin_cylinder_theta(r / R0, FO, lam, Cn)
    return float(np.max(np.abs(T - Tan)))


if __name__ == "__main__":
    hr("E4 reconciliation: cell (user) surface variant")
    print(f"  {'M':>5} {'dt':>8} {'mine':>14} {'repo fn, my series':>20} "
          f"{'repo fn + repo series':>22} {'ratio repo/mine':>16}")
    for M in (400, 800, 1600):
        for dt in (0.02, 0.002, 0.0005):
            a = errs_for(M, dt, "user")
            b = errs_repo(M, dt, "cell")
            c = errs_repo_vs_repo_series(M, dt, "cell")
            print(f"  {M:>5} {dt:>8.4f} {a:>14.6e} {b:>20.6e} {c:>22.6e} {c/a:>16.4f}")

    hr("which analytic series is right? compare the two series implementations")
    lam_a, Cn_a = series_eigs(BI, 400)
    lam_b, Cn_b = qec.robin_cylinder_eigen(BI, n_modes=400)
    print(f"  mine : n={len(lam_a)} first 3 = {np.round(lam_a[:3], 8)}")
    print(f"  repo : n={len(lam_b)} first 3 = {np.round(lam_b[:3], 8)}")
    rr = np.linspace(0, 1, 11)
    ta = theta_series(rr, FO, lam_a, Cn_a)
    tb = qec.robin_cylinder_theta(rr, FO, lam_b, Cn_b)
    print(f"  max|theta_mine - theta_repo| over r/R in [0,1] = {np.max(np.abs(ta-tb)):.3e}")
    # independent high-accuracy reference: increase modes
    lam_c, Cn_c = series_eigs(BI, 1500)
    tc = theta_series(rr, FO, lam_c, Cn_c)
    print(f"  with 1500 modes (mine) max|theta_400 - theta_1500| = {np.max(np.abs(ta-tc)):.3e}")
    print(f"  theta(rho=1): mine(400)={ta[-1]:.10f} repo(400)={tb[-1]:.10f} mine(1500)={tc[-1]:.10f}")
    print(f"  repo D1 log quoted theta(rho=1)=0.562338928033")

    hr("E5 reconciliation: first NON-FINITE time of the user's moisture diagonal")
    fT, fC = make_env("pchip")
    print(f"  {'dt':>7} {'mine (blow_tol=inf)':>20} {'repo E5':>10} {'mine (blow_tol=1e120)':>22}")
    for dt in (0.1, 0.05, 0.01):
        r1 = run(200, dt, 1800.0, fT, fC, Tdiag="fixed", Cdiag="user", Dface="fixed",
                 blow_tol=np.inf)
        r2 = run(200, dt, 1800.0, fT, fC, Tdiag="fixed", Cdiag="user", Dface="fixed",
                 blow_tol=1e120)
        tb, _, _ = qec.solve_q1_user_diag_moist(200, dt, 1800.0, qec.Env(*qec.load_attachment1()))
        print(f"  {dt:>7} {str(r1['t_blow']):>20} {str(tb):>10} {str(r2['t_blow']):>22}")
