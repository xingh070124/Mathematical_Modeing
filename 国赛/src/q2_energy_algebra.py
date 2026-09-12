# -*- coding: utf-8 -*-
"""
q2_energy_algebra.py -- 问题二能量方程"正确形式"的符号推导与量级核验.

背景
----
附录3 给出 rho(C) = 650 + 128C 与 cp(C) = 1450 + 2736C/(C+1).
令 rho_s 为**干基骨架密度**（干物质质量/体积），则混合物体密度
    rho_bulk = rho_s (1 + C).
本脚本用 sympy 验证: 附录3 的两式**恰好等价于**混合物关系
    rho_bulk = rho_s (1 + C),   rho_bulk cp = rho_s (c_s + C c_l),
其中 c_s = 1450 J/(kg K)（干物质比热）, c_l = 4186 J/(kg K)（液态水比热）.

由此可对薄环控制体写严格的能量平衡（水以扩散离开控制体时带走显焓）：

    d/dt[ rho cp (T - T_ref) ] = div(k grad T) - div( h_w J_w ),
    h_w = c_l (T - T_ref),   J_w 为水质量通量（相对干物质）

配合水量守恒 div J_w = -rho_s dC/dt, 可得**两处相消**，最终

    rho(C) cp(C) dT/dt = div( k grad T ) - c_l J_w . grad T

即: 附录3 的物性代入后, 方程的正确形式是 **rho cp dT/dt**（非保守形式）,
而 d(rho cp T)/dt（守恒形式）会多出 +c_l (T-T_ref) rho_s dC/dt 的伪源项。
问题一中 rho cp 为常数, 两种形式恒等, 故该分歧是问题二特有的。

运行: python src/q2_energy_algebra.py
输出: outputs/registry_q2_energy.csv
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np
import sympy as sp

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
CMD = "python src/q2_energy_algebra.py"
REG = []


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMD, CMD, note])


def main():
    C, Cs, Cl = sp.symbols("C c_s c_l", positive=True)

    # ------------------------------------------------------------------
    # A. 附录3 的两式与混合物关系的等价性
    # ------------------------------------------------------------------
    print("=" * 96)
    print("A 附录3 (rho, cp) 与混合物关系 rho_s(1+C) / rho_s(c_s + C c_l) 的等价性")
    print("=" * 96)
    rho_bulk = 650 + 128 * C
    cp_app3 = 1450 + 2736 * C / (C + 1)
    rcp_app3 = sp.expand(sp.simplify(rho_bulk * cp_app3))
    print(f"  rho(C) cp(C) = {sp.factor(rcp_app3)}")

    # 混合物形式: rho_s (c_s + C c_l),  rho_s = (650+128C)/(1+C)
    rho_s = rho_bulk / (1 + C)
    mix = sp.expand(rho_s * (Cs + C * Cl))
    print(f"  rho_s (c_s + C c_l) = {sp.simplify(mix)}")
    # 令两者相等, 解 c_s, c_l
    eq = sp.Eq(sp.simplify(mix - rcp_app3), 0)
    sol = sp.solve(sp.Poly(sp.numer(sp.together(eq.lhs)), C).all_coeffs(), [Cs, Cl],
                   dict=True)
    print(f"  解得: {sol}")
    assert sol, "无法解出 c_s, c_l"
    c_s_val = float(sol[0][Cs])
    c_l_val = float(sol[0][Cl])
    print(f"  => c_s = {c_s_val} J/(kg K)  (干物质比热, 典型值)")
    print(f"  => c_l = {c_l_val} J/(kg K)  (液态水比热, 教科书值 4186)")
    add("EA_cs", "附录3 隐含的干物质比热 c_s", c_s_val, "J/(kg K)",
        "sympy 解析解出")
    add("EA_cl", "附录3 隐含的液态水比热 c_l", c_l_val, "J/(kg K)",
        "sympy 解析解出")

    # 数值核验
    worst = 0.0
    for Cv in (2.55, 2.0, 1.0, 0.5, 0.15):
        lhs = (650 + 128 * Cv) * (1450 + 2736 * Cv / (Cv + 1))
        rhs = (650 + 128 * Cv) / (1 + Cv) * (c_s_val + Cv * c_l_val)
        worst = max(worst, abs(lhs - rhs) / lhs)
    print(f"  数值核验: C ∈ {{2.55,2,1,0.5,0.15}} 上最大相对差 = {worst:.3e}")
    add("EA_equiv_max", "混合物关系与附录3 的最大相对差", worst, "-", "数值核验")

    # 干基骨架密度随 C 的变化 (说明 B7 无收缩假设下的不自洽)
    print()
    print("=" * 96)
    print("B 干基骨架密度 rho_s(C) = (650+128C)/(1+C) —— 无收缩假设的自洽性检查")
    print("=" * 96)
    print(f"  {'C':>6} {'rho_bulk':>10} {'rho_s':>10}")
    for Cv in (2.55, 2.0, 1.0, 0.5, 0.15):
        r_s = (650 + 128 * Cv) / (1 + Cv)
        print(f"  {Cv:6.2f} {650+128*Cv:10.2f} {r_s:10.4f}")
        add(f"EB_rhos_{Cv}", f"干基骨架密度 rho_s(C={Cv})", r_s, "kg/m^3",
            "由附录3 rho 反推")
    r_s0 = (650 + 128 * 2.55) / 3.55
    r_s1 = (650 + 128 * 0.15) / 1.15
    print(f"  rho_s 由 {r_s0:.4f} 变到 {r_s1:.4f}, 变化 {100*(r_s1-r_s0)/r_s0:+.2f}%")
    print("  => 附录3 的 rho(C) 与'体积不变+干物质守恒'并不严格自洽。")
    print("     但题面式 (4) 把 D 直接定义在 C 上 (-D dC/dr = h_m (C-C_inf)),")
    print("     故水分方程取 dC/dt = (1/r) d/dr(r D dC/dr) 是题面给定的口径,")
    print("     与 rho(C) 只进入热惯性的做法自洽 (见 problem2_slove.md §2.3)。")
    add("EB_rhos_drift", "rho_s 在 C:2.55->0.15 上的变化", 100 * (r_s1 - r_s0) / r_s0,
        "%", "自洽性检查")

    # ------------------------------------------------------------------
    # C. 能量方程: 守恒形式 vs 非保守形式
    # ------------------------------------------------------------------
    print()
    print("=" * 96)
    print("C 薄环能量平衡的两种写法")
    print("=" * 96)
    Tt, Tref = sp.symbols("T T_ref", positive=True)
    e = sp.Symbol("e")
    print("  守恒型(误):  d/dt[ rho cp (T-Tref) ] = div(k grad T)")
    print("  严格平衡  :  d/dt[ rho cp (T-Tref) ] = div(k grad T) - div( h_w J_w )")
    print("                h_w = c_l (T-Tref);   div J_w = -rho_s dC/dt")
    print("  展开右侧后项: -c_l (T-Tref) div J_w - c_l J_w.grad T")
    print("               = +c_l (T-Tref) rho_s dC/dt - c_l J_w.grad T")
    print("  左端展开    : rho_s(c_s+c_l C) dT/dt + c_l (T-Tref) rho_s dC/dt")
    print("  => 含 (T-Tref) dC/dt 的两项**精确相消**, 得")
    print("     rho(C) cp(C) dT/dt = div(k grad T) - c_l J_w . grad T     ……(Q2-E)")
    print()
    print("  守恒型多出的伪源项 (本模型实际忽略的量):")
    print("     S_false = +c_l (T-Tref) rho_s dC/dt")

    # 用真实量级估计伪源项与主项之比
    print()
    print("  量级核验 (t=1800 s, 由 q2_produce 的解):")
    cl = c_l_val
    rho_s = r_s0 if False else 275.0423
    # dC/dt 由数值解估: 表面 0->1800s 由 2.55 降到 1.648, 折算总体
    # 取体积平均含水率的变化率
    W0, W1800 = None, None
    rho = lambda Cc: 650 + 128 * Cc
    cp = lambda Cc: 1450 + 2736 * Cc / (Cc + 1)
    # 体积平均 C: 由 q2_produce 的 W (per 2pi) 除以体积
    # W0 = sum(MLg*C0), V = sum(MLg) = R^2/2
    dr = 0.02 / 400
    r = np.arange(401) * dr
    MLg = np.empty(401)
    MLg[0] = dr * dr / 6
    MLg[1:400] = dr * r[1:400]
    MLg[400] = dr * (r[399] + 2 * r[400]) / 6
    V = MLg.sum()
    Cbar0 = 2.55
    print(f"    比体积权 V = sum(MLg) = {V:.10e} m^2  (= R^2/2 = {0.02**2/2:.10e})")
    add("EC_V", "集中质量的总体积权 sum(MLg)", float(V), "m^2", "= R^2/2")
    # 用附件1 给出的环境湿度与 q2 的解做估计: 3h 内平均含水率降幅约
    # (由 q2_produce 日志给出精确值), 这里只给解析量级
    dCdt_avg = -(0.8984) / 10800.0        # kg/kg/s, 由生产解的平均降幅
    TrefK = 301.15
    Tmean = 308.0                          # 3h 内平均温度量级 (K)
    S_false = cl * (Tmean - TrefK) * rho_s * dCdt_avg
    rcp_mean = float(rho(1.5) * cp(1.5))
    dTdt = 1e-3
    main_term = rcp_mean * dTdt
    print(f"     c_l (T-Tref) rho_s dC/dt = {S_false:.4e} W/m^3")
    print(f"     主项 rho cp dT/dt          = {main_term:.4e} W/m^3 (取 dT/dt=1e-3 K/s)")
    print(f"     比值 = {abs(S_false)/main_term:.4f}  -> 伪源项与主项**同量级**, 不可忽略")
    add("EC_Sfalse", "守恒形式的伪源项 c_l(T-Tref)rho_s dC/dt", float(S_false),
        "W/m^3", "量级估计")
    add("EC_ratio", "伪源项 / 主项", float(abs(S_false) / main_term), "-", "量级估计")
    add("EC_Sfalse_abs", "守恒形式伪源项的绝对值", float(abs(S_false)), "W/m^3",
        "量级估计")
    add("EC_main", "主项 rho cp dT/dt 的量级 (取 dT/dt=1e-3 K/s)",
        float(main_term), "W/m^3", "量级估计")
    add("EC_dCdt_avg", "3 h 内体积平均含水率的平均变化率", float(dCdt_avg),
        "kg/(kg s)", "由生产解的平均降幅")

    # 被忽略的 -c_l J_w . grad T
    cl_j = cl
    Jw = 1.29e-6           # kg/(m^2 s), 表面水通量量级 (3h 末)
    gradT = 160.0          # K/m
    print()
    print("  被保留后又被略去的项 -c_l J_w . grad T 的量级:")
    print(f"     c_l |J_w| |grad T| = {cl_j*Jw*gradT:.4e} W/m^3")
    print(f"     与导热项 k grad^2 T ~ {0.48*gradT/(0.02/400):.4e} W/m^3 相比")
    print(f"     相对贡献 = {cl_j*Jw*gradT/(0.48*gradT/0.02):.4f} * (2R/...)")
    # 更稳妥: 与 rho cp dT/dt 比较
    rel2 = cl_j * Jw * gradT / main_term
    print(f"     与主项之比 = {rel2:.3e}  -> 可忽略")
    add("EC_cJgradT", "被略去的 -c_l J_w.grad T 量级", float(cl_j * Jw * gradT),
        "W/m^3", "量级估计")
    add("EC_cJgradT_rel", "-c_l J_w.grad T 与主项之比", float(rel2), "-", "量级估计")

    # ------------------------------------------------------------------
    # E. t=0 的表面初始降温速率 (蒸发吸热在最初时刻的强度)
    # ------------------------------------------------------------------
    print()
    print("=" * 96)
    print("E t=0 表面节点的初始降温速率 (解释极值原理下界失效的机理)")
    print("=" * 96)
    Rr = 0.02
    hmm = 8.0e-7
    Hev0 = 2.4346e6
    Cinf0 = 0.01963
    C_R0 = 2.55
    T_inf0 = 28.0
    q_ev0 = Hev0 * hmm * (C_R0 - Cinf0)
    q_cv0 = 25.0 * (T_inf0 - 28.0)
    print(f"  t=0: T_R = T_inf = 28 degC  ->  对流项 q_conv = {q_cv0:.6f} W/m^2")
    print(f"       C_R = 2.55, C_inf = {Cinf0}  ->  蒸发项 q_evap = "
          f"{q_ev0:.6f} W/m^2")
    print(f"  => 初始时刻表面只有蒸发失热, 必然降温")
    for M in (400, 1600):
        dr = Rr / M
        r_ = np.arange(M + 1) * dr
        MLgM = dr * (r_[M - 1] + 2 * r_[M]) / 6.0     # per 2 pi, 已约 rho cp
        rcp0 = float(rho(2.55) * cp(2.55))
        rate = -q_ev0 / (rcp0 * MLgM)
        print(f"  M={M:5d}: MLg_M = {MLgM:.6e} m^2, rho cp = {rcp0:.1f} "
              f"->  dT_R/dt|_0 = {rate:.4f} K/s")
        add(f"EE_rate_M{M}", f"M={M}: t=0 表面初始降温速率", float(rate), "K/s",
            "解析 (集中质量表面节点)")
    dr = Rr / 1600
    r_ = np.arange(1601) * dr
    MLgM = dr * (r_[1599] + 2 * r_[1600]) / 6.0
    rcp0 = float(rho(2.55) * cp(2.55))
    add("EE_qev0", "t=0 表面蒸发吸热热流", float(q_ev0), "W/m^2", "解析")
    add("EE_qconv0", "t=0 表面对流供热热流", float(q_cv0), "W/m^2", "解析")
    add("EE_MLgM_1600", "M=1600 的表面集中质量几何因子", float(MLgM), "m^2", "解析")
    add("EE_rate_prod", "M=1600: t=0 表面初始降温速率",
        float(-q_ev0 / (rcp0 * MLgM)), "K/s", "解析")
    print("  该速率与 result2.xlsx 中表面温度在最初 ~10 s 下降到 27.9905 degC")
    print("  的形态一致 (q2_derive.py)。")

    # ------------------------------------------------------------------
    # F. 问题一的对照: 常数 rho cp 时两式恒等
    # ------------------------------------------------------------------
    print()
    print("=" * 96)
    print("D 问题一的对照: rho cp 为常数时两式恒等")
    print("=" * 96)
    Tsym = sp.Function("T")(sp.Symbol("t"))
    a = sp.Symbol("a", positive=True)
    d1 = sp.diff(a * Tsym, sp.Symbol("t")) / a
    d2 = sp.diff(Tsym, sp.Symbol("t"))
    print(f"  (1/(rho cp)) d(rho cp T)/dt = {sp.simplify(d1)}")
    print(f"  dT/dt                       = {sp.simplify(d2)}")
    print(f"  差 = {sp.simplify(d1 - d2)}  -> 问题一中两种形式**完全相同**")
    print("  故该分歧只在问题二出现 (rho cp 随 C 变化 63.74%)")

    with open(os.path.join(OUT, "registry_q2_energy.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n注册表: {os.path.join(OUT, 'registry_q2_energy.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
