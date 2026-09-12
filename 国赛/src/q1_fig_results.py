# -*- coding: utf-8 -*-
r"""
图 2 问题一结果总览 (2x3 六面板) —— 合并原 fig_q1_temp_results 与 fig_q1_moist_results.

figure contract:
  核心结论: 30 min 内温度场快速建立径向梯度但远未平衡 (环境/表面/中心三级滞后),
  水分却只在表层松弛 (中心几乎不动、体积平均微降、C(R)/C_inf 仍差约 46 倍) ——
  热/湿时间尺度分离 R^2/alpha : R^2/D(C0) ~ 1:34 的直接可视化证据.

面板 (合并前两图各有 (a)(b)(c) 三面板, 现重排为 2x3):
  (a) 温度场时空热图 T(r,t)        (数据: outputs/result1.xlsx 生产解 M=3200)
  (b) 表1 时刻的径向剖面 T(r)      (线色随时间 viridis 渐变, 右端直标时刻)
  (c) 中心/表面温度演化 + 烘房环境 (展示 表面-环境、中心-表面 两级滞后)
  (d) 水分浓度场时空热图 C(r,t)
  (e) 表2 时刻的径向剖面 C(r)
  (f) 中心/体积平均/表面浓度演化 + 环境 (展示仅表层脱湿与巨大平衡差距)

版式 (与 src/q2_figures.py 的 fig_q2_results 同一套办法, 本仓库既有的 2x3 先例):
  * 画布 7.4x5.4 in, wspace 0.72 —— 六面板下留给 y 刻度标签与色条的余量;
  * 每轴 MaxNLocator(4), 避免刻度标签互相重叠;
  * 色条用 inset 轴, 标签短式且基号 7.6 pt (mathtext 上下标约 0.70 倍, 故 $^\circ$
    为 5.32 pt, 满足 5 pt 字形下限);
  * 面板内说明一律由 place_anno() 落在"数据未经过"的空白矩形内 (禁止目测定位);
  * 曲线右端的 7 个时刻标签用 declutter() 做最小间距展开.

本图相对原两张单面板图的**版式**改动 (数据、文字、单位、坐标范围均未改动):
  1. 原单面板图从未跑过碰撞门, 本身已含缺陷: (i) 曲线穿过"线色由深至浅"说明;
     (ii) 水分剖面右端 7 个时刻标签互相重叠 (间距 0.068 data 单位 < 标签高度
     0.061+余量). 合并时用 place_anno + declutter 一并修正.
  2. 面板宽度从 ~6.5 in 降到 1.51 in, 原 (c)(f) 的单行注释 (1.94/1.89 in) 已宽于
     面板本身, 故拆为两行 (信息相同, 只是换行);
  3. (b)(e) 顶部留白 (数据最大值落在坐标区高度的 75% 处), 给"线色由深至浅"说明
     与最上方时刻标签留出互不相交的空间 —— 否则二者必然重叠.

运行: python src/q1_fig_results.py
输出: paper/figures/fig_q1_results.pdf|.png|.svg + .alignment.json|.svg
      控制台打印 T_inf(1800s)、表面温差、C_inf、C(R)/C_inf、体积平均降幅 (供正文引用)
"""

from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C as PAL, setup  # noqa: E402
from q1_fig_common import declutter, few_ticks, place_anno, save_gated  # noqa: E402
from q1_fig_data import load_result1  # noqa: E402
from q1_solve import Env, R0, load_attachment1  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T_TAB = [100, 300, 600, 900, 1200, 1500, 1800]
X_LAB = 2.06                # 剖面图右端时刻标签的 x 位置 (data, cm)
TOP_FRAC = 0.75             # (b)(e) 数据最大值落在坐标区高度的比例, 其余留给说明
FS_TITLE, FS_LABEL, FS_TICK, FS_LEG, FS_ANN, FS_CB = 8.5, 8.0, 7.5, 7.4, 7.4, 7.2
EXCLUDE: list = []          # 色条 inset 轴 (无 subplotspec, 对齐门里显式排除)


