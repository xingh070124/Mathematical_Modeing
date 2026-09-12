# -*- coding: utf-8 -*-
r"""
图 1 物理建模示意图 (schematic-led composite) —— 三面板合并版.

核心结论 (figure contract): 药材烘干问题在"中截面对称 + 轴对称"下归结为
一维径向传热/传质抛物型方程组, 配中心对称条件与表面第三类(Robin)边界条件;
数值上用节点式有限体积离散, 通量在控制体界面上守恒.

面板 (合并原 fig_q1_model / fig_q1_fvm / fig_q1_fick 三张单面板图):
  (a) 圆柱几何 + 坐标 + 热风对流边界条件 (第三类换热/传质);
  (b) 一维径向求解域的节点式 FV 网格与控制体 (图示 M=8);
  (c) 水分径向扩散示意 (浓度梯度驱动 / 表面蒸发).

版式 (为什么不是 1x3 一行):
  (a) 用等比例坐标绘制 L=25 cm / R=2 cm 的圆柱, 数据窗口宽高比 = 41/15.2 = 2.70,
  即 (a) 的高度由它的宽度唯一决定; (b)(c) 的注释文字宽度则是硬下界
  ((b) 中心边界条件文本 1.407 in, (c) 扩散标注 1.318 in, 由
  src/_q1_scheme_layout_probe.py 实测). 三者并排时
  (a) 的宽度被压到 ~2.2 in, (b)(c) 各 ~1.1 in, 文字必然互相重叠.
  因此采用: 第 0 行 (a) 横贯全宽; 第 1 行 (b) 占两列、(c) 占一列.
  画布高度由 _calibrate() **自标定**到第 0 行恰好等于 (a) 等比例所需高度,
  既不纵向压缩 (a), 也不留无用的白边.

  字号: 面板内注释 7.2~9 pt, 标题 8.5 pt; SimHei 缺 U+2212, 字体回退链末尾追加
  DejaVu Sans (只影响缺失字形).

运行:  python src/q1_fig_schematic.py            # 只出合并图 fig_q1_scheme
       python src/q1_fig_schematic.py --legacy   # 另出旧的三张单面板图
输出:  paper/figures/fig_q1_scheme.pdf|.png + .alignment.json|.svg
"""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Ellipse, FancyArrowPatch, Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C, GREY, save, setup  # noqa: E402
from q1_fig_common import save_gated  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FIG_W = 7.4                 # 画布宽 (in); 高度由 _calibrate() 标定
MID_GAP = 0.7               # 中截面虚线的让位半宽 (data 单位), 见 panel_a
LBL_HALF = 1.7              # "中截面 z=0" 标签的让位半宽 (data 单位; 文字实测 39.8 pt
                            # = 3.13 data 单位, 取其半宽并留余量). 轴线与剖面线都必须
                            # 在该带内断开, 否则碰撞门判 text-stroke FAIL —— 白底 bbox
                            # 只在绘制上遮住线, 几何上折线仍穿过文字包围盒.


