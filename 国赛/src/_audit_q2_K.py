# -*- coding: utf-8 -*-
"""Audit K: reproduce q2_moist_diag's M=3200 t=1 s profile exactly (dt=1/256, t_end=60)."""
from __future__ import annotations
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from q1_solve import Env, load_attachment1
from q2_solve import Par, march

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")
for M, dt in ((3200, 1.0 / 256), (1600, 1.0 / 256), (200, 1.0 / 256)):
    idx = np.unique(np.concatenate([[0, M // 2], np.arange(max(0, M - 10), M + 1)]))
    o = march(M, dt, 60.0, env, Par(), out_idx=idx)
    C = o["C_snap"]
    cols = [float(C[0, -1 - k]) for k in range(min(8, C.shape[1]))]
    print(f"M={M:5d} dr={0.02/M*100:.6f} cm  t=1 s surface={C[0,-1]:.8f}")
    print("   k=0..7 inward: " + "".join(f"{v:12.7f}" for v in cols))
    print(f"   node k=8 = {C[0,-1-8]:.7f}   doc claims 2.53286 ; "
          f"doc claims surface 2.51983")
    # convergence at the same physical radius: 1st node inward
    print(f"   surface C(R,1s) = {C[0,-1]:.8f}   C(R,60s) = {C[59,-1]:.8f}")
