# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 3: independent re-run of the production and variant solves.

Recomputes, from the solvers, every headline number in the problem-4 claim:
  PROD t_dry (M=200), M=100, M=400, app3+Rconst (V0), app4+Rconst (3-day net),
  app3+shrink, table-6 values, crossing times, R(t)=r exit times, shrink fraction.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (solve_q4, sample_q4, crossing_times_q4, Q4Radius,
                      load_attachment2, APP, CSTAR, T_MAX)
from q3_solve import Q3Env

OUT = []


def p(s):
    print(s, flush=True)
    OUT.append(s)


t_all = time.time()

p("=" * 76)
p("AUDIT PROBE 3: independent re-run of the problem-4 solves")
p("=" * 76)

cases = [
    ("PROD_M200", dict(M=200)),
    ("PROD_M100", dict(M=100)),
    ("PROD_M400", dict(M=400)),
    ("V0_app3_Rconst_M200", dict(M=200, app="app3", rad_mode="const")),
    ("app3_shrink_M200", dict(M=200, app="app3", rad_mode="data")),
]
res = {}
for tag, kw in cases:
    t0 = time.time()
    r = solve_q4(**kw)
    res[tag] = r
    p(f"  {tag:22s} t_dry = {r['t_dry']:14.4f} s = {r['t_dry']/3600:10.5f} h"
      f"  nsteps={r['nsteps']:6d} wall={time.time()-t0:5.1f}s")

p("")
p("[app4 + frozen shrinkage: does the event trigger inside 259200 s?]")
try:
    r = solve_q4(M=200, app="app4", rad_mode="const", t_max=259200.0)
    p(f"  TRIGGERED at {r['t_dry']:.4f} s -- claim of non-trigger would be FALSE")
except RuntimeError as e:
    p(f"  NOT triggered: {e}")
try:
    r2 = solve_q4(M=200, app="app4", rad_mode="const", t_max=864000.0)
    p(f"  with t_max=10 d : t_dry = {r2['t_dry']:.4f} s = {r2['t_dry']/3600:.5f} h"
      f" = {r2['t_dry']/86400:.4f} d")
    res["app4_Rconst_10d"] = r2
except RuntimeError as e:
    p(f"  with t_max=10 d : still not triggered: {e}")

# ---- max_i C_i at t = 259200 s for app4 + frozen shrinkage ----------------
p("")
p("[max_i C_i at 3 days, app4 + frozen shrinkage]  (claim: 0.2247)")
from q4_solve import make_rhs, make_jac, geometry_xi, make_event
from scipy.integrate import solve_ivp
g = geometry_xi(200)
n = g["n"]
env = Q3Env(*__import__("q1_solve").load_attachment1())
radc = Q4Radius(mode="const")
rhs = make_rhs(g, env, radc, params=APP["app4"])
jac = make_jac(g, env, radc, params=APP["app4"])
U0 = np.concatenate([np.full(n, 20.0 + 273.15), np.full(n, 2.55)])
sol = solve_ivp(rhs, (0.0, 259200.0), U0, method="BDF", rtol=1e-9,
                atol=np.concatenate([np.full(n, 1e-6), np.full(n, 1e-9)]),
                max_step=3600.0, jac=jac, dense_output=True)
Cend = sol.y[n:, -1]
p(f"  status={sol.status}  t_end={sol.t[-1]:.1f} s  max_i C_i = {Cend.max():.6f}"
  f"  at xi={g['xi'][int(Cend.argmax())]:.3f}")
p(f"  C at centre = {Cend[0]:.6f}, at surface = {Cend[-1]:.6f}")

# ---- production detail ---------------------------------------------------
r = res["PROD_M200"]
g = r["g"]
s = sample_q4(r["sol"], g, r["rad"], r["t_dry"])
MLsum = g["MLg"].sum()
p("")
p("[production detail]")
p(f"  t_dry            = {r['t_dry']:.6f} s = {r['t_dry']/3600:.6f} h"
  f" = {r['t_dry']/86400:.6f} d")
p(f"  n60              = {s['n60']}   last 60 s row = {s['t60'][-1]:.1f} s")
p(f"  R(t_dry)         = {s['Rs'][-1]:.6f} cm   ratio = {s['Rs'][-1]/2.0:.6f}")
p(f"  C surface        = {s['Cs'][-1]:.6f}")
p(f"  C centre         = {s['Cg'][-1, 0]:.6f}")
p(f"  C bar (xi-wt)    = {s['W60'][-1]/MLsum:.6f}")
p(f"  T surface        = {s['Ts'][-1]:.6f} degC")
p(f"  T max            = {s['Tmax'][-1]:.6f} degC")