def panel_a(ax):
    """圆柱几何与边界条件. 版式: 上带=热风+热流入, 下带=质流出+尺寸标注."""
    L, R = 25.0, 2.0            # cm, 真实比例
    Re = 1.1                    # 端面椭圆半短轴 (透视)
    xc = L / 2                  # 中截面位置

    # ---- 圆柱体 ----
    ax.add_patch(Rectangle((0, -R), L, 2 * R, facecolor="#fdeedd",
                           edgecolor=GREY["ink"], lw=1.0, zorder=1))
    for x in np.arange(2.0, L, 2.4):          # 材质剖面线
        if (x + 1.0 > xc - LBL_HALF) and (x < xc + LBL_HALF):
            continue                          # 与标签带相交的斜线不画
        ax.plot([x, x + 1.0], [R, -R], color="#ead9c2", lw=0.5, zorder=1)
    ax.add_patch(Ellipse((0, 0), 2 * Re, 2 * R, facecolor="white",
                         edgecolor=GREY["ink"], lw=1.0, zorder=3))

    # ---- 轴线 z 与径向 r (在标签带内断开) ----
    ax.plot([-3.5, xc - LBL_HALF], [0, 0], color=GREY["dark"], lw=0.7,
            ls=(0, (6, 3, 1, 3)), zorder=2)
    ax.plot([xc + LBL_HALF, 29.0], [0, 0], color=GREY["dark"], lw=0.7,
            ls=(0, (6, 3, 1, 3)), zorder=2)
    ax.text(29.6, 0.05, "$z$", fontsize=9, color=GREY["dark"])
    ax.annotate("", xy=(25.8, R), xytext=(25.8, 0),
                arrowprops=dict(arrowstyle="-|>", color=GREY["ink"], lw=0.9),
                zorder=4)
    ax.text(26.3, 1.0, "$r$", fontsize=9)

    # ---- 中截面: 虚线在标签处断开 ----
    ax.plot([xc, xc], [-R, -MID_GAP], color=GREY["dark"], lw=0.8,
            ls=(0, (4, 2)), zorder=3)
    ax.plot([xc, xc], [MID_GAP, R], color=GREY["dark"], lw=0.8,
            ls=(0, (4, 2)), zorder=3)
    ax.text(xc, 0, "中截面 $z=0$", ha="center", va="center", fontsize=7.2,
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
    # 下标一律写成 i-1/2 而非 i-\frac{1}{2}: mathtext 的二级脚本缩放 0.49,
    # 7.5 pt 的 \frac 上下标只剩 3.675 pt, 低于字号门下限 (实测 FAIL), 且
    # \frac 的分子/分母文本框在 PDF 里互相重叠, 又被判 text-text FAIL.
    for x in (r[4] - dr / 2, r[4] + dr / 2):
        ax.annotate("", xy=(x, 1.08), xytext=(x, 0.62),
                    arrowprops=dict(arrowstyle="-|>", color=C["teal"], lw=0.8))
    ax.text(r[4] - dr / 2, 1.28, "$G_{i-1/2}$", ha="center", fontsize=8,
            color=C["teal"])
    ax.text(r[4] + dr / 2, 1.28, "$G_{i+1/2}$", ha="center", fontsize=8,
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
    ax.text(dr / 2, -0.62, "$r_{1/2}$", ha="center", fontsize=7.5,
            color=GREY["dark"])
    ax.text(R - dr / 2, -0.62, "$r_{M-1/2}$", ha="center", fontsize=7.5,
            color=GREY["dark"])
    ax.annotate("$V_i=\\pi\\left(r_{i+1/2}^2-r_{i-1/2}^2\\right)$"
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
    # "$C(r)$" 与扩散标注都必须在**曲线之上或之外**: 合并后面板变窄, 该文字 (1.29 in)
    # 在 data 坐标下宽 1.89 单位 (占 3.2 单轴宽的 59%), 原先的位置会被曲线下降段、
    # 蓝框右边线与蒸发箭头穿过 (碰撞门 3 处 text-stroke FAIL). 现改为:
    #   "$C(r)$" 落在曲线平台之上的左上空带; 扩散标注落在蓝框之上的空带, 右端止于
    #   1.73 (蒸发箭头起于 1.82), 左端 -0.16 仍在 xlim 内.
    ax.text(0.02, 1.58, "$C(r)$", color=C["teal"], fontsize=9)
    ax.text(0.10, 0.22, "内部：$C\\approx C_0$", fontsize=7.5, color=GREY["dark"])
    for x in (1.15, 1.38, 1.61):
        ax.annotate("", xy=(x + 0.17, 0.44), xytext=(x, 0.44),
                    arrowprops=dict(arrowstyle="-|>", color=C["blue"], lw=1.0))
    ax.text(-0.16, 1.12, "浓度梯度驱动扩散 $-D(C)\\,\\partial_rC$", fontsize=7.3,
            color=C["blue"])
    ax.plot([R, R], [0, 1], color=C["orange"], lw=1.0, ls=(0, (4, 2)), zorder=2)
    for x in (1.82, 2.02):
        ax.annotate("", xy=(x, 1.46), xytext=(x, 1.06),
                    arrowprops=dict(arrowstyle="-|>", color=C["orange"], lw=1.2,
                                    linestyle=(0, (3, 2))))
    # 该标注原锚在 x=1.30; 合并后面板变窄, 1.30+1.08 in 会溢出坐标区右边界,
    # 左移到 1.12 使其落在 2.80 的 xlim 内 (内容不变, 仅重排).
    ax.text(1.12, 1.60, "表面蒸发 $j=h_m\\,[C-C_\\infty]$", fontsize=7.3,
            color=C["orange"])
    ax.annotate("", xy=(R, -0.30), xytext=(0, -0.30),
                arrowprops=dict(arrowstyle="->", color=GREY["dark"], lw=0.8))
    ax.text(-0.06, -0.52, "$r=0$（中心）", fontsize=7.5)
    ax.text(R, -0.52, "$r=R$（表面）", fontsize=7.5, ha="center")
    # 多行文字在 va='baseline' 下按**最后一行**对齐, 故 "烘房" 实际落在锚点之上约
    # 一行高处 (原锚 0.42 时第一行到 0.68, 正好压住扩散标注) -> 锚点下移到 0.20.
    ax.text(2.10, 0.20, "烘房\n$C_\\infty$", fontsize=7.5, color=GREY["dark"])
    ax.set_xlim(-0.40, 2.80)
    ax.set_ylim(-0.62, 1.92)
    ax.axis("off")
    ax.set_title("(c) 水分径向扩散示意", fontsize=8.5, pad=4)


def _calibrate(fig, ax_ref, tol_pt=0.5):
    """把画布高度标定到参考子图所在行恰好等于该子图等比例绘制所需高度.

    高度是画布高度的定比, 故一次线性标定即精确. 标定后 (a) 不发生纵向压缩,
    其左右边也不被 aspect 调整移动 (对齐门的 left/right 共享边界检查依赖这一点).
    """
    fig.canvas.draw()
    cell = ax_ref.get_position(original=True)
    x0, x1 = ax_ref.get_xlim()
    y0, y1 = ax_ref.get_ylim()
    aspect = (x1 - x0) / (y1 - y0)
    w_in, h_in = fig.get_size_inches()
    need_in = cell.width * w_in / aspect
    fig.set_size_inches(w_in, need_in / cell.height)
    fig.canvas.draw()

    w_in, h_in = fig.get_size_inches()
    p0 = ax_ref.get_position(original=True)
    p1 = ax_ref.get_position(original=False)
    dx_pt = (abs(p1.x0 - p0.x0) + abs(p1.x1 - p0.x1)) * w_in * 72
    dy_pt = (abs(p1.y0 - p0.y0) + abs(p1.y1 - p0.y1)) * h_in * 72
    if max(dx_pt, dy_pt) > tol_pt:
        raise AssertionError(
            f"自标定失败: (a) 仍被 aspect 调整 (dx={dx_pt:.2f} pt, dy={dy_pt:.2f} pt)")
    return h_in, need_in


def build_scheme():
    """三面板合并图: 第 0 行 (a) 横贯全宽; 第 1 行 (b) 两列 + (c) 一列."""
    fig = plt.figure(figsize=(FIG_W, 5.6))
    gs = fig.add_gridspec(2, 3, left=0.010, right=0.990, bottom=0.030, top=0.905,
                          width_ratios=[1.0, 1.0, 1.0], height_ratios=[1.0, 0.707],
                          hspace=0.22, wspace=0.16)
    ax_a = fig.add_subplot(gs[0, :])
    ax_b = fig.add_subplot(gs[1, 0:2])
    ax_c = fig.add_subplot(gs[1, 2])
    for ax, gid in ((ax_a, "a"), (ax_b, "b"), (ax_c, "c")):
        ax.set_gid(gid)

    panel_a(ax_a)
    panel_b(ax_b)
    panel_fick(ax_c)

    h_in, need_in = _calibrate(fig, ax_a)
    print(f"  [自标定] 画布 {FIG_W:.2f} x {h_in:.4f} in; 第 0 行高度 = "
          f"{need_in:.4f} in (等比例所需), (a) 未发生纵向压缩")
    for ax in (ax_a, ax_b, ax_c):
        p = ax.get_position(original=False)
        print(f"  [面板] ({ax.get_gid()}) 宽 {p.width * FIG_W:.3f} in, "
              f"高 {p.height * h_in:.3f} in, x0={p.x0:.4f}, y0={p.y0:.4f}")
    return fig


def legacy_figures():
    """旧的三张单面板图 (论文已不再引用; --legacy 时才重绘)."""
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

    fig_s, axes = plt.subplots(1, 2, figsize=(7.1, 3.1), width_ratios=[1.12, 1.0])
    panel_a(axes[0])
    panel_b(axes[1])
    fig_s.subplots_adjust(wspace=0.10)
    save(fig_s, "fig_q1_schematic")
    plt.close(fig_s)


def main(argv=None):
    ap = argparse.ArgumentParser(description="问题一三面板合并示意图")
    ap.add_argument("--legacy", action="store_true",
                    help="同时重绘旧的三张单面板图 (paper 已不再引用)")
    args = ap.parse_args(argv)

    setup()
    matplotlib.rcParams["font.sans-serif"] = list(
        matplotlib.rcParams["font.sans-serif"]) + ["DejaVu Sans"]
    print(f"字体回退链: {matplotlib.rcParams['font.sans-serif']}")

    fig = build_scheme()
    save_gated(fig, "fig_q1_scheme")
    plt.close(fig)

    if args.legacy:
        legacy_figures()


if __name__ == "__main__":
    main()
