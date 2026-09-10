"""
AUDIT SCRIPT 5 -- two things the claims do NOT state:

  (A) C8 is claimed "correct at least asymptotically".  The user's surface numbers
      are the M->inf limit of the node-centred HALF-CV balance.  At finite M they
      are NOT the coefficients of any exactly conservative FV balance.  Measured
      here: (i) the discrete global energy-balance residual, (ii) the convergence
      order of each surface variant against the analytic Robin-cylinder series.

  (B) The user recommends M=200, dt=0.1 s.  Even with b_i repaired, is that grid
      accurate enough for the 4-decimal output required by 附件3?

Run:  python src/audit_extra.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import solve_banded
from scipy.optimize import brentq
from scipy.special import j0, j1

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (ALPHA, CP, HCONV, HM, KCOND, R0, RHO, T0K, geom,  # noqa: E402
                          make_env, run)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))
T_CONST_C = 50.0
T_CONST = T_CONST_C + 273.15
BI = HCONV * R0 / KCOND


# ---------------------------------------------------------------- analytic
def series_eigs(Bi, n=400):
    """Roots of lam*J1(lam) = Bi*J0(lam) + coefficients (Carslaw & Jaeger)."""
    f = lambda lam: lam * j1(lam) - Bi * j0(lam)
    grid = np.linspace(1e-8, 500.0, 400001)
    v = f(grid)
    roots = []
    for k in range(len(grid) - 1):
        if v[k] == 0.0:
            roots.append(grid[k])
        elif v[k] * v[k + 1] < 0:
            roots.append(brentq(f, grid[k], grid[k + 1], xtol=1e-15))
        if len(roots) >= n:
            break
    lam = np.array(roots[:n])
    Cn = 2 * j1(lam) / (lam * (j0(lam) ** 2 + j1(lam) ** 2))
    return lam, Cn


def theta_series(rho, Fo, lam, Cn):
    rho = np.atleast_1d(rho)
    th = np.zeros_like(rho)
    for l, c in zip(lam, Cn):
        th += c * j0(l * rho) * np.exp(-l ** 2 * Fo)
    return th


# ---------------------------------------------------------------- variant solver
def banded(a, b, c, d):
    n = len(d)
    ab = np.zeros((3, n))
    ab[0, 1:] = c[:-1]
    ab[1, :] = b
    ab[2, :-1] = a[1:]
    return solve_banded((1, 1), ab, d)


def run_T(M, dt, t_end, Tinf_func, surface="halfcv"):
    """Temperature only.  surface in {'halfcv','user','fullcell'}."""
    dr, r, V, A_m, A_p = geom(M)
    n = M + 1
    nsteps = int(round(t_end / dt))
    ii = np.arange(1, M)
    T = np.full(n, T0K)
    a, b, c = np.zeros(n), np.zeros(n), np.zeros(n)
    b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0])
    c[0] = -ALPHA * A_p[0] / (dr * V[0])
    a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
    b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
    c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
    a[M] = -ALPHA * A_m[M] / (dr * V[M])
    if surface == "halfcv":
        b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M])
        g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * V[M])
    elif surface == "user":
        # the coefficients exactly as the user wrote them
        a[M] = -2 * ALPHA / dr ** 2
        b[M] = 1 / dt + 2 * ALPHA / dr ** 2
        g_h = 2 * ALPHA * HCONV / (KCOND * dr)
    elif surface == "fullcell":
        # cell-centred FULL CV [R-dr, R] (the variant the withdrawn hypothesis used)
        VF = np.pi * (R0 ** 2 - (R0 - dr) ** 2)
        a[M] = -ALPHA * 2 * np.pi * (R0 - dr) / (dr * VF)
        b[M] = 1 / dt + ALPHA * 2 * np.pi * (R0 - dr) / (dr * VF)
        g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * VF)
    else:
        raise ValueError(surface)
    b[M] += g_h
    for k in range(nsteps):
        tn1 = (k + 1) * dt
        Tinf = float(Tinf_func(tn1))
        d = T / dt
        d[M] += g_h * Tinf
        T = banded(a, b, c, d)
    return r, T


def energy_residual(M, dt, surface, Tinf=T_CONST, nsteps=1):
    """Exact discrete global energy balance residual of one implicit-Euler step.

    For the assembly to be conservative, sum_i V_i (T_i^{n+1}-T_i^n)/dt  must equal
    -2*pi*R*h*(T_M^{n+1} - Tinf)  (convection is the only boundary flux).
    """
    dr, r, V, A_m, A_p = geom(M)
    n = M + 1
    ii = np.arange(1, M)
    T = np.full(n, T0K) + 1.0 * np.cos(np.pi * r / R0)   # a non-trivial profile
    a, b, c = np.zeros(n), np.zeros(n), np.zeros(n)
    b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0])
    c[0] = -ALPHA * A_p[0] / (dr * V[0])
    a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
    b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
    c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
    if surface == "halfcv":
        a[M] = -ALPHA * A_m[M] / (dr * V[M])
        b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M])
        g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * V[M])
    elif surface == "user":
        a[M] = -2 * ALPHA / dr ** 2
        b[M] = 1 / dt + 2 * ALPHA / dr ** 2
        g_h = 2 * ALPHA * HCONV / (KCOND * dr)
    b[M] += g_h
    d = T / dt
    d[M] += g_h * Tinf
    Tn = banded(a, b, c, d)
    lhs = float(np.sum(V * (Tn - T) / dt))
    rhs = -2 * np.pi * R0 * HCONV * (Tn[M] - Tinf) / (RHO * CP)
    return lhs, rhs, abs(lhs - rhs) / abs(rhs)


# ---------------------------------------------------------------- (A)
def partA():
    hr("(A) surface-node variants: exact energy balance and convergence order")
    lam, Cn = series_eigs(BI, 400)
    rho_t = np.linspace(0, 0.9, 37)
    rec = np.array([theta_series(rr, 1e-14, lam, Cn)[0] for rr in rho_t])
    print(f"  analytic series self-check (interior, rho<=0.9): "
          f"max|sum C_n J0(lam_n rho) - 1| = {np.max(np.abs(rec-1.0)):.3e}  (n_modes={len(lam)})")
    rho_b = np.linspace(0, 1, 41)
    recb = np.array([theta_series(rr, 1e-14, lam, Cn)[0] for rr in rho_b])
    print(f"  same including the boundary (rho=1, where the series converges only as 1/lam): "
          f"{np.max(np.abs(recb-1.0)):.3e}")
    print(f"  roots 1-5: {np.round(lam[:5], 6)}")
    print(f"  Bi = {BI:.6f}")

    print("\n  exact discrete global energy balance, one step, dt=0.05 s:")
    print(f"  {'M':>5} {'surface':>9} {'lhs sum V dT/dt':>19} {'-2 pi R h (T_M-Tinf)':>22} {'rel gap':>12}")
    for M in (100, 200, 400, 800):
        for s in ("halfcv", "user"):
            lhs, rhs, gap = energy_residual(M, 0.05, s)
            print(f"  {M:>5} {s:>9} {lhs:>19.10e} {rhs:>22.10e} {gap:>12.3e}")

    print("\n  convergence vs the analytic Robin-cylinder series (const T_inf=50 C, t=300 s):")
    t_chk = 300.0
    Fo = ALPHA * t_chk / R0 ** 2
    print(f"  Fo = {Fo:.6f}")
    fT = lambda tt: T_CONST
    print(f"  {'M':>5} " + "".join(f"{s:>18}" for s in ("halfcv", "user", "fullcell")))
    errs = {}
    for M in (50, 100, 200, 400, 800, 1600):
        row = []
        for s in ("halfcv", "user", "fullcell"):
            r, T = run_T(M, 0.01, t_chk, fT, surface=s)
            e = np.max(np.abs(T - (T_CONST + (T0K - T_CONST) * theta_series(r / R0, Fo, lam, Cn))))
            errs.setdefault(s, []).append(e)
            row.append(e)
        print(f"  {M:>5} " + "".join(f"{e:>18.6e}" for e in row))
    print("  observed order (log2 of successive error ratios):")
    for s in ("halfcv", "user", "fullcell"):
        e = errs[s]
        print(f"    {s:>8}: " + " ".join(f"{np.log2(e[i]/e[i+1]):.3f}" for i in range(len(e)-1)))


# ---------------------------------------------------------------- (B)
def partB():
    hr("(B) is the user's recommended grid (M=200, dt=0.1) adequate after the b_i repair?")
    fT, fC = make_env("pchip")
    pr = np.array([0.0, 0.005, 0.01, 0.015, 0.02])
    t_end = 1800.0
    ref = run(1600, 0.0125, t_end, fT, fC, moisture=False)
    Tref = np.interp(pr, ref["r"], ref["T"])
    print("  temperature only (heat equation is independent of moisture)")
    print(f"  reference: M=1600, dt=0.0125 s ; production in repo: M=800, dt=0.125 s")
    print(f"  {'M':>5} {'dt[s]':>8} {'max|dT| [K]':>14} {'T(r,t=1800) degC at 0/0.5/1/1.5/2 cm':>52}")
    for M, dt in ((200, 0.1), (200, 0.05), (400, 0.1), (800, 0.125), (800, 0.1),
                  (800, 0.05), (800, 0.0125)):
        o = run(M, dt, t_end, fT, fC, moisture=False)
        Tm = np.interp(pr, o["r"], o["T"])
        print(f"  {M:>5} {dt:>8.4f} {np.max(np.abs(Tm-Tref)):>14.6e} "
              + " ".join(f"{v:>10.4f}" for v in Tm - 273.15))
    print(f"  reference values                              "
          + " ".join(f"{v:>10.4f}" for v in Tref - 273.15))


if __name__ == "__main__":
    partA()
    partB()