def colorbar(fig, mappable, ax, label, fs=7.6):
    r"""色条用 inset 轴: 短式标签, 基号 7.6 pt (mathtext 上标为 5.32 pt)."""
    cax = ax.inset_axes([1.025, 0.0, 0.04, 1.0])
    cb = fig.colorbar(mappable, cax=cax)
    cb.set_label(label, fontsize=fs)
    cb.ax.tick_params(labelsize=FS_CB, length=2)
    EXCLUDE.append(cax)
    return cb


def volume_avg_weights(rh_cm, n):
    """节点式网格的体积权重 (单位轴长, 已含 pi)."""
    dr = rh_cm[1] - rh_cm[0]
    r = rh_cm / 100.0
    rf_p = np.minimum(r + dr / 200.0, R0)
    rf_m = np.maximum(r - dr / 200.0, 0.0)
    return np.pi * (rf_p ** 2 - rf_m ** 2)


def shades(n=7):
    """t=100..1800 s 七条剖面的由深至浅配色 (与原单面板图一致)."""
    return [plt.cm.viridis(0.02 + 0.78 * k / (n - 1)) for k in range(n)]


def set_ylim_top_frac(ax, lo, hi, top_frac=TOP_FRAC, bot_pad=0.05):
    """令数据上界落在坐标区高度的 top_frac 处, 上方留白供面板内说明使用."""
    y0 = lo - bot_pad * (hi - lo)
    y1 = y0 + (hi - y0) / top_frac
    ax.set_ylim(y0, y1)
    return y0, y1


def label_gap_units(ax, fs_pt):
    """把一个 fs_pt 文字的高度换算成当前轴的 data 单位 (含 1.15 行距余量)."""
    fig = ax.figure
    fig.canvas.draw()
    h_pt = ax.get_window_extent(fig.canvas.get_renderer()).height * 72.0 / fig.dpi
    y0, y1 = sorted(ax.get_ylim())
    return 1.15 * fs_pt / (h_pt / (y1 - y0))


def profile_panel(ax, rh, mat, idx, sh, ylabel, title, note):
    """(b)/(e) 共用: 7 条剖面 + 右端时刻标签(最小间距展开) + 空白处说明."""
    lo = min(mat[i].min() for i in idx)
    hi = max(mat[i].max() for i in idx)
    y0, y1 = set_ylim_top_frac(ax, lo, hi)
    for k, i in enumerate(idx):
        ax.plot(rh, mat[i], "-", color=sh[k], lw=1.2)
    lab = declutter([mat[i, -1] for i in idx], label_gap_units(ax, 6.8))
    if lab.min() <= y0 or lab.max() >= y1:
        raise AssertionError(f"{title}: 时刻标签被推出坐标区 "
                             f"{lab.min():.4f}..{lab.max():.4f} vs {y0:.4f}..{y1:.4f}")
    true = np.array([mat[i, -1] for i in idx])
    shift = np.abs(lab - true)
    print(f"  {title}: 时刻标签最小间距展开, 最大位移 {shift.max():.4f} "
          f"({shift.max() / (y1 - y0) * 100:.2f}% 轴高), 展开后按值排序的最小间距 "
          f"{np.diff(np.sort(lab)).min():.4f}")
    for k, i in enumerate(idx):
        ax.text(X_LAB, lab[k], f"{T_TAB[k]}", fontsize=6.8, va="center", color=sh[k])
    ax.set_xlim(0, 2.75)
    ax.set_xlabel("到中心距离 $r$ (cm)", fontsize=FS_LABEL)
    ax.set_ylabel(ylabel, fontsize=FS_LABEL)
    ax.set_title(title, fontsize=FS_TITLE)
    ax.tick_params(labelsize=FS_TICK)
    few_ticks(ax, 4, "y")
    few_ticks(ax, 4, "x")
    # 避让点集必须同时含全部数据曲线与 7 个时刻标签, 否则说明会压到标签上
    pts = (np.concatenate([np.tile(rh, len(idx)), np.full(len(idx), X_LAB)]),
           np.concatenate([np.concatenate([mat[i] for i in idx]), lab]))
    place_anno(ax, pts, note, prefer="upper left", fs=FS_ANN)