# ---- table 6 -------------------------------------------------------------
p("")
p("[table 6 recomputed, 4 dp]   columns 0,0.5,1.0,1.5 cm + surface")
cols = [0.0, 0.5, 1.0, 1.5]
j5 = [int(np.argmin(np.abs(s["grid_cm"] - c))) for c in cols]
hours = np.arange(6.0, np.floor(r["t_dry"] / 3600.0 / 6.0) * 6.0 + 1e-9, 6.0)
p("        t/h     0.0cm     0.5cm     1.0cm     1.5cm    surface")
for h in list(hours) + [r["t_dry"] / 3600.0]:
    if abs(h - r["t_dry"] / 3600.0) < 1e-9:
        i = s["n60"] - 1
        lab = f"{h:10.4f}"
    else:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        lab = f"{h:10.1f}"
    vals = [s["Cg"][i, j] for j in j5] + [s["Cs"][i]]
    p(lab + "".join(f"{v:10.4f}" if not np.isnan(v) else "         -" for v in vals))

# ---- crossing times ------------------------------------------------------
p("")
p("[crossing times at fixed physical radius]")
tg = np.unique(np.concatenate([np.arange(60.0, r["t_dry"], 60.0), [r["t_dry"]]]))
xt, xf = crossing_times_q4(r["sol"], g, r["rad"], r["t_dry"], CSTAR,
                           r_out_cm=(0.0, 0.5, 1.0, 1.5, 2.0), t_grid=tg)
for k in xt:
    v = xt[k]
    p(f"  r={k:4.1f} cm : " + (f"{v:12.2f} s = {v/3600:8.4f} h" if v is not None
                              else f"none (flag={xf[k]})"))

p("")
p("[R(t) = r  exit times]")
rad = Q4Radius()
ta, Ra = load_attachment2()
from scipy.optimize import brentq
for rcm in (1.5, 2.0, 1.0, 1.2):
    try:
        t_out = brentq(lambda x, _r=rcm: float(rad.R(x)) - _r * 1e-2, 0.0, 259200.0,
                       xtol=1e-9)
        p(f"  R(t) = {rcm} cm at t = {t_out:.4f} s = {t_out/3600:.5f} h")
    except ValueError:
        p(f"  R(t) = {rcm} cm : not reached in 3 d")

p("")
p("[shrink fraction in first 6 h]")
i6 = int(np.argmin(np.abs(ta - 6 * 3600)))
p(f"  R(0)={Ra[0]:.4f}  R(6h)={Ra[i6]:.4f}  R(end)={Ra[-1]:.4f}")
p(f"  fraction = {(Ra[0]-Ra[i6])/(Ra[0]-Ra[-1]):.6f}")
i4 = int(np.argmin(np.abs(ta - 4 * 3600)))
p(f"  fraction in first 4 h = {(Ra[0]-Ra[i4])/(Ra[0]-Ra[-1]):.6f}")
p(f"  R0/Rend squared boost = {(Ra[0]/Ra[-1])**2:.6f}")

p("")
p("[effect decomposition]")
tq3 = res["V0_app3_Rconst_M200"]["t_dry"]
p(f"  app3 + R const  (= q3) : {tq3:.4f} s = {tq3/3600:.5f} h")
if "app4_Rconst_10d" in res:
    t4ns = res["app4_Rconst_10d"]["t_dry"]
    p(f"  app4 + R const        : {t4ns:.4f} s = {t4ns/3600:.5f} h"
      f"  ({t4ns/86400:.4f} d)")
    p(f"    ratio app4const/q3   = {t4ns/tq3:.4f}")
    p(f"    ratio app4const/prod = {t4ns/r['t_dry']:.4f}")
    p(f"    shrink reduction pct = {100*(1-r['t_dry']/t4ns):.4f} %")
t3s = res["app3_shrink_M200"]["t_dry"]
p(f"  app3 + shrink          : {t3s:.4f} s = {t3s/3600:.5f} h")
p(f"  app4 + shrink (PROD)   : {r['t_dry']:.4f} s = {r['t_dry']/3600:.5f} h")
p(f"    net vs q3            = {(r['t_dry']-tq3)/3600:+.4f} h"
  f" = {100*(r['t_dry']-tq3)/tq3:+.4f} %")
p(f"    app3 shrink ratio    = {tq3/t3s:.4f}")

p("")
p("[grid convergence]")
t100 = res["PROD_M100"]["t_dry"]
t200 = r["t_dry"]
t400 = res["PROD_M400"]["t_dry"]
d1, d2 = t200 - t100, t400 - t200
import math
pp = math.log2(d1 / d2)
tr = t400 + d2 / (2 ** pp - 1)
p(f"  M=100 {t100:.4f}   M=200 {t200:.4f}   M=400 {t400:.4f}")
p(f"  d1={d1:.4f} d2={d2:.4f} ratio={d1/d2:.4f} p={pp:.6f}")
p(f"  Richardson = {tr:.4f} s = {tr/3600:.6f} h")
p(f"  |rich - M200| = {abs(tr-t200)/3600:.6f} h ; |rich - M400| = {abs(tr-t400)/3600:.6f} h")

p("")
p(f"total wall = {time.time()-t_all:.1f} s")

with open(os.path.join("outputs", "_audit_q4_rerun.log"), "w",
          encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
