# -*- coding: utf-8 -*-
"""
2024 CUMCM A 题 —— 问题 5 图表（Nature 风格：Okabe-Ito 色板、去顶右框线、300 dpi）

  fig_问题五速度传递机理.png —— (a) 跨缝放大几何示意  (b) 峰值构型弦切角分布
  fig_问题五速度比场.png   —— (a) 比场热力图 + 事件线  (b) 全域 max ρ 与搜索域
  fig_问题五三模型收敛.png —— (a) 峰窗三模型对比 + 认证区间  (b) 模型 A 网格收敛
  fig_问题五临界构型.png   —— 峰值时刻局部构型（板凳矩形 + 速度箭头）
  fig_问题五结构权衡.png   —— (a) 两条调头曲线  (b) 长度-速度权衡

依赖：src/problem5_results.json（由 problem5_solve.py 生成）。
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
from matplotlib.patches import Circle, FancyArrowPatch, Arc

# ---------------- 几何（自包含，与 problem4/5 求解脚本一致） ----------------
PITCH = 1.7
B = PITCH / (2 * np.pi)
R_SPACE = 4.5
HEAD_L, BODY_L = 3.41, 2.20
HOLE_OFF = 0.275
D_HEAD = HEAD_L - 2 * HOLE_OFF
D_BODY = BODY_L - 2 * HOLE_OFF
D_ALL = [D_HEAD] + [D_BODY] * 222
N_H = 224
TH_A = R_SPACE / B


def arc_len(th):
    return 0.5 * B * (th * np.hypot(th, 1.0) + np.arcsinh(th))


def d_arc_len(th):
    return B * np.hypot(th, 1.0)


S_A = arc_len(TH_A)


def spiral_point(th):
    r = B * th
    return np.array([r * np.cos(th), r * np.sin(th)])


def spiral_dpoint(th):
    return B * np.array([np.cos(th) - th * np.sin(th),
                         np.sin(th) + th * np.cos(th)])


def theta_of_arc(s):
    th = np.sqrt(2.0 * s / B) + 1e-9
    for _ in range(60):
        f = arc_len(th) - s
        if abs(f) < 1e-13:
            break
        th -= f / d_arc_len(th)
        if th <= 0:
            th = 1e-9
    return th


def rot90(v):
    return np.array([-v[1], v[0]])


E = spiral_point(TH_A)
tE = -spiral_dpoint(TH_A) / np.linalg.norm(spiral_dpoint(TH_A))
nE = rot90(tE)
F = -E
S_STAR = -np.dot(F - E, F - E) / (2.0 * np.dot(F - E, nE))
R1_0, R2_0 = 2.0 / 3.0 * S_STAR, 1.0 / 3.0 * S_STAR
O1_0 = E - R1_0 * nE
O2_0 = F + R2_0 * nE
m0 = (O2_0 - O1_0) / np.linalg.norm(O2_0 - O1_0)
T0 = O1_0 + R1_0 * m0
phi_E0 = np.arctan2(*(E - O1_0)[::-1])
phi_T20 = np.arctan2(*(T0 - O2_0)[::-1])
phi_F0 = np.arctan2(*(F - O2_0)[::-1])
L1_0 = R1_0 * ((phi_E0 - np.arctan2(*m0[::-1])) % (2 * np.pi))
L_C = L1_0 + R2_0 * ((phi_F0 - phi_T20) % (2 * np.pi))


def curve_point(u):
    if u < 0:
        return spiral_point(theta_of_arc(S_A - u))
    if u <= L1_0:
        phi = phi_E0 - u / R1_0
        return O1_0 + R1_0 * np.array([np.cos(phi), np.sin(phi)])
    if u <= L_C:
        phi = phi_T20 + (u - L1_0) / R2_0
        return O2_0 + R2_0 * np.array([np.cos(phi), np.sin(phi)])
    return -spiral_point(theta_of_arc(S_A + (u - L_C)))


def curve_tangent(u):
    if u < 0:
        th = theta_of_arc(S_A - u)
        v = spiral_dpoint(th)
        return -v / np.linalg.norm(v)
    if u <= L1_0:
        phi = phi_E0 - u / R1_0
        return np.array([np.sin(phi), -np.cos(phi)])
    if u <= L_C:
        phi = phi_T20 + (u - L1_0) / R2_0
        return np.array([-np.sin(phi), np.cos(phi)])
    th = theta_of_arc(S_A + (u - L_C))
    v = -spiral_dpoint(th)
    return v / np.linalg.norm(v)


def config_at(t):
    from scipy.optimize import brentq
    us = np.empty(N_H)
    us[0] = t
    for i in range(223):
        di = D_ALL[i]
        P = curve_point(us[i])
        f = lambda dl: np.linalg.norm(curve_point(us[i] - dl) - P) - di
        us[i + 1] = us[i] - brentq(f, 0.4 * di, 2.6 * di, xtol=1e-12)
    return us


def positions(us):
    return np.array([curve_point(u) for u in us])


def velocities(us):
    Ps = positions(us)
    v = np.empty(N_H)
    v[0] = 1.0
    for i in range(223):
        e = Ps[i + 1] - Ps[i]
        e = e / np.linalg.norm(e)
        v[i + 1] = v[i] * np.dot(curve_tangent(us[i]), e) / \
            np.dot(curve_tangent(us[i + 1]), e)
    return v


# ---------------- 风格 ----------------
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

C_BLUE, C_ORANGE, C_GREEN = "#0072B2", "#E69F00", "#009E73"
C_VERM, C_SKY, C_PURPLE, C_GRAY = "#D55E00", "#56B4E9", "#CC79A7", "#7F7F7F"
C_DARK = "#2B2B2B"

with open(os.path.join(ROOT, "src", "problem5_results.json"), encoding="utf-8") as f:
    RES = json.load(f)

V_STAR = RES["v_star"]
R_B = RES["R_max"]["B"]
U1_PK = RES["peak"]["u1"]
H_PK = RES["peak"]["handles"]


def seg_color(u):
    """复合曲线分段配色：盘入螺线-绿、弧1-蓝、弧2-橙、盘出螺线-紫."""
    if u < 0:
        return C_GREEN
    if u <= L1_0:
        return C_BLUE
    if u <= L_C:
        return C_ORANGE
    return C_PURPLE


def plot_curve_seg(ax, u_lo, u_hi, n=400, **kw):
    uu = np.linspace(u_lo, u_hi, n)
    P = np.array([curve_point(u) for u in uu])
    ax.plot(P[:, 0], P[:, 1], **kw)
    return P


# ================================================================
# 图 1  速度传递机理
# ================================================================
def fig_mechanism():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.1),
                                   gridspec_kw={"width_ratios": [1, 1.25]})
    us_full = config_at(U1_PK)
    Ps = positions(us_full)

    # ---- (a) 几何示意：峰窗局部（聚焦跨 F 缝） ----
    plot_curve_seg(ax1, 6.8, 15.8, n=900, color=C_GRAY, lw=1.0, zorder=1)
    for lo, hi, c in [(6.8, L1_0, C_BLUE), (L1_0, L_C, C_ORANGE),
                      (L_C, 15.8, C_PURPLE)]:
        plot_curve_seg(ax1, lo, hi, n=300, color=c, lw=2.2, zorder=2)

    def ang_arc(ax, P, d1, d2, r, color, label, lab_scale=1.45):
        """在 P 处画 d1→d2 的角弧并标注（取劣角）."""
        t1 = np.degrees(np.arctan2(d1[1], d1[0])) % 360.0
        t2 = np.degrees(np.arctan2(d2[1], d2[0])) % 360.0
        span = (t2 - t1) % 360.0
        if span > 180.0:
            t1, span = t2, 360.0 - span
        ax.add_patch(Arc(P, 2 * r, 2 * r, angle=0, theta1=t1, theta2=t1 + span,
                         color=color, lw=1.3, zorder=6))
        mid = np.radians(t1 + span / 2)
        ax.annotate(label, P + lab_scale * r * np.array([np.cos(mid), np.sin(mid)]),
                    fontsize=9.5, color=color, ha="center", va="center",
                    fontweight="bold", zorder=7)

    # 把手 1-4 与弦
    for i in range(4):
        ax1.plot(*Ps[i], "o", ms=5, color=seg_color(us_full[i]),
                 mec="white", mew=0.6, zorder=5)
        ax1.annotate(str(i + 1), Ps[i], textcoords="offset points",
                     xytext=(5, 4), fontsize=8, color=C_DARK, zorder=7)
    for i in range(3):
        ax1.plot([Ps[i][0], Ps[i + 1][0]], [Ps[i][1], Ps[i + 1][1]],
                 color=C_DARK, lw=1.0, zorder=3)
    # 弦 1 加粗 + 前向弦方向
    e1 = Ps[0] - Ps[1]
    e1 /= np.linalg.norm(e1)
    ax1.add_patch(FancyArrowPatch(Ps[1], Ps[1] + 1.5 * e1, arrowstyle="-|>",
                                  mutation_scale=9, color=C_DARK, lw=1.4,
                                  zorder=4))
    # 把手 1、2 切向箭头 + 弦切角 α₁（把手 1）、β₁（把手 2）
    for i, ang_lab, col in ((0, r"$\alpha_1$", C_BLUE), (1, r"$\beta_1$", C_ORANGE)):
        tau = curve_tangent(us_full[i])
        ax1.add_patch(FancyArrowPatch(Ps[i], Ps[i] + 1.5 * tau,
                                      arrowstyle="-|>", mutation_scale=9,
                                      color=col, lw=1.4, zorder=4))
        ang_arc(ax1, Ps[i], tau, e1, 0.85, C_VERM, ang_lab)
    # 缝标记
    for u_s, lab, dxy in ((L1_0, "$T$", (-10, 4)), (L_C, "$F$", (-2, 7))):
        P_s = curve_point(u_s)
        ax1.plot(*P_s, "s", ms=4.5, color=C_DARK, zorder=5)
        ax1.annotate(lab, P_s, textcoords="offset points", xytext=dxy,
                     fontsize=9, color=C_DARK)
    fF = RES["decomposition"]["f_F_cross_F"]
    fT = RES["decomposition"]["f_T_cross_T"]
    ax1.annotate(f"跨$F$缝: $\\cos\\alpha_1/\\cos\\beta_1={fF:.4f}$\n"
                 f"跨$T$缝: 因子 $={fT:.4f}$\n同弧内: $=1$（恒速）",
                 xy=(0.02, 0.02), xycoords="axes fraction", va="bottom",
                 fontsize=7, color=C_DARK,
                 bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=C_GRAY,
                           lw=0.6, alpha=0.9))
    ax1.set_aspect("equal")
    ax1.set_title("(a) 跨缝放大的弦切角几何（峰值构型）", fontsize=8)
    ax1.axis("off")

    # ---- (b) 峰值构型弦切角沿弦编号 ----
    alphas, betas = [], []
    for i in range(12):
        e = Ps[i + 1] - Ps[i]
        e /= np.linalg.norm(e)
        alphas.append(np.degrees(np.arccos(
            np.clip(curve_tangent(us_full[i]) @ (-e), -1, 1))))
        betas.append(np.degrees(np.arccos(
            np.clip(curve_tangent(us_full[i + 1]) @ (-e), -1, 1))))
    xs = np.arange(1, 13)
    ax2.bar(xs - 0.18, alphas, width=0.36, color=C_BLUE, label=r"$\alpha_j$（前把手）")
    ax2.bar(xs + 0.18, betas, width=0.36, color=C_ORANGE, label=r"$\beta_j$（后把手）")
    for j, txt in ((1, "跨$F$缝\n放大"), (3, "跨$T$缝\n放大"), (8, "跨$E$缝\n衰减")):
        ax2.annotate(txt, xy=(j, max(alphas[j - 1], betas[j - 1]) + 2.5),
                     ha="center", fontsize=6.5, color=C_VERM)
    ax2.set_xticks(xs)
    ax2.set_xlabel("弦编号 $j$（连接把手 $j$ 与 $j{+}1$）")
    ax2.set_ylabel("弦切角（°）")
    ax2.set_title("(b) 峰值构型的弦切角分布：$\\beta_j>\\alpha_j$ 处放大", fontsize=8)
    ax2.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题五速度传递机理.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("[图1] fig_问题五速度传递机理.png")


# ================================================================
# 图 2  速度比场
# ================================================================
def fig_field():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 2.9))

    # ---- (a) 热力图 ρ_i(u1)，把手 1~45，u1 ∈ [-25, 80] ----
    u1s = np.arange(-25.0, 80.01, 0.25)
    nshow = 45
    M = np.empty((nshow, len(u1s)))
    for k, u1 in enumerate(u1s):
        r = velocities(config_at(float(u1)))
        M[:, k] = r[:nshow]
    im = ax1.pcolormesh(u1s, np.arange(1, nshow + 1), M,
                        cmap="viridis", shading="auto",
                        vmin=0.93, vmax=float(M.max()))
    cb = fig.colorbar(im, ax=ax1, pad=0.015)
    cb.set_label(r"速度比 $\rho_i$", fontsize=7)
    # 事件线（前 9 把手跨缝）：底部标记替代贯穿全高的线
    from scipy.optimize import brentq
    def u_at(u1, i):
        return config_at(float(u1))[i - 1]
    ev_lines = []
    for i in range(1, 10):
        for c in (0.0, L1_0, L_C):
            g0 = c + sum(D_ALL[:i - 1])
            lo, hi = g0 - 8, g0 + 8
            try:
                if (u_at(lo, i) - c) * (u_at(hi, i) - c) < 0:
                    ev_lines.append(brentq(lambda uu: u_at(uu, i) - c, lo, hi,
                                           xtol=1e-10))
            except Exception:
                pass
    ax1.plot(ev_lines, np.full(len(ev_lines), 0.35), "|", ms=5,
             color="white", mew=0.8, zorder=3)
    ax1.annotate("事件", xy=(ev_lines[len(ev_lines) // 2], 1.8),
                 fontsize=6, color="white", ha="center")
    # 主峰标记
    ax1.plot(U1_PK, 5, "*", ms=9, color=C_VERM, mec="white", mew=0.4, zorder=5)
    ax1.annotate(f"主峰\n$u_1^*={U1_PK:.2f}$", xy=(U1_PK, 5),
                 xytext=(U1_PK + 9, 12), fontsize=6.5, color=C_VERM,
                 arrowprops=dict(arrowstyle="-", color=C_VERM, lw=0.6))
    ax1.set_xlabel(r"龙头弧长位置 $u_1$ (m)")
    ax1.set_ylabel("把手编号 $i$")
    ax1.set_title(r"(a) 速度比场 $\rho_i(u_1)$（底缘刻度：跨缝事件）", fontsize=8)

    # ---- (b) 全域 max ρ ----
    d = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "_explore_q5.npz"))
    ax2.plot(d["grid"], d["R"], color=C_BLUE, lw=0.8)
    ax2.axhline(R_B, color=C_VERM, lw=0.8, ls=(0, (4, 2)))
    ax2.annotate(f"$R_{{\\max}}={R_B:.6f}$", xy=(180, R_B),
                 xytext=(55, 1.545), fontsize=7.5, color=C_VERM)
    ax2.axhspan(0.98, 1.005, color=C_GRAY, alpha=0.15, lw=0)
    ax2.annotate("螺线段：$\\rho\\leq 1.004$", xy=(-62, 1.045), fontsize=6.5,
                 color=C_GRAY)
    sec = RES["model_B"]["secondary_peak"]["R"]
    ax2.annotate(f"次级峰 {sec:.4f}\n（链中段穿越）",
                 xy=(352, sec), xytext=(255, 1.30), fontsize=6.5, color=C_DARK,
                 arrowprops=dict(arrowstyle="-", color=C_GRAY, lw=0.6))
    for x in (-70, 410):
        ax2.axvline(x, color=C_DARK, lw=0.6, ls=(0, (2, 2)))
    ax2.annotate("搜索域\n$[-70,\\,410]$", xy=(410, 1.45), xytext=(330, 1.50),
                 fontsize=6.5, ha="center")
    ax2.set_xlabel(r"龙头弧长位置 $u_1$ (m)")
    ax2.set_ylabel(r"$R(u_1)=\max_i\ \rho_i(u_1)$")
    ax2.set_title("(b) 全域包络：主峰唯一，端部回落", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题五速度比场.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("[图2] fig_问题五速度比场.png")


# ================================================================
# 图 3  三模型收敛
# ================================================================
def fig_convergence():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.0))

    # ---- (a) 峰窗 R(u1) + 三模型 ----
    uu = np.arange(12.0, 17.0, 0.01)
    RR = np.array([np.max(velocities(config_at(float(u)))) for u in uu])
    ax1.plot(uu, RR, color=C_GRAY, lw=1.0, label=r"$R(u_1)$（$\Delta=0.01$ 参考线）")
    # 模型 A 采样点
    for step, mk, c in ((1.0, "s", C_PURPLE), (0.25, "^", C_SKY), (0.05, "o", C_GREEN)):
        gg = np.arange(12.0, 17.0 + step / 2, step)
        vv = [np.max(velocities(config_at(float(g)))) for g in gg]
        ax1.plot(gg, vv, mk, ms=3.5, color=c, ls="none",
                 label=f"模型 A：$\\Delta={step}$ m")
    # 模型 B / C
    ax1.axvline(U1_PK, color=C_VERM, lw=0.8, ls=(0, (4, 2)))
    ax1.plot([U1_PK], [R_B], "*", ms=10, color=C_VERM, mec="white", mew=0.4,
             zorder=6, label=f"模型 B/C 精确峰 $u_1^*={U1_PK:.4f}$")
    R_lo, R_hi = RES["R_max"]["C_lo"], RES["R_max"]["C_hi"]
    ax1.axhspan(R_lo, R_hi, color=C_VERM, alpha=0.35, lw=0,
                label="模型 C 认证区间（宽 $<10^{-8}$）")
    ax1.set_xlim(12.4, 16.6)
    ax1.set_ylim(1.38, 1.625)
    ax1.set_xlabel(r"$u_1$ (m)")
    ax1.set_ylabel(r"$R(u_1)=\max_i\rho_i$")
    ax1.set_title("(a) 峰窗：模型 A 采样点 vs 模型 B/C 精确峰", fontsize=8)
    ax1.legend(loc="lower left", fontsize=6)

    # ---- (b) 模型 A 收敛表 ----
    tab = RES["model_A_table"]
    steps = [t["step"] for t in tab]
    vA = [t["v_star_A"] for t in tab]
    ax2.plot(steps, vA, "o-", color=C_BLUE, ms=4, label="模型 A：$v^*_A=2/\\hat R_\\Delta$")
    ax2.axhspan(RES["model_C"]["v_lo"], RES["model_C"]["v_hi"],
                color=C_VERM, alpha=0.35, lw=0,
                label="模型 C 认证 $v^*$ 区间")
    ax2.axhline(V_STAR, color=C_VERM, lw=0.8, ls=(0, (4, 2)))
    ax2.annotate(f"$v^*={V_STAR:.6f}$", xy=(0.06, V_STAR),
                 xytext=(0.06, V_STAR + 0.004), fontsize=7, color=C_VERM)
    # Δ=1 高估标注
    ax2.annotate(f"$\\Delta=1$：高估 {(vA[0]/V_STAR-1)*100:.1f}%",
                 xy=(1.0, vA[0]), xytext=(0.11, vA[0] + 0.008), fontsize=6.5,
                 color=C_PURPLE,
                 arrowprops=dict(arrowstyle="-", color=C_PURPLE, lw=0.6))
    ax2.set_xscale("log")
    ax2.set_xlabel("网格步长 $\\Delta$ (m)（对数轴）")
    ax2.set_ylabel(r"$v^*_A$ (m/s)")
    ax2.set_title("(b) 模型 A 网格收敛：单调逼近但恒偏高", fontsize=8)
    ax2.legend(loc="center left", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题五三模型收敛.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("[图3] fig_问题五三模型收敛.png")


# ================================================================
# 图 4  临界构型
# ================================================================
def fig_critical():
    fig, ax = plt.subplots(figsize=(5.4, 4.2))
    us_full = config_at(U1_PK)
    Ps = positions(us_full)
    vs = velocities(us_full)

    # 曲线分段
    plot_curve_seg(ax, us_full[8] - 1.5, L1_0, n=500, color=C_BLUE, lw=2.0)
    plot_curve_seg(ax, L1_0, L_C, n=400, color=C_ORANGE, lw=2.0)
    plot_curve_seg(ax, L_C, us_full[0] + 1.5, n=300, color=C_PURPLE, lw=2.0)
    # 缝
    for u_s, lab in ((0.0, "$E$"), (L1_0, "$T$"), (L_C, "$F$")):
        P_s = curve_point(u_s)
        ax.plot(*P_s, "s", ms=4, color=C_DARK, zorder=6)
        ax.annotate(lab, P_s, textcoords="offset points", xytext=(-9, 5),
                    fontsize=9)
    # 板凳矩形（把手 1-9）
    for i in range(9):
        p0, p1 = Ps[i], Ps[i + 1]
        vv = p1 - p0
        u = vv / np.linalg.norm(vv)
        n = np.array([-u[1], u[0]])
        L = HEAD_L if i == 0 else BODY_L
        corners = np.array([0.5*(p0+p1) + (L/2)*u + 0.15*n,
                            0.5*(p0+p1) + (L/2)*u - 0.15*n,
                            0.5*(p0+p1) - (L/2)*u - 0.15*n,
                            0.5*(p0+p1) - (L/2)*u + 0.15*n])
        ax.fill(corners[:, 0], corners[:, 1], facecolor=C_GRAY,
                alpha=0.18, edgecolor=C_GRAY, lw=0.5, zorder=2)
    # 把手与速度箭头
    crit = set(H_PK)
    for i in range(10):
        c = C_VERM if (i + 1) in crit else C_BLUE
        ax.plot(*Ps[i], "o", ms=4.5, color=c, mec="white", mew=0.6, zorder=5)
        tau = curve_tangent(us_full[i])
        ax.add_patch(FancyArrowPatch(Ps[i], Ps[i] + (vs[i] * 1.8) * tau,
                                     arrowstyle="-|>", mutation_scale=9,
                                     color=c, lw=1.4, zorder=6))
        ax.annotate(f"{i+1}", Ps[i], textcoords="offset points",
                    xytext=(-8, 3), fontsize=7, color=C_DARK)
    ax.plot([], [], "o", color=C_VERM, label=f"临界把手 {H_PK[0]}–{H_PK[-1]}（$v_i=v^*\\cdot R_{{\\max}}=2$ m/s）")
    ax.plot([], [], "o", color=C_BLUE, label="其余把手（$v_i<2$ m/s）")
    ax.legend(loc="upper left", fontsize=6.5)
    ax.annotate(
        f"峰值构型：$u_1^*={U1_PK:.4f}$ m\n"
        f"龙头已过 $F$，把手 2–3 仍在弧 2（$R_2={R2_0:.3f}$ m）\n"
        f" $\\Rightarrow\\ \\rho_{{\\max}}={R_B:.6f}$，$t^*=u_1^*/v^*={RES['peak']['t_at_v_star']:.3f}$ s",
        xy=(0.97, 0.97), xycoords="axes fraction", va="top", ha="right",
        fontsize=7, bbox=dict(boxstyle="round,pad=0.4", fc="white",
                              ec=C_GRAY, lw=0.6))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"问题五临界构型（龙头速度 $v^*={V_STAR:.6f}$ m/s 时把手速度达 $2$ m/s）",
                 fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题五临界构型.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("[图4] fig_问题五临界构型.png")


# ================================================================
# 图 5  结构权衡
# ================================================================
def fig_tradeoff():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.2, 3.1),
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    # ---- (a) 两条调头曲线 ----
    th = np.linspace(TH_A - 2.2, TH_A + 3.5, 900)
    Pin = np.array([spiral_point(t) for t in th])
    ax1.plot(Pin[:, 0], Pin[:, 1], color=C_GRAY, lw=0.6, alpha=0.5)
    ax1.plot(-Pin[:, 0], -Pin[:, 1], color=C_GRAY, lw=0.6, alpha=0.5,
             ls=(0, (4, 2)))
    ax1.add_patch(Circle((0, 0), 4.5, fill=False, edgecolor=C_DARK, lw=0.8,
                         ls=(0, (5, 3))))
    u = np.linspace(0, L_C, 600)
    S = np.array([curve_point(x) for x in u])
    ax1.plot(S[:, 0], S[:, 1], color=C_BLUE, lw=2.0,
             label=f"基线两弧 $L_0={L_C:.4f}$ m")
    # 弧-线-弧
    alt = RES["alt_curve"]
    R1a, R2a, al = alt["R1"], alt["R2"], np.radians(alt["alpha_deg"])
    T1 = E + R1a * np.sin(al) * tE - R1a * (1 - np.cos(al)) * nE
    md = np.array([np.cos(-al) * tE[0] - np.sin(-al) * tE[1],
                   np.sin(-al) * tE[0] + np.cos(-al) * tE[1]])
    nm = rot90(md)
    ell = alt["ell"]
    T2 = T1 + ell * md
    O1a = E - R1a * nE
    O2a = T2 + R2a * nm
    phiE = np.arctan2(*(E - O1a)[::-1])
    s1 = np.linspace(0, 1, 300)
    A1 = O1a[None] + R1a * np.stack([np.cos(phiE - s1 * al),
                                     np.sin(phiE - s1 * al)], 1)
    ax1.plot(A1[:, 0], A1[:, 1], color=C_VERM, lw=2.0)
    ax1.plot([T1[0], T2[0]], [T1[1], T2[1]], color=C_VERM, lw=2.0)
    phiT2 = np.arctan2(*(T2 - O2a)[::-1])
    A2 = O2a[None] + R2a * np.stack([np.cos(phiT2 + s1 * al),
                                     np.sin(phiT2 + s1 * al)], 1)
    ax1.plot(A2[:, 0], A2[:, 1], color=C_VERM, lw=2.0,
             label=f"弧–线–弧 $L^*={alt['L']:.4f}$ m（$-26.11\\%$）")
    for P, lab in ((E, "$E$"), (F, "$F$")):
        ax1.plot(*P, "s", ms=3.5, color=C_DARK)
        ax1.annotate(lab, P, textcoords="offset points", xytext=(-8, 4),
                     fontsize=8)
    ax1.set_aspect("equal")
    ax1.set_title("(a) 基线调头曲线 vs 弧–线–弧优化曲线", fontsize=8)
    ax1.legend(loc="upper left", fontsize=6.5)
    ax1.axis("off")

    # ---- (b) 长度-速度权衡 ----
    Ls = [L_C, alt["L"]]
    Vs = [V_STAR, alt["v_star"]]
    ax2.plot([Ls[0], Ls[0]], [0, Vs[0]], color=C_BLUE, lw=0.8, ls=(0, (2, 2)))
    ax2.plot([Ls[1], Ls[1]], [0, Vs[1]], color=C_VERM, lw=0.8, ls=(0, (2, 2)))
    ax2.plot(Ls, Vs, "o", ms=6, color=C_DARK, zorder=5)
    ax2.plot(Ls, Vs, color=C_GRAY, lw=0.8, ls=(0, (4, 2)), zorder=3)
    ax2.annotate(f"基线两弧\n$L_0={Ls[0]:.3f}$ m\n$v^*={Vs[0]:.4f}$ m/s",
                 xy=(Ls[0], Vs[0]), xytext=(12.6, 1.06),
                 fontsize=7, color=C_BLUE, ha="center")
    ax2.annotate(f"弧–线–弧\n$L^*={Ls[1]:.3f}$ m\n$v^*_{{opt}}={Vs[1]:.4f}$ m/s",
                 xy=(Ls[1], Vs[1]), xytext=(11.9, 0.72), fontsize=7,
                 color=C_VERM, ha="center")
    # 理想下界方向（L→8.98 时需无穷大曲率，v*→0）
    ax2.axvline(8.9836, color=C_GRAY, lw=0.8, ls=(0, (1, 2)))
    ax2.annotate("理论下界 8.98 m\n（需无穷大曲率）", xy=(8.9836, 0.15),
                 fontsize=6.5, color=C_GRAY, ha="center")
    ax2.annotate("", xy=(Ls[1] + 0.06, Vs[1] + 0.03), xytext=(Ls[0] - 0.06, Vs[0] - 0.03),
                 arrowprops=dict(arrowstyle="-|>", color=C_DARK, lw=1.0,
                                 ls=(0, (4, 2))))
    ax2.annotate(f"缩短 {alt['curve_shorten_pct']:.1f}%\n速度 −{alt['v_drop_pct']:.1f}%",
                 xy=(0.5, 0.32), xycoords="axes fraction", fontsize=7.5,
                 color=C_DARK, ha="center",
                 bbox=dict(boxstyle="round,pad=0.3", fc="#F5F5F5",
                           ec=C_GRAY, lw=0.6))
    ax2.set_xlim(8.4, 14.2)
    ax2.set_ylim(0, 1.45)
    ax2.set_xlabel("调头曲线长度 (m)")
    ax2.set_ylabel(r"龙头最大行进速度 $v^*$ (m/s)")
    ax2.set_title("(b) “盘得紧”与“跑得快”的权衡", fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIGDIR, "fig_问题五结构权衡.png"),
                bbox_inches="tight")
    plt.close(fig)
    print("[图5] fig_问题五结构权衡.png")


if __name__ == "__main__":
    fig_mechanism()
    fig_field()
    fig_convergence()
    fig_critical()
    fig_tradeoff()
    print(f"[done] 全部图表输出至 {FIGDIR}")
