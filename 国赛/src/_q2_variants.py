# -*- coding: utf-8 -*-
"""临时: 对照各模型变体 (t=1800 s, M=200, dt=0.25)."""
import os, sys
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
idx = out_indices(200)
M, dt, TE = 200, 0.25, 1800.0

cases = [
    ("基准: H_evap(T), rho cp dT/dt, 集中质量", Par()),
    ("H_evap = 0", Par(hevap="off")),
    ("H_evap 常数 40C 值", Par(hevap="const", hevap_const=2.405908e6)),
    ("H_evap x 10", Par(hevap_mult=10.0)),
    ("守恒形式 d(rho cp T)/dt", Par(energy="conserv")),
    ("halfcv 边界", Par(boundary="halfcv")),
    ("系数冻结 Picard", Par(frozen=True)),
    ("附录2 物性 (问题一口径)", Par(mode="app2")),
]
res = {}
for name, p in cases:
    o = march(M, dt, TE, env, p, out_idx=idx)
    res[name] = o
    print(f"{name:38s} T0={o['T_snap'][-1,0]-273.15:9.4f} TR={o['T_snap'][-1,-1]-273.15:9.4f}"
          f"  C0={o['C_snap'][-1,0]:8.5f} CR={o['C_snap'][-1,-1]:8.5f}"
          f"  it={o['stats']['iters'].mean():.2f}  wall={o['stats']['wall']:5.1f}s")

base = res[cases[0][0]]
print("\n与基准的差 (t=1800 s):")
for name, _ in cases[1:]:
    o = res[name]
    dT = np.abs(o["T_snap"][-1] - base["T_snap"][-1]).max()
    dC = np.abs(o["C_snap"][-1] - base["C_snap"][-1]).max()
    print(f"  {name:38s} max|dT|={dT:12.5e} K   max|dC|={dC:12.5e} kg/kg")

print("\n收支核对 (基准, 非保守形式):")
o = base
print(f"  ΔE={o['E'][-1]-o['stats']['E0']:.6e}  -Fh={-o['Fh'][-1]:.6e}  "
      f"ΔE-(-Fh)={o['E'][-1]-o['stats']['E0']+o['Fh'][-1]:.6e}")
oc = res[cases[4][0]]
print("收支核对 (守恒形式):")
print(f"  ΔE={oc['E'][-1]-oc['stats']['E0']:.6e}  -Fh={-oc['Fh'][-1]:.6e}  "
      f"相对残差={abs(oc['E'][-1]-oc['stats']['E0']+oc['Fh'][-1])/abs(oc['Fh'][-1]):.3e}")
