# -*- coding: utf-8 -*-
"""Independent sympy re-derivation of the Q2 energy-form algebra (claim C1).

Not a re-run of q2_energy_algebra.py: this rebuilds the argument from the
problem statement's appendix-3 expressions and checks
  (a) uniqueness / exactness of the (rho_s, c_s, c_l) map,
  (b) the cancellation of the (T-T_ref) dC/dt terms,
  (c) the form of the spurious source term carried by the conservative form,
  (d) the ratio S_false / (rho cp dT/dt) for several choices of dT/dt.
"""
from __future__ import annotations

import sys

import sympy as sp

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

C, cs, cl, rs = sp.symbols("C c_s c_l rho_s", positive=True)

print("=" * 100)
print("(a) 附录3 rho(C)=650+128C, cp(C)=1450+2736C/(C+1)")
print("=" * 100)
rho = 650 + 128 * C
cp = 1450 + 2736 * C / (C + 1)
rcp = sp.expand(sp.simplify(rho * cp))
print(f"  rho*cp = {sp.factor(rcp)}")

# mixture closure with rho_s eliminated by definition rho_s := rho/(1+C)
rs_def = rho / (1 + C)
mix = sp.expand(sp.simplify(rs_def * (cs + C * cl)))
print(f"  rho_s(c_s + C c_l) with rho_s := rho/(1+C)  =  {sp.factor(mix)}")
eq = sp.Eq(sp.simplify(mix - rcp), 0)
poly = sp.Poly(sp.numer(sp.together(eq.lhs)), C)
print(f"  等价方程: {sp.Eq(poly.as_expr(), 0)}")
coeffs = poly.all_coeffs()
sol = sp.solve(coeffs, [cs, cl], dict=True)
print(f"  系数方程 {coeffs}  ->  解 {sol}")
assert sol and len(sol) == 1, "解不唯一或不存在"
c_sv, c_lv = sol[0][cs], sol[0][cl]
print(f"  => c_s = {c_sv}, c_l = {c_lv}   (唯一解)")
print(f"  c_l - c_s = {sp.simplify(c_lv - c_sv)} = 附录3 的分子 2736 ? "
      f"{sp.simplify(c_lv - c_sv) == 2736}")
print(f"  c_s = 附录3 的常数项 1450 ? {c_sv == 1450}")
# residual: exact or floating point?
for Cv in (2.55, 2.0, 1.0, 0.5, 0.15, 0.001, 100):
    lhs = rho.subs(C, sp.Rational(str(Cv))) * cp.subs(C, sp.Rational(str(Cv)))
    rhs = (rs_def * (cs + C * cl)).subs({C: sp.Rational(str(Cv)), cs: c_sv,
                                         cl: c_lv})
    print(f"    C={Cv:>7}: 精确差 = {sp.simplify(lhs - rhs)}")
print("  -> 恒等式在所有 C 上精确成立; 1.93e-16 只是 float 回代的舍入")

print()
print("=" * 100)
print("(b) 薄环能量平衡: (T-T_ref) dC/dt 两项的相消")
print("=" * 100)
t = sp.Symbol("t")
T = sp.Function("T")(t)
Cc = sp.Function("C")(t)
Tref = sp.Symbol("T_ref", positive=True)
rho_s = sp.Symbol("rho_s", positive=True)
lhs = sp.diff(rho_s * (cs + Cc * cl) * (T - Tref), t)
lhs = sp.expand(lhs)
print(f"  LHS = d/dt[rho_s(c_s+C c_l)(T-T_ref)] = {lhs}")
# RHS: div(k grad T) - div(h_w J_w), h_w = c_l (T-Tref), div J_w = -rho_s dC/dt
divhw_Jw = cl * sp.diff(T, t) * sp.Symbol("dummy0")  # placeholder
rhs_extra = cl * (T - Tref) * rho_s * sp.diff(Cc, t) - cl * sp.Symbol("Jw_gradT")
print("  RHS 中的 -div(h_w J_w) = +c_l(T-T_ref) rho_s dC/dt - c_l J_w.grad T")
diff = sp.simplify(lhs - (cl * (T - Tref) * rho_s * sp.diff(Cc, t)))
print(f"  LHS - [RHS 中的 +c_l(T-T_ref)rho_s dC/dt] = {sp.expand(diff)}")
print("  两者相等, 故相消后:  rho(C)c_p(C) dT/dt = div(k grad T) - c_l J_w.grad T")
print("  守恒形式 d(rho cp T)/dt = div(k grad T) 的残差(伪源项):")
print("    S_false = +c_l (T-T_ref) rho_s dC/dt   (符号: 失水 dC/dt<0 -> S<0)")

print()
print("=" * 100)
print("(d) 伪源项与主项的量级比 (对 dT/dt 的取法做敏感性)")
print("=" * 100)
cl_n = 4186.0
rho_s_n = 275.0423
dCdt = -(0.8984) / 10800.0
rho_cp = (650 + 128 * 1.5) * (1450 + 2736 * 1.5 / 2.5)
print(f"  c_l={cl_n}, rho_s={rho_s_n}, dC/dt={dCdt:.6e}, "
      f"rho cp(C=1.5)={rho_cp:.1f}")
for dTdT, lbl in ((1e-3, "论文所用假设 1e-3 K/s (EC_main)"),
                  (2.0e-3, "由中心温度 28->49.77/10800 s 的时均"),
                  (1.85e-3, "体积平均时均"),
                  (4.5e-3, "升温段瞬时 (t=0.5~1 h)")):
    for dTref, tlbl in ((7.0, "T-T_ref=7 K (论文正文)"),
                        (6.85, "T-T_ref=6.85 K (脚本 T=308 K)")):
        S = cl_n * dTref * rho_s_n * dCdt
        print(f"    {lbl:36s} {tlbl:32s} |S|={abs(S):8.2f} W/m^3, "
              f"主项={rho_cp*dTdT:9.1f}, 比值={abs(S)/(rho_cp*dTdT):.4f}")
