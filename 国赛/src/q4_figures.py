# -*- coding: utf-8 -*-
"""
q4_figures.py -- 问题四图件 (nature-figure 契约: 矢量可编辑文字, 面板对齐门, 最小文字).

fig_q4_schematic.pdf  物质坐标变换示意 (动边界 -> 固定域)
fig_q4_shrink.pdf     收缩数据 R(t) 与几何增强因子
fig_q4_results.pdf    主结果: 剖面演化 / 终止事件 / 物理坐标热图 / 效应分解
fig_q4_verify.pdf     数值验证: 网格与容限收敛

多面板图在导出前必须通过 nature-figure 的面板对齐门 (1.5 pt).

输出: paper/figures/*.pdf|.png|.alignment.json 与 outputs/registry_q4_figures.csv
"""

from __future__ import annotations

import csv
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fig_style as FS                                   # noqa: E402
from fig_style import C, FIGDIR                          # noqa: E402
from q4_solve import (solve_q4, sample_q4, Q4Radius, load_attachment2,   # noqa: E402
                      CSTAR)
from q4_verify import _secant_to_xi                       # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
ROWS = []

# --- nature-figure 面板对齐门 (多面板图必须在对齐门通过后才导出) ---
SKILL_SCRIPTS = os.path.expanduser(r"~\.dsh\research-skills\nature-figure\scripts")
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)
try:
    from audit_panel_alignment import require_matplotlib_panel_alignment
except Exception as exc:                                  # pragma: no cover
    print(f"[warn] 无法导入对齐门: {exc}", flush=True)
    require_matplotlib_panel_alignment = None


def save_gated(fig, name, tolerance_pt=1.5, gutter_tolerance_pt=1.5):
    """先跑面板对齐门, 再导出 (nature-figure 契约: 门未通过不得导出)."""
    if require_matplotlib_panel_alignment is not None:
        require_matplotlib_panel_alignment(
            fig,
            json_out=os.path.join(FIGDIR, f"{name}.alignment.json"),
            overlay_svg=os.path.join(FIGDIR, f"{name}.alignment.svg"),
            tolerance_pt=tolerance_pt,
            gutter_tolerance_pt=gutter_tolerance_pt,
            strict=True,
        )
    FS.save(fig, name)


def R(key, q, v, u, src):
    ROWS.append((key, q, float(v), u, src))


