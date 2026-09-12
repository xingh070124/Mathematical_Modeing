# -*- coding: utf-8 -*-
"""Audit J: C4 boundary layer on the FULL grid (previous attempt indexed output columns)."""
from __future__ import annotations
import os, sys

import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from q1_solve import Env, load_attachment1
from q2_solve import Par, march, Dfun

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")
D0 = float(Dfun(2.55, 301.15))
print(f"D(C0,T0) = {D0:.6e} m^2/s")
for M, dt in ((3200, 1.0 / 64),):
    o = march(M, dt, 60.0, env, Par(), out_idx=None)   # FULL grid
    g = o["geom"]
    dr_cm = g["dr"] * 100
    print(f"M={M}  dr={dr_cm:.8f} cm")
    for it in (0, 59):
        tt = o["t_snap"][it]
        Cc = o["C_snap"][it]          # full grid, index 0 = centre, M = surface
        Cs = Cc[-1]
        dlt = np.sqrt(D0 * tt) * 100.0
        print(f"\n  t={tt:4.0f} s: C_surface={Cs:.6f}  C_centre={Cc[0]:.6f}")
        print(f"    sqrt(Dt) = {dlt:.6f} cm = {dlt/dr_cm:.2f} cells")
        for k in (0, 1, 2, 4, 6, 8, 10, 12, 16, 20):
            if k <= M:
                print(f"      node M-{k:<2d} (r={g['r'][M-k]*100:.5f} cm): "
                      f"C={Cc[M-k]:.6f}  C-C_surf={Cc[M-k]-Cs:.6f}")
        # how deep does the boundary-layer perturbation reach?
        d = np.abs(Cc - Cc[0])
        kk = np.where(d > 5e-5)[0]
        print(f"    |C - C_centre| > 5e-5 for surface nodes 0..{M-kk.min() if len(kk) else -1}"
              f"  => perturbation confined to the outer {M-kk.min() if len(kk) else 0} cells")
        if it == 0:
            print(f"    doc claims at t=1 s, M=3200: surface 2.51983 -> node 8 (inward) "
                  f"2.53286")
            print(f"    actual: surface={Cc[M]:.5f}  node M-8 (r="
                  f"{g['r'][M-8]*100:.5f} cm)={Cc[M-8]:.5f}  node M-12="
                  f"{Cc[M-12]:.5f}  centre={Cc[0]:.5f}")
            print(f"    monotone increasing inward over the outer 12 cells? "
                  f"{bool(np.all(np.diff(Cc[M-12:]) > 0))}")
            print(f"    cells needed for the profile to come back within 1e-5 of 2.55: "
                  f"{M - np.max(np.where(np.abs(Cc - 2.55) < 1e-5)[0][np.where(np.abs(Cc-2.55)<1e-5)[0] < M-1])}")
