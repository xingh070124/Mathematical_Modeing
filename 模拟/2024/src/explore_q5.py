# -*- coding: utf-8 -*-
"""问题5探索脚本：粗扫速度比场 rho_i(u1)，定位峰值区与贡献把手（临时脚本）."""
import sys, os, time, json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import problem4_solve as p4

t0 = time.time()

# ---- 粗扫 u1 in [-60, 400]，步长 0.25 ----
grid = np.arange(-60.0, 400.01, 0.25)
R = np.empty(len(grid))
Iarg = np.empty(len(grid), dtype=int)
for k, t in enumerate(grid):
    u = p4.config_at(float(t))
    v = p4.velocities(u)
    j = int(np.argmax(v))
    R[k] = v[j]
    Iarg[k] = j
    if k % 200 == 0:
        print(f"[scan] {k}/{len(grid)}  {time.time()-t0:.0f}s", flush=True)

kmax = int(np.argmax(R))
print(f"\n粗扫最大 rho = {R[kmax]:.6f} @ u1={grid[kmax]:.3f}, 把手 {Iarg[kmax]+1}")
print(f"对应 v* = {2.0/R[kmax]:.6f} m/s")

# ---- 峰值附近 top 局部峰 ----
from scipy.signal import argrelextrema
loc = argrelextrema(R, np.greater_equal, order=8)[0]
cand = sorted(zip(R[loc], grid[loc], Iarg[loc]), reverse=True)[:12]
print("\n局部峰值 top12 (rho, u1, 把手):")
for r, u, i in cand:
    print(f"  rho={r:.6f}  u1={u:8.3f}  handle={i+1}")

# ---- 峰值时刻前10把手明细 ----
t_peak = float(grid[kmax])
u = p4.config_at(t_peak)
v = p4.velocities(u)
print(f"\n峰值时刻 u1={t_peak:.3f} 各把手 u 位置与速度（前12）:")
for i in range(12):
    print(f"  handle {i+1:>2}: u={u[i]:9.4f}  v={v[i]:.6f}")
# 缝位置
print(f"\n缝位置: E(u=0), T(u={p4.L1_0:.4f}), F(u={p4.L_C:.4f})")

# ---- 端部区域检查（截断域合理性）----
for t_chk in (-60.0, -30.0, 395.0, 400.0):
    u = p4.config_at(t_chk)
    v = p4.velocities(u)
    print(f"t={t_chk:>6}: max rho = {np.max(v):.6f} (handle {int(np.argmax(v))+1})")

np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_explore_q5.npz"),
         grid=grid, R=R, Iarg=Iarg)
print(f"\n[done] {time.time()-t0:.0f}s, 结果存 _explore_q5.npz")
