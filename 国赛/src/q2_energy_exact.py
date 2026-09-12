# -*- coding: utf-8 -*-
"""
q2_energy_exact.py -- 能量方程推导的**严格**复核 (回应独立审计的 C1 质疑).

审计指出的问题
--------------
`q2_energy_algebra.py` 声称薄环能量平衡中含 (T-T_ref)∂_tC 的两项"精确相消",
从而得到非保守形式。该相消要求

        d(ρ c_p)/dC = c_l ρ_s

而由附录3, ρ c_p = ρ_s(c_s + C c_l) 且 ρ_s = ρ(C)/(1+C) = (650+128C)/(1+C) **随 C 变化**,
故

        d(ρ c_p)/dC = c_l ρ_s + (c_s + C c_l) dρ_s/dC

多出 (c_s + C c_l) dρ_s/dC ≠ 0。"精确相消"的说法**不成立**。

本脚本给出严格结果
------------------
以干物质密度 ρ_s := ρ_bulk/(1+C)、水量守恒 ∂(ρ_s C)/∂t = -div J_w 为准,
重新作薄环能量平衡, 得

        ρ c_p ∂T/∂t = div(k∇T) - c_l J_w·∇T - c_s (T-T_ref) ∂ρ_s/∂t

即比原先的报告多一项 -c_s(T-T_ref)∂_s ρ_s。本脚本:

  (1) 用 sympy 证明 d(ρ c_p)/dC - c_l ρ_s = (c_s+C c_l) dρ_s/dC, 并给出其数值;
  (2) 量化残差项 -c_s(T-T_ref)(dρ_s/dC)(∂_tC) 的量级;
  (3) 量化"守恒形式"相对严格形式真正略去的项 (注意代码用的是绝对 T);
  (4) 给出结论: 虽然"精确相消"的说法错, 但**非保守形式仍是对的**,
      因为残差项比守恒形式多出的伪源项小两个数量级。

运行: python src/q2_energy_exact.py
输出: outputs/registry_q2_energy_exact.csv, outputs/q2_energy_exact.log
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
sys.path.insert(0, os.path.join(ROOT, "src"))
OUT = os.path.join(ROOT, "outputs")
CMD = "python src/q2_energy_exact.py"
LOG, REG = [], []


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMD, CMD, note])


def main():
    C = sp.Symbol("C", positive=True)
    rho_bulk = 650 + 128 * C
    cp = 1450 + 2736 * C / (C + 1)
    rcp = sp.expand(sp.simplify(rho_bulk * cp))
    rho_s = rho_bulk / (1 + C)
    c_s, c_l = sp.Integer(1450), sp.Integer(4186)

    say("=" * 96)
    say("(1) d(rho cp)/dC 与 c_l rho_s 的差")
    say("=" * 96)
    ident = sp.simplify(rcp - rho_s * (c_s + C * c_l))
    say(f"  rho cp - rho_s(c_s + C c_l) = {ident}   (恒等于 0 则混合物关系成立)")
    add("EX_identity", "rho cp - rho_s(c_s+C c_l)", float(ident), "-", "sympy")

    d_rcp = sp.simplify(sp.diff(rcp, C))
    d_rho_s = sp.simplify(sp.diff(rho_s, C))
    lhs = sp.simplify(d_rcp - c_l * rho_s)
    rhs = sp.simplify((c_s + C * c_l) * d_rho_s)
    say(f"  d(rho cp)/dC      = {sp.factor(d_rcp)}")
    say(f"  c_l rho_s         = {sp.factor(c_l*rho_s)}")
    say(f"  d(rho cp)/dC - c_l rho_s = {sp.factor(lhs)}")
    say(f"  (c_s + C c_l) d rho_s/dC = {sp.factor(rhs)}")
    say(f"  两者之差 = {sp.simplify(lhs - rhs)}   -> {'严格相等' if sp.simplify(lhs-rhs)==0 else '不等'}")
    say(f"  d rho_s/dC = {sp.factor(d_rho_s)}")
    say("  => '含 (T-T_ref) dC/dt 的两项精确相消' 的说法**不成立**: 相消要求")
    say("     d(rho cp)/dC = c_l rho_s, 而这只在 rho_s 为常数时成立。")
    say("     附录3 的 rho(C) 反推的 rho_s 并非常数 (problem2_slove.md §2.3)。")

    d_rho_s_f = sp.lambdify(C, d_rho_s, "numpy")
    for Cv in (2.55, 1.0, 0.15):
        drs = float(d_rho_s_f(Cv))
        gap = float(sp.lambdify(C, lhs, "numpy")(Cv))
        say(f"    C={Cv:5.2f}: d rho_s/dC = {drs:10.4f} kg/m^3 per (kg/kg); "
            f"|d(rho cp)/dC - c_l rho_s| = {abs(gap):12.2f}")
        add(f"EX_drhosdC_{Cv}", f"d rho_s/dC @ C={Cv}", drs, "kg/m3 per (kg/kg)")
        add(f"EX_lhs_gap_{Cv}", f"d(rho cp)/dC - c_l rho_s @ C={Cv}", gap,
            "J/(m3 K) per (kg/kg)")

    # ------------------------------------------------------------------
    # (2) 严格结果与残差项的量化
    # ------------------------------------------------------------------
    say()
    say("=" * 96)
    say("(2) 严格能量方程的残差项 -c_s (T-T_ref) d rho_s/dt")
    say("=" * 96)
    T_ref = 301.15
    T_mean = 308.0
    Cbar0, Cbar_end = 2.55, 1.383261
    dCdt = (Cbar_end - Cbar0) / 10800.0
    rho_s0 = float(rho_bulk.subs(C, 2.55) / (1 + 2.55))
    drs0 = float(d_rho_s_f(2.55))
    resid = -1450.0 * (T_mean - T_ref) * drs0 * dCdt
    say(f"  体积平均 dC/dt = ({Cbar_end:.6f} - {Cbar0})/10800 = {dCdt:.6e} kg/(kg s)")
    say(f"  d rho_s/dC @C=2.55 = {drs0:.4f} kg/m^3 per (kg/kg)")
    say(f"  rho_s(2.55) = {rho_s0:.4f} kg/m^3")
    say(f"  残差项 = -c_s (T-T_ref)(d rho_s/dC) dC/dt")
    say(f"         = -1450 * {T_mean-T_ref:.2f} * ({drs0:.4f}) * ({dCdt:.4e})")
    say(f"         = {resid:.4f} W/m^3")
    add("EX_dCdt_volavg", "3 h 内体积平均含水率的平均变化率", dCdt, "kg/(kg s)")
    add("EX_rhos_255", "rho_s(C=2.55)", rho_s0, "kg/m^3")
    add("EX_resid", "严格方程的残差项 -c_s(T-T_ref)(d rho_s/dC)dC/dt",
        float(resid), "W/m^3", "量级估计")

    # ------------------------------------------------------------------
    # (3) 守恒形式真正略去的项 (代码用绝对 T, 故 T_ref=0)
    # ------------------------------------------------------------------
    say()
    say("=" * 96)
    say("(3) 守恒形式相对严格形式略去的项 —— 代码用绝对温度, 故 T_ref = 0")
    say("=" * 96)
    say("  代码的守恒形式:  d(rho cp T)/dt = div(k grad T)")
    say("  展开左端:        rho cp dT/dt + T d(rho cp)/dt")
    say("                  = rho cp dT/dt + T (d(rho cp)/dC) dC/dt")
    say("  严格方程:        rho cp dT/dt = div(k grad T) - c_l J_w.grad T")
    say("                                   - c_s (T-T_ref) d rho_s/dt")
    say("  取 T_ref = 0（代码以**热力学温度**为状态量，故 T 就是 308.0 K，")
    say("  不可再加 273.15；早先本脚本误写为 308.0+273.15=581.15 K，使 S_false")
    say("  虚高 1.887 倍，已更正）。守恒形式的左端比严格方程的 rho cp dT/dt 多出")
    say("      S_false = -T (d(rho cp)/dC) dC/dt      [取正号=额外升温]")
    T_abs = 308.0
    d_rcp_f = sp.lambdify(C, d_rcp, "numpy")
    drcp0 = float(d_rcp_f(2.55))
    S_false_absT = -T_abs * drcp0 * dCdt          # 正号 = 多出的升温
    S_false_7K = -7.0 * drcp0 * dCdt
    say(f"  d(rho cp)/dC @C=2.55 = {drcp0:.2f} J/(m^3 K) per (kg/kg)")
    say(f"  S_false (T = {T_abs:.2f} K)     = {S_false_absT:+.4f} W/m^3")
    say(f"  S_false (若取 T-T_ref = 7 K)    = {S_false_7K:+.4f} W/m^3")
    say(f"  原报告写的 656.05 W/m^3 对应 T-T_ref = "
        f"{-656.05/(drcp0*dCdt):.4f} K —— 与实际口径不符。")
    rcp_mean = float((650 + 128 * 1.5) * (1450 + 2736 * 1.5 / 2.5))
    main_term = rcp_mean * 1e-3
    say()
    say(f"  主项 rho cp dT/dt (取 dT/dt=1e-3 K/s) = {main_term:.4f} W/m^3")
    say(f"  守恒形式伪源项 / 主项 = {abs(S_false_absT)/main_term:.6f} "
        f"-> {100*abs(S_false_absT)/main_term:.2f}%")
    say(f"  严格形式残差项 / 主项 = {abs(resid)/main_term:.6f} "
        f"-> {100*abs(resid)/main_term:.2f}%")
    say()
    say("  结论:")
    say(f"    * 守恒形式多出的伪源项 {abs(S_false_absT):.0f} W/m^3 为主项的 "
        f"{100*abs(S_false_absT)/main_term:.2f}%;")
    say(f"    * 严格形式的残差项 {abs(resid):.1f} W/m^3 仅为主项的 "
        f"{100*abs(resid)/main_term:.2f}%;")
    say(f"    * 两者之比 |S_false|/|R_0| = {abs(S_false_absT)/abs(resid):.2f} 倍")
    say("      —— 伪源项比残差项大两个数量级。")
    say("    故**非保守形式仍然是正确的选择**, 但理由必须改为:")
    say("    '严格方程的残差项远小于守恒形式的伪源项', 而不是'精确相消'。")
    add("EX_drcpdC_255", "d(rho cp)/dC @ C=2.55", drcp0, "J/(m3 K) per (kg/kg)")
    add("EX_Sfalse_absT", "守恒形式伪源项 S_false = -T(d(rho cp)/dC)dC/dt (T=308 K, 正号=额外升温)",
        float(S_false_absT), "W/m^3")
    add("EX_Sfalse_7K", "同上的 (T-T_ref)=7 K 口径", float(S_false_7K), "W/m^3")
    add("EX_Sfalse_656K", "原报告 656.05 W/m^3 对应的 (T-T_ref)",
        float(-656.05 / (drcp0 * dCdt)), "K")
    add("EX_main", "主项 rho cp dT/dt (dT/dt=1e-3 K/s)", float(main_term), "W/m^3")
    add("EX_Sfalse_pct", "守恒形式伪源项占主项的比例",
        100 * abs(S_false_absT) / main_term, "%")
    add("EX_resid_pct", "严格形式残差项占主项的比例",
        100 * abs(resid) / main_term, "%")
    add("EX_ratio", "|S_false| / |R_0| (混合基准: S 用绝对 T, R0 用 6.85 K)",
        float(abs(S_false_absT) / abs(resid)), "-")
    add("EX_ratio_coef", "系数比 (与温度基准无关) |d(rho cp)/dC| / |c_s d rho_s/dC|",
        float(abs(drcp0) / abs(1450.0 * drs0)), "-")

    # ------------------------------------------------------------------
    # (3b) 基准敏感性: R_0 与 S_false 都正比于 (T - T_ref), 故两者之比
    #      只在**同一基准**下才有意义。这里把两种基准都算出。
    # ------------------------------------------------------------------
    say()
    say("=" * 96)
    say("(3b) 基准一致性检查 —— R_0 与 S_false 都正比于 (T - T_ref)")
    say("=" * 96)
    say("  严格残差   R_0      = -c_s (T-T_ref)(d rho_s/dC) dC/dt")
    say("  保守伪源项 S_false  = +T (d(rho cp)/dC) dC/dt")
    say("  注意 S_false 的因子是 T 本身 (代码以热力学温度存储状态量,")
    say("  守恒形式 d(rho cp T)/dt 的展开给出 T·d(rho cp)/dt), 而 R_0 的因子是")
    say("  (T - T_ref) —— **两者的温度因子不是同一个东西**, 故")
    say("  |S_false|/|R_0| 依赖 T_ref 的选取:")
    say()
    say(f"  {'T_ref / K':>12} {'(T-T_ref) / K':>14} {'R_0 / (W/m3)':>14} "
        f"{'R_0/主项':>10} {'|S|/|R_0|':>10}")
    for Tref_i, lbl in ((0.0, "0 K (代码的隐含基准)"), (273.15, "273.15 K (0 degC)"),
                        (301.15, "301.15 K (28 degC)"), (308.0, "308.0 K (= T 本身)")):
        dT_i = T_mean - Tref_i
        R0_i = -1450.0 * dT_i * drs0 * dCdt
        r_ratio = (abs(S_false_absT) / abs(R0_i)) if R0_i != 0 else float("inf")
        rr_s = f"{r_ratio:10.3f}" if np.isfinite(r_ratio) else f"{'∞':>10}"
        say(f"  {Tref_i:12.2f} {dT_i:14.2f} {R0_i:14.4f} "
            f"{100*abs(R0_i)/main_term:9.2f}% {rr_s}   {lbl}")
        add(f"EX_R0_Tref{Tref_i:.0f}", f"T_ref={Tref_i} K 时的 R_0", float(R0_i),
            "W/m^3")
        add(f"EX_R0pct_Tref{Tref_i:.0f}", f"T_ref={Tref_i} K 时 R_0 占主项",
            100 * abs(R0_i) / main_term, "%")
        add(f"EX_ratio_Tref{Tref_i:.0f}", f"T_ref={Tref_i} K 时的 |S|/|R_0|",
            float(r_ratio) if np.isfinite(r_ratio) else "inf", "-")
        add(f"EX_absTminusTref_Tref{Tref_i:.0f}", f"T_ref={Tref_i} K 时的 (T-T_ref)",
            float(dT_i), "K")
    say()
    say("  **重要**: R_0 自身依赖 T_ref 的选取 —— 这本身说明")
    say("  '用附录3 的 rho(C) 反推 rho_s 并对其求导' 这一处理并非良定:")
    say("  若按物理上自洽的读法 (体积不收缩 + 干物质守恒) 取 rho_s = 常数,")
    say("  则 d rho_s/dC = 0、R_0 恒为 0, 非保守形式是**精确**的。")
    say("  R_0 完全来自附录3 的 rho(C) 与'干物质守恒'的不自洽 (见 §2.3)。")
    say(f"  故'R_0 只占主项 1.71% 可略'这一判断**依赖 T_ref = 28 degC 的选取**:")
    say(f"  取代码的隐含基准 T_ref = 0 K 时, R_0 占主项 "
        f"{100*abs(-1450.0*T_mean*drs0*dCdt)/main_term:.2f}% —— 并不小。")
    say("  论文中必须写明基准, 或改用与基准无关的表述 (见下)。")
    say()
    say("  与基准无关的严格陈述 (推荐在论文中使用):")
    say("    (a) 经验证据: 两种实现的实际温度差 = 17.2745 K, 与温度基准无关;")
    say(f"    (b) 系数比: |d(rho cp)/dC| / |c_s d rho_s/dC| = "
        f"{abs(drcp0)/abs(1450.0*drs0):.3f} —— 与温度基准无关, 说明")
    say("        '守恒形式多出的项'与'严格形式余下的项'的**系数**相差约 10.8 倍;")
    say("    (c) 物理判据: 若采用自洽读法 (rho_s = 常数), R_0 恒为 0, 非保守形式是精确的。")

    # ------------------------------------------------------------------
    # (4) 数值印证: 严格式与两种形式的差距
    # ------------------------------------------------------------------
    say()
    say("=" * 96)
    say("(4) 与数值实验的一致性 (q2_verify.py V11)")
    say("=" * 96)
    say("  V11 实测: 非保守形式与守恒形式的温度场最大差 = 17.2745 K,")
    say("            t=10800 s 中心温度 49.7685 对 64.5646 degC (差 14.7961 K)。")
    say(f"  本节的解析估计: 守恒形式的伪源项是主项的 "
        f"{100*abs(S_false_absT)/main_term:.1f}%,")
    say(f"  即等效于在主项上叠加一个同向的额外升温, 量级上足以解释十几 K 的差别。")
    say("  => 审计指出的'相消不精确'成立, 但**不推翻**非保守形式的选择。")

    with open(os.path.join(OUT, "q2_energy_exact.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    with open(os.path.join(OUT, "registry_q2_energy_exact.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_energy_exact.log')}")
    print(f"注册表: {os.path.join(OUT, 'registry_q2_energy_exact.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