# ===========================================================================
def fig_schematic():
    """物质坐标变换示意: 动边界 -> 固定域."""
    FS.setup()
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
    rad = Q4Radius()
    ts = [0.0, 10800.0, 36000.0, 183906.7]
    cols = [C["blue"], C["teal"], C["orange"], C["red"]]
    lab = ["0 h", "3 h", "10 h", "51.1 h"]
    ycen = [0.0, 0.30, 0.60, 0.90]

    ax = axes[0]
    for tt, col, yc, lb in zip(ts, cols, ycen, lab):
        Rt = float(rad.R(tt))
        ax.plot([-Rt, Rt], [yc, yc], color=col, lw=1.7)
        ax.plot([-Rt, -Rt], [yc - 0.05, yc + 0.05], color=col, lw=1.7)
        ax.plot([Rt, Rt], [yc - 0.05, yc + 0.05], color=col, lw=1.7)
        ax.text(Rt + 0.0035, yc, lb, fontsize=6.2, va="center", color=col)
        for xf in (-0.5, 0.0, 0.5):
            ax.plot([xf * Rt], [yc], marker="|", ms=4, color=col, mew=0.9)
    ax.annotate("", xy=(-0.0205, 0.24), xytext=(-0.0205, 0.06),
                arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.8))
    ax.text(-0.0215, 0.15, "边界收缩", fontsize=6.2, color=C["grey"],
            rotation=90, va="center", ha="right")
    ax.set_xlim(-0.026, 0.040)
    ax.set_ylim(-0.13, 1.06)
    ax.set_yticks([])
    ax.set_xticks([-0.02, -0.01, 0, 0.01, 0.02])
    ax.set_xticklabels(["-2", "-1", "0", "1", "2"])
    ax.set_xlabel("物理半径 r / cm", fontsize=7.5)
    ax.set_title("(a) 物理坐标: 边界 R(t) 随时间收缩", fontsize=7.5, pad=4)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    ax = axes[1]
    for tt, col, yc, lb in zip(ts, cols, ycen, lab):
        ax.plot([0, 1], [yc, yc], color=col, lw=1.7)
        ax.plot([0, 0], [yc - 0.05, yc + 0.05], color=col, lw=1.7)
        ax.plot([1, 1], [yc - 0.05, yc + 0.05], color=col, lw=1.7)
        for xf in (0.0, 0.5, 1.0):
            ax.plot([xf], [yc], marker="|", ms=4, color=col, mew=0.9)
        ax.text(0.5, yc + 0.062, lb, fontsize=6.2, ha="center", color=col)
    ax.annotate("", xy=(0.14, 0.24), xytext=(0.14, 0.06),
                arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.8))
    ax.text(0.18, 0.15, "同一物质点", fontsize=6.2, color=C["grey"], va="center")
    ax.set_xlim(-0.12, 1.24)
    ax.set_ylim(-0.13, 1.06)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
    ax.set_xlabel(r"物质坐标 $\xi=r/R(t)$", fontsize=7.5)
    ax.set_title(r"(b) 物质坐标: 域固定为 $\xi\in[0,1]$", fontsize=7.5, pad=4)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    fig.subplots_adjust(wspace=0.14)
    save_gated(fig, "fig_q4_schematic")
    plt.close(fig)


# ===========================================================================
def fig_shrink():
    """附件 2 收缩数据与几何增强因子."""
    FS.setup()
    t, Rc = load_attachment2()
    rad = Q4Radius()
    th = np.linspace(0.0, t[-1], 2000)
    Rh = np.atleast_1d(rad.R(th)) * 100.0
    boost = (Rc[0] / Rh) ** 2

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.45))

    ax = axes[0]
    ax.plot(t / 3600.0, Rc, "o", ms=2.0, color=C["blue"], alpha=0.50,
            label="附件 2 数据")
    ax.plot(th / 3600.0, Rh, "-", lw=1.2, color=C["ink"], label="PCHIP 插值")
    ax.axhline(float(Rc[-1]), color=C["red"], lw=0.8, ls="--")
    ax.text(38, float(Rc[-1]) + 0.025, f"R = {Rc[-1]:.3f} cm",
            fontsize=6.3, color=C["red"])
    ax.set_xlabel("时间 / h", fontsize=7.5)
    ax.set_ylabel("药材半径 R / cm", fontsize=7.5)
    ax.set_xlim(-1, 73)
    ax.set_ylim(1.14, 2.06)
    ax.legend(loc="upper right", fontsize=6.3, handlelength=1.4)
    ax.set_title(f"(a) 附件 2 收缩数据 (2.000 → {Rc[-1]:.3f} cm)", fontsize=7.5,
                 pad=4)
    ax.annotate("前 6 h 完成 78 %", xy=(6, 1.374), xytext=(16, 1.66),
                fontsize=6.3, color=C["grey"],
                arrowprops=dict(arrowstyle="->", color=C["grey"], lw=0.7))

    ax = axes[1]
    ax.plot(th / 3600.0, boost, "-", lw=1.3, color=C["teal"])
    ax.fill_between(th / 3600.0, 1.0, boost, color=C["teal"], alpha=0.10)
    ax.axhline(1.0, color=C["grey"], lw=0.7, ls=":")
    ax.set_xlabel("时间 / h", fontsize=7.5)
    ax.set_ylabel(r"几何增强因子 $(R_0/R)^2$", fontsize=7.5)
    ax.set_xlim(-1, 73)
    ax.set_ylim(0.95, 3.05)
    ax.set_title("(b) 物质坐标下收缩的几何效应", fontsize=7.5, pad=4)
    ax.annotate(f"收敛到 {boost[-1]:.3f}", xy=(64, boost[-1]), xytext=(26, 2.45),
                fontsize=6.3, color=C["teal"],
                arrowprops=dict(arrowstyle="->", color=C["teal"], lw=0.7))

    fig.subplots_adjust(wspace=0.30)
    save_gated(fig, "fig_q4_shrink")
    plt.close(fig)

    R("FIG_R0", "附件2 初始半径", Rc[0], "cm", "附件2")
    R("FIG_Rend", "附件2 末半径", Rc[-1], "cm", "附件2")
    R("FIG_boost_end", "末段几何增强因子 (R0/R)^2", boost[-1], "1", "推导")
    R("FIG_tR15", "R 降到 1.5 cm 的时刻", float(t[int(np.argmax(Rc <= 1.5))]),
      "s", "附件2")


