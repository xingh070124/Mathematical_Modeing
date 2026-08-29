# -*- coding: utf-8 -*-
"""
2024 CUMCM A 题 —— 问题 4 图表（Nature 风格：Okabe-Ito 色板、去顶右框线、300 dpi）

  fig_问题四S形调头示意.png   —— S 形调头曲线几何示意图（主图）
  fig_问题四曲线族与优化.png —— (a) 两弧族不变性  (b) 弧-线-弧 L*(R1) 极小化
  fig_问题四全龙构型.png     —— 全景 + 五个关键时刻龙身构型快照
  fig_问题四把手速度.png     —— (a) 速度-时间曲线  (b) 速度-把手编号曲线
"""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

from problem4_solve import (B, TH_A, E, F, tE, nE, O1_0, O2_0, T0, R1_0, R2_0,
                            L0, L1_0, curve_point, config_at, positions,
                            velocities, spiral_point, DELTA, nE as N_E)

# ---------------- 全局风格（nature-figure 规范） ----------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "figures")
os.makedirs(FIGDIR, exist_ok=True)

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial"],
    "axes.unicode_minus": False,
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.labelsize": 8,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.frameon": False,
    "legend.fontsize": 7,
    "lines.linewidth": 1.2,
    "savefig.dpi": 300,
})

# Okabe-Ito
C_BLUE, C_ORANGE, C_GREEN = "#0072B2", "#E69F00", "#009E73"
C_VERM, C_SKY, C_PURPLE, C_GRAY = "#D55E00", "#56B4E9", "#CC79A7", "#7F7F7F"
C_DARK = "#2B2B2B"

with open(os.path.join(ROOT, "src", "problem4_results.json"), encoding="utf-8") as f:
    RES = json.load(f)


def spiral_pts(th_lo, th_hi, n=800):
    th = np.linspace(th_lo, th_hi, n)
    P = np.array([spiral_point(t) for t in th])
    return P


def draw_setup(ax, spiral_lo=TH_A, spiral_hi=TH_A + 4 * np.pi, show_spiral=True):
    """调头空间 + 双螺线 + 基线 S 曲线."""
    if show_spiral:
        Pin = spiral_pts(spiral_lo, spiral_hi)
        ax.plot(Pin[:, 0], Pin[:, 1], color=C_GRAY, lw=0.6, alpha=0.55, zorder=1)
        ax.plot(-Pin[:, 0], -Pin[:, 1], color=C_GRAY, lw=0.6, alpha=0.55,
                ls=(0, (4, 2)), zorder=1)
    circ = Circle((0, 0), 4.5, fill=False, edgecolor=C_DARK, lw=0.9,
                  ls=(0, (5, 3)), zorder=2)
    ax.add_patch(circ)
    # 基线 S 曲线
    u = np.linspace(0, L0, 600)
    S = np.array([curve_point(x) for x in u])
    ax.plot(S[:, 0], S[:, 1], color=C_BLUE, lw=2.2, zorder=4, solid_capstyle="round")
    return S


def panel_label(ax, s, dx=-0.02, dy=1.04):
    ax.text(dx, dy, s, transform=ax.transAxes, fontsize=9, fontweight="bold",
            va="bottom", ha="right")


