# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 6: reproduce the Monte Carlo exactly as q4_sensitivity does.

Checks the seed, the +/-5% uniform support, the count of samples that fail to
reach the event within 10 days (censoring), and the reported statistics.
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q4_solve import solve_q4, P4

P4_KEYS = ["rho0", "krho", "cp0", "kcp", "k0", "kk", "D0", "kD", "EA"]
OUT = []


def p(s):
    print(s, flush=True)
    OUT.append(s)


TMAX_MC = 864000.0
t0 = time.time()
for lev, N, seed in ((0.05, 100, 2026),):
    rng = np.random.default_rng(seed)
    ts, over3, fails = [], 0, 0
    factors = []
    for i in range(N):
        f = 1.0 + lev * (2.0 * rng.random(len(P4_KEYS)) - 1.0)
        factors.append(f)
        p4 = {k: P4[k] * fi for k, fi in zip(P4_KEYS, f)}
        try:
            r = solve_q4(M=200, params=p4, t_max=TMAX_MC)
            ts.append(r["t_dry"])
            if r["t_dry"] > 259200.0:
                over3 += 1
        except RuntimeError as e:
            fails += 1
            p(f"    sample {i} FAILED to reach event in 10 d: {e}")
    ts = np.array(ts)
    F = np.array(factors)
    p("=" * 74)
    p(f"AUDIT PROBE 6: MC reproduction, level +/-{lev*100:.0f}%, N={N}, seed={seed}")
    p("=" * 74)
    p(f"  perturbation support: min {F.min():.6f}, max {F.max():.6f} "
      f"(expected [{1-lev:.4f}, {1+lev:.4f}])")
    p(f"  n per-perturbation: {len(P4_KEYS)} keys = {P4_KEYS}")
    p(f"  samples reaching the event within 10 d : {ts.size}/{N}")
    p(f"  samples that FAILED (silently dropped): {fails}")
    p(f"  samples exceeding 3 d                 : {over3}  "
      f"({100.0*over3/N:.1f} % of N)")
    p(f"  mean   = {ts.mean():.4f} s = {ts.mean()/3600:.4f} h")
    p(f"  median = {np.median(ts):.4f} s = {np.median(ts)/3600:.4f} h")
    p(f"  std(ddof=1) = {ts.std(ddof=1):.4f} s = {ts.std(ddof=1)/3600:.4f} h")
    q = np.percentile(ts, [2.5, 50, 97.5])
    p(f"  2.5/50/97.5 pct = {q[0]/3600:.4f} / {q[1]/3600:.4f} / {q[2]/3600:.4f} h")
    p(f"  max = {ts.max()/3600:.4f} h ; min = {ts.min()/3600:.4f} h")
    # bootstrap CI on the mean, to show how uncertain the MC summary is
    rg = np.random.default_rng(11)
    bs = np.array([ts[rg.integers(0, ts.size, ts.size)].mean() for _ in range(2000)])
    p(f"  bootstrap 95% CI for the MEAN = "
      f"[{np.percentile(bs,2.5)/3600:.3f}, {np.percentile(bs,97.5)/3600:.3f}] h")
    # and the sampling uncertainty of the 97.5 percentile
    bs2 = np.array([np.percentile(ts[rg.integers(0, ts.size, ts.size)], 97.5)
                    for _ in range(2000)])
    p(f"  bootstrap 95% CI for the 97.5 pct = "
      f"[{np.percentile(bs2,2.5)/3600:.3f}, {np.percentile(bs2,97.5)/3600:.3f}] h")

p(f"\ntotal wall = {time.time()-t0:.1f} s")
with open(os.path.join("outputs", "_audit_q4_mc.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(OUT) + "\n")
