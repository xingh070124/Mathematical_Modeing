# -*- coding: utf-8 -*-
"""
q2_latent_heat.py -- 问题二 §4.4(c) 水汽化潜热 H_evap(T) 的热力学推导与数值定标

推导链条（写入 model/problem2.md §4.4(c)）:
  (1) 相平衡条件  mu_l(T,p) = mu_v(T,p)  ->  Clapeyron 方程
      dp_sat/dT = L / (T * (v_g - v_f))                        [精确]
  (2) Clausius-Clapeyron 近似（理想气体 v_g = R_v T / p，v_f << v_g）
      L = R_v * T^2 * d(ln p_sat)/dT
  (3) Kirchhoff 定律 dL/dT = c_p,v - c_p,l  ->  L 关于 T 的线性化
  (4) 数值定标：用 IAPWS-95 参考值拟合线性式的截距与斜率
  (5) 一致性验证：由 (3) 线性式积分反演 p_sat(T)，与 IAPWS-95 对比

参考数据源: IAPWS-95（纯 Python 实现），水三相点 273.16 K，饱和线 T ∈ [273.15, 373.15] K。

依赖:  pip install iapws      # 1.5.5，纯 Python，无编译依赖

输出:
  outputs/registry_q2_latent_heat.csv   数值注册表（论文对账用）
  控制台：推导所需全部中间量表
"""

import os
import csv

import numpy as np
from iapws import IAPWS95

# ----------------------------------------------------------------------------
# 0. 常量
# ----------------------------------------------------------------------------
T_TRIPLE = 273.16          # K  水三相点
T_REF_C = 0.0              # °C 线性式锚点（三相点附近）
DT_DERIV = 5.0e-3          # K  饱和线数值微分步长

OUT_CSV = os.path.join(os.path.dirname(__file__), "..", "outputs",
                       "registry_q2_latent_heat.csv")


def sat(T):
    """饱和线上物性（IAPWS-95）。返回 dict，焓单位 J/kg，比容 m^3/kg。"""
    liq = IAPWS95(T=T, x=0)
    vap = IAPWS95(T=T, x=1)
    return dict(
        T=T,
        psat=vap.P * 1.0e6,               # MPa -> Pa
        vf=1.0 / liq.rho,                 # m^3/kg
        Z=vap.Z,                          # 压缩因子 p v_g /(R_v T)
        vg=1.0 / vap.rho,                 # m^3/kg
        hf=liq.h * 1000.0,                # J/kg
        hg=vap.h * 1000.0,                # J/kg
        hfg=(vap.h - liq.h) * 1000.0,     # J/kg  参考潜热
        cp_l=liq.cp * 1000.0,             # J/(kg.K)
        cp_v=vap.cp * 1000.0,             # J/(kg.K) 真实气体
        cp_v0=vap.cp0 * 1000.0,           # J/(kg.K) 理想气体
        Rv=vap.R * 1000.0,                # J/(kg.K)
    )


def dpsat_dT(T):
    """饱和蒸气压对温度的中心差分导数 (Pa/K)。"""
    return (sat(T + DT_DERIV)["psat"] - sat(T - DT_DERIV)["psat"]) / (2 * DT_DERIV)