# ================================================================
# 图 1：S 形调头曲线几何示意（主图）
# ================================================================
def fig_schematic():
    fig, ax = plt.subplots(figsize=(4.8, 4.8))
    draw_setup(ax, spiral_hi=TH_A + 5 * np.pi)
    ax.set_aspect("equal")

    # 圆心与切点
    ax.plot(*O1_0, marker="o", ms=3.5, color=C_VERM, zorder=6)
    ax.plot(*O2_0, marker="o", ms=3.5, color=C_GREEN, zorder=6)
    ax.plot([O1_0[0], T0[0]], [O1_0[1], T0[1]], color=C_VERM, lw=0.9,
            ls=":", zorder=3)
    ax.plot([O2_0[0], T0[0]], [O2_0[1], T0[1]], color=C_GREEN, lw=0.9,
            ls=":", zorder=3)
    ax.plot(*T0, marker="o", ms=4, color=C_DARK, zorder=6)
    for P, name, dxy in ((E, "E", (-0.85, -0.75)), (F, "F", (0.35, 0.35)),
                         (T0, "T", (0.18, -0.55))):
        ax.plot(*P, marker="s", ms=3.6, color=C_DARK, zorder=6)
        ax.annotate(name, P, xytext=(P[0] + dxy[0], P[1] + dxy[1]),
                    fontsize=8.5, fontweight="bold", color=C_DARK)
    ax.annotate(f"O1", O1_0, xytext=(O1_0[0] - 0.42, O1_0[1] - 0.32),
                fontsize=8, color=C_VERM)
    ax.annotate(f"O2", O2_0, xytext=(O2_0[0] + 0.16, O2_0[1] + 0.14),
                fontsize=8, color=C_GREEN)

    # 行进方向箭头
    for P, c in ((E, C_VERM), (F, C_GREEN)):
        arr = FancyArrowPatch(P, P + 1.15 * tE, arrowstyle="-|>",
                              mutation_scale=11, color=c, lw=1.4, zorder=7)
        ax.add_patch(arr)

    # 半径标注
    mid1 = 0.5 * (np.array(O1_0) + T0) + np.array([-0.28, 0.42])
    ax.text(*mid1, f"$R_1$={R1_0:.4f} m", fontsize=7.2, color=C_VERM,
            rotation=52, ha="center")
    mid2 = 0.5 * (np.array(O2_0) + T0) + np.array([0.42, -0.30])
    ax.text(*mid2, f"$R_2$={R2_0:.4f} m", fontsize=7.2, color=C_GREEN,
            rotation=52, ha="center")

    # 调头空间标注（置于圆内左上空白区）
    ax.text(-2.5, 3.2, "调头空间\n$r\\leq 4.5$ m", fontsize=8, color=C_DARK,
            ha="center", va="center")
    # 螺线标注（实线=盘入，虚线=盘出；分别标在各自孤段旁）
    ax.annotate("盘入螺线", xy=(-1.9, -6.6), xytext=(-7.6, -5.2),
                fontsize=7.5, color=C_GRAY,
                arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=0.6))
    ax.annotate("盘出螺线（中心对称）", xy=(4.15, 5.9), xytext=(3.1, 8.6),
                fontsize=7.5, color=C_GRAY,
                arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=0.6))

    # 信息框
    info = (f"$R_1=2R_2$：$R_1$={R1_0:.4f} m, $R_2$={R2_0:.4f} m\n"
            f"扫角 $\\gamma$={np.degrees(RES['gamma_rad']):.2f}°（两弧相等）\n"
            f"调头曲线长 $L_0$={L0:.4f} m")
    ax.text(0.02, 0.02, info, transform=ax.transAxes, fontsize=7.4, va="bottom",
            bbox=dict(boxstyle="round,pad=0.45", fc="white", ec="#CCCCCC", lw=0.7))

    ax.set_xlim(-10.2, 10.2)
    ax.set_ylim(-10.2, 10.2)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title("问题四：S 形调头曲线几何（切于盘入/盘出螺线，R1 = 2R2）",
                 fontsize=8.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题四S形调头示意.png"))
    plt.close(fig)
    print("[图1] fig_问题四S形调头示意.png")


# ================================================================
# 图 2：(a) 两弧族不变性  (b) 弧-线-弧极小化
# ================================================================
def alt_L_of_R1(R1, n_a=400):
    """给定 R1 扫 alpha 返回该档最优 (L, alpha, R2, ell)（几何约束同求解脚本）."""
    best = None
    for ag in np.linspace(0.3, 3.0, n_a):
        T1 = E + R1 * np.sin(ag) * tE - R1 * (1 - np.cos(ag)) * nE
        mdir = np.array([np.cos(-ag) * tE[0] - np.sin(-ag) * tE[1],
                         np.sin(-ag) * tE[0] + np.cos(-ag) * tE[1]])
        nm = np.array([-mdir[1], mdir[0]])
        rhs = F - T1
        c = 1 - np.cos(ag)
        if abs(c) < 1e-9:
            continue
        R2 = np.dot(rhs, nm) / c
        if R2 < 0.825 or R2 > 4.4:
            continue
        el = np.dot(rhs, mdir) - R2 * np.sin(ag)
        if el < 1e-6:
            continue
        O1 = E - R1 * nE
        O2 = T1 + el * mdir + R2 * nm
        s1 = np.linspace(0, 1, 200)
        pE = np.arctan2(*(E - O1)[::-1])
        a1 = O1[None] + R1 * np.stack(
            [np.cos(pE - s1 * ag), np.sin(pE - s1 * ag)], 1)
        T2 = T1 + el * mdir
        ln = T1[None] + s1[:, None] * (el * mdir)[None]
        p2s = np.arctan2(*(T2 - O2)[::-1])
        a2 = O2[None] + R2 * np.stack(
            [np.cos(p2s + s1 * ag), np.sin(p2s + s1 * ag)], 1)
        rmax = max(np.max(np.linalg.norm(a1, axis=1)),
                   np.max(np.linalg.norm(ln, axis=1)),
                   np.max(np.linalg.norm(a2, axis=1)))
        if rmax > 4.5 + 1e-9:
            continue
        L = (R1 + R2) * ag + el
        if best is None or L < best[0]:
            best = (L, ag, R2, el)
    return best


def fig_family_opt():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.1))

    # ---- (a) 不变性：不同比例的两弧族 ----
    draw_setup(ax1, spiral_hi=TH_A + 3 * np.pi)
    ax1.set_aspect("equal")
    for k, c, ls in ((0.5, C_SKY, "-"), (1.0, C_GREEN, "-"), (5.0, C_PURPLE, "-")):
        S = -np.dot(DELTA, DELTA) / (2.0 * np.dot(DELTA, nE))
        r2 = S / (k + 1.0)
        r1 = k * r2
        O1 = E - r1 * nE
        O2 = F + r2 * nE
        m = (O2 - O1) / np.linalg.norm(O2 - O1)
        T = O1 + r1 * m
        pE = np.arctan2(*(E - O1)[::-1])
        pT1 = np.arctan2(*m[::-1])
        pT2 = np.arctan2(*(T - O2)[::-1])
        pF = np.arctan2(*(F - O2)[::-1])
        g1 = (pE - pT1) % (2 * np.pi)
        g2 = (pF - pT2) % (2 * np.pi)
        s1 = np.linspace(0, 1, 400)
        a1 = O1[None] + r1 * np.stack([np.cos(pE - s1 * g1),
                                       np.sin(pE - s1 * g1)], 1)
        a2 = O2[None] + r2 * np.stack([np.cos(pT2 + s1 * g2),
                                       np.sin(pT2 + s1 * g2)], 1)
        ax1.plot(a1[:, 0], a1[:, 1], color=c, lw=1.3, ls=ls,
                 label=f"k={k:g}")
        ax1.plot(a2[:, 0], a2[:, 1], color=c, lw=1.3, ls=ls)
    ax1.plot([], [], color=C_BLUE, lw=2.2, label="k=2（题目基线）")
    ax1.legend(loc="upper left", fontsize=6.6, handlelength=1.4)
    ax1.set_xlim(-7.2, 7.2)
    ax1.set_ylim(-7.2, 7.2)
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("(a) 两弧族：半径比例可变，长度不变")
    panel_label(ax1, "a")

    # ---- (b) 弧-线-弧 L*(R1) ----
    R1s = np.linspace(0.825, 3.2, 40)
    Ls, ok_x, ok_y = [], [], []
    for r1 in R1s:
        b = alt_L_of_R1(r1, n_a=260)
        if b is None:
            Ls.append(np.nan)
        else:
            Ls.append(b[0])
            ok_x.append(r1)
            ok_y.append(b[0])
    ax2.plot(ok_x, ok_y, color=C_BLUE, lw=1.6)
    ax2.axhline(L0, color=C_GRAY, lw=1.0, ls=(0, (5, 3)))
    ax2.text(2.55, L0 + 0.13, f"两弧基线 $L_0$={L0:.3f} m", fontsize=7.2,
             color=C_GRAY)
    opt = RES["alt_opt"]
    ax2.plot(opt["R1"], opt["L"], marker="*", ms=11, color=C_VERM, zorder=6)
    ax2.annotate(f"最优 $L^*$={opt['L']:.3f} m\n"
                 f"($-26.11\\%$, $R_1\\to D$/2)",
                 (opt["R1"], opt["L"]), xytext=(1.35, 9.62),
                 fontsize=7.4, color=C_VERM,
                 arrowprops=dict(arrowstyle="-", color=C_VERM, lw=0.8))
    ax2.axvline(0.825, color=C_VERM, lw=0.8, ls=":")
    ax2.text(0.86, 12.9, "可跟随性下界\n$R\\geq D_{\\rm body}/2$", fontsize=6.8,
             color=C_VERM)
    ax2.set_xlabel("弧 1 半径 $R_1$ (m)")
    ax2.set_ylabel("最优长度 $L^{*}(R_1)$ (m)")
    ax2.set_title("(b) 弧–线–弧结构：长度可缩短 26.11%")
    ax2.set_ylim(8.8, 13.9)
    panel_label(ax2, "b")

    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题四曲线族与优化.png"))
    plt.close(fig)
    print("[图2] fig_问题四曲线族与优化.png")


