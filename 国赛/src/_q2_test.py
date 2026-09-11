# -*- coding: utf-8 -*-
"""临时: 核验 q2_solve 的核心 (质量矩阵 / Jacobian / 短时推进)."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from q2_solve import (Par, geometry, check_lumped_mass, check_jacobian, march,
                      props, Dfun, out_indices, HEVAP_28, HEVAP_SLOPE)
from q1_solve import Env, load_attachment1

print("S1 集中质量恒等式")
for M in (10, 100, 800):
    a, b = check_lumped_mass(M)
    print(f"   M={M:5d}  行和式偏差={a:.3e}   dr*r_i 偏差={b:.3e}")

print("\nS2 Jacobian 有限差分校核")
cases = [("默认 (H_evap(T), rho cp dT/dt)", Par()),
         ("H_evap = 0", Par(hevap="off")),
         ("守恒形式 d(rho cp T)/dt", Par(energy="conserv")),
         ("halfcv 边界", Par(boundary="halfcv")),
         ("系数冻结 Picard", Par(frozen=True)),
         ("附录2 物性", Par(mode="app2"))]
for name, p in cases:
    rel = check_jacobian(par=p)
    print(f"   {name:34s}  max|J_ana-J_fd|/max|J_fd| = {rel:.3e}  "
          f"{'OK' if rel < 1e-6 else '!!'}")

print("\nS3 物性与 D")
for C in (2.55, 2.00, 1.00, 0.50, 0.15):
    rho, cp, k, *_ = props(C)
    print(f"   C={C:5.2f} rho={rho:8.2f} cp={cp:9.2f} k={k:7.5f} "
          f"rho cp={rho*cp:12.1f} alpha={k/(rho*cp):.4e}")
print(f"   D(2.55,301.15)={float(Dfun(2.55,301.15)):.6e}  "
      f"D(2.55,323.15)={float(Dfun(2.55,323.15)):.6e}")
T = 313.15
print(f"   H_evap(28C)={HEVAP_28:.1f}  H_evap(40C)={HEVAP_28+HEVAP_SLOPE*(T-301.15):.1f}")

print("\nS4 短时推进 (M=200, dt=0.25, t=1800 s)")
t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")
out = march(200, 0.25, 1800.0, env, Par(), out_idx=out_indices(200), verbose=True)
s = out["stats"]
print(f"   wall={s['wall']:.1f}s  steps={s['nsteps']}  "
      f"iter: mean={s['iters'].mean():.2f} max={s['iters'].max()}")
print(f"   t=1800s  T(r=0)={out['T_snap'][-1,0]-273.15:.4f} C   "
      f"T(R)={out['T_snap'][-1,-1]-273.15:.4f} C")
print(f"   t=1800s  C(r=0)={out['C_snap'][-1,0]:.5f}  C(R)={out['C_snap'][-1,-1]:.5f}")
print(f"   env: Tinf(1800)={env.T(1800)-273.15:.4f} C  Cinf={env.C(1800):.5f}")

# 守恒/极值检验
E0, W0 = s["E0"], s["W0"]
print(f"\nS5 收支 (per 2pi, 单位轴长)")
print(f"   E0={E0:.6e}  E(1800)={out['E'][-1]:.6e}  ΔE={out['E'][-1]-E0:.6e}")
print(f"   累积边界热流 -Fh = {-out['Fh'][-1]:.6e}  比值 ΔE/(-Fh)={(
    out['E'][-1]-E0)/(-out['Fh'][-1]):.6f}")
print(f"   W0={W0:.6e}  W(1800)={out['W'][-1]:.6e}  ΔW={out['W'][-1]-W0:.6e}")
print(f"   累积边界水流 -Fw = {-out['Fw'][-1]:.6e}  比值 ΔW/(-Fw)={(
    out['W'][-1]-W0)/(-out['Fw'][-1]):.6f}")
print(f"   水量收支相对残差 = {abs((out['W'][-1]-W0)-(-out['Fw'][-1]))/abs(out['Fw'][-1]):.3e}")
