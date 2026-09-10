"""
AUDIT SCRIPT 2 -- Claims C5 (anti-dissipative operator) and C6 (divergence for all dt).

A_corr / A_user are re-built here from scratch.  Conventions identical to the
repo's E1 check so the numbers are comparable, plus two additions the claim does
not mention:
  * the operator WITH the Robin convection term (the one actually solved);
  * the full spectrum, used to compute max_dt |1/(1-dt*lambda)| -- the true
    implicit-Euler growth factor per step -- over a wide range of dt.

Run:  python src/audit_eigs_dt.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (ALPHA, C0, CP, HCONV, RHO, R0, T0K, geom,  # noqa: E402
                          make_env, run)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))


def operators(M, with_robin=False):
    dr, r, V, A_m, A_p = geom(M)
    n = M + 1
    Ac = np.zeros((n, n))
    Au = np.zeros((n, n))
    Ac[0, 0] = -ALPHA * A_p[0] / (dr * V[0])
    Ac[0, 1] = ALPHA * A_p[0] / (dr * V[0])
    ii = np.arange(1, M)
    Ac[ii, ii - 1] = ALPHA * A_m[ii] / (dr * V[ii])
    Ac[ii, ii] = -ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
    Ac[ii, ii + 1] = ALPHA * A_p[ii] / (dr * V[ii])
    Ac[M, M - 1] = ALPHA * A_m[M] / (dr * V[M])
    Ac[M, M] = -ALPHA * A_m[M] / (dr * V[M])
    Au[:] = Ac
    Au[ii, ii] = -ALPHA * A_p[ii] / (dr * V[ii])      # user's written diagonal
    if with_robin:
        g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * V[M])
        Ac[M, M] -= g_h
        Au[M, M] -= g_h
    return Ac, Au


def c5():
    hr("C5. Spectrum of the implied spatial operator (conduction only, no Robin term)")
    print(f"  alpha/dr^2 at M=200 (dr={R0/200:g} m) = {ALPHA/(R0/200)**2:.6f} 1/s")
    for M in (50, 100, 200, 400, 800):
        Ac, Au = operators(M, with_robin=False)
        ev_c = np.linalg.eigvals(Ac)
        ev_u = np.linalg.eigvals(Au)
        dr = R0 / M
        print(f"  M={M:>4}: max Re l_corr = {ev_c.real.max():+.6e}   max Re l_user = {ev_u.real.max():+.6e}"
              f"   l_user/(alpha/dr^2) = {ev_u.real.max()/(ALPHA/dr**2):.6f}"
              f"   min Re l_user = {ev_u.real.min():+.6e}"
              f"   imag part max = {np.abs(ev_u.imag).max():.3e}")
    Ac, Au = operators(200, with_robin=True)
    ev_c = np.linalg.eigvals(Ac)
    ev_u = np.linalg.eigvals(Au)
    g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * geom(200)[2][200])
    print(f"  with Robin term (g_h={g_h:.6f} 1/s), M=200:")
    print(f"      max Re l_corr = {ev_c.real.max():+.6e}  (strictly dissipative? "
          f"{ev_c.real.max() < 0})")
    print(f"      max Re l_user = {ev_u.real.max():+.6e}")
    return Au


def c6_spectral(Au):
    hr("C6a. Implicit-Euler growth factor from the spectrum: max_lambda |1/(1-dt*lambda)|")
    ev = np.linalg.eigvals(Au)
    lam = ev.real
    print(f"  spectrum of A_user (M=200): [{lam.min():.6e}, {lam.max():.6e}] 1/s")
    print(f"  {2/lam.max():.6f} s = 2/lambda_max ;  1/lambda_max = {1/lam.max():.6f} s")
    print(f"  {'dt[s]':>12} {'max|1/(1-dt*l)|':>18} {'argmax lambda':>16} {'>=1 ?':>7} {'g^N(60s)':>12}")
    for dt in (1e-4, 5e-4, 1e-3, 5e-3, 1e-2, 5e-2, 0.1, 0.1189, 0.12, 0.15, 0.2, 0.3, 0.5,
               1.0, 2.0, 5.0, 10.0, 50.0, 100.0, 1e3, 1e4, 1e5, 1e6):
        g = 1.0 / np.abs(1.0 - dt * lam)
        k = int(np.argmax(g))
        n = int(60.0 / dt)
        gg = g.max() ** n
        print(f"  {dt:>12.6g} {g.max():>18.6e} {lam[k]:>16.8f} {str(g.max()>=1.0):>7} {gg:>12.4e}")
    return lam


def c6_numeric(fT, fC):
    hr("C6b. Actual runs of the user's scheme (M=200, pure conduction, t_end=60 s)")
    print(f"  {'dt[s]':>9} {'blow-up time':>14} {'T_max at stop':>16} {'note':>34}")
    for dt in (0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.1189, 0.15, 0.2, 0.5,
               1.0, 5.0, 20.0):
        r = run(200, dt, 60.0, fT, fC, Tdiag="user", moisture=False, blow_tol=1e120)
        note = ""
        if r["ok"]:
            T = r["T"]
            note = (f"bounded: T in [{T.min():.4f},{T.max():.4f}] K, "
                    f"span={T.max()-T.min():.3e}, sign-change-free={np.all(T>0)}")
        else:
            note = "non-finite / overflow"
        print(f"  {dt:>9.6g} {('%.2f' % r['t_blow']) if r['t_blow'] is not None else 'no blow-up':>14}"
              f" {np.abs(r['T']).max():>16.6e} {note:>34}")
    hr("C6c. The same dt values with the CORRECTED diagonal (control)")
    for dt in (0.0001, 0.0005, 0.1, 1.0, 20.0):
        r = run(200, dt, 60.0, fT, fC, Tdiag="fixed", moisture=False, blow_tol=1e120)
        T = r["T"]
        print(f"  dt={dt:>9.6g}: ok={r['ok']}  T in [{T.min():.4f},{T.max():.4f}] K  "
              f"T_inf(60)={float(np.atleast_1d(fT(60.0))[0]):.4f} K")
    hr("C6d. Quantitative check of the growth law  g = 1/(1-dt*lambda)")
    Au = operators(200)[1]
    lam = np.linalg.eigvals(Au).real
    for dt, t_end in ((0.1, 5.0), (0.05, 5.0), (0.01, 5.0), (0.0005, 5.0), (0.005, 5.0)):
        n = int(round(t_end / dt))
        g = 1.0 / np.abs(1.0 - dt * lam)
        pred = g.max() ** n
        r = run(200, dt, t_end, fT, fC, Tdiag="user", moisture=False, blow_tol=1e200)
        obs = np.abs(r["T"]).max() / T0K
        pred2 = (1 + dt * lam.max()) ** n
        print(f"  dt={dt:>8.6g} t={t_end:>4}s: observed growth={obs:.6e} | "
              f"max 1/|1-dt l|^n={pred:.6e} (ratio {obs/pred:.4f}) | "
              f"(1+dt*l_max)^n={pred2:.6e}")


if __name__ == "__main__":
    Au = c5()
    c6_spectral(Au)
    fT, fC = make_env("pchip")
    c6_numeric(fT, fC)