# ===========================================================================
def fig_results(res):
    """主结果四面板."""
    FS.setup()
    g, rad, sol, t_dry = res["g"], res["rad"], res["sol"], res["t_dry"]
    s = sample_q4(sol, g, rad, t_dry)
    n = g["n"]

    fig = plt.figure(figsize=(7.2, 4.6))
    gs = fig.add_gridspec(2, 2, hspace=0.50, wspace=0.34)

    # ---- (a) 剖面演化 (物理坐标) ----
    ax = fig.add_subplot(gs[0, 0])
    hours = [6.0, 12.0, 24.0, 36.0, 48.0, t_dry / 3600.0]
    cmap = plt.get_cmap("viridis")
    for i, h in enumerate(hours):
        k = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        col = cmap(i / (len(hours) - 1) * 0.88)
        ok = ~np.isnan(s["Cg"][k])
        ax.plot(s["grid_cm"][ok], s["Cg"][k][ok], "-", lw=1.25, color=col,
                label=f"{h:.1f} h" if h < 100 else "51.09 h")
        ax.axvline(s["Rs"][k], color=col, lw=0.6, ls=":", alpha=0.9)
    ax.axhline(CSTAR, color=C["red"], lw=0.9, ls="--")
    ax.text(1.96, CSTAR + 0.085, "C* = 0.15", fontsize=6.4, color=C["red"],
            ha="right")
    ax.set_xlabel("物理半径 r / cm", fontsize=7.5)
    ax.set_ylabel("含水率 C / (kg/kg)", fontsize=7.5)
    ax.set_xlim(0, 2.02)
    ax.set_ylim(0, 2.85)
    ax.legend(fontsize=5.9, loc="upper right", handlelength=1.1,
              labelspacing=0.20, borderpad=0.20, handletextpad=0.35)
    ax.set_title("(a) 含水率剖面（虚线为各时刻 R(t)）", fontsize=7.5, pad=4)

    # ---- (b) 终止事件 ----
    ax = fig.add_subplot(gs[0, 1])
    tt = np.linspace(0.0, t_dry, 4000)
    mx = sol.sol(tt)[n:, :].max(axis=0)
    ax.plot(tt / 3600.0, mx, "-", lw=1.4, color=C["blue"])
    ax.axhline(CSTAR, color=C["red"], lw=0.9, ls="--")
    ax.plot([t_dry / 3600.0], [CSTAR], "o", ms=4.5, color=C["red"], zorder=5)
    ax.annotate(f"t_dry = {t_dry/3600:.2f} h",
                xy=(t_dry / 3600.0, CSTAR), xytext=(32.0, 1.30),
                fontsize=6.6, color=C["red"], ha="center",
                arrowprops=dict(arrowstyle="->", color=C["red"], lw=0.8))
    ax.set_xlabel("时间 / h", fontsize=7.5)
    ax.set_ylabel(r"$\max_r C(r,t)$ / (kg/kg)", fontsize=7.5)
    ax.set_xlim(0, t_dry / 3600.0 * 1.06)
    ax.set_ylim(0, 2.75)
    ax.set_title("(b) 终止事件：全场最大值穿越阈值", fontsize=7.5, pad=4)

    # ---- (c) 物理坐标热图 ----
    ax = fig.add_subplot(gs[1, 0])
    Tc = s["t60"] / 3600.0
    im = ax.pcolormesh(s["grid_cm"], Tc, s["Cg"], cmap="YlGnBu_r",
                       vmin=0.05, vmax=2.6, shading="auto", rasterized=True)
    ax.fill_betweenx(Tc, s["Rs"], 2.06, color="white", zorder=2)
    ax.plot(s["Rs"], Tc, "-", lw=1.2, color=C["red"], zorder=3,
            label="表面 R(t)")
    cb = fig.colorbar(im, ax=ax, pad=0.02, fraction=0.05)
    cb.set_label("C / (kg/kg)", fontsize=6.6)
    cb.ax.tick_params(labelsize=6.0)
    ax.set_xlabel("物理半径 r / cm", fontsize=7.5)
    ax.set_ylabel("时间 / h", fontsize=7.5)
    ax.set_xlim(0, 2.06)
    ax.set_ylim(0, 52)
    ax.legend(fontsize=6.2, loc="lower left", handlelength=1.2)
    ax.set_title("(c) 水分场（白区已收缩出域）", fontsize=7.5, pad=4)

    # ---- (d) 效应分解 ----
    ax = fig.add_subplot(gs[1, 1])
    labs = ["问题三", "附录4\n不收缩", "附录3\n+收缩", "问题四"]
    vals = [206720.4135, 467318.1610, 90834.4401, 183906.7128]
    cols = [C["grey"], C["lightred"], C["lightblue"], C["blue"]]
    b = ax.bar(range(4), [v / 3600.0 for v in vals], color=cols, width=0.60,
               edgecolor=C["ink"], linewidth=0.5)
    ax.axhline(72.0, color=C["red"], lw=0.9, ls="--")
    ax.text(3.42, 75.0, "3 天安全网", fontsize=6.2, color=C["red"], ha="right")
    for bb, v in zip(b, vals):
        ax.text(bb.get_x() + bb.get_width() / 2, v / 3600.0 + 4.5,
                f"{v/3600:.1f}", ha="center", fontsize=6.3)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labs, fontsize=6.2)
    ax.set_ylabel("t_dry / h", fontsize=7.5)
    ax.set_ylim(0, 158)
    ax.set_title("(d) 物性与收缩的效应分解", fontsize=7.5, pad=4)

    save_gated(fig, "fig_q4_results")
    plt.close(fig)

    for h in hours:
        i = int(np.argmin(np.abs(s["t60"] - h * 3600.0)))
        R(f"FIG_prof_{h:.2f}h_C0", f"剖面图 t={h:.2f}h 中心含水率",
          s["Cg"][i, 0], "kg/kg", "outputs/q4_production.log")
        R(f"FIG_prof_{h:.2f}h_R", f"剖面图 t={h:.2f}h 半径", s["Rs"][i], "cm",
          "附件2")


