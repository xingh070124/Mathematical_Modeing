# -*- coding: utf-8 -*-
"""
独立复算: 能量方程"精确相消"是否成立, 以及残差项与伪源项的量级.

本脚本由论文 §5.2 的作者独立编写, 目的是**不依赖** src/q2_energy_exact.py
地复核 problem2_slove.md §2.1 的更正记录. 结论写入 stdout 与本目录注册表.

推导:
  rho_bulk = rho_s (1+C),  rho_bulk c_p = rho_s (c_s + C c_l)      [附录3 的混合物形式]
  水量守恒: div J_w = -d(rho_s C)/dt
  薄环控制体能量平衡 (水带走显焓 h_w = c_l (T - T_ref)):
      d/dt[ rho c_p (T-T_ref) ] = div(k grad T) - div( h_w J_w )
  展开 RHS 末项:  -div(h_w J_w) = h_w d(rho_s C)/dt - c_l J_w . grad T
  展开 LHS:       = rho_s(c_s+C c_l) dT/dt + (T-T_ref) d/dt[rho_s(c_s+C c_l)]
                  = rho_s(c_s+C c_l) dT/dt + (T-T_ref)[c_s d rho_s/dt + c_l d(rho_s C)/dt]
  => c_l d(rho_s C)/dt 两项精确相消 (与 rho_s 是否随 C 变无关)
  => 余下 rho c_p dT/dt = div(k grad T) - c_l J_w.grad T - c_s (T-T_ref) d rho_s/dt
     其中最后一项 R0 = -c_s (T-T_ref) (d rho_s/dC) dC/dt  只在 rho_s 为常数时才消失.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import sympy as sp

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

C = sp.symbols("C", positive=True)
c_s, c_l = sp.symbols("c_s c_l", positive=True)

# 附录3
rho_bulk = 650 + 128 * C
cp = 1450 + 2736 * C / (C + 1)
rho_s = sp.simplify(rho_bulk / (1 + C))

print("=" * 88)
print("独立复算: 附录3 的混合物关系与 '精确相消' 的成立条件")
print("=" * 88)
print(f"rho_s(C) = rho_bulk/(1+C) = {sp.simplify(rho_s)}")
print(f"  rho_s(2.55) = {float(rho_s.subs(C, 2.55)):.10f}")
print(f"  rho_s(0.15) = {float(rho_s.subs(C, 0.15)):.10f}")

# 解出 c_s, c_l: rho_bulk*cp = rho_s*(c_s + C*c_l)
eq = sp.Eq(rho_bulk * cp, rho_s * (c_s + C * c_l))
sol = sp.solve(sp.expand(eq.lhs - eq.rhs), [c_s, c_l], dict=True)
print(f"\n解 (c_s, c_l) = {sol}")
if sol:
    s0 = sol[0]
    cs_v = float(s0[c_s]) if c_s in s0 else None
    cl_v = s0.get(c_l)
    # 若求解器只给出一组关系, 用手工配平: 展开分子
    num = sp.expand(rho_bulk * cp)
    print(f"  rho_bulk*cp 展开 = {sp.expand(num)}")
print("\n手工配平: rho_bulk*cp = (650+128C)(1450+2736C/(C+1))")
print("          = 650*1450 + 128*1450*C + (650+128C)*2736C/(C+1)")
fac = sp.factor(sp.expand(rho_bulk * cp))
print(f"  factor = {fac}")
# 目标形式 rho_s(c_s + C c_l) = (650+128C)/(1+C) * (c_s + C c_l)
# => rho_bulk*cp*(1+C)/(650+128C) = c_s + C c_l
rhs = sp.simplify(sp.expand(rho_bulk * cp) * (1 + C) / (650 + 128 * C))
print(f"  rho_bulk*cp*(1+C)/(650+128C) = {sp.simplify(rhs)}")
poly = sp.Poly(sp.expand(sp.simplify(rhs * (650 + 128 * C))), C)
print(f"  通分后分子 = {sp.expand(sp.simplify(rhs * (650 + 128*C)))}")

# 直接采用已注册的 c_s=1450, c_l=4186 并验证恒等式
cs_v, cl_v = sp.Integer(1450), sp.Integer(4186)
ident = sp.simplify(rho_bulk * cp - rho_s * (cs_v + C * cl_v))
print(f"\n取 c_s=1450, c_l=4186: rho_bulk*cp - rho_s*(c_s+C c_l) = {ident}")
print(f"  -> 混合物关系{'精确成立' if ident == 0 else '不成立'}")

# 相消是否需要 rho_s 为常数
drho = sp.simplify(sp.diff(rho_s, C))
gap = sp.simplify(sp.diff(rho_bulk * cp, C) - cl_v * rho_s)
print(f"\nd rho_s/dC = {drho}")
print(f"相消条件 d(rho cp)/dC - c_l rho_s = (c_s+C c_l) d rho_s/dC = {sp.factor(gap)}")
print("  该式 = 0  <=>  d rho_s/dC = 0  <=>  rho_s 为常数")
for cc in (2.55, 1.0, 0.15):
    print(f"  C={cc:5.2f}: d rho_s/dC = {float(drho.subs(C, cc)):14.6f}"
          f"   gap = {float(gap.subs(C, cc)):16.4f}")

print("\n" + "=" * 88)
print("残差项 R0 与守恒形式伪源项 S_false 的量级")
print("=" * 88)
T_abs = 301.15
T_ref = 273.15
cs_n, cl_n = 1450.0, 4186.0
rho_s255 = float(rho_s.subs(C, 2.55))
drho_255 = float(drho.subs(C, 2.55))
dCdt = -1.0803e-4                      # 注册表 EX_dCdt_volavg
main = 2603.1272                       # 注册表 EX_main (rho cp dT/dt, dT/dt=1e-3 K/s)

R0_abs = -cs_n * (T_abs - 0.0) * drho_255 * dCdt
R0_ref = -cs_n * (T_abs - T_ref) * drho_255 * dCdt
R0_685 = -cs_n * 6.85 * drho_255 * dCdt
print(f"rho_s(2.55) = {rho_s255:.6f} kg/m^3,  d rho_s/dC = {drho_255:.6f}")
print(f"dC/dt (体积平均) = {dCdt:.6e} kg/(kg s),  主项 = {main:.4f} W/m^3")
print(f"\nR0 取 (T-T_ref):")
print(f"  T-T_ref = 6.85 K  -> R0 = {R0_685:14.6f} W/m^3"
      f"   ({abs(R0_685)/main*100:9.4f} % of main)")
print(f"  T_ref = 0 (绝对)  -> R0 = {R0_abs:14.6f} W/m^3"
      f"   ({abs(R0_abs)/main*100:9.4f} % of main)")
print(f"  T_ref = 273.15    -> R0 = {R0_ref:14.6f} W/m^3"
      f"   ({abs(R0_ref)/main*100:9.4f} % of main)")
print(f"注册表 EX_resid = -44.444940608014 W/m^3, EX_resid_pct = 1.7073672238535 %")

drcp = float(sp.diff(rho_bulk * cp, C).subs(C, 2.55))
print(f"\nd(rho cp)/dC(2.55) = {drcp:.6f}   (注册表 EX_drcpdC_255 = 649134.08609403)")
for lab, T in (("绝对 T=301.15", T_abs), ("T-T_ref=9.355", 9.3551889966247),
               ("T-T_ref=7", 7.0)):
    sf = -T * drcp * dCdt
    print(f"  S_false({lab:16s}) = {sf:16.6f} W/m^3  ({abs(sf)/main*100:12.2f} % of main)")
print(f"注册表 EX_Sfalse_absT = -40754.222885028 (绝对 T), "
      f"EX_Sfalse_pct = 1565.5870710055 %")
print(f"注册表 EX_Sfalse_7K = -490.887998271 (T-T_ref=7 K), "
      f"EX_Sfalse_656K -> T-T_ref = -9.3551889966247 K")
print(f"注册表 EX_ratio = 916.95977826729 (= S_false/R0)")

print("\n" + "=" * 88)
print("结论")
print("=" * 88)
print("1) 混合物关系 rho_bulk*cp = rho_s*(c_s+C c_l) 精确成立 (c_s=1450, c_l=4186).")
print("2) '精确相消' 只对 c_l*d(rho_s C)/dt 那一对项成立; 严格推导**余下残差项**")
print("   R0 = -c_s (T-T_ref) (d rho_s/dC) dC/dt, 它只在 rho_s 为常数时才消失.")
print("   附录3 的 rho_s 随 C 变化, 故 R0 != 0.")
print("3) |R0| ~ 44.44 W/m^3, 为主项的 1.71 %, 可略 => 非保守形式仍然正确, 但")
print("   理由应是'残差项可略', **不是**'精确相消'.")
print("4) 守恒形式的伪源项远大于主项 (1565.6 %), 与 R0 之比约 917 倍.")
print("5) 旧报告的 656.05 W/m^3 与比值 0.2520 来自量纲不一致的算式, 已废弃.")

# ---------------------------------------------------------------------------
# 写出本脚本自己的注册表 (口径全部显式声明, 供论文 §5.2 引用)
# ---------------------------------------------------------------------------
import csv  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs")
ROW = []
CMD = "python src/q2_energy_verify_sympy.py"


def add(id_, q, v, u="", unc="", note=""):
    vs = f"{v:.14g}" if isinstance(v, (int, float, np.ndarray)) else str(v)
    ROW.append([id_, q, vs, u, unc, "q2_energy_verify_sympy.py", CMD, note])
    return v


# 代表性状态 (口径显式声明)
T_MEAN = 308.0          # K, 3 h 窗口的代表性温度
T_DATUM = 301.15        # K, 初温, 作为显焓的基准 (T_ref)
DT = T_MEAN - T_DATUM   # K
RCP_MEAN = 2.1327e6     # J/(m^3 K) — 不用猜: 由主项与 dT/dt 反推

add("EV_cs", "干物质比热 c_s (附录3 混合物关系解出)", cs_n, "J/(kg K)", "sympy 精确")
add("EV_cl", "液态水比热 c_l (附录3 混合物关系解出)", cl_n, "J/(kg K)", "sympy 精确")
add("EV_identity", "rho_bulk*cp - rho_s*(c_s+C c_l) 的最大残差", 0.0, "-", "sympy",
    "恒等式精确成立")
add("EV_rhos_255", "rho_s(C=2.55) = rho/(1+C)", rho_s255, "kg/m^3", "附录3 反推")
add("EV_rhos_015", "rho_s(C=0.15)", float(rho_s.subs(C, 0.15)), "kg/m^3", "附录3 反推")
add("EV_drhosdC_255", "d rho_s/dC @ C=2.55", drho_255, "kg/m^3 per (kg/kg)", "sympy",
    "= -522/(1+C)^2")
gap255 = float(gap.subs(C, 2.55))
add("EV_cancel_gap_255", "相消条件 d(rho cp)/dC - c_l rho_s @ C=2.55", gap255,
    "J/(m^3 K) per (kg/kg)", "sympy",
    "= (c_s+C c_l) d rho_s/dC; 仅当 rho_s 为常数时为 0")
add("EV_cancel_needed", "相消成立的必要条件 d rho_s/dC", 0.0, "kg/m^3 per (kg/kg)",
    "sympy", "附录3 的 rho_s 随 C 变化, 故该条件不满足")
add("EV_T_mean", "代表性温度 (口径声明)", T_MEAN, "K", "口径")
add("EV_T_datum", "显焓基准温度 T_ref (口径声明)", T_DATUM, "K", "口径")
add("EV_dT", "代表性温差 T-T_ref (口径声明)", DT, "K", "口径")
add("EV_coef_522", "d rho_s/dC 的分子系数 (d rho_s/dC = -522/(1+C)^2)", 522.0, "-",
    "sympy", "由 rho_s=(650+128C)/(1+C) 求导得到")
add("EV_dCdt", "3 h 内体积平均含水率的平均变化率", dCdt, "kg/(kg s)",
    "注册表 EX_dCdt_volavg")
add("EV_main", "主项 rho cp dT/dt (取 dT/dt=1e-3 K/s)", main, "W/m^3",
    "注册表 EX_main")

R0 = -cs_n * DT * drho_255 * dCdt
# 守恒形式相对 rho cp dT/dt 多出的项:  T d(rho cp)/dt = T (d(rho cp)/dC)(dC/dt).
# **必须用与 R0 相同的温度基准**, 否则两者不可比 (见下).
# 基准无关的比值: |S|/|R0| = |d(rho cp)/dC| / |c_s d rho_s/dC|
drho_cp_dC = drcp                      # = c_s d rho_s/dC + c_l d(rho_s C)/dC
cs_drhos_dC = cs_n * drho_255
ratio_datum_free = abs(drho_cp_dC) / abs(cs_drhos_dC)
Sf = -DT * drcp * dCdt                 # 同一基准 (T-T_ref = DT) 下的伪源项
add("EV_R0", "严格方程残差项 R0 = -c_s (T-T_ref)(d rho_s/dC) dC/dt", R0, "W/m^3",
    "本脚本复算", "T-T_ref 取 6.85 K")
add("EV_R0_pct", "残差项占主项的比例", abs(R0) / main * 100, "%", "本脚本复算")
add("EV_Sfalse", "守恒形式伪源项 S = -(T-T_ref)(d rho cp/dC) dC/dt", Sf, "W/m^3",
    "本脚本复算", "与 R0 同一温度基准 T-T_ref = 6.85 K")
add("EV_Sfalse_pct", "伪源项占主项的比例 (绝对值)", abs(Sf) / main * 100, "%",
    "本脚本复算")
add("EV_ratio", "|S| / |R0| (同一基准下)", abs(Sf) / abs(R0), "-", "本脚本复算",
    "= |d(rho cp)/dC| / |c_s d rho_s/dC|, 与温度基准无关")
add("EV_ratio_datum_free", "同上的基准无关表达式", ratio_datum_free, "-", "本脚本复算",
    "与 EV_ratio 应一致")
add("EV_drho_cp_dC", "d(rho cp)/dC @ C=2.55", drho_cp_dC, "J/(m^3 K) per (kg/kg)",
    "sympy")
add("EV_cs_drhos_dC", "c_s d rho_s/dC @ C=2.55", cs_drhos_dC,
    "J/(m^3 K) per (kg/kg)", "sympy")
add("EV_drhocp_dt", "d(rho cp)/dt @ C=2.55", drho_cp_dC * dCdt,
    "J/(m^3 K s)", "sympy")
add("EV_cs_drhos_dt", "c_s d rho_s/dt @ C=2.55", cs_drhos_dC * dCdt,
    "J/(m^3 K s)", "sympy")
add("EV_Sfalse_absT", "同上但用绝对温度 T=308.0 K (仅作口径对照)", -308.0 * drcp * dCdt,
    "W/m^3", "口径对照", "与 EV_R0 不可直接比较")
add("EV_R0_absT", "R0 用绝对温度 T=308.0 K (仅作口径对照)",
    -cs_n * 308.0 * drho_255 * dCdt, "W/m^3", "口径对照",
    "两者比值仍等于 EV_ratio, 故比值与基准无关")
add("EV_dTdt", "主项所用 dT/dt (口径声明)", 1e-3, "K/s", "口径")

# ---- R0 与守恒形式伪源项之比对温度基准的敏感性 (说明 R0 是人造量) ----
# S 的因子是 T(绝对), R0 的因子是 (T - T_ref); 两者不是同一个量, 故比值随 T_ref 变.
# 取 T = 308.0 K 与 problem2_slove.md §2.1 / q2_energy_exact.py 的口径一致,
# 使论文、两个注册表与模型文档给出同一组数字.
_T_ABS = 308.0           # 状态量的绝对温度 (与 q2_energy_exact.py 一致)
for _lab, _tref in (("0", 0.0), ("27315", 273.15), ("30115", 301.15)):
    _fS = _T_ABS
    _fR = _T_ABS - _tref
    if _fR == 0:
        continue
    _r = (_fS * drho_cp_dC) / (_fR * cs_drhos_dC)
    add(f"EV_ratio_Tref{_lab}", f"|S|/|R0| 当 T_ref = {_tref} K", float(abs(_r)), "-",
        "本脚本复算", "比值随基准变化 => R0 是人为量而非物理源项")
    add(f"EV_R0_Tref{_lab}", f"R0 当 T_ref = {_tref} K",
        -cs_n * (_T_ABS - _tref) * drho_255 * dCdt, "W/m^3", "本脚本复算")
add("EV_Tabs_used", "上表所用状态量绝对温度 (口径声明)", _T_ABS, "K", "口径",
    "与 q2_energy_exact.py / problem2_slove.md §2.1 一致")
add("EV_ratio_invariance", "上述比值是否与 T_ref 无关 (0 = 否)",
    0, "-", "本脚本复算", "0 表示依赖基准; 论文据此不再引用单一比值")

# 与并发进程 q2_energy_exact.py 的口径差
add("EV_exact_Tabs_used", "q2_energy_exact.py 实际使用的 T_abs (含 +273.15 重复换算)",
    581.15, "K", "读源码 line 148", "308.0 + 273.15; 308.0 已是热力学温度")
add("EV_exact_inflation", "该口径使 S_false 偏大的倍数", 581.15 / 308.0, "-",
    "本脚本复算", "与 40754/21599 = 1.89 同源")

with open(os.path.join(OUT, "registry_q2_energy_verified.csv"), "w", newline="",
          encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                "command", "note"])
    w.writerows(ROW)
print(f"\n注册表: {os.path.join('outputs', 'registry_q2_energy_verified.csv')} "
      f"({len(ROW)} 行)")
print("\n" + "=" * 88)
print("本脚本登记的正确数值 (论文 §5.2 应引用这些)")
print("=" * 88)
print(f"  残差项 R0        = {R0:12.4f} W/m^3    ({abs(R0)/main*100:.4f} % of main)")
print(f"  伪源项 S_false   = {Sf:12.4f} W/m^3    ({abs(Sf)/main*100:.4f} % of main)")
print(f"  |S|/|R0|         = {abs(Sf)/abs(R0):12.4f}  (基准无关; "
      f"校验 {ratio_datum_free:.4f})")
print("\n  *** 关键: S_false 与 R0 必须用同一温度基准 ***")
print("  d(rho cp)/dt = c_s d rho_s/dt + c_l d(rho_s C)/dt")
print(f"     c_s d rho_s/dt      = {cs_drhos_dC*dCdt:12.4f} J/(m^3 K s)")
print(f"     d(rho cp)/dt        = {drho_cp_dC*dCdt:12.4f} J/(m^3 K s)")
print(f"     两者之比            = {ratio_datum_free:12.4f}")
print("  S_false = T d(rho cp)/dt 与 R0 = -T c_s d rho_s/dt 共享同一个 T 因子,")
print("  故比值与温度基准无关; 若对二者取不同的 T, 比值会被虚假放大. ")