def main():
    Rv = sat(300.0)["Rv"]
    Mw = 8.314462618 / Rv
    print("=" * 78)
    print("[0] 常量")
    print(f"  R_v = R_u / M_w = 8.314462618 / {Mw:.8f} = {Rv:.4f} J/(kg.K)")
    print(f"  T_ref = {T_TRIPLE} K (三相点), 工作区间 28~50 degC = 301.15~323.15 K")
    print("=" * 78)

    # ------------------------------------------------------------------
    # 1. 三条推导路线在 20~50 degC 上的对比
    # ------------------------------------------------------------------
    Tcs = np.arange(20.0, 50.0 + 1e-9, 5.0)
    rows = []
    print("\n[1] 三条热力学路线的对比（20~50 degC）")
    print(f"{'T(C)':>6} {'p_sat(kPa)':>11} {'dp/dT(Pa/K)':>12} "
          f"{'v_g(m3/kg)':>11} {'L_ref(J/kg)':>13} {'L_Clap':>13} "
          f"{'L_CC':>13} {'err_CC(%)':>10}")
    for Tc in Tcs:
        T = Tc + 273.15
        s = sat(T)
        dpdT = dpsat_dT(T)
        # Route 1: 精确 Clapeyron
        L1 = T * (s["vg"] - s["vf"]) * dpdT
        # Route 2: Clausius-Clapeyron（理想气体 + 忽略 v_f）
        L2 = Rv * T ** 2 * dpdT / s["psat"]
        err = (L2 - s["hfg"]) / s["hfg"] * 100.0
        print(f"{Tc:6.1f} {s['psat']/1e3:11.5f} {dpdT:12.4f} "
              f"{s['vg']:11.4f} {s['hfg']:13.1f} {L1:13.1f} {L2:13.1f} {err:10.4f}")
        rows.append(dict(Tc=Tc, T=T, psat=s["psat"], dpdT=dpdT, vf=s["vf"], vg=s["vg"],
                         hfg=s["hfg"], L_clapeyron=L1, L_cc=L2, err_cc_pct=err,
                         cp_l=s["cp_l"], cp_v=s["cp_v"], cp_v0=s["cp_v0"]))
    vf_over_vg = rows[0]["vf"] / rows[0]["vg"]
    print(f"\n  近似 1（v_f << v_g）: v_f/v_g = {vf_over_vg:.3e} @20degC  -> 忽略 v_f 误差 ~1e-5")
    print(f"  近似 2（理想气体）  : L_CC 相对 L_ref 偏差 "
          f"{min(r['err_cc_pct'] for r in rows):.4f}% ~ {max(r['err_cc_pct'] for r in rows):.4f}%")
    print("\n  CC 近似误差的精确解释: L_CC / L_true = 1/Z  (Z = p*v_g/(R_v*T) 为压缩因子)")
    print(f"  {'T(C)':>6} {'Z':>10} {'1/Z-1 (%)':>12} {'err_CC 实测 (%)':>17} {'差':>10}")
    for Tc in Tcs:
        T = Tc + 273.15
        s = sat(T)
        one_over_Z = 1.0 / s["Z"] - 1.0
        err_cc = (Rv * T ** 2 * dpsat_dT(T) / s["psat"] - s["hfg"]) / s["hfg"]
        print(f"  {Tc:6.1f} {s['Z']:10.6f} {100*one_over_Z:12.4f} "
              f"{100*err_cc:17.4f} {100*(err_cc-one_over_Z):10.4f}")

    # ------------------------------------------------------------------
    # 2. Kirchhoff 定律: dL/dT = c_p,v - c_p,l
    # ------------------------------------------------------------------
    print("\n[2] Kirchhoff 定律斜率 dL/dT = c_p,v - c_p,l")
    print(f"{'T(C)':>6} {'c_p,l':>10} {'c_p,v(ideal)':>13} {'c_p,v(real)':>12} "
          f"{'dcp_ideal':>10} {'dcp_real':>10} {'dL/dT数值':>11}")
    kirch = []
    for r in rows:
        dcp_i = r["cp_v0"] - r["cp_l"]
        dcp_r = r["cp_v"] - r["cp_l"]
        kirch.append(dcp_i)
        # 数值斜率
        h1 = sat(r["T"] - 1.0)["hfg"]
        h2 = sat(r["T"] + 1.0)["hfg"]
        print(f"{r['Tc']:6.1f} {r['cp_l']:10.1f} {r['cp_v0']:13.1f} {r['cp_v']:12.1f} "
              f"{dcp_i:10.1f} {dcp_r:10.1f} {(h2-h1)/2.0:11.1f}")
        r["dcp_ideal"] = dcp_i
        r["dcp_real"] = dcp_r
        r["dLdT_num"] = (h2 - h1) / 2.0
    dcp_ideal_mean = float(np.mean(kirch))
    dcp_num_mean = float(np.mean([r["dLdT_num"] for r in rows]))
    print(f"\n  <c_p,v^0 - c_p,l>      = {dcp_ideal_mean:9.1f} J/(kg.K)   （理想气体，一阶主项）")
    print(f"  <dL/dT> 数值（IAPWS）  = {dcp_num_mean:9.1f} J/(kg.K)")
    print(f"  残差（真实气体修正项） = {dcp_num_mean - dcp_ideal_mean:9.1f} J/(kg.K)"
          f"  占 {100*(dcp_num_mean-dcp_ideal_mean)/dcp_num_mean:.1f}%")

    # ------------------------------------------------------------------
    # 3. 线性化定标: H_evap(T_C) = a + b * T_C   （工作区间 28~50 degC）
    # ------------------------------------------------------------------
    print("\n[3] 线性定标 H_evap(T_C) = a + b*T_C")
    for label, Tc_lo, Tc_hi in [("工作区间 28~50 degC", 28.0, 50.0),
                                ("全程 0~50 degC", 0.5, 50.0),
                                ("全程 0~100 degC", 0.5, 100.0)]:
        Tc_fit = np.arange(Tc_lo, Tc_hi + 1e-9, 0.5)
        L_fit = np.array([sat(tc + 273.15)["hfg"] for tc in Tc_fit])
        b, a = np.polyfit(Tc_fit, L_fit, 1)
        resid = L_fit - (a + b * Tc_fit)
        print(f"  {label:>18}: a = {a:.1f} J/kg, b = {b:.3f} J/(kg.K), "
              f"max|resid| = {np.max(np.abs(resid)):.1f} J/kg "
              f"({100*np.max(np.abs(resid))/np.mean(L_fit):.4f}%)")
        if label.startswith("工作区间"):
            a_work, b_work = a, b

    # 28 degC 锚点式（物料初温为物理锚点）
    L28 = sat(28.0 + 273.15)["hfg"]
    Tc_fit = np.arange(20.0, 50.0 + 1e-9, 0.5)
    L_fit = np.array([sat(tc + 273.15)["hfg"] for tc in Tc_fit])
    b28 = float(np.polyfit(Tc_fit - 28.0, L_fit, 1)[0])
    print(f"\n  28 degC 锚点式: H_evap(28) = {L28:.1f} J/kg, "
          f"斜率 = {b28:.1f} J/(kg.K)")
    print(f"  -> H_evap(T) = {L28/1e6:.4f}e6 {b28/1e3:+.3f}e3 * (T - 28 degC)   (J/kg)")
    print(f"  -> H_evap(T) = {(L28 - b28*28)/1e6:.4f}e6 {b28/1e3:+.3f}e3 * T_degC"
          f"   (J/kg)")
    err28 = np.array([sat(tc + 273.15)["hfg"] for tc in Tc_fit]) - (L28 + b28 * (Tc_fit - 28.0))
    print(f"     28 degC 锚点式在 20~50 degC 上 max|resid| = "
          f"{np.max(np.abs(err28)):.1f} J/kg ({100*np.max(np.abs(err28))/L28:.4f}%)")

    # 全局（锚点固定在三相点）形式
    L0 = sat(T_TRIPLE + 0.02)["hfg"]   # 三相点潜热（273.16 K 恰在 IAPWS-95 边界上，退 0.02 K）
    print(f"\n  三相点潜热 L(T_t) = {L0:.1f} J/kg")
    b_anchor = np.polyfit([r["Tc"] for r in rows], [r["hfg"] for r in rows], 1)[0]
    print(f"\n  锚点式（三相点定标）: L(0 degC) = {L0:.1f} J/kg, "
          f"斜率 = {b_anchor:.1f} J/(kg.K)")
    print(f"  -> H_evap(T) = {L0/1e6:.4f}e6 - {abs(b_anchor)/1e3:.3f}e3 * T_degC   (J/kg)")

    # 与 problem2.md 现用线性式对比
    a_doc, b_doc = 2.501e6, -2.369e3
    print("\n  problem2.md 现用式对比:")
    print(f"  {'T(C)':>6} {'IAPWS 参考':>13} {'锚点式':>13} {'现用式':>13} "
          f"{'锚点误差%':>11} {'现用误差%':>11}")
    for r in rows:
        L_anchor = L0 + b_anchor * r["Tc"]
        L_doc = a_doc + b_doc * r["Tc"]
        print(f"  {r['Tc']:6.1f} {r['hfg']:13.1f} {L_anchor:13.1f} {L_doc:13.1f} "
              f"{100*(L_anchor-r['hfg'])/r['hfg']:11.4f} {100*(L_doc-r['hfg'])/r['hfg']:11.4f}")

    # ------------------------------------------------------------------
    # 4. 一致性验证: Kirchhoff 积分反演 p_sat(T)
    # ------------------------------------------------------------------
    print("\n[4] 一致性验证 —— 由 Kirchhoff 线性式积分反演 p_sat(T)")
    print("    Clausius-Clapeyron: d(ln p_sat)/dT = L(T)/(R_v T^2),  L(T)=L0+b*T_C")
    # 从三相点出发积分到 100 degC
    Ts = np.linspace(T_TRIPLE, 373.15, 20001)
    Ls = L0 + b_anchor * (Ts - 273.15)
    integrand = Ls / (Rv * Ts ** 2)
    lnp = np.concatenate(([0.0], np.cumsum(
        0.5 * (integrand[1:] + integrand[:-1]) * np.diff(Ts))))
    p0 = sat(T_TRIPLE)["psat"]
    p_model = p0 * np.exp(lnp)
    print(f"  {'T(C)':>6} {'p_sat IAPWS(kPa)':>18} {'p_sat 反演(kPa)':>17} {'相对偏差%':>11}")
    for Tc in [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0]:
        T = Tc + 273.15
        p_exact = sat(T)["psat"]
        p_m = float(np.interp(T, Ts, p_model))
        print(f"  {Tc:6.1f} {p_exact/1e3:18.5f} {p_m/1e3:17.5f} "
              f"{100*(p_m-p_exact)/p_exact:11.4f}")
    print("  注: 偏差为负且随 T 增大 —— 即 CC 近似中令 Z=1（理想气体）导致的系统性")
    print("      偏差；其在 [1] 中已定量确认为 1/Z-1，方向与量级完全一致。")

    # ------------------------------------------------------------------
    # 5. 输出注册表
    # ------------------------------------------------------------------
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["T_C", "T_K", "p_sat_Pa", "dp_sat_dT_Pa_per_K", "v_f_m3_per_kg",
                    "v_g_m3_per_kg", "h_fg_ref_J_per_kg", "L_clapeyron_J_per_kg",
                    "L_CC_J_per_kg", "err_CC_pct", "cp_liquid_J_per_kgK",
                    "cp_vapor_ideal_J_per_kgK", "cp_vapor_real_J_per_kgK",
                    "dL_dT_numeric_J_per_kgK"])
        for r in rows:
            w.writerow([f"{r['Tc']:.2f}", f"{r['T']:.2f}", f"{r['psat']:.6f}",
                        f"{r['dpdT']:.6f}", f"{r['vf']:.10e}", f"{r['vg']:.10e}",
                        f"{r['hfg']:.4f}", f"{r['L_clapeyron']:.4f}",
                        f"{r['L_cc']:.4f}", f"{r['err_cc_pct']:.6f}",
                        f"{r['cp_l']:.4f}", f"{r['cp_v0']:.4f}", f"{r['cp_v']:.4f}",
                        f"{r['dLdT_num']:.4f}"])
    print(f"\n[5] 注册表已写出: {os.path.normpath(OUT_CSV)}")

    # ------------------------------------------------------------------
    # 6. 供 problem2.md 引用的定标常数
    # ------------------------------------------------------------------
    h_m = 8.0e-7
    R = 0.02
    h = 25.0
    print("\n" + "=" * 78)
    print("[6] problem2.md §4.4(c) / §11.2 / §14 引用常数")
    print(f"  定标式: H_evap(T) = {L28/1e6:.4f}e6 {b_work/1e3:+.3f}e3*(T-28degC) J/kg")
    print(f"  等价:   H_evap   = {(L28 - b_work*28)/1e6:.4f}e6 {b_work/1e3:+.3f}e3*T_degC J/kg")
    print(f"    {'T(degC)':>8} {'定标式':>12} {'IAPWS-95':>12} {'误差%':>9}")
    for tc in [20.0, 28.0, 40.0, 50.0]:
        lv = L28 + b_work * (tc - 28.0)
        lr = sat(tc + 273.15)["hfg"]
        print(f"    {tc:8.1f} {lv:12.1f} {lr:12.1f} {100*(lv-lr)/lr:+9.4f}")
    L40 = L28 + b_work * (40 - 28)
    print(f"\n  q_evap 系数 L*h_m (@40degC) = {L40*h_m:.4f} J/(m2.s) per (C_R-C_inf)")
    print(f"  Jacobian 元 H_evap*h_m*R    = {L40*h_m*R:.6f}  (对角元 1/dt = 4 s^-1 的 "
          f"{100*L40*h_m*R/4:.2f}%)")
    print(f"  表面温降 dT_R = q_evap/h      @C_R=2.5, C_inf=0.0427: "
          f"{L40*h_m*(2.5-0.0427):.4f} J/(m2.s) -> {L40*h_m*(2.5-0.0427)/h:.4f} K")
    print("=" * 78)


if __name__ == "__main__":
    np.seterr(all="ignore")
    main()