# ================================================================
# 图 3：全景 + 关键时刻构型快照
# ================================================================
def _dragon(ax, t, highlight_pair=None):
    us = config_at(float(t))
    Ps = positions(us)
    # 板凳矩形（浅填充）+ 把手折线（细描）
    from problem4_solve import bench_rect, rect_corners
    for i in range(223):
        hit = highlight_pair is not None and (i + 1) in highlight_pair
        c = C_ORANGE if hit else "#B9CDDC"
        poly = rect_corners(bench_rect(i, Ps))
        ax.fill(poly[:, 0], poly[:, 1], color=c,
                alpha=0.95 if hit else 0.35, lw=0, zorder=4)
    ax.plot(Ps[:, 0], Ps[:, 1], color=C_DARK, lw=0.55, zorder=5,
            solid_capstyle="round")
    ax.plot(*Ps[0], marker="o", ms=4, color=C_VERM, zorder=7)
    ax.plot(*Ps[223], marker="o", ms=3.4, color=C_GREEN, zorder=7)
    return Ps


def fig_snapshots():
    fig, axes = plt.subplots(2, 3, figsize=(7.2, 5.0))
    # (a) 全景 t=0
    ax = axes[0, 0]
    Pin = spiral_pts(TH_A, TH_A + 15 * np.pi, 3000)
    ax.plot(Pin[:, 0], Pin[:, 1], color=C_GRAY, lw=0.4, alpha=0.5)
    us = config_at(0.0)
    Ps = positions(us)
    ax.plot(Ps[:, 0], Ps[:, 1], color=C_DARK, lw=0.9)
    ax.plot(*Ps[0], marker="o", ms=3.5, color=C_VERM)
    ax.plot(*Ps[223], marker="o", ms=3, color=C_GREEN)
    circ = Circle((0, 0), 4.5, fill=False, edgecolor=C_DARK, lw=0.8,
                  ls=(0, (5, 3)))
    ax.add_patch(circ)
    u = np.linspace(0, L0, 300)
    S = np.array([curve_point(x) for x in u])
    ax.plot(S[:, 0], S[:, 1], color=C_BLUE, lw=1.6)
    ax.set_xlim(-17.5, 17.5)
    ax.set_ylim(-17.5, 17.5)
    ax.set_aspect("equal")
    ax.set_title("全景 t = 0 s（龙头到达边界 E）")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    panel_label(ax, "a")

    # (b-f) 时刻快照（调头区放大）
    snaps = [(-50, "b", None), (0, "c", None), (29.95, "d", (1, 17)),
             (50, "e", None), (100, "f", None)]
    for t, lab, hp in snaps:
        ax = axes[lab2idx(lab)]
        draw_setup(ax, spiral_hi=TH_A + 2.6 * np.pi)
        _dragon(ax, t, highlight_pair=hp)
        if hp:
            ax.annotate(f"最小间隙对 ({hp[0]},{hp[1]})，gap = 0.406 m",
                        xy=(-3.7, -2.7), xytext=(-7.6, 6.6), fontsize=6.8,
                        color=C_ORANGE,
                        arrowprops=dict(arrowstyle="-", color=C_ORANGE, lw=0.7),
                        bbox=dict(boxstyle="round,pad=0.3", fc="white",
                                  ec=C_ORANGE, lw=0.6, alpha=0.9))
        ax.set_xlim(-8, 8)
        ax.set_ylim(-8, 8)
        ax.set_aspect("equal")
        tt = int(t) if float(t).is_integer() else t
        ax.set_title(f"t = {tt} s")
        ax.set_xlabel("x (m)")
        ax.set_ylabel("y (m)")
        panel_label(ax, lab)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题四全龙构型.png"))
    plt.close(fig)
    print("[图3] fig_问题四全龙构型.png")


