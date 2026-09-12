# -*- coding: utf-8 -*-
r"""核验"表面温度下穿初温"这一现象:

  1. 附件1 的环境采样间隔 (决定 t=10 s 的 T_inf 是实测还是插值);
  2. 初期表面热流三项的逐秒值 (q_conv / q_evap / q_cond);
  3. 解析估计 q_evap/h 与实测下穿深度 0.0095 K 的对照;
  4. 下穿深度对 T_inf 插值方式的敏感性 (线性 vs PCHIP vs 三次样条).
"""
from __future__ import annotations

import os
import sys

import numpy as np
import openpyxl
from scipy.interpolate import PchipInterpolator, CubicSpline

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A1 = os.path.join(ROOT, "A题", "附件", "附件1.xlsx")

ws = openpyxl.load_workbook(A1, data_only=True).worksheets[0]
rows = [[c.value for c in r] for r in ws.iter_rows()]
print("附件1 表头:", rows[0])
print("前 4 行数据:")
for r in rows[1:5]:
    print("   ", r)
print(f"总行数 {len(rows) - 1}")

t = np.array([float(r[0]) for r in rows[1:]], dtype=float)
Tinf = np.array([float(r[1]) for r in rows[1:]], dtype=float)
Cinf = np.array([float(r[2]) for r in rows[1:]], dtype=float)
dt_env = np.diff(t)
print(f"\n时间范围 {t[0]:.0f}..{t[-1]:.0f} s; 采样间隔: "
      f"min={dt_env.min():.0f} max={dt_env.max():.0f} (唯一值 {np.unique(dt_env)[:6]})")
print(f"T_inf(0) = {Tinf[0]:.4f} degC,  T_inf(60) = {Tinf[1]:.4f} degC")

# ---- 初期环境 ----
print("\n=== 窗口内 T_inf / C_inf 的最初 6 个采样 ===")
for i in range(6):
    print(f"  t={t[i]:6.0f} s   T_inf={Tinf[i]:8.4f} degC   C_inf={Cinf[i]:8.5f} kg/kg")

# ---- 三种插值在 t=10 s 的取值 ----
tt = np.arange(0, 61, 1.0)
pch = PchipInterpolator(t[:6], Tinf[:6])(tt)
lin = np.interp(tt, t[:6], Tinf[:6])
cub = CubicSpline(t[:6], Tinf[:6])(tt)
print("\n=== t=0..20 s 的 T_inf 插值 (三种方式) ===")
print(f"  {'t/s':>4} {'PCHIP':>9} {'线性':>9} {'三次样条':>10}")
for i in range(0, 21, 5):
    print(f"  {tt[i]:4.0f} {pch[i]:9.4f} {lin[i]:9.4f} {cub[i]:10.4f}")
print(f"  最大差异 (t<=60 s): PCHIP-线性 {np.abs(pch-lin).max():.4f} K, "
      f"PCHIP-样条 {np.abs(pch-cub).max():.4f} K")

# ---- 初期热流: 用问题二实际输出的 T、C 反推 (60 s 粒度只有 2 点, 故用解析式估计) ----
# 表面能量平衡: q_cond = q_conv - q_evap,  各量单位 W/m^2
h, hm = 25.0, 8e-7
Hv0, Hv_slope = 2.4346e6, -2.391e3
T0, C0 = 28.0, 2.55
print("\n=== 初期表面热流 (W/m^2), T_R 取初温 28 degC 起算 ===")
print(f"  {'t/s':>4} {'T_inf':>8} {'q_conv':>9} {'H_evap':>10} {'q_evap':>8} "
      f"{'q_cond':>9} {'q_evap/h':>9}")
for i in (1, 5, 10, 20, 34, 60):
    Ti = float(PchipInterpolator(t[:6], Tinf[:6])(i))
    Hv = Hv0 + Hv_slope * (T0 + 273.15 - 301.15)   # 以 28 degC 为锚点, T_R≈28 时
    qc = h * (Ti - T0)
    qe = Hv * hm * (C0 - Cinf[0])
    print(f"  {i:4d} {Ti:8.4f} {qc:9.3f} {Hv:10.1f} {qe:8.3f} {qc - qe:9.3f} "
          f"{qe / h:9.4f}")
print("\n  注: q_evap 用 C_R=C0=2.55 (初期表面尚未脱水) 与 C_inf(0) 计算, "
      "是**上界**估计")
