# -*- coding: utf-8 -*-
"""
q4_derived.py -- 问题四的**派生量**注册表.

从 q4 各注册表 (生产/验证/灵敏度/相容性/图件) 读入实测值, 计算论文中引用的
比值、百分比与外推量, 逐条写明由哪两个注册表条目导出. 目的: 使论文问题四小节
里的每一个数字都在注册表里有据可查 (含派生关系), 供 q2_reconcile 对账.

输出: outputs/registry_q4_derived.csv
"""

from __future__ import annotations

import csv
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
LOG = []


def say(m):
    print(m, flush=True)
    LOG.append(m)


def load(name):
    path = os.path.join(OUT, name)
    d = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                d[row["key"]] = float(row["value"])
            except (KeyError, ValueError):
                pass
    return d


def main():
    prod = load("registry_q4.csv")
    ver = load("registry_q4_verify.csv")
    sens = load("registry_q4_sens.csv")
    fig = load("registry_q4_figures.csv")
    comp = load("registry_q4_compat.csv")

    rows = []

    def add(key, q, v, unit, n1, n2, note=""):
        rows.append((key, q, float(v), unit, f"{n1} / {n2}", note))

    # ---- 收缩效应分解 ----
    t_q3 = ver["V0_tdry_q3ref"]                  # 问题三: 附录3 无收缩
    t_a4ns = ver["V0b_app4_Rconst"]              # 附录4 无收缩
    t_a3s = ver["V0b_app3_shrink"]               # 附录3 有收缩
    t_prod = ver["PROD_tdry"]                    # 附录4 有收缩
    add("D_slow_by_app4", "附录4 物性使 t_dry 变慢的倍数", t_a4ns / t_q3, "1",
        "V0b_app4_Rconst", "V0_tdry_q3ref")
    add("D_speedup_by_shrink", "收缩使 t_dry 加快的倍数", t_a4ns / t_prod, "1",
        "V0b_app4_Rconst", "PROD_tdry")
    add("D_moist_reduction_pct", "收缩使 t_dry 缩短的百分比（附录4 口径）",
        100.0 * (1.0 - t_prod / t_a4ns), "%", "PROD_tdry", "V0b_app4_Rconst")
    add("D_net_vs_q3_pct", "问题四相对问题三 t_dry 的净变化率",
        100.0 * (t_prod - t_q3) / t_q3, "%", "PROD_tdry", "V0_tdry_q3ref")
    add("D_delta_vs_q3_h", "问题四相对问题三 t_dry 的差值",
        (t_prod - t_q3) / 3600.0, "h", "PROD_tdry", "V0_tdry_q3ref")
    add("D_noshink_delta_h", "冻结收缩相对生产解的 t_dry 增量",
        (t_a4ns - t_prod) / 3600.0, "h", "V0b_app4_Rconst", "PROD_tdry")
    add("D_a3shrink_ratio", "只加收缩（附录3 物性）时 t_dry 的缩小倍数",
        t_q3 / t_a3s, "1", "V0_tdry_q3ref", "V0b_app3_shrink")

    # ---- 网格与外推 ----
    t100, t200, t400 = ver["V1_M100"], ver["V1_M200"], ver["V1_M400"]
    add("D_order_p_pre", "由 M=100→200→400 估计的收敛阶 (前渐近)",
        ver["V1_p_100"], "1", "V1_p_100", "推导")
    add("D_order_p", "渐近收敛阶 p (由 M=800→1600→3200)",
        ver["V1_p_asym"], "1", "V1_p_asym", "推导")
    add("D_diff_ratio", "M=800→1600→3200 的相邻差之比",
        2.0 ** ver["V1_p_asym"], "1", "V1_p_asym", "推导")
    t_rich = ver["V1_rich_s"]
    add("D_richardson_s", "Richardson 外推 t_dry (渐近阶)", t_rich, "s",
        "V1_rich_s", "推导")
    add("D_richardson_h", "Richardson 外推 t_dry (渐近阶)", t_rich / 3600.0, "h",
        "V1_rich_s", "推导")
    for M in (100, 200, 400, 800, 1600, 3200):
        add(f"D_grid_err_M{M}", f"M={M} 相对外推极限的误差",
            ver[f"V1_err_M{M}"], "h", f"V1_err_M{M}", "推导")

    # ---- 独立 FV 求解到事件的对照 ----
    add("D_FV_p", "独立 FV 格式的实测收敛阶", ver["V5b_p_FV"], "1",
        "V5b_p_FV", "推导")
    add("D_FV_rich_h", "独立 FV 的一阶外推极限", ver["V5b_FV_rich"] / 3600.0, "h",
        "V5b_FV_rich", "推导")
    add("D_FV_vs_main_h", "FV 外推极限与主格式 M=3200 之差",
        ver["V5b_limit_diff"], "h", "V5b_limit_diff", "推导")
    for M in (100, 200, 400, 800):
        add(f"D_FV_diff_M{M}", f"FV 与主格式 t_dry 之差 (M={M})",
            ver[f"V5b_diff_M{M}"], "h", f"V5b_diff_M{M}", "推导")
    add("D_main_M3200_h", "主格式 M=3200 的 t_dry",
        ver["V1_M3200"] / 3600.0, "h", "V1_M3200", "推导")
    add("D_dT_domain_M400", "两格式在 M=400 的全域最大温度差 (生产口径)",
        ver["V5_dT_app4_400"], "K", "V5_dT_app4_400", "推导")
    add("D_dT_domain_M400_app3", "两格式在 M=400 的全域最大温度差 (附录3)",
        ver["V5_dT_app3_400"], "K", "V5_dT_app3_400", "推导")
    add("D_dTsurf_M400", "两格式在 M=400 的表面温度差 (生产口径)",
        ver["V5_dTsurf_app4_400"], "K", "V5_dTsurf_app4_400", "推导")

    # ---- 时间容限 ----
    tv = [ver["V2_rtol1e7"], ver["PROD_tdry"], ver["V2_rtol1e11"]]
    add("D_rtol_span_s", "三种 rtol 下 t_dry 的极差", max(tv) - min(tv), "s",
        "V2_rtol1e7", "V2_rtol1e11")
    add("D_rtol_span_h", "三种 rtol 下 t_dry 的极差",
        (max(tv) - min(tv)) / 3600.0, "h", "V2_rtol1e7", "V2_rtol1e11")

    # ---- 收缩数据口径 ----
    add("D_interp_s", "线性插值与 PCHIP 的 t_dry 差",
        ver["V4_V4_lin"] - t_prod, "s", "V4_V4_lin", "PROD_tdry")
    add("D_interp_h", "线性插值与 PCHIP 的 t_dry 差",
        (ver["V4_V4_lin"] - t_prod) / 3600.0, "h", "V4_V4_lin", "PROD_tdry")
    add("D_tau1800_s", "过渡段 1800 s 相对 600 s 的 t_dry 差",
        ver["V4_V4_tau1800"] - t_prod, "s", "V4_V4_tau1800", "PROD_tdry")

    # ---- 收缩数据统计 ----
    t, R = None, None
    import numpy as np
    tt = []
    Rc = []
    with open(os.path.join(OUT, "registry_q4_compat.csv"), encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["key"].startswith("compat_R_") and row["key"].endswith("h"):
                tt.append(float(row["key"].split("_")[-1][:-1]))
    R0, R6, Rend = comp.get("compat_R_0.5h"), None, None
    # 直接从附件重算, 避免依赖 key 命名
    from q4_solve import load_attachment2
    ta, Ra = load_attachment2()
    i6 = int(np.argmin(np.abs(ta - 6 * 3600)))
    add("D_shrink_frac_6h", "前 6 h 完成的收缩量占全程的比例",
        (Ra[0] - Ra[i6]) / (Ra[0] - Ra[-1]), "1", "附件2 R(0),R(6h),R(72h)", "推导")
    add("D_shrink_ratio", "末半径与初始半径之比", Ra[-1] / Ra[0], "1", "附件2", "推导")
    add("D_boost_end", "末段几何增强因子 (R0/R_END)^2",
        (Ra[0] / Ra[-1]) ** 2, "1", "附件2", "推导")
    add("D_R_at_tdry_cm", "t_dry 时刻的半径",
        float(np.interp(t_prod, ta, Ra)), "cm", "附件2", "PROD_tdry")

    # ---- 输出文件规格 ----
    n60 = int(math.floor(t_prod / 60.0))
    add("D_n60", "result4.xlsx 数据行数", n60, "1", "PROD_tdry", "推导")
    add("D_last_sec", "result4.xlsx 末行时间", 60.0 * n60, "s", "PROD_tdry", "推导")
    add("D_ncols_radius", "result4.xlsx 半径列数（0.0~2.0, 步长 0.1）",
        21, "1", "题面口径", "推导")

    # ---- 达标次序换算 ----
    for r in ("0.5", "1"):
        k = f"Q4_tcross_r{r}"
        if k in prod:
            add(f"D_tcross_r{r}_h", f"r={r} cm 首次达标时刻",
                prod[k] / 3600.0, "h", k, "推导")

    # ---- 收缩越出时刻 (物理半径 r 被收缩越过的时刻: R(t) = r) ----
    from scipy.optimize import brentq
    from q4_solve import Q4Radius
    rad = Q4Radius()
    for rcm in (1.5, 2.0):
        try:
            t_out = brentq(lambda x, _r=rcm: float(rad.R(x)) - _r * 1e-2,
                           0.0, 259200.0, xtol=1e-6)
            add(f"D_t_out_r{rcm}_h", f"r={rcm} cm 被收缩越过的时刻",
                t_out / 3600.0, "h", "附件2 R(t)", "推导")
            add(f"D_t_out_r{rcm}_s", f"r={rcm} cm 被收缩越过的时刻",
                t_out, "s", "附件2 R(t)", "推导")
        except ValueError:
            say(f"  [warn] r={rcm} cm 在 3 天内未被收缩越过")

    # ---- 图件派生 ----
    add("D_boost_end_fig", "图 3(b) 末段几何增强因子标注值",
        fig["FIG_boost_end"], "1", "FIG_boost_end", "推导")
    add("D_rtol_span_fig", "图 5(b) 时间容限极差标注值",
        fig["FIG_V2_span"], "s", "FIG_V2_span", "推导")

    # ---- 灵敏度派生 ----
    for k, lab, u in (("G1_hm_x0.5", "h_m 减半的 t_dry 增量", "h"),
                      ("G1_hm_x1000", "h_m 增至 1000 倍的 t_dry 变化", "h"),
                      ("G2_EA_-10%", "活化能 -10% 的 t_dry 变化", "h"),
                      ("G2_kD_+10%", "扩散指数 kD +10% 的 t_dry 变化", "h"),
                      ("G4_R_x1.1", "半径幅值 +10% 的 t_dry 变化", "h"),
                      ("G5_eta_p1", "收缩模式 eta=+1 的 t_dry", "h")):
        if k in sens:
            v = sens[k] - t_prod
            rows.append((f"D_{k.replace('%','pct').replace('.','p').replace('+','P').replace('-','M')}",
                         lab, v / 3600.0, u, f"{k} - PROD_tdry", "sensitivity"))
    for k, lab in (("MC5_mean", "蒙特卡洛 ±5% 均值"),
                   ("MC5_median", "蒙特卡洛 ±5% 中位数"),
                   ("MC5_std", "蒙特卡洛 ±5% 标准差"),
                   ("MC5_p2p5", "蒙特卡洛 ±5% 2.5% 分位"),
                   ("MC5_p97p5", "蒙特卡洛 ±5% 97.5% 分位"),
                   ("MC10_mean", "蒙特卡洛 ±10% 均值"),
                   ("MC10_median", "蒙特卡洛 ±10% 中位数"),
                   ("MC10_std", "蒙特卡洛 ±10% 标准差"),
                   ("MC10_p2p5", "蒙特卡洛 ±10% 2.5% 分位"),
                   ("MC10_p97p5", "蒙特卡洛 ±10% 97.5% 分位")):
        if k in sens:
            add(f"D_{k}", lab, sens[k] / 3600.0, "h", k, "推导")

    # ---- 相容性 ----
    add("D_compat_Cb_72h_rho1300", "rho_d=1300 时体积可加关系在 72 h 给出的 Cbar",
        comp["compat_Cb_rho1300_72h"], "kg/kg", "compat_Cb_rho1300_72h", "推导")
    add("D_compat_ratio_72h", "上述 Cbar 与阈值 0.15 之比",
        comp["compat_Cb_rho1300_72h"] / 0.15, "1", "compat_Cb_rho1300_72h", "C*")
    add("D_compat_kappa_ratio", "反解 kappa 的首末比值",
        comp["compat_kappa_ratio"], "1", "compat_kappa_ratio", "推导")
    add("D_compat_rC0_900", "rho_d=900 时隐含 C=0 的半径",
        comp["compat_rC0_k1.111"], "cm", "compat_rC0_k1.111", "推导")
    add("D_compat_rC0_1500", "rho_d=1500 时隐含 C=0 的半径",
        comp["compat_rC0_k0.667"], "cm", "compat_rC0_k0.667", "推导")

    with open(os.path.join(OUT, "registry_q4_derived.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "derived_from", "note"])
        for r in rows:
            w.writerow([r[0], r[1], repr(r[2]), r[3], r[4], r[5]])
    say(f"写出: outputs/registry_q4_derived.csv ({len(rows)} 行)")
    for r in rows[:60]:
        say(f"  {r[0]:34s} {r[2]:16.6f} {r[3]:8s} <- {r[4]}")


if __name__ == "__main__":
    main()
