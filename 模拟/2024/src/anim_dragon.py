# -*- coding: utf-8 -*-
"""
2024 CUMCM A 题"板凳龙" —— 动态仿真（盘入过程动画 GIF）

展示板凳龙从 t=0（第16圈起点）顺时针盘入，到碰撞临界时刻 t*=412.48 s 的完整过程。
每帧绘制整条龙 224 个把手中心的连线（龙头红、龙身蓝、龙尾绿），并随时间推进。

输出：paper/figures/anim_盘入仿真.gif
"""
import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.animation import FuncAnimation, PillowWriter

# 显式注册中文字体（Windows .ttc）
for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

# ---------------- 求解核心（与 problem2_collision.py 一致） ----------------
PITCH = 0.55
B = PITCH / (2 * np.pi)
THETA0 = 32 * np.pi
HEAD_L, BODY_L = 3.41, 2.20
HOLE_OFF = 0.275
D_HEAD = HEAD_L - 2 * HOLE_OFF
D_BODY = BODY_L - 2 * HOLE_OFF


def pos(theta):
    r = B * theta
    return np.array([r * np.cos(theta), r * np.sin(theta)])


def arc_len(theta):
    return 0.5 * B * (theta * np.sqrt(theta * theta + 1) + np.arcsinh(theta))


F0 = arc_len(THETA0)


def theta_head(t):
    lo, hi = 0.0, THETA0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if F0 - arc_len(mid) > t:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def next_theta(th, d):
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
    return th + 0.5 * (lo + hi)


def all_thetas(t):
    ths = np.empty(224)
    ths[0] = theta_head(t)
    for i in range(223):
        ths[i + 1] = next_theta(ths[i], D_HEAD if i == 0 else D_BODY)
    return ths


def all_positions(t):
    return np.array([pos(th) for th in all_thetas(t)])


# ---------------- 动画 ----------------
T_STOP = 412.48
N_FRAMES = 150
times = np.linspace(0, T_STOP, N_FRAMES)

# 预计算每帧位置
print("[动画] 预计算 %d 帧位置..." % N_FRAMES)
frames = [all_positions(t) for t in times]

# 螺线背景
th_lin = np.linspace(0, THETA0, 4000)
spiral = np.array([pos(th) for th in th_lin])

fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(spiral[:, 0], spiral[:, 1], color="#c8d8e8", lw=1.0, zorder=1)

# 用细分颜色：龙头红，龙身蓝渐变，龙尾绿
body_colors = plt.cm.Blues(np.linspace(0.4, 0.9, 221))
tail_colors = plt.cm.Greens(np.linspace(0.55, 0.75, 1))

line_head, = ax.plot([], [], color="#d9534f", lw=3.0, zorder=5, label="龙头")
line_body, = ax.plot([], [], color="#6baed6", lw=2.0, zorder=4, label="龙身")
line_tail, = ax.plot([], [], color="#5cb85c", lw=2.0, zorder=4, label="龙尾")
pt_head, = ax.plot([], [], "o", ms=6, color="#8b0000", zorder=6)
txt_time = ax.text(0.02, 0.96, "", transform=ax.transAxes, fontsize=14,
                   va="top", fontweight="bold",
                   bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.85))

ax.set_aspect("equal")
ax.set_xlim(-13, 13)
ax.set_ylim(-13, 13)
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_title("板凳龙沿等距螺线盘入（动态仿真）")
ax.grid(alpha=0.3)
ax.legend(loc="lower right", fontsize=10)


def update(frame_idx):
    P = frames[frame_idx]
    t = times[frame_idx]
    line_head.set_data(P[0:1, 0], P[0:1, 1])            # 龙头（第1节）把手
    line_body.set_data(P[1:222, 0], P[1:222, 1])        # 龙身 221 节
    line_tail.set_data(P[222:224, 0], P[222:224, 1])    # 龙尾（含后把手）
    pt_head.set_data([P[0, 0]], [P[0, 1]])
    txt_time.set_text(f"t = {t:6.2f} s\n龙头半径 = {np.linalg.norm(P[0]):5.2f} m")
    return line_head, line_body, line_tail, pt_head, txt_time


anim = FuncAnimation(fig, update, frames=N_FRAMES, interval=80, blit=True)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "paper", "figures", "anim_盘入仿真.gif")
print("[动画] 写出 GIF ...")
anim.save(out, writer=PillowWriter(fps=15))
print("[动画] 已保存:", out)