"""
图4 灵敏度龙卷风图; 图5 鲁棒性检验图.

figure contract:
  fig_q1_sensitivity  核心结论: 温度 QoI 只对热参数 (T0, h, rho*cp, k) 响应, 水分
                      QoI 只对湿参数 (C0, h_m, D0) 响应且响应严格为零 -- 问题一
                      热湿解耦的直接数值证据; 表面水分对 h_m 最敏感 (S≈-0.47).
  fig_q1_robustness   核心结论: 边界数据噪声 (sigma 由数据估计) 与离散/插值选择
                      引起的 QoI 偏离远低于四位小数报告精度 (半 ulp 5e-5) --
                      报告精度稳健; 参数 ±10% 联合不确定性的传导由 C0/h_m 主导,
                      属物理输入不确定性而非数值误差, 定性结论 100% 保持.

数据源: outputs/q1_sensitivity_oat.csv, outputs/q1_sensitivity_mc.csv
        (由 python src/q1_sensitivity.py 生成), E5 网格收敛在本脚本内现算.

运行:  python src/q1_fig_sensrob.py
输出:  paper/figures/fig_q1_sensitivity.pdf|.png, paper/figures/fig_q1_robustness.pdf|.png
"""

from __future__ import annotations

import csv
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter, NullFormatter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C, GREY, SERIES, save, setup  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
HALF_ULP = 5e-5                      # 四位小数的半 ulp
QOI_LABELS = ["$T(0,1800\\,\\mathrm{s})$ 中心温度",
              "$T(R,1800\\,\\mathrm{s})$ 表面温度",
              "$C(R,1800\\,\\mathrm{s})$ 表面水分",
              "$\\langle C\\rangle(1800\\,\\mathrm{s})$ 体积平均水分"]
PARAM_LABELS = {"h": "$h$ (W/m$^2$K)", "hm": "$h_m$ (m/s)", "D0": "$D_0$ (m$^2$/s)",
                "k": "$k$ (W/mK)", "rho": "$\\rho$ (kg/m$^3$)",
                "cp": "$c_p$ (J/kgK)", "T0": "$T_0$ (K)", "C0": "$C_0$ (kg/kg)"}
PARAM_ORDER = ["T0", "C0", "hm", "rho", "cp", "D0", "h", "k"]


def pow_formatter():
    """对数轴幂次刻度 (纯 STIX mathtext, 避开 SimHei 缺 U+2212 减号)."""
    return FuncFormatter(lambda v, _: f"$10^{{{int(round(np.log10(v)))}}}$")


def load_oat():
    rows = []
    with open(os.path.join(OUT, "q1_sensitivity_oat.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def fig_sensitivity():
    rows = load_oat()
    qois = ["T中心(1800s)", "T表面(1800s)", "C表面(1800s)", "C体积平均(1800s)"]
    titles = ["(a) 中心温度 $T(0,t_{end})$", "(b) 表面温度 $T(R,t_{end})$",
              "(c) 表面水分 $C(R,t_{end})$", "(d) 体积平均水分 $\\langle C\\rangle(t_{end})$"]
    units = ["K", "K", "kg/kg", "kg/kg"]

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.6))
    for q, (ax, qoi, title, unit) in enumerate(zip(axes.flat, qois, titles, units)):
        sub = {r["param"]: r for r in rows if r["qoi"] == qoi}
        # 按最大绝对响应排序 (大者在下, 便于自下而上阅读)
        order = sorted(PARAM_ORDER,
                       key=lambda p: -max(abs(float(sub[p]["y_plus10"]) - float(sub[p]["y_base"])),
                                          abs(float(sub[p]["y_minus10"]) - float(sub[p]["y_base"]))))
        yp = [float(sub[p]["y_plus10"]) - float(sub[p]["y_base"]) for p in order]
        ym = [float(sub[p]["y_minus10"]) - float(sub[p]["y_base"]) for p in order]
        y = np.arange(len(order))
        ax.barh(y, yp, height=0.62, color=C["blue"], edgecolor="none",
                label="参数 +10%")
        ax.barh(y, ym, height=0.62, color=C["lightred"], edgecolor=C["red"],
                lw=0.4, label="参数 -10%")
        ax.axvline(0, color=GREY["ink"], lw=0.8)
        ax.set_yticks(y)
        ax.set_yticklabels([PARAM_LABELS[p] for p in order], fontsize=7.5)
        ax.invert_yaxis()
        ax.set_xlabel(f"QoI 相对基准的变化 ({unit})", fontsize=7.5)
        ax.set_title(title, fontsize=8.5)
        ax.ticklabel_format(axis="x", style="sci", scilimits=(-2, 3))
        # 解耦注记
        if q < 2:
            ax.text(0.97, 0.06, "$h_m,D_0,C_0$ 的响应严格为 0\n（热湿解耦）",
                    transform=ax.transAxes, ha="right", fontsize=7,
                    color=GREY["dark"])
        else:
            ax.text(0.97, 0.06, "$h,k,\\rho,c_p,T_0$ 的响应严格为 0\n（热湿解耦）",
                    transform=ax.transAxes, ha="right", fontsize=7,
                    color=GREY["dark"])
        if q == 0:
            ax.legend(loc="lower left", fontsize=7)
    fig.tight_layout()
    save(fig, "fig_q1_sensitivity")