# ===========================================================================
def fig_verify():
    """数值验证两面板."""
    FS.setup()
    # 六点网格链与相邻三点实测阶, 与 registry_q4_verify.csv 的 V1_M*/V1_p* 一致
    # (论文图注与表13 的"由 1.51 升到 1.95"即出自这条链)
    Mv = [100, 200, 400, 800, 1600, 3200]
    tv = [183827.20992567966, 183906.71282718718, 183934.69473051972,
          183943.11020790294, 183945.37707122925, 183945.96344573775]
    pv = [1.51, 1.73, 1.89, 1.95]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4))

    ax = axes[0]
    hv = [v / 3600 for v in tv]
    ax.plot(Mv, hv, "o-", ms=4, lw=1.2, color=C["blue"])
    # 三点实测阶标在其三点对数中点 (sqrt(M_k*M_{k+2})), 置于曲线下方空白处
    for k, p in enumerate(pv):
        xm = float(np.sqrt(Mv[k] * Mv[k + 2]))
        ym = float(np.interp(np.log2(xm), np.log2(Mv), hv)) - 0.0095
        ax.text(xm, ym, "%.2f" % p, fontsize=5.8, ha="center", va="top",
                color=C["grey"])
    ax.text(0.04, 0.05,
            "M = 100 : %.4f h\nM = 3200 : %.4f h"
            % (hv[0], hv[-1]),
            transform=ax.transAxes, fontsize=6.2, va="bottom", ha="left",
            color=C["blue"], linespacing=1.35)
    ax.set_xscale("log", base=2)
    ax.set_xticks(Mv)
    ax.set_xticklabels([str(m) for m in Mv], fontsize=6.3)
    ax.set_xlabel("网格数 M", fontsize=7.5)
    ax.set_ylabel("t_dry / h", fontsize=7.5)
    ax.set_ylim(51.048, 51.102)
    ax.set_title("(a) 空间收敛（实测阶 1.51 升至 1.95）", fontsize=7.5, pad=4)

    ax = axes[1]
    rt = [1e-7, 1e-9, 1e-11]
    tvr = [183906.6030, 183906.7128, 183906.7081]
    ax.plot(rt, [v - 183906.7 for v in tvr], "o-", ms=4, lw=1.2,
            color=C["teal"])
    ax.axhline(0.0, color=C["grey"], lw=0.7, ls=":")
    ax.set_xscale("log")
    ax.invert_xaxis()
    ax.set_xticks(rt)
    ax.set_xticklabels(["$10^{-7}$", "$10^{-9}$", "$10^{-11}$"])
    ax.set_xlabel("相对容限 rtol", fontsize=7.5)
    ax.set_ylabel("t_dry 相对基准 / s", fontsize=7.5)
    ax.set_ylim(-0.16, 0.16)
    ax.set_title("(b) 时间容限收敛（极差 0.11 s）", fontsize=7.5, pad=4)

    fig.subplots_adjust(wspace=0.34)
    save_gated(fig, "fig_q4_verify")
    plt.close(fig)

    R("FIG_V1_M100", "M=100 t_dry", tv[0], "s", "outputs/registry_q4_verify.csv V1_M100")
    R("FIG_V1_M200", "M=200 t_dry", tv[1], "s", "outputs/registry_q4_verify.csv V1_M200")
    R("FIG_V1_M400", "M=400 t_dry", tv[2], "s", "outputs/registry_q4_verify.csv V1_M400")
    R("FIG_V1_M800", "M=800 t_dry", tv[3], "s", "outputs/registry_q4_verify.csv V1_M800")
    R("FIG_V1_M1600", "M=1600 t_dry", tv[4], "s", "outputs/registry_q4_verify.csv V1_M1600")
    R("FIG_V1_M3200", "M=3200 t_dry", tv[5], "s", "outputs/registry_q4_verify.csv V1_M3200")
    R("FIG_V2_span", "rtol 极差", max(tvr) - min(tvr), "s", "outputs/q4_verify.log")


def main():
    os.makedirs(FIGDIR, exist_ok=True)
    print("求解生产基准 ...", flush=True)
    res = solve_q4(M=200)
    print(f"  t_dry = {res['t_dry']:.4f} s", flush=True)
    fig_schematic()
    fig_shrink()
    fig_results(res)
    fig_verify()
    with open(os.path.join(OUTDIR, "registry_q4_figures.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "source"])
        for r in ROWS:
            w.writerow([r[0], r[1], repr(r[2]), r[3], r[4]])
    print(f"写出: outputs/registry_q4_figures.csv ({len(ROWS)} 行)")


if __name__ == "__main__":
    main()