def lab2idx(lab):
    return {"a": (0, 0), "b": (0, 1), "c": (0, 2), "d": (1, 0), "e": (1, 1),
            "f": (1, 2)}[lab]


# ================================================================
# 图 4：速度分析
# ================================================================
def fig_speeds():
    times = np.arange(-100, 101)
    sel = [0, 1, 50, 100, 150, 200, 223]
    names = ["龙头(1)", "第1节(2)", "第51节(52)", "第101节(102)", "第151节(152)",
             "第201节(202)", "龙尾后(224)"]
    colors = [C_VERM, C_ORANGE, C_SKY, C_GREEN, C_PURPLE, C_GRAY, C_DARK]
    V = np.empty((len(times), 224))
    for j, t in enumerate(times):
        V[j] = velocities(config_at(float(t)))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))

    # (a) 速度-时间
    for i, nm, c in zip(sel, names, colors):
        ax1.plot(times, V[:, i], color=c, lw=1.0 if i else 1.5, label=nm)
    ax1.axvline(0, color="#BBBBBB", lw=0.7, ls=":")
    ax1.text(1.5, 1.405, "t=0 开始调头", fontsize=6.6, color="#999999",
             rotation=90, va="top")
    ax1.set_xlabel("t (s)")
    ax1.set_ylabel("把手速度 (m/s)")
    ax1.set_title("(a) 典型把手速度随时间变化")
    ax1.legend(loc="lower left", fontsize=6.2, ncol=2, handlelength=1.3,
               columnspacing=0.9)
    ax1.set_ylim(0.90, 1.46)
    panel_label(ax1, "a")

    # (b) 速度-编号
    idx = np.arange(1, 225)
    for t, c in ((-50, C_SKY), (0, C_GREEN), (50, C_ORANGE), (100, C_VERM)):
        ax2.plot(idx, V[t + 100], color=c, lw=1.1, label=f"t = {t} s")
    ax2.set_xlabel("把手编号")
    ax2.set_ylabel("把手速度 (m/s)")
    ax2.set_title("(b) 同一时刻沿龙身的速度分布")
    ax2.legend(loc="lower left", fontsize=6.6, handlelength=1.3)
    panel_label(ax2, "b")

    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题四把手速度.png"))
    plt.close(fig)
    print("[图4] fig_问题四把手速度.png")


if __name__ == "__main__":
    fig_schematic()
    fig_family_opt()
    fig_snapshots()
    fig_speeds()
    print("全部问题四图表已生成 ->", FIGDIR)
