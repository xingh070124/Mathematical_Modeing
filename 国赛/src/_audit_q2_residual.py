# -*- coding: utf-8 -*-
"""C1 residual check: is the (T-T_ref) dC/dt cancellation *exact* under the
literal appendix-3 reading of rho(C)?

Identity (verified exactly in sympy):
    (650+128 C) * (1450 + 2736 C/(1+C))  ==  rho_s(C) * (c_s + C c_l)
with rho_s(C) = (650+128C)/(1+C), c_s = 1450, c_l = 4186.

If the SAME rho_s(C) is used in the water-mass balance div J_w = -rho_s dC/dt,
then expanding d/dt[rho_s(C)(c_s+C c_l)(T-T_ref)] leaves
    (c_s + C c_l) rho_s'(C) (T - T_ref) dC/dt
after the c_l (T-T_ref) rho_s dC/dt terms cancel.  This script evaluates that
residual and compares it with the pseudo-source and the main term.
"""
from __future__ import annotations

import sys

import sympy as sp

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

C, T, Tref = sp.symbols("C T T_ref", positive=True)
cs, cl = sp.Integer(1450), sp.Integer(4186)

rho_bulk = 650 + 128 * C
cp = 1450 + 2736 * C / (C + 1)
rho_s = rho_bulk / (1 + C)

print("=" * 100)
print("(1) 恒等式与 rho_s(C) 的导数")
print("=" * 100)
lhs = sp.expand(rho_s * (cs + C * cl))
rhs = sp.expand(rho_bulk * cp)
print(f"  rho_s(C)(c_s+C c_l) - rho_bulk cp = "
      f"{sp.simplify(lhs - rhs)}   (0 表示恒等)")
drs = sp.simplify(sp.diff(rho_s, C))
print(f"  rho_s(C)  = {sp.simplify(rho_s)}")
print(f"  rho_s'(C) = {sp.factor(drs)}")
print(f"  d(rho_bulk cp)/dC = {sp.factor(sp.simplify(sp.diff(rhs, C)))}")

print()
print("=" * 100)
print("(2) 相消后残留项 (c_s+C c_l) rho_s'(C) (T-T_ref) dC/dt")
print("=" * 100)
resid = (cs + C * cl) * drs          # 乘以 (T-T_ref) dC/dt
TrefC, Tmean, dCdt = 28.0, 36.0, -8.3185185185185e-05
print(f"  取 T-T_ref = {Tmean-TrefC} K, dC/dt = {dCdt:.6e} kg/(kg s)")
print(f"  {'C':>6} {'(c_s+C c_l) rho_s\'':>22} {'残留项 W/m^3':>14} "
      f"{'rho cp dT/dt (1e-3)':>21} {'比主项':>9} {'比伪源项':>9}")
for Cv in (2.55, 2.0, 1.5, 1.0, 0.5, 0.15):
    a = float(resid.subs(C, Cv))
    val = a * (Tmean - TrefC) * dCdt
    rcp = float((rho_bulk * cp).subs(C, Cv))
    main = rcp * 1e-3
    rho_s_v = float(rho_s.subs(C, Cv))
    sfalse = float(cl) * (Tmean - TrefC) * rho_s_v * dCdt
    print(f"  {Cv:6.2f} {a:22.1f} {val:14.1f} {main:21.1f} "
          f"{val/main:9.4f} {val/sfalse:9.4f}")

print()
print("=" * 100)
print("(3) rho_s 随 C 的变化 (论文 §局限 的 +111.57 %)")
print("=" * 100)
r0 = float(rho_s.subs(C, 2.55))
r1 = float(rho_s.subs(C, 0.15))
print(f"  rho_s(2.55) = {r0:.4f}, rho_s(0.15) = {r1:.4f}, "
      f"变化 {100*(r1-r0)/r0:+.2f} %")
print("  => 附录3 的 rho(C) 使 rho_s 随 C 变化; 相消式要求它在 C 上为常数.")

print()
print("=" * 100)
print("(4) 实际水质量通量 (由表面热流反推, 检查 rho_s 因子的口径)")
print("=" * 100)
H_evap = 2.4346e6 - 2.391e3 * 8.8888
q_evap_per_area = 0.03651648422704 / (2 * sp.pi * 0.02)   # W/m^2
J_mass = q_evap_per_area / H_evap
print(f"  t=3 h: q_evap = 0.0365165 W/m (per 2pi) = "
      f"{float(q_evap_per_area):.4f} W/m^2")
print(f"  => 实际水质量通量 J = q_evap/H_evap = {float(J_mass):.4e} kg/(m^2 s)")
print(f"     注册表 EC_cJgradT 所用的 J_w = 1.29e-6 kg/(m^2 s) "
      f"(比实际大 {1.29e-6/float(J_mass):.1f} 倍, 偏保守)")
print(f"     rho_s * (D dC/dr)|_R = 275.04 * 8e-7*0.958 = "
      f"{275.0423*8e-7*0.958:.4e} kg/(m^2 s)  (该口径比实际大 "
      f"{275.0423*8e-7*0.958/float(J_mass):.0f} 倍, 与实际热流不符)")
