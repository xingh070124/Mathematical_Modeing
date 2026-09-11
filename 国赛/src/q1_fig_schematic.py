"""
图1 物理建模示意图 (schematic-led composite).

核心结论 (figure contract): 药材烘干问题在"中截面对称 + 轴对称"下归结为
一维径向传热/传质抛物型方程组, 配中心对称条件与表面第三类(Robin)边界条件;
数值上用节点式有限体积离散, 通量在控制体界面上守恒.

面板:
  (a) 圆柱几何 + 坐标 + 热风对流边界条件 (第三类换热/传质);
  (b) 一维径向求解域的节点式 FV 网格与控制体 (图示 M=8).

风格: 黑白线稿, 与论文既有的黑白流程图/几何图一致.

运行:  python src/q1_fig_schematic.py
输出:  paper/figures/fig_q1_schematic.pdf|.png
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C, GREY, save, setup  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def panel_a(ax):
    """圆柱几何与边界条件. 版式: 上带=热风+热流入, 下带=质流出+尺寸标注."""
    L, R = 25.0, 2.0            # cm, 真实比例
    Re = 1.1                    # 端面椭圆半短轴 (透视)

    # ---- 圆柱体 ----
    ax.add_patch(Rectangle((0, -R), L, 2 * R, facecolor="#fdeedd",
                           edgecolor=GREY["ink"], lw=1.0, zorder=1))
    for x in np.arange(2.0, L, 2.4):          # 材质剖面线
        ax.plot([x, x + 1.0], [R, -R], color="#ead9c2", lw=0.5, zorder=1)
    ax.add_patch(Ellipse((0, 0), 2 * Re, 2 * R, facecolor="white",
                         edgecolor=GREY["ink"], lw=1.0, zorder=3))

    # ---- 轴线 z 与径向 r ----
    ax.plot([-3.5, 29.0], [0, 0], color=GREY["dark"], lw=0.7,
            ls=(0, (6, 3, 1, 3)), zorder=2)
    ax.text(29.6, 0.05, "$z$", fontsize=9, color=GREY["dark"])
    ax.annotate("", xy=(25.8, R), xytext=(25.8, 0),
                arrowprops=dict(arrowstyle="-|>", color=GREY["ink"], lw=0.9),
                zorder=4)
    ax.text(26.3, 1.0, "$r$", fontsize=9)

    # ---- 中截面 ----
    ax.plot([L / 2, L / 2], [-R, R], color=GREY["dark"], lw=0.8,
            ls=(0, (4, 2)), zorder=3)
    ax.text(L / 2, 0, "中截面 $z=0$", ha="center", va="center", fontsize=7.2,
            color=GREY["dark"], zorder=4,
            bbox=dict(fc="white", ec="none", pad=1.2))

    # ---- 上带: 热风 + 热流 (入) ----
    ax.add_patch(FancyArrowPatch((-4.0, 5.6), (13.0, 5.6), arrowstyle="-|>",
                                 mutation_scale=16, color=C["orange"],
                                 lw=2.2, alpha=0.85))
    ax.text(4.5, 6.5, "热风 $T_\\infty(t),\\ C_\\infty(t)$", ha="center",
            fontsize=8.5, color=C["orange"])
    for x in (6.0, 9.5, 13.0, 16.5):
        ax.annotate("", xy=(x, 2.2), xytext=(x, 4.4),
                    arrowprops=dict(arrowstyle="-|>", color=C["red"], lw=1.0))
    ax.text(-6.8, 5.0, "热流 $q=h\\,[T_\\infty-T]$（入）", fontsize=7.3,
            va="center", color=C["red"])

    # ---- 下带: 质流 (出) ----
    for x in (9.0, 12.5, 16.0, 19.5):
        ax.annotate("", xy=(x, -4.4), xytext=(x, -2.2),
                    arrowprops=dict(arrowstyle="-|>", color=C["blue"], lw=1.0,
                                    linestyle=(0, (3, 2))))
    ax.text(21.0, -3.3, "质流 $j=h_m\\,[C-C_\\infty]$（出）", fontsize=7.3,
            va="center", color=C["blue"])

    # ---- 尺寸标注 ----
    ax.annotate("", xy=(0, -5.9), xytext=(L, -5.9),
                arrowprops=dict(arrowstyle="<->", color=GREY["ink"], lw=0.7))
    ax.text(L / 2, -6.9, "$L=25\\ \\mathrm{cm}$", ha="center", fontsize=7.5)
    ax.annotate("", xy=(-2.4, 0), xytext=(-2.4, R),
                arrowprops=dict(arrowstyle="<->", color=GREY["ink"], lw=0.7))
    ax.text(-3.0, 1.0, "$R=2\\ \\mathrm{cm}$", ha="right", va="center", fontsize=7.5)

    ax.set_xlim(-8.0, 33.0)
    ax.set_ylim(-7.6, 7.6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("(a) 物理模型：圆柱药材与第三类边界条件", fontsize=8.5, pad=6)


def panel_b(ax, M=8):
    """节点式有限体积网格 (图示 M=8). 非等比例坐标, 长文字用轴坐标锚定."""
    R = 2.0
    r = np.linspace(0, R, M + 1)
    dr = R / M

    # ---- 控制体: 中心半格 / 内部整格 / 表面半格 ----
    shades = ["#e8f1fa", "white", "#fbe3d3"]
    for i in range(M + 1):
        lo = max(r[i] - dr / 2, 0.0)
        hi = min(r[i] + dr / 2, R)
        ax.add_patch(Rectangle((lo, 0), hi - lo, 1.0,
                               facecolor=shades[0 if i == 0 else 2 if i == M else 1],
                               edgecolor=GREY["mid"], lw=0.6, zorder=1))

    # ---- 界面通量 (以节点 4 为例, 避开 V_i 标注) ----
    for x in (r[4] - dr / 2, r[4] + dr / 2):
        ax.annotate("", xy=(x, 0.66), xytext=(x, 1.18),
                    arrowprops=dict(arrowstyle="-|>", color=C["teal"], lw=0.8))
    ax.text(r[4] - dr / 2, 1.24, "$G_{i-\\frac{1}{2}}$", ha="center", fontsize=8,
            color=C["teal"])
    ax.text(r[4] + dr / 2, 1.24, "$G_{i+\\frac{1}{2}}$", ha="center", fontsize=8,
            color=C["teal"])

    # ---- 节点与标签 ----
    ax.plot(r, np.full(M + 1, 0.5), "o", ms=4.5, mfc="white", mec=GREY["ink"],
            mew=1.0, zorder=4)
    for i in range(5):
        ax.text(r[i], -0.22, f"$r_{i}$", ha="center", fontsize=8)
    ax.text(0.5 * (r[5] + r[6]), -0.22, "$\\cdots$", ha="center", fontsize=8,
            color=GREY["dark"])
    ax.text(r[M], -0.22, "$r_M$", ha="center", fontsize=8)

    # ---- 界面虚线与控制体标注 ----
    for x in (dr / 2, R - dr / 2):
        ax.plot([x, x], [0, 1], color=C["orange"], lw=0.7, ls=(0, (3, 2)), zorder=2)
    ax.text(dr / 2, -0.62, "$r_{\\frac{1}{2}}$", ha="center", fontsize=7.5,
            color=GREY["dark"])
    ax.text(R - dr / 2, -0.62, "$r_{M-\\frac{1}{2}}$", ha="center", fontsize=7.5,
            color=GREY["dark"])
    ax.annotate("$V_i=\\pi\\left(r_{i+\\frac{1}{2}}^2-r_{i-\\frac{1}{2}}^2\\right)$"
                "（单位轴长）",
                xy=(r[2], 1.0), xytext=(0.02, 1.58), textcoords="data",
                fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color=GREY["dark"], lw=0.7))

    # ---- 边界条件 (数据坐标, 分行锚定) ----
    ax.text(0.0, -1.05, "中心：$\\partial T/\\partial r=\\partial C/\\partial r=0$（对称）",
            fontsize=7.5, va="top")
    ax.text(R, -1.50, "表面：$-k\\,\\partial_r T=h\\,(T-T_\\infty)$，",
            fontsize=7.5, va="top", ha="right")
    ax.text(R, -1.92, "$-D\\,\\partial_r C=h_m\\,(C-C_\\infty)$",
            fontsize=7.5, va="top", ha="right")

    ax.annotate("", xy=(0, 0.5), xytext=(-0.10, 0.5),
                arrowprops=dict(arrowstyle="-|>", color=GREY["ink"], lw=0.9))
    ax.annotate("", xy=(R, 0.5), xytext=(R + 0.10, 0.5),
                arrowprops=dict(arrowstyle="<|-", color=GREY["ink"], lw=0.9))

    ax.set_xlim(-0.13, R + 0.13)
    ax.set_ylim(-2.50, 1.90)
    ax.axis("off")
    ax.set_title("(b) 一维径向求解域与节点式有限体积（图示 $M=8$）",
                 fontsize=8.5, pad=6)


def panel_fick(ax):
    """Fick 扩散示意: 浓度梯度驱动水分向表面输运并蒸发."""
    R = 2.0
    ax.add_patch(Rectangle((0, 0), R, 1.0, facecolor="#e8f1fa",
                           edgecolor=GREY["ink"], lw=1.0, zorder=1))
    r = np.linspace(0, R, 300)
    Cc = 2.55 - 1.05 / (1 + np.exp(-(r - 1.62) / 0.09))
    y = (Cc - 1.45) / 1.15
    ax.plot(r, y, color=C["teal"], lw=1.8, zorder=3)
    ax.text(0.42, 0.82, "$C(r)$", color=C["teal"], fontsize=9)
    ax.text(0.10, 0.22, "内部：$C\\approx C_0$", fontsize=7.5, color=GREY["dark"])
    for x in (1.15, 1.38, 1.61):
        ax.annotate("", xy=(x + 0.17, 0.60), xytext=(x, 0.60),
                    arrowprops=dict(arrowstyle="-|>", color=C["blue"], lw=1.0))
    ax.text(0.62, 0.70, "浓度梯度驱动扩散 $-D(C)\\,\\partial_rC$", fontsize=7.3,
            color=C["blue"])
    ax.plot([R, R], [0, 1], color=C["orange"], lw=1.0, ls=(0, (4, 2)), zorder=2)
    for x in (1.82, 2.02):
        ax.annotate("", xy=(x, 1.46), xytext=(x, 1.06),
                    arrowprops=dict(arrowstyle="-|>", color=C["orange"], lw=1.2,
                                    linestyle=(0, (3, 2))))
    ax.text(1.30, 1.60, "表面蒸发 $j=h_m\\,[C-C_\\infty]$", fontsize=7.3,
            color=C["orange"])
    ax.annotate("", xy=(R, -0.30), xytext=(0, -0.30),
                arrowprops=dict(arrowstyle="->", color=GREY["dark"], lw=0.8))
    ax.text(-0.06, -0.52, "$r=0$（中心）", fontsize=7.5)
    ax.text(R, -0.52, "$r=R$（表面）", fontsize=7.5, ha="center")
    ax.text(2.10, 0.42, "烘房\n$C_\\infty$", fontsize=7.5, color=GREY["dark"])
    ax.set_xlim(-0.40, 2.80)
    ax.set_ylim(-0.62, 1.92)
    ax.axis("off")
    ax.set_title("水分径向扩散示意", fontsize=8.5, pad=4)


def main():
    setup()
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.1), width_ratios=[1.12, 1.0])
    panel_a(axes[0])
    panel_b(axes[1])
    fig.subplots_adjust(wspace=0.10)
    save(fig, "fig_q1_schematic")

    # 单面板版本 (论文 5.1.2 / 5.1.3 / 5.1.4 分别引用)
    fig_a, ax_a = plt.subplots(figsize=(4.8, 3.0))
    panel_a(ax_a)
    fig_a.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.02)
    save(fig_a, "fig_q1_model")
    plt.close(fig_a)

    fig_c, ax_c = plt.subplots(figsize=(4.8, 2.7))
    panel_fick(ax_c)
    fig_c.subplots_adjust(left=0.02, right=0.98, top=0.88, bottom=0.04)
    save(fig_c, "fig_q1_fick")
    plt.close(fig_c)

    fig_b, ax_b = plt.subplots(figsize=(4.8, 3.0))
    panel_b(ax_b)
    fig_b.subplots_adjust(left=0.02, right=0.98, top=0.90, bottom=0.02)
    save(fig_b, "fig_q1_fvm")
    plt.close(fig_b)


if __name__ == "__main__":
    main()
