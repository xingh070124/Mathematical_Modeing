# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 4.

(a) Does the FV reference (make_rhs_fv) reach the SAME t_dry as the main solver?
(b) Is the main-vs-FV max|dC| a real scheme difference or a node/cell-centre
    location mismatch?  Compare like with like at the SAME xi points.
(c) Is the "euler" physical-coordinate scheme in make_rhs a genuinely
    different formulation (the doc claims V5 uses it)?
"""
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (Q4Radius, geometry_xi, make_rhs, make_jac, APP, CSTAR,
                      PROD_MAX_STEP, T0K, C0)
from q3_solve import Q3Env
from q1_solve import load_attachment1
from q4_verify import make_rhs_fv, compare_formulations, _secant_to_xi

P = []
OUT = []


def p(s):
    print(s, flush=True)
    OUT.append(s)


p("=" * 76)
p("AUDIT PROBE 4")
p("=" * 76)

t1, T1, C1 = load_attachment1()
env = Q3Env(t1, T1, C1)

# ---------- (a) FV end-to-end t_dry ----------------------------------------
p("\n(a) FV (independent scheme) solved to the terminal event")
for M in (100, 200, 400):
    rad = Q4Radius(mode="data")
    g = geometry_xi(M)
    rhs, xi_c, xi_f = make_rhs_fv(g, env, rad, APP["app4"])
    n = M
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atol = np.concatenate([np.full(n, 1e-6), np.full(n, 1e-9)])

    def ev(t, U, _n=n):
        return U[_n:].max() - CSTAR
    ev.terminal = True
    ev.direction = -1.0
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, 259200.0), U0, method="BDF", rtol=1e-9, atol=atol,
                    max_step=PROD_MAX_STEP, events=ev, dense_output=True,
                    jac_sparsity=sp.diags([np.ones(2 * n - 1), np.ones(2 * n),
                                           np.ones(2 * n - 1)], [-1, 0, 1],
                                          format="csr"))
    if sol.status == 1 and len(sol.t_events[0]):
        td = float(sol.t_events[0][0])
        p(f"    M={M:3d}: FV t_dry = {td:14.4f} s = {td/3600:9.5f} h  "
          f"(main 51.0852 h)  diff = {(td-183906.712827)/3600:+.6f} h  "
          f"wall={time.time()-t0:.1f}s")
    else:
        p(f"    M={M:3d}: FV event NOT triggered status={sol.status} "
          f"t={sol.t[-1]:.0f}")

# ---------- (b) like-with-like ---------------------------------------------
p("\n(b) main vs FV at the SAME xi points (cell centres), M=200, t=6 h")
M = 200
rad = Q4Radius(mode="data")
g = geometry_xi(M)
n = g["n"]
xi_n = g["xi"]
xi_f = np.arange(M + 1) / M
xi_c = 0.5 * (xi_f[:-1] + xi_f[1:])

rhs_m = make_rhs(g, env, rad, params=APP["app4"])
jac_m = make_jac(g, env, rad, params=APP["app4"])
sm = solve_ivp(rhs_m, (0.0, 21600.0), np.concatenate([np.full(n, T0K), np.full(n, C0)]),
               method="BDF", rtol=1e-9,
               atol=np.concatenate([np.full(n, 1e-6), np.full(n, 1e-9)]),
               max_step=PROD_MAX_STEP, jac=jac_m)
rhs_f, xic_f, xif_f = make_rhs_fv(g, env, rad, APP["app4"])
sf = solve_ivp(rhs_f, (0.0, 21600.0), np.concatenate([np.full(M, T0K), np.full(M, C0)]),
               method="BDF", rtol=1e-9,
               atol=np.concatenate([np.full(M, 1e-6), np.full(M, 1e-9)]),
               max_step=PROD_MAX_STEP,
               jac_sparsity=sp.diags([np.ones(2 * M - 1), np.ones(2 * M),
                                      np.ones(2 * M - 1)], [-1, 0, 1], format="csr"))

Cm_node = sm.y[n:, -1]
Cc = sf.y[M:, -1]
Cm_cell = np.interp(xi_c, xi_n, Cm_node)      # main solver at cell centres
d_same = np.abs(Cm_cell - Cc)
p(f"    max|dC| at SAME xi (cell centres)      = {d_same.max():.4e} kg/kg")
p(f"    max|dC| as reported by compare_formulations = "
  f"{compare_formulations(M=200, t_end=21600.0, app='app4')['max_dC']:.4e} kg/kg")
p(f"    C main at xi=1 (node) = {Cm_node[-1]:.6f}")
p(f"    C FV  at xi=1-1/2M   = {Cc[-1]:.6f}")
p(f"    -> the 'C_surf' pair printed by V5 is at DIFFERENT locations "
  f"(xi=1 vs xi={xi_c[-1]:.4f})")
# converge the like-with-like difference
for Mc in (100, 200, 400):
    gc = geometry_xi(Mc)
    nc = gc["n"]
    rc = Q4Radius(mode="data")
    rm = make_rhs(gc, env, rc, params=APP["app4"])
    jm = make_jac(gc, env, rc, params=APP["app4"])
    U0 = np.concatenate([np.full(nc, T0K), np.full(nc, C0)])
    a = np.concatenate([np.full(nc, 1e-6), np.full(nc, 1e-9)])
    s1 = solve_ivp(rm, (0.0, 21600.0), U0, method="BDF", rtol=1e-9, atol=a,
                   max_step=PROD_MAX_STEP, jac=jm)
    rf, xcf, xff = make_rhs_fv(gc, env, rc, APP["app4"])
    U0c = np.concatenate([np.full(Mc, T0K), np.full(Mc, C0)])
    ac = np.concatenate([np.full(Mc, 1e-6), np.full(Mc, 1e-9)])
    s2 = solve_ivp(rf, (0.0, 21600.0), U0c, method="BDF", rtol=1e-9, atol=ac,
                   max_step=PROD_MAX_STEP,
                   jac_sparsity=sp.diags([np.ones(2 * Mc - 1), np.ones(2 * Mc),
                                          np.ones(2 * Mc - 1)], [-1, 0, 1],
                                         format="csr"))
    Cn = s1.y[nc:, -1]
    Ccc = s2.y[Mc:, -1]
    Cmc = np.interp(xcf, gc["xi"], Cn)
    d = np.abs(Cmc - Ccc)
    p(f"    M={Mc:3d}: like-with-like max|dC| = {d.max():.4e}, "
      f"argmax xi = {xcf[int(d.argmax())]:.4f}")

# ---------- (c) the "euler" form -------------------------------------------
p("\n(c) form='euler' in make_rhs: is it the physical-coordinate scheme?")
from q4_solve import solve_q4
for form in ("material", "euler"):
    try:
        r = solve_q4(M=200, form=form)
        p(f"    form={form:9s}: t_dry = {r['t_dry']:14.4f} s = "
          f"{r['t_dry']/3600:9.4f} h")
    except RuntimeError as e:
        p(f"    form={form:9s}: not triggered: {e}")

p(f"\n    note: xi in make_rhs is ALWAYS the material coordinate i/M; the "
  f"'euler' branch adds xi*(Rdot/R)*dU/dxi on top of the material-coordinate "
  f"flux divergence, so it is not the fixed-physical-grid scheme "
  f"described in problem4.md Sec 5.5.")

with open(os.path.join("outputs", "_audit_q4_probe4.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
