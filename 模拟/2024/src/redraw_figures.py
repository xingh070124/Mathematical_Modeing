"""重绘 2024 板凳龙论文示意图（黑白风格）：
  1. 问题二算法流程与 CCD 检测逻辑流程图  → paper/figures/ccd_flow.png
  2. 板凳龙沿等距螺线盘入的几何结构示意  → paper/figures/dragon_geometry.png
"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# ---------------- 中文字体 ----------------
def _setup_font():
    for name in ["Microsoft YaHei", "SimHei", "DengXian", "SimSun"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue

_setup_font()

# 黑白主色板
INK = "#111111"       # 主墨色
DARK = "#444444"      # 深灰
MID = "#9A9A9A"       # 中灰
LIGHT = "#E9E9E9"     # 浅灰填充
PAPER = "#FFFFFF"     # 纸白

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.normpath(os.path.join(HERE, "..", "paper", "figures"))
os.makedirs(FIGDIR, exist_ok=True)

# 参数
PITCH = 0.55
B = PITCH / (2 * np.pi)
HEAD_L, BODY_L = 3.41, 2.20
HOLE = 0.275
D_HEAD = HEAD_L - 2 * HOLE
D_BODY = BODY_L - 2 * HOLE
WIDTH = 0.30
THETA0 = 32 * np.pi


def pos(theta):
    r = B * theta
    return np.array([r * np.cos(theta), r * np.sin(theta)])


def arc_len(theta):
    return 0.5 * B * (theta * np.sqrt(theta * theta + 1) + np.arcsinh(theta))


def theta_head(t):
    lo, hi = 0.0, THETA0
    F0 = arc_len(THETA0)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if F0 - arc_len(mid) > t:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def all_thetas(t):
    ths = np.empty(224)
    ths[0] = theta_head(t)
    for i in range(223):
        th = ths[i]
        d = D_HEAD if i == 0 else D_BODY
        P = pos(th)
        hi = 0.8
        while np.linalg.norm(pos(th + hi) - P) < d and hi < 3.2:
            hi *= 2.0
        lo = 0.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if np.linalg.norm(pos(th + mid) - P) > d:
                hi = mid
            else:
                lo = mid
        ths[i + 1] = th + 0.5 * (lo + hi)
    return ths


def bench_rect_coords(p0, p1, hlen):
    """返回旋转矩形的角点 (4×2)。"""
    v = p1 - p0
    u = v / np.linalg.norm(v)
    n = np.array([-u[1], u[0]])
    c = 0.5 * (p0 + p1)
    return np.array([
        c + hlen * u + (WIDTH / 2) * n,
        c + hlen * u - (WIDTH / 2) * n,
        c - hlen * u - (WIDTH / 2) * n,
        c - hlen * u + (WIDTH / 2) * n,
    ])


# ===================================================================
# 图 1：问题二算法流程与 CCD 检测逻辑（黑白流程图）
# ===================================================================
def draw_flowchart(path):
    fig, ax = plt.subplots(figsize=(8.6, 11.4), dpi=200)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13.4)
    ax.axis("off")

    def box(x, y, w, h, text, fc=LIGHT, fs=10.0, bold=False):
        bb = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                            boxstyle="round,pad=0.03,rounding_size=0.14",
                            facecolor=fc, edgecolor=INK, linewidth=1.3, zorder=2)
        ax.add_patch(bb)
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                color=INK, zorder=3, fontweight="bold" if bold else "normal",
                linespacing=1.4)

    def diamond(x, y, w, h, text, fs=10.0):
        pts = [(x, y + h / 2), (x + w / 2, y), (x, y - h / 2), (x - w / 2, y)]
        poly = plt.Polygon(pts, closed=True, facecolor=PAPER, edgecolor=INK,
                           linewidth=1.3, zorder=2)
        ax.add_patch(poly)
        ax.text(x, y, text, ha="center", va="center", fontsize=fs,
                color=INK, zorder=3, linespacing=1.35)
        return (x, y)

    def start_stop(x, y, text):
        bb = FancyBboxPatch((x - 1.15, y - 0.30), 2.3, 0.60,
                            boxstyle="round,pad=0.02,rounding_size=0.30",
                            facecolor=INK, edgecolor=INK, linewidth=1.3, zorder=2)
        ax.add_patch(bb)
        ax.text(x, y, text, ha="center", va="center", fontsize=11,
                color=PAPER, zorder=3, fontweight="bold")

    def arrow(x1, y1, x2, y2, lw=1.4):
        ar = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                             mutation_scale=13, linewidth=lw, color=INK,
                             zorder=1)
        ax.add_patch(ar)

    cx = 4.6
    # 顶部主流程
    start_stop(cx, 13.1, "开始")
    arrow(cx, 12.80, cx, 12.46)

    box(cx, 12.06, 7.4, 0.68,
        "输入螺线参数 $p, b$，龙头速度 $v_0$，步长 $\\Delta t$")
    arrow(cx, 11.72, cx, 11.38)

    box(cx, 10.98, 7.4, 0.68,
        "Brent 求根逐节递推 → 224 个把手节点坐标 $P_i(t)$")
    arrow(cx, 10.64, cx, 10.30)

    box(cx, 9.90, 7.4, 0.68,
        "构造各板凳旋转矩形 + 轴向包围盒 AABB")
    arrow(cx, 9.56, cx, 9.22)

    box(cx, 8.82, 7.4, 0.68,
        "AABB 宽相预筛选 → 候选碰撞对集合")
    arrow(cx, 8.48, cx, 8.14)

    box(cx, 7.74, 7.4, 0.68,
        "精确干涉判定：SAT 分离轴 + 顶点包容检验")
    arrow(cx, 7.40, cx, 7.06)

    # 判断菱形
    d = diamond(cx, 6.40, 2.9, 1.5, "是否存在\n碰撞?")
    arrow(cx, 6.65, cx + 0.6, 6.65)

    # 否 → 右侧 时间推进
    box(cx + 3.1, 6.40, 2.6, 0.78, "时间推进\n$t \\leftarrow t + \\Delta t$",
        fc=PAPER, fs=9.5)
    arrow(cx + 2.05, 6.40, cx + 1.79, 6.40)

    # 右侧回环：时间推进 → 向上 → 回到递推步
    ar = FancyArrowPatch((cx + 3.1, 6.78), (cx + 3.1, 10.98),
                         arrowstyle="-|>", mutation_scale=13, linewidth=1.4,
                         color=INK, zorder=1,
                         connectionstyle="arc3,rad=-0.5")
    ax.add_patch(ar)
    ax.text(cx + 3.9, 9.2, "否", fontsize=10, color=DARK, ha="center", zorder=4)
    ar2 = FancyArrowPatch((cx + 3.1, 10.98), (cx + 0.62, 10.98),
                          arrowstyle="-|>", mutation_scale=13, linewidth=1.4,
                          color=INK, zorder=1)
    ax.add_patch(ar2)

    # 是 → 下
    arrow(cx, 6.15, cx, 5.80)
    ax.text(cx + 0.22, 6.0, "是", fontsize=10, color=DARK, zorder=4)

    # CCD 精化
    box(cx, 5.32, 7.4, 0.84,
        "CCD 连续碰撞检测：\n二分收缩时间区间 ＋ 黄金分割求 $\\min g(t)$",
        fs=9.8)
    arrow(cx, 4.90, cx, 4.56)

    box(cx, 4.12, 7.4, 0.76,
        "输出极限终止时刻 $t^* = 412.47$ s，碰撞对 $(1, 9)$", bold=True)
    arrow(cx, 3.74, cx, 3.40)

    start_stop(cx, 3.10, "结束")

    # 图注
    ax.text(cx, 1.35,
            "虚线回环表示：当前时间步无碰撞则增大步长继续扫描；\n"
            "一旦检测到碰撞，即转入 CCD 时间精化，逼近临界时刻 $t^*$。",
            ha="center", va="center", fontsize=8.5, color=DARK)

    fig.tight_layout(pad=0.4)
    fig.savefig(path, dpi=200, facecolor=PAPER)
    plt.close(fig)
    print("流程图已保存:", path)


# ===================================================================
# 图 2：板凳龙沿等距螺线盘入的几何结构示意（黑白）
# ===================================================================
def draw_geometry(path):
    # 龙头 t=0 附近构型（内圈局部）
    ths = all_thetas(0.0)
    Ps = np.array([pos(th) for th in ths])
    n_show = 14   # 显示 14 节，画面清晰
    shown = Ps[: n_show + 1]

    # 视窗以板凳区域为中心
    cx, cy = shown.mean(axis=0)
    span = max(float(np.ptp(shown[:, 0])), float(np.ptp(shown[:, 1])), 4.0)
    half = span / 2 * 1.35

    fig, ax = plt.subplots(figsize=(8.4, 8.4), dpi=200)
    ax.set_aspect("equal")

    # 背景螺线（浅灰虚线，多圈）
    thg = np.linspace(30 * np.pi, 36 * np.pi, 2500)
    ax.plot(pos(thg)[0], pos(thg)[1], color=MID, lw=0.8,
            linestyle=(0, (2, 2)), zorder=1, alpha=0.55)

    # 板凳：渐近灰度
    for i in range(n_show):
        shade = 0.85 - 0.55 * (i / n_show)
        corner = bench_rect_coords(Ps[i], Ps[i + 1],
                                   D_HEAD / 2 if i == 0 else D_BODY / 2)
        poly = plt.Polygon(corner, closed=True, facecolor=str(shade),
                           edgecolor=INK, lw=0.7, zorder=3)
        ax.add_patch(poly)
        ax.plot([Ps[i][0], Ps[i + 1][0]], [Ps[i][1], Ps[i + 1][1]], "o",
                ms=1.4, color=INK, zorder=4)

    # 龙头（第1节）深色强调
    c0 = bench_rect_coords(Ps[0], Ps[1], D_HEAD / 2)
    ax.add_patch(plt.Polygon(c0, closed=True, facecolor=DARK,
                             edgecolor=INK, lw=1.3, zorder=5))

    # 第 9 节描边强调（碰撞对）
    c9 = bench_rect_coords(Ps[8], Ps[9], D_BODY / 2)
    ax.add_patch(plt.Polygon(c9, closed=True, facecolor="none",
                             edgecolor=INK, lw=2.2, zorder=6))

    # 标注
    hp = Ps[0]
    ax.annotate("龙头\n(前把手, 第1节)", xy=hp, xytext=(hp[0] + 0.7, hp[1] + 1.0),
                fontsize=9, color=INK, ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.1))
    n9 = 0.5 * (Ps[8] + Ps[9])
    ax.annotate("第9节\n(首次干涉对象)", xy=n9,
                xytext=(n9[0] - 0.6, n9[1] - 1.1),
                fontsize=9, color=DARK, ha="center", va="center",
                arrowprops=dict(arrowstyle="->", color=DARK, lw=1.1))

    # 相邻把手间距标注
    a, b = Ps[5], Ps[6]
    am = 0.5 * (a + b)
    ax.annotate("", xy=(a[0], a[1]), xytext=(b[0], b[1]),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.1,
                                connectionstyle="arc3,rad=-0.35"))
    ax.text(am[0] + 0.55, am[1] - 0.55, "把手间距 $L_i$",
            fontsize=8.5, color=INK, ha="center")

    # 螺距标注（用画面内的两圈）
    r0, r1 = cx - 0.5, cx + 0.5
    ax.annotate("", xy=(r1, cy + 0.7), xytext=(r0, cy + 0.7),
                arrowprops=dict(arrowstyle="<->", color=MID, lw=1.1))
    ax.text(cx, cy + 1.05, "螺距 $p = 55$ cm", fontsize=8.5,
            color=MID, ha="center")

    # 比例尺
    ax.plot([cx - 1.1, cx + 0.9], [cy - 1.55, cy - 1.55], color=INK, lw=1.2)
    ax.plot([cx - 1.1, cx - 1.1], [cy - 1.66, cy - 1.44], color=INK, lw=1.0)
    ax.plot([cx + 0.9, cx + 0.9], [cy - 1.66, cy - 1.44], color=INK, lw=1.0)
    ax.text(cx - 0.1, cy - 1.9, "2 m", ha="center", fontsize=8.5, color=INK)

    ax.set_xlim(cx - half, cx + half)
    ax.set_ylim(cy - half, cy + half)
    ax.set_xlabel("$x$ / m")
    ax.set_ylabel("$y$ / m")
    ax.set_title("板凳龙沿等距螺线盘入的几何结构（内圈局部，黑白示意）",
                 fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=200, facecolor=PAPER)
    plt.close(fig)
    print("几何示意图已保存:", path)


if __name__ == "__main__":
    draw_flowchart(os.path.join(FIGDIR, "ccd_flow.png"))
    draw_geometry(os.path.join(FIGDIR, "dragon_geometry.png"))
    print("完成。输出目录:", FIGDIR)
