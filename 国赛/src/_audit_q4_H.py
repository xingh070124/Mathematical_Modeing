# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 8: is the grid convergence really order ~1.5 (so that the
Richardson extrapolation and the +/-0.012 h budget are valid), or is the
observed ratio 2.841 a pre-asymptotic artefact of a first-order scheme?

Runs the production solver and the FV reference at M = 100..3200.
"""
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q4_solve import (solve_q4, geometry_xi, make_rhs, make_jac, Q4Radius,
                      APP, CSTAR, T0K, C0, PROD_MAX_STEP)
from q3_solve import Q3Env
from q1_solve import load_attachment1
from q4_verify import make_rhs_fv

OUT = []


def p(s):
    print(s, flush=True)
    OUT.append(s)


p("=" * 78)
p("AUDIT PROBE 8: convergence of t_dry at high M")
p("=" * 78)
t0 = time.time()
p("\n[main material-coordinate solver]")
res = {}
for M in (100, 200, 400, 800, 1600, 3200):
    try:
        r = solve_q4(M=M)
        res[M] = r["t_dry"]
        p(f"  M={M:5d}  t_dry = {r['t_dry']:15.6f} s = {r['t_dry']/3600:11.7f} h"
          f"  nsteps={r['nsteps']:6d}")
    except RuntimeError as e:
        p(f"  M={M:5d}  failed: {e}")

Ms = sorted(res)
p("")
p("  adjacent differences and observed order p = log2(d_k / d_{k+1}):")
for i in range(len(Ms) - 1):
    d = res[Ms[i + 1]] - res[Ms[i]]
    if i + 1 < len(Ms) - 1:
        d2 = res[Ms[i + 2]] - res[Ms[i + 1]]
        p(f"    M {Ms[i]:5d} -> {Ms[i+1]:5d}: d = {d:12.6f} s,  "
          f"ratio = {d/d2:7.4f}  -> p = {np.log2(d/d2):7.4f}")
    else:
        p(f"    M {Ms[i]:5d} -> {Ms[i+1]:5d}: d = {d:12.6f} s")

# Richardson with the locally observed order, at each level
p("")
p("  Richardson extrapolation with the LOCAL order:")
for i in range(len(Ms) - 2):
    d1 = res[Ms[i + 1]] - res[Ms[i]]
    d2 = res[Ms[i + 2]] - res[Ms[i + 1]]
    pp = np.log2(d1 / d2)
    tr = res[Ms[i + 2]] + d2 / (2 ** pp - 1)
    p(f"    using M={Ms[i]},{Ms[i+1]},{Ms[i+2]}: p={pp:.4f}  t* = {tr:.4f} s "
      f"= {tr/3600:.7f} h")

# the scheme's formal order: check the plain M=200->400->800 chain
if 800 in res:
    d1 = res[400] - res[200]
    d2 = res[800] - res[400]
    pp = np.log2(d1 / d2)
    tr = res[800] + d2 / (2 ** pp - 1)
    p("")
    p(f"  M=400/800 pair: ratio {d1/d2:.4f}, p={pp:.4f}, t*={tr:.4f} s, "
      f"M=200 error vs t* = {abs(tr-res[200])/3600:.6f} h")

# ---------- FV convergence ---------------------------------------------------
p("")
p("[independent FV reference, end-to-end t_dry]")
t1, T1, C1 = load_attachment1()
env = Q3Env(t1, T1, C1)
fv = {}
for M in (100, 200, 400, 800):
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
    tt = time.time()
    sol = solve_ivp(rhs, (0.0, 259200.0), U0, method="BDF", rtol=1e-9, atol=atol,
                    max_step=PROD_MAX_STEP, events=ev, dense_output=True,
                    jac_sparsity=sp.diags([np.ones(2 * n - 1), np.ones(2 * n),
                                           np.ones(2 * n - 1)], [-1, 0, 1],
                                          format="csr"))
    td = float(sol.t_events[0][0])
    fv[M] = td
    p(f"  FV M={M:4d}: t_dry = {td:15.6f} s = {td/3600:11.7f} h  "
      f"wall={time.time()-tt:5.1f}s")
    if M in res:
        p(f"            main - FV = {(res[M]-td)/3600:+.6f} h "
          f"({res[M]-td:+.3f} s)")
p("")
for i in range(len(fv) - 1):
    a, b = sorted(fv)[i], sorted(fv)[i + 1]
    p(f"    FV {a:4d} -> {b:4d}: d = {fv[b]-fv[a]:12.6f} s")
if len(fv) >= 3:
    ks = sorted(fv)
    d1 = fv[ks[1]] - fv[ks[0]]
    d2 = fv[ks[2]] - fv[ks[1]]
    pp = np.log2(d1 / d2)
    tr = fv[ks[2]] + d2 / (2 ** pp - 1)
    p(f"    FV order p = {pp:.4f}, FV Richardson t* = {tr:.4f} s "
      f"= {tr/3600:.7f} h")
    if 1600 in res:
        p(f"    main(M=1600) - FV(t*) = {(res[1600]-tr)/3600:+.7f} h")

p(f"\ntotal wall = {time.time()-t0:.1f} s")
with open(os.path.join("outputs", "_audit_q4_conv.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
