# -*- coding: utf-8 -*-
"""基准: 每步成本随 M 的变化."""
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from q2_solve import Par, march, out_indices
from q1_solve import Env, load_attachment1

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")
NSTEP = 2000
for M in (200, 400, 800, 1600, 3200):
    dt = 0.01
    te = NSTEP * dt
    t0 = time.time()
    o = march(M, dt, te, env, Par(line_search=False), out_idx=out_indices(M))
    el = time.time() - t0
    it = o["stats"]["iters"].mean()
    print(f"M={M:5d}  {NSTEP} 步  wall={el:6.2f}s  {1000*el/NSTEP:7.3f} ms/步  "
          f"iter={it:.2f}  -> 10800s@dt=0.01 预计 {el/NSTEP*1.08e6/60:7.1f} min")