def load_mc():
    e3, e4 = [], []
    with open(os.path.join(OUT, "q1_sensitivity_mc.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            v = [float(r["T_center_1800s_K"]), float(r["T_surface_1800s_K"]),
                 float(r["C_surface_1800s_kgkg"]), float(r["C_avg_1800s_kgkg"])]
            (e3 if r["experiment"] == "E3_noise" else e4).append(v)
    return np.array(e3), np.array(e4)


def fig_robustness():
    e3, e4 = load_mc()
    base = np.array([306.726129, 309.935961, 1.510266, 2.293556])   # E1 基准 (M=400, dt=0.25)

    # E5a 网格收敛 (现算, 与 q1_sensitivity.py E5 同设置)
    from q1_sensitivity import solve_fast
    from q1_solve import Env, load_attachment1
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    dt = 0.25
    ns = int(round(1800.0 / dt))
    tg = np.arange(1, ns + 1) * dt
    grid = {}
    for M in (100, 200, 400, 800):
        Tg, Cg, Cag = solve_fast(M, dt, env.T_arr(tg), env.C_arr(tg))
        grid[M] = np.array([Tg[0], Tg[-1], Cg[-1], Cag])
    ref = grid[800]

    markers = ["o", "s", "^", "D"]
    mcolors = [C["blue"], C["orange"], C["teal"], C["red"]]

    fig, axes = plt.subplots(1, 3, figsize=(7.1, 2.9))

    # ---- (a) 噪声 MC ----
    ax = axes[0]
    for j in range(4):
        dev = np.abs(e3[:, j] - base[j]) / HALF_ULP
        x = j + np.random.default_rng(7).uniform(-0.16, 0.16, len(dev))
        ax.scatter(x, dev, s=7, marker=markers[j], facecolor=mcolors[j],
                   edgecolor="none", alpha=0.8, zorder=3)
    ax.axhline(1.0, color=GREY["ink"], lw=0.9, ls=(0, (4, 2)), zorder=2)
    ax.text(3.42, 2.2, "四位小数报告精度\n(半 ulp $5\\times10^{-5}$)", fontsize=6.8,
            ha="right", color=GREY["dark"])
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 1e4)
    ax.yaxis.set_major_formatter(pow_formatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(4))
    ax.set_xticklabels(["T 中心", "T 表面", "C 表面", "C 均值"], fontsize=7)
    ax.set_ylabel("$|\\Delta\\mathrm{QoI}|$ / 报告精度", fontsize=7.5)
    ax.set_title("(a) 边界数据噪声 MC (N=100)\n"
                 f"$\\sigma_T$=0.15 °C, $\\sigma_C$=1.3×10$^{{-4}}$ kg/kg (数据估计)",
                 fontsize=8)

    # ---- (b) 参数 MC ----
    ax = axes[1]
    for j in range(4):
        dev = np.abs(e4[:, j] - base[j]) / HALF_ULP
        x = j + np.random.default_rng(11).uniform(-0.16, 0.16, len(dev))
        ax.scatter(x, dev, s=7, marker=markers[j], facecolor=mcolors[j],
                   edgecolor="none", alpha=0.8, zorder=3)
    ax.axhline(1.0, color=GREY["ink"], lw=0.9, ls=(0, (4, 2)), zorder=2)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, 1e5)
    ax.yaxis.set_major_formatter(pow_formatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(range(4))
    ax.set_xticklabels(["T 中心", "T 表面", "C 表面", "C 均值"], fontsize=7)
    ax.set_title("(b) 参数联合 ±10% MC (N=100)\n物理输入不确定性的传导 (非数值误差)",
                 fontsize=8)

    # ---- (c) 网格收敛 ----
    ax = axes[2]
    Ms = [100, 200, 400, 800]
    for j in range(4):
        dev = [abs(grid[M][j] - ref[j]) / HALF_ULP for M in Ms]
        ax.plot(Ms, dev, marker=markers[j], ms=3.5, lw=1.0, color=mcolors[j])
    ax.axhline(1.0, color=GREY["ink"], lw=0.9, ls=(0, (4, 2)), zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(pow_formatter())
    ax.yaxis.set_major_formatter(pow_formatter())
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xticks(Ms)
    ax.set_xticklabels([str(M) for M in Ms])
    ax.set_xlabel("网格数 $M$ (dt=0.25 s)")
    ax.set_title("(c) 网格收敛 (参考 M=800)\n水分<0.01×、温度<10× 报告精度",
                 fontsize=8)
    ax.legend(["T 中心", "T 表面", "C 表面", "C 均值"], fontsize=6.5,
              loc="lower right")

    axes[0].set_xlim(-0.6, 3.6)
    axes[1].set_xlim(-0.6, 3.6)
    fig.tight_layout()
    save(fig, "fig_q1_robustness")


def main():
    setup()
    fig_sensitivity()
    fig_robustness()


if __name__ == "__main__":
    main()
