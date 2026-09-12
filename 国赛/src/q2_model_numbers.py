# -*- coding: utf-8 -*-
"""
q2_model_numbers.py -- 复算 problem2.md / problem2_slove.md 中引用的全部模型数字.

产出 outputs/registry_q2_model.csv, 供 src/q2_reconcile.py 逐字对账.
每条 = 模型中一个可直接复算的量 (物性、特征数、潜热、热流、Jacobian 元等).

运行: python src/q2_model_numbers.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q2_solve import (props, Dfun, D_derivs, hevap_of, Par, geometry,   # noqa: E402
                      HEVAP_28, HEVAP_SLOPE, HEVAP_TREF, H_CONV, HM, R, T0K, C0)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
CMD = "python src/q2_model_numbers.py"

REG = []


def add(id_, q, v, u="", unc="", src=CMD, note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])


def main():
    # ---------------------------------------------------------------
    # A. 附录3 物性表 (problem2.md §5)
    # ---------------------------------------------------------------
    for C in (2.55, 2.00, 1.00, 0.50, 0.15):
        rho, cp, k, drho, dcp, dk = props(C, "app3")
        add(f"A_rho_{C}", f"附录3 rho(C={C})", float(rho), "kg/m^3")
        add(f"A_cp_{C}", f"附录3 cp(C={C})", float(cp), "J/(kg K)")
        add(f"A_k_{C}", f"附录3 k(C={C})", float(k), "W/(m K)")
        add(f"A_alpha_{C}", f"附录3 alpha(C={C})", float(k / (rho * cp)), "m^2/s")
        add(f"A_rcp_{C}", f"附录3 rho*cp(C={C})", float(rho * cp), "J/(m^3 K)")
    rcp0 = float(props(2.55, "app3")[0] * props(2.55, "app3")[1])
    rcp1 = float(props(0.15, "app3")[0] * props(0.15, "app3")[1])
    add("A_rcp_drop", "rho cp 由 C=2.55 到 0.15 的降幅",
        100 * (rcp0 - rcp1) / rcp0, "%")

    # 导数
    for C in (2.55, 1.00, 0.50, 0.15):
        _, cp, _, drho, dcp, dk = props(C, "app3")
        add(f"A_dcp_{C}", f"dcp/dC(C={C})", float(dcp), "J/(kg K)/(kg/kg)")
        add(f"A_dk_{C}", f"dk/dC(C={C})", float(dk), "W/(m K)/(kg/kg)")
    for C in (2.55, 1.00):
        rho, cp, k, drho, dcp, dk = props(C, "app3")
        add(f"A_drcp_{C}", f"d(rho cp)/dC(C={C})",
            float(drho * cp + rho * dcp), "J/(m^3 K)/(kg/kg)")

    # ---------------------------------------------------------------
    # B. D(C,T) (problem2.md §5)
    # ---------------------------------------------------------------
    for C, Tc in ((2.55, 28), (2.55, 50), (1.00, 50), (0.15, 50), (0.05, 50),
                  (2.55, 30), (1.00, 30)):
        add(f"B_D_{C}_{Tc}", f"D(C={C}, T={Tc} degC)",
            float(Dfun(C, Tc + 273.15)), "m^2/s")
        dC_, dT_ = D_derivs(C, Tc + 273.15)
        add(f"B_dDdC_{C}_{Tc}", f"dD/dC(C={C}, T={Tc})", float(dC_), "m^2/s per (kg/kg)")
        add(f"B_dDdT_{C}_{Tc}", f"dD/dT(C={C}, T={Tc})", float(dT_), "m^2/(s K)")
    add("B_dlnD_dT", "d ln D / dT @ (2.55, 28 degC)", 3850.0 / T0K ** 2, "1/K")
    add("B_D_ratio_28_50", "D(C0,50C) / D(C0,28C)",
        float(Dfun(2.55, 323.15) / Dfun(2.55, 301.15)), "-")
    add("B_D_ratio_50_60", "D 在 T 由 50 到 60 degC 的倍率",
        float(np.exp(-3850.0 / 333.15) / np.exp(-3850.0 / 323.15)), "-")

    # ---------------------------------------------------------------
    # C. 特征数 (problem2.md §7.1)
    # ---------------------------------------------------------------
    rho0, cp0, k0, *_ = props(C0, "app3")
    a0 = float(k0 / (rho0 * cp0))
    D0 = float(Dfun(C0, T0K))
    add("C_Bi", "热 Biot 数 hR/k(C0)", H_CONV * R / float(k0), "-")
    add("C_Bim", "传质 Biot 数 h_m R/D(C0,T0)", HM * R / D0, "-")
    add("C_tauT", "导热特征时间 R^2/alpha(C0)", R * R / a0, "s")
    add("C_tauC", "湿分特征时间 R^2/D(C0,T0)", R * R / D0, "s")
    add("C_ratio", "D/alpha (时间尺度比)", D0 / a0, "-")
    add("C_ratio_inv", "alpha/D", a0 / D0, "-")
    add("C_endface", "单端面/侧面 面积比 R/(2L)", R / (2 * 0.25), "-")
    add("C_endface2", "双端面/侧面 面积比 R/L", R / 0.25, "-")

    # ---------------------------------------------------------------
    # D. 潜热 (problem2.md §4.4c) —— 由定标式复算
    # ---------------------------------------------------------------
    for Tc in (20, 28, 40, 50):
        hv, dh = hevap_of(Tc + 273.15, Par())
        add(f"D_Hevap_{Tc}", f"H_evap({Tc} degC)", float(hv), "J/kg")
    add("D_Hevap_int", "定标式截距 H_evap(28 degC)", HEVAP_28, "J/kg")
    add("D_Hevap_slope", "定标式斜率 dH_evap/dT", HEVAP_SLOPE, "J/(kg K)")
    add("D_Hevap_0C", "定标式外推 H_evap(0 degC)",
        HEVAP_28 - HEVAP_SLOPE * 28.0, "J/kg")
    # 由 28 degC 截距+斜率写成的摄氏展开式
    add("D_Hevap_a_C", "摄氏展开式截距 (2.5015e6 的复算)",
        HEVAP_28 - HEVAP_SLOPE * 28.0, "J/kg")
    add("D_qevap_coef", "q_evap 系数 H_evap(40 degC) h_m",
        float(hevap_of(313.15, Par())[0]) * HM, "J/(m^2 s) per (kg/kg)")
    add("D_qevap_coef28", "q_evap 系数 H_evap(28 degC) h_m",
        HEVAP_28 * HM, "J/(m^2 s) per (kg/kg)")
    add("D_deTR_ana", "解析表面温降 q_evap/h @ C_R=2.5, C_inf=0.0427",
        float(hevap_of(313.15, Par())[0]) * HM * (2.5 - 0.0427) / H_CONV, "K")
    add("D_Jac_evap", "Jacobian 元 H_evap h_m R @40 degC",
        float(hevap_of(313.15, Par())[0]) * HM * R, "J/(m^2 s K)*(m^2 K/J)... ")
    add("D_Jac_evap28", "Jacobian 元 H_evap(28) h_m R", HEVAP_28 * HM * R, "-")
    add("D_Jac_ratio", "Jacobian 元占对角元 1/dt (dt=0.25 s) 的比例",
        100 * HEVAP_28 * HM * R / (1.0 / 0.25), "%")
    add("D_Jac_ratio32", "Jacobian 元占对角元 1/dt (dt=1/32 s) 的比例",
        100 * HEVAP_28 * HM * R * 32.0, "%")
    # 严格的耦合权重: (1,2) 元应与其所在行 (温度方程) 的对角元相比。
    # 温度方程在 r=R 的对角元 = M^L_MM rho cp / dt + h R。
    # M^L_MM 的几何部分 (已约 2 pi 与 rho cp) = dr (r_{M-1} + 2 r_M)/6 ≈ R^2/(2M)。
    for M, dt in ((800, 1.0 / 16), (1600, 1.0 / 32), (400, 0.25)):
        g = geometry(M, "lumped")
        mtM = float(g["MLg"][M]) * float(rho0) * float(cp0)      # per 2 pi
        diag = mtM / dt + H_CONV * R
        frac = 100 * (HEVAP_28 * HM * R) / diag
        add(f"D_MTM_{M}", f"M={M}: 表面节点热容 M^L_MM rho cp (per 2 pi)", mtM,
            "J/(m K)")
        add(f"D_JTdiag_M{M}_dt{dt:.6g}", f"M={M}, dt={dt:.6g}: 温度方程表面对角元",
            diag, "-")
        add(f"D_fusion_M{M}_dt{dt:.6g}",
            f"M={M}, dt={dt:.6g}: 蒸发(1,2)元占温度方程对角元的比例", frac, "%")
    add("D_dDdC_smallC", "dD/dC @ (C=0.05, T=323.15 K)",
        float(D_derivs(0.05, 323.15)[0]), "m^2/s per (kg/kg)")
    add("D_dDdC_rel", "d ln D / dC 的相对灵敏系数 0.45/C^2 @ C=0.05",
        0.45 / 0.05 ** 2, "-")
    add("D_Hevap_a40", "定标式在 40 degC 的取值 (H_evap(40))",
        float(hevap_of(313.15, Par())[0]), "J/kg")
    # 热流对比表 (§4.4c(vi))
    for tt, Cin, Tin_con, TR in ((0, 0.0196, 28.0, 28.0),
                                 (1800, 0.0331, 41.5, 28.0),
                                 (3600, 0.0427, 47.5, 28.0)):
        add(f"D_qev_{tt}", f"t={tt} s: H_evap(40C) h_m (2.5-C_inf)",
            float(hevap_of(313.15, Par())[0]) * HM * (2.5 - Cin), "J/(m^2 s)")
        add(f"D_qconv_{tt}", f"t={tt} s: h (T_inf - T_R)",
            H_CONV * (Tin_con - TR), "J/(m^2 s)")
        add(f"D_qratio_{tt}", f"t={tt} s: q_evap/q_conv",
            float(hevap_of(313.15, Par())[0]) * HM * (2.5 - Cin)
            / max(H_CONV * (Tin_con - TR), 1e-30), "-")
    add("D_dTR_over_dT", "蒸发温降占总温升 28->50 degC 的比例",
        100 * 0.19 / 22.0, "%")

    # ---------------------------------------------------------------
    # E. 网格与单元几何 (problem2.md §9)
    # ---------------------------------------------------------------
    for M in (100, 200, 400, 800, 1600):
        g = geometry(M, "lumped")
        add(f"E_dr_{M}", f"M={M}: dr", float(g["dr"]) * 1000, "mm")
        add(f"E_ML00_{M}", f"M={M}: M^L_00/(rho cp)", float(g["MLg"][0]), "m^2")
        add(f"E_MLM_{M}", f"M={M}: M^L_MM/(rho cp)", float(g["MLg"][M]), "m^2")
        add(f"E_ML0r_{M}", f"M={M}: dr^2/6", float(g["dr"] ** 2 / 6), "m^2")
        add(f"E_MLMr_{M}", f"M={M}: dr^2(3M-1)/6",
            float(g["dr"] ** 2 * (3 * M - 1) / 6), "m^2")
        add(f"E_ML0h_{M}", f"M={M}: 半控制体 dr^2/8 (问题一口径)",
            float(g["dr"] ** 2 / 8), "m^2")
    # 一致质量矩阵的退化检验: 中置单元应回到 h/3, h/6
    h = 1.0
    a, b = h / 2 - h / 2, h / 2 + h / 2
    Me = np.array([[3 * a + b, a + b], [a + b, a + 3 * b]]) * h / 12
    add("E_Mcons_11", "一致质量矩阵中置单元 M11/h", float(Me[0, 0]), "-")
    add("E_Mcons_12", "一致质量矩阵中置单元 M12/h", float(Me[0, 1]), "-")

    # ---------------------------------------------------------------
    # F. Newton 收敛判据与迭代 (problem2.md §11.4)
    # ---------------------------------------------------------------
    p = Par()
    add("F_rtol", "Newton 相对残差判据", p.rtol_R, "-")
    add("F_kmax", "Newton 最大迭代数", p.max_newton, "-")

    # ---------------------------------------------------------------
    # G. 输出约定 (problem2.md §13)
    # ---------------------------------------------------------------
    add("G_nT", "result2 时间行数", 10800, "-")
    add("G_nR", "result2 半径列数", 21, "-")
    add("G_ntab", "表3/表4 行数", 6, "-")
    add("G_ntabr", "表3/表4 列数", 5, "-")
    add("G_halfL", "药材半长 L/2", 12.5, "cm")
    add("G_nnode100", "M=100 时的节点数 M+1", 101, "-")
    add("G_Cfront", "干燥前沿判别值 0.9*C0", 0.9 * C0, "kg/kg")
    add("G_3h_over_tauC", "3 h 与湿分特征时间之比",
        10800.0 / 70900.86172065, "-")

    # ---------------------------------------------------------------
    # H. 附件2: 半径随时间的变化 (B7 收缩假设的依据)
    # ---------------------------------------------------------------
    for tt, Rc in ((0, 2.000), (1800, 1.873), (3600, 1.794), (5400, 1.703),
                   (7200, 1.625), (10800, 1.552), (14400, 1.477),
                   (259200, 1.198)):
        add(f"H_R_{tt}", f"附件2: t={tt} s 的半径", Rc, "cm", "附件2")
        add(f"H_shrink_{tt}", f"附件2: t={tt} s 相对初始半径的收缩",
            100 * (1 - Rc / 2.000), "%", "附件2")

    with open(os.path.join(OUT, "registry_q2_model.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"registry_q2_model.csv: {len(REG)} 行")
    for r in REG:
        print(f"  {r[0]:24s} {r[2]:>22s}  {r[1]}")


if __name__ == "__main__":
    main()
