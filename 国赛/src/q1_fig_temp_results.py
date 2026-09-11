"""
图: 问题一温度场结果呈现 (与论文 5.1.5 结果呈现小节配套).

figure contract:
  核心结论: 30 min 内温度场快速建立径向梯度但远未平衡 --
  环境/表面/中心三层滞后清晰可见, 预热阶段结束时热平衡尚未完成.

面板:
  (a) 温度场时空热图 T(r,t)        (数据: outputs/result1.xlsx 生产解)
  (b) 表1 时刻的径向剖面 T(r)      (线色随时间 viridis 渐变, 右端直标时刻)
  (c) 中心/表面温度演化 + 环境参考  (展示 表面-环境、中心-表面 两级滞后)

运行:  python src/q1_fig_temp_results.py
输出:  paper/figures/fig_q1_temp_results.pdf|.png
       控制台打印 T_inf(1800s) 与表面温差 (供正文引用)
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C, GREY, save, setup  # noqa: E402
from q1_fig_data import load_result1  # noqa: E402
from q1_solve import Env, load_attachment1  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T_TAB = [100, 300, 600, 900, 1200, 1500, 1800]


def main():
    setup()
    rh, tt, T, _C = load_result1()
    t1, T1, _C1 = load_attachment1()
    env = Env(t1, T1, _C1, method="pchip")

    print(f"T_inf(1800s) = {env.T(1800.0) - 273.15:.4f} degC; "
          f"gap to surface = {env.T(1800.0) - 273.15 - T[-1, -1]:.4f} K; "
          f"gap to center = {env.T(1800.0) - 273.15 - T[-1, 0]:.4f} K")

    fig = plt.figure(figsize=(7.1, 6.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.85], hspace=0.42, wspace=0.30)

    # ---- (a) 时空热图 ----
    ax = fig.add_subplot(gs[0, 0])
    Tm = ax.pcolormesh(tt, rh, T.T, cmap="inferno", shading="auto",
                       vmin=T.min(), vmax=T.max())
    cb = fig.colorbar(Tm, ax=ax, pad=0.015)
    cb.set_label("温度 $T$ (°C)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    ax.set_xlabel("时间 $t$ (s)")
    ax.set_ylabel("到中心距离 $r$ (cm)")
    ax.set_title("(a) 温度场时空热图 $T(r,t)$", fontsize=8.5)

    # ---- (b) 径向剖面 ----
    ax = fig.add_subplot(gs[0, 1])
    t_idx = [int(np.where(tt == v)[0][0]) for v in T_TAB]
    shades = [plt.cm.viridis(0.02 + 0.78 * k / (len(T_TAB) - 1)) for k in range(len(T_TAB))]
    for k, i in enumerate(t_idx):
        ax.plot(rh, T[i, :], "-", color=shades[k], lw=1.2)
        ax.text(2.06, T[i, -1], f"{T_TAB[k]}", fontsize=6.8, va="center",
                color=shades[k])
    ax.text(0.08, T.max() - 0.6, "线色由深至浅：$t=100\\to1800$ s", fontsize=7,
            color=GREY["dark"])
    ax.set_xlim(0, 2.75)
    ax.set_xlabel("到中心距离 $r$ (cm)")
    ax.set_ylabel("温度 $T$ (°C)")
    ax.set_title("(b) 径向剖面（表1 时刻）", fontsize=8.5)

    # ---- (c) 时间演化: 中心/表面/环境 ----
    ax = fig.add_subplot(gs[1, :])
    ax.plot(tt, T[:, 0], "-", color=C["blue"], lw=1.4, label="中心 $T(0,t)$")
    ax.plot(tt, T[:, -1], "-", color=C["red"], lw=1.4, label="表面 $T(R,t)$")
    tt_fine = np.linspace(0, 1800, 600)
    ax.plot(tt_fine, env.T_arr(tt_fine) - 273.15, "--", color=C["orange"], lw=1.2,
            label="烘房 $T_\\infty(t)$")
    gap = env.T(1800.0) - 273.15 - T[-1, -1]
    ax.annotate(f"$t=1800$ s：$T_\\infty-T(R)\\approx{gap:.1f}$ °C",
                xy=(1800, T[-1, -1]), xytext=(1120, 42.2), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color=GREY["dark"], lw=0.7))
    ax.set_xlabel("时间 $t$ (s)")
    ax.set_ylabel("温度 $T$ (°C)")
    ax.set_ylim(27, 52)
    ax.legend(loc="lower right", ncol=3)
    ax.set_title("(c) 中心/表面温度演化与烘房环境对比：三级滞后，预热未完成", fontsize=8.5)

    fig.tight_layout()
    save(fig, "fig_q1_temp_results")


if __name__ == "__main__":
    main()
