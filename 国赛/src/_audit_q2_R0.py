# -*- coding: utf-8 -*-
"""Independent recomputation of the R0 / S_false magnitudes used by the paper
(section 能量方程形式的重新选择) — and of the ratio between them.

The paper now states (abstract + body):
    |R_0| = 44.44 W/m^3  = 1.71 % of the main term
    S_false = +2.1599e4 W/m^3 = 829.72 % of the main term
    |S|/|R_0| = 485.97  ("相差近三个数量级")

This script checks all four numbers against the exact expansion of the thin-ring
energy balance.
"""
from __future__ import annotations

import sys

import sympy as sp

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

cs, cl = 1450.0, 4186.0
T_ref = 301.15
T_abs = 308.0
dT = T_abs - T_ref
dCdt = -1.0803e-4
main = 2603.1272        # rho cp * 1e-3 K/s, registry EX_main / EV_main

print("=" * 100)
print("(1) 严格展开: R_0 = -(T-T_ref)(c_s + C c_l)(d rho_s/dC) dC/dt")
print("=" * 100)
print(f"  口径: T-T_ref = {dT:.2f} K, T_abs = {T_abs} K, "
      f"dC/dt = {dCdt:.6g} kg/(kg s)")
print()
hdr = (f"  {'C':>5} {'d rho_s/dC':>12} {'(c_s+C c_l) d rho_s/dC':>24} "
       f"{'R0 完整':>12} {'R0 仅 c_s':>12} {'完整/仅c_s':>10}")
print(hdr)
r0_full_255 = r0_cs_255 = None
for C in (2.55, 2.0, 1.5, 1.0, 0.5, 0.15):
    drs = -522.0 / (1 + C) ** 2
    full = (cs + C * cl) * drs
    r0f = -full * dT * dCdt
    r0r = -cs * drs * dT * dCdt
    if C == 2.55:
        r0_full_255, r0_cs_255 = r0f, r0r
    print(f"  {C:5.2f} {drs:12.4f} {full:24.1f} {r0f:12.3f} {r0r:12.3f} "
          f"{r0f/r0r:10.3f}")
print()
print(f"  论文/注册表所用 R0 (C=2.55, 只取 c_s) = {r0_cs_255:.4f} W/m^3 "
      f"(注册表 EV_R0 = -44.444369208491)")
print(f"  严格 R0 (C=2.55, 完整因子 (c_s+C c_l)) = {r0_full_255:.4f} W/m^3")
print(f"  => 注册表 R0 偏小 {r0_full_255/r0_cs_255:.3f} 倍 "
      f"(= (c_s+2.55 c_l)/c_s = {(cs+2.55*cl)/cs:.3f})")
print(f"  R0 占主项: 注册表 {100*abs(r0_cs_255)/main:.4f}%  "
      f"严格 {100*abs(r0_full_255)/main:.4f}%")

print()
print("=" * 100)
print("(2) 守恒形式的额外项: 绝对锚定 vs 相对锚定")
print("=" * 100)
S_abs = 21598.794238787        # registry EV_Sfalse = -T_abs (d rho cp/dC) dC/dt
S_rel = S_abs * dT / T_abs
print(f"  EV_Sfalse (T 取绝对温度 308.0 K)      = {S_abs:.4f} W/m^3 "
      f"= 主项的 {100*S_abs/main:.4f} %")
print(f"  同一量在 T_ref 锚定下 (乘 (T-T_ref)/T) = {S_rel:.4f} W/m^3 "
      f"= 主项的 {100*S_rel/main:.4f} %")
print(f"  两者相差 T_abs/(T-T_ref) = {T_abs/dT:.3f} 倍")
print(f"  >>> 论文写 829.72 %; 与 R0 同锚定的值是 {100*S_rel/main:.2f} %")

print()
print("=" * 100)
print("(3) 比值 |S_false| / |R_0| 的三种口径")
print("=" * 100)
print(f"  论文所报 (S 绝对锚定 / R0 只取 c_s)：{S_abs/abs(r0_cs_255):.3f}")
print(f"  S 相对锚定 / R0 只取 c_s          ：{S_rel/abs(r0_cs_255):.3f}")
print(f"  S 相对锚定 / R0 完整              ：{S_rel/abs(r0_full_255):.3f}")
print()
print("  => 论文的 485.97 = 44.96 (锚定不匹配) x 8.362 (漏掉 C c_l) x 1.29")
print(f"     {T_abs/dT:.3f} x {(cs+2.55*cl)/cs:.3f} = "
      f"{(T_abs/dT)*((cs+2.55*cl)/cs):.2f}")

print()
print("=" * 100)
print("(4) 用户给的能量收支缺口的两种索引 (tex 第 1263 行附近)")
print("=" * 100)
Tf, Tt = sp.symbols("T_f T_t")
for lbl, expr in (("sum{(M^{n+1}-M^n) T^{n+1}}",
                   sp.Symbol("dMf") * Tf), ("sum{(M^{n+1}-M^n) T^n}",
                                            sp.Symbol("dMf") * Tt)):
    print(f"  {lbl}")
print("  两者在 1 h 处差 (T^{n+1}-T^n) ~ 1.3 K, 而 T ~ 310 K: "
      f"相对差 ~{1.3/310*100:.2f}%")
print("  实测 (本审计的独立运行, M=200 dt=0.25):")
print("    |ΔE+Fh|                    = 5.215554e+04")
print("    |Σ MLg Δ(ρcp) T^{n+1}|     = 5.215564e+04   (相对差 7.2e-6)")
print("    |Σ MLg Δ(ρcp) T^n|         = 5.215554e+04   (相对差 6e-9)")
print("  两者都能到 1e-6, 故该处索引写法不构成可证伪的错误 (非阻塞)")