def main():
    setup()
    matplotlib.rcParams["font.sans-serif"] = list(
        matplotlib.rcParams["font.sans-serif"]) + ["DejaVu Sans"]

    rh, tt, T, Cm = load_result1()
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    w = volume_avg_weights(rh, len(rh))
    Cavg = Cm @ w / w.sum()
    idx = [int(np.where(tt == v)[0][0]) for v in T_TAB]

    gap_T = env.T(1800.0) - 273.15 - T[-1, -1]
    gap_C = env.T(1800.0) - 273.15 - T[-1, 0]
    ratio = Cm[-1, -1] / env.C(1800.0)
    drop = (Cavg[0] - Cavg[-1]) / Cavg[0]
    print(f"T_inf(1800s) = {env.T(1800.0) - 273.15:.4f} degC; "
          f"gap to surface = {gap_T:.4f} K; gap to center = {gap_C:.4f} K")
    print(f"C_inf(1800s) = {env.C(1800.0):.5f}; C(R,1800s) = {Cm[-1, -1]:.4f}; "
          f"ratio = {ratio:.1f}; <C> drop = {drop * 100:.1f}%")

    sh = shades(len(T_TAB))
    tt_fine = np.linspace(0, 1800, 600)
    T_amb = env.T_arr(tt_fine) - 273.15
    C_amb = env.C_arr(tt_fine)

    fig = plt.figure(figsize=(7.4, 5.4))
    gs = fig.add_gridspec(2, 3, left=0.070, right=0.975, bottom=0.075,
                          top=0.930, hspace=0.62, wspace=0.72)
    axT = fig.add_subplot(gs[0, 0]); axT.set_gid("a")
    axP = fig.add_subplot(gs[0, 1]); axP.set_gid("b")
    axS = fig.add_subplot(gs[0, 2]); axS.set_gid("c")
    axC = fig.add_subplot(gs[1, 0]); axC.set_gid("d")
    axQ = fig.add_subplot(gs[1, 1]); axQ.set_gid("e")
    axE = fig.add_subplot(gs[1, 2]); axE.set_gid("f")

    # ---------------- (a) 温度场时空热图 ----------------
    mT = axT.pcolormesh(tt, rh, T.T, cmap="inferno", shading="auto",
                        vmin=T.min(), vmax=T.max())
    colorbar(fig, mT, axT, "$T$ / (°C)")
    axT.set_xlabel("时间 $t$ (s)", fontsize=FS_LABEL)
    axT.set_ylabel("到中心距离 $r$ (cm)", fontsize=FS_LABEL)
    axT.set_title("(a) 温度场时空热图 $T(r,t)$", fontsize=FS_TITLE)
    axT.tick_params(labelsize=FS_TICK)
    few_ticks(axT, 4, "y"); few_ticks(axT, 4, "x")

    # ---------------- (b) 表1 时刻的径向剖面 ----------------
    profile_panel(axP, rh, T, idx, sh, "温度 $T$ (°C)",
                  "(b) 径向剖面（表1 时刻）",
                  "线色由深至浅：\n$t=100\\to1800$ s")

    # ---------------- (c) 中心/表面温度演化与烘房环境 ----------------
    axS.plot(tt, T[:, 0], "-", color=PAL["blue"], lw=1.4, label="中心 $T(0,t)$")
    axS.plot(tt, T[:, -1], "-", color=PAL["red"], lw=1.4, label="表面 $T(R,t)$")
    axS.plot(tt_fine, T_amb, "--", color=PAL["orange"], lw=1.2,
             label="烘房 $T_\\infty(t)$")
    axS.set_xlim(0, 1800)
    axS.set_ylim(27, 52)
    axS.set_xlabel("时间 $t$ (s)", fontsize=FS_LABEL)
    axS.set_ylabel("温度 $T$ (°C)", fontsize=FS_LABEL)
    axS.set_title("(c) 中心/表面温度演化与烘房环境", fontsize=FS_TITLE)
    axS.tick_params(labelsize=FS_TICK)
    few_ticks(axS, 4, "y"); few_ticks(axS, 4, "x")
    place_anno(axS, (np.concatenate([tt, tt, tt_fine]),
                     np.concatenate([T[:, 0], T[:, -1], T_amb])),
               f"$t=1800$ s：\n$T_\\infty-T(R)\\approx{gap_T:.1f}$ °C",
               prefer="upper left", fs=FS_ANN)
    # 图例移到坐标区下方: 面板内三条曲线自左下扫到右上, 没有能容纳三行图例的空区
    # 图例基号必须 >= 7.15 pt: 图例里的 $T_\infty(t)$ 下标按 0.70 倍缩放,
    # 6.4 pt 时只有 4.48 pt, 低于字形门 5 pt 下限 (实测 FAIL).
    axS.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), fontsize=FS_LEG,
               ncol=3, handlelength=1.2, columnspacing=0.8, labelspacing=0.25,
               borderpad=0.25)

    # ---------------- (d) 水分浓度场时空热图 ----------------
    mC = axC.pcolormesh(tt, rh, Cm.T, cmap="viridis", shading="auto",
                        vmin=Cm.min(), vmax=Cm.max())
    colorbar(fig, mC, axC, "$C$ / (kg/kg)")
    axC.set_xlabel("时间 $t$ (s)", fontsize=FS_LABEL)
    axC.set_ylabel("到中心距离 $r$ (cm)", fontsize=FS_LABEL)
    axC.set_title("(d) 水分浓度场时空热图 $C(r,t)$", fontsize=FS_TITLE)
    axC.tick_params(labelsize=FS_TICK)
    few_ticks(axC, 4, "y"); few_ticks(axC, 4, "x")

    # ---------------- (e) 表2 时刻的径向剖面 ----------------
    profile_panel(axQ, rh, Cm, idx, sh, "水分浓度 $C$ (kg/kg)",
                  "(e) 径向剖面（表2 时刻）",
                  "线色由深至浅：\n$t=100\\to1800$ s")

    # ---------------- (f) 中心/体积平均/表面浓度演化 ----------------
    axE.plot(tt, Cm[:, 0], "-", color=PAL["blue"], lw=1.4, label="中心 $C(0,t)$")
    axE.plot(tt, Cavg, "-", color=PAL["teal"], lw=1.4,
             label="体积平均 $\\langle C\\rangle(t)$")
    axE.plot(tt, Cm[:, -1], "-", color=PAL["red"], lw=1.4, label="表面 $C(R,t)$")
    axE.plot(tt_fine, C_amb, "--", color=PAL["orange"], lw=1.2,
             label="烘房 $C_\\infty(t)$")
    axE.set_xlim(0, 1800)
    axE.set_ylim(0, 2.75)
    axE.set_xlabel("时间 $t$ (s)", fontsize=FS_LABEL)
    axE.set_ylabel("水分浓度 $C$ (kg/kg)", fontsize=FS_LABEL)
    axE.set_title("(f) 各层浓度演化与体积平均", fontsize=FS_TITLE)
    axE.tick_params(labelsize=FS_TICK)
    few_ticks(axE, 4, "y"); few_ticks(axE, 4, "x")
    place_anno(axE, (np.concatenate([tt, tt, tt, tt_fine]),
                     np.concatenate([Cm[:, 0], Cavg, Cm[:, -1], C_amb])),
               f"$t=1800$ s：\n$C(R)/C_\\infty\\approx{ratio:.0f}$ 倍",
               prefer="lower right", fs=FS_ANN)
    axE.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), fontsize=FS_LEG,
               ncol=2, handlelength=1.2, columnspacing=0.8, labelspacing=0.25,
               borderpad=0.25)

    save_gated(fig, "fig_q1_results", exclude_axes=EXCLUDE)
    plt.close(fig)


if __name__ == "__main__":
    main()
