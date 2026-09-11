"""
图: 问题一水分浓度场结果呈现 (与论文 5.1.7 结果呈现小节配套).

figure contract:
  核心结论: 30 min 内水分仅在表层松弛 -- 中心几乎不动、体积平均微降、
  表面远未与热风平衡 (C(R)/C_inf~46 倍), 时间尺度分离 (R^2/D(C0) >> 1800 s)
  的直接可视化证据.

面板:
  (a) 水分浓度场时空热图 C(r,t)      (数据: outputs/result1.xlsx 生产解)
  (b) 表2 时刻的径向剖面 C(r)
  (c) 中心/体积平均/表面浓度演化 + 环境参考 (展示表层脱湿与巨大平衡差距)

运行:  python src/q1_fig_moist_results.py
输出:  paper/figures/fig_q1_moist_results.pdf|.png
       控制台打印 C_inf(1800s)、C(R,1800s)、比值、体积平均降幅 (供正文引用)
"""

from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import C, GREY, save, setup  # noqa: E402
from q1_fig_data import load_result1  # noqa: E402
from q1_solve import Env, load_attachment1, R0  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

T_TAB = [100, 300, 600, 900, 1200, 1500, 1800]


def volume_avg_weights(rh_cm, n):
    """节点式网格的体积权重 (单位轴长, 已含 pi)."""
    dr = rh_cm[1] - rh_cm[0]
    r = rh_cm / 100.0
    rf_p = np.minimum(r + dr / 200.0, R0)
    rf_m = np.maximum(r - dr / 200.0, 0.0)
    return np.pi * (rf_p ** 2 - rf_m ** 2)


def main():
    setup()
    rh, tt, _T, Cm = load_result1()
    t1, _T1, C1 = load_attachment1()
    env = Env(t1, _T1, C1, method="pchip")
    w = volume_avg_weights(rh, len(rh))
    Cavg = Cm @ w / w.sum()

    ratio = Cm[-1, -1] / env.C(1800.0)
    drop = (Cavg[0] - Cavg[-1]) / Cavg[0]
    print(f"C_inf(1800s) = {env.C(1800.0):.5f}; C(R,1800s) = {Cm[-1,-1]:.4f}; "
          f"ratio = {ratio:.1f}; <C> drop = {drop*100:.1f}%")

    fig = plt.figure(figsize=(7.1, 6.0))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.85], hspace=0.42, wspace=0.30)

    # ---- (a) 时空热图 ----
    ax = fig.add_subplot(gs[0, 0])
    Pm = ax.pcolormesh(tt, rh, Cm.T, cmap="viridis", shading="auto",
                       vmin=Cm.min(), vmax=Cm.max())
    cb = fig.colorbar(Pm, ax=ax, pad=0.015)
    cb.set_label("水分浓度 $C$ (kg/kg)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    ax.set_xlabel("时间 $t$ (s)")
    ax.set_ylabel("到中心距离 $r$ (cm)")
    ax.set_title("(a) 水分浓度场时空热图 $C(r,t)$", fontsize=8.5)

    # ---- (b) 径向剖面 ----
    ax = fig.add_subplot(gs[0, 1])
    t_idx = [int(np.where(tt == v)[0][0]) for v in T_TAB]
    shades = [plt.cm.viridis(0.02 + 0.78 * k / (len(T_TAB) - 1)) for k in range(len(T_TAB))]
    for k, i in enumerate(t_idx):
        ax.plot(rh, Cm[i, :], "-", color=shades[k], lw=1.2)
        ax.text(2.06, Cm[i, -1], f"{T_TAB[k]}", fontsize=6.8, va="center",
                color=shades[k])
    ax.text(0.08, 2.47, "线色由深至浅：$t=100\\to1800$ s", fontsize=7,
            color=GREY["dark"])
    ax.set_xlim(0, 2.75)
    ax.set_xlabel("到中心距离 $r$ (cm)")
    ax.set_ylabel("水分浓度 $C$ (kg/kg)")
    ax.set_title("(b) 径向剖面（表2 时刻）", fontsize=8.5)

    # ---- (c) 时间演化: 中心/体积平均/表面/环境 ----
    ax = fig.add_subplot(gs[1, :])
    ax.plot(tt, Cm[:, 0], "-", color=C["blue"], lw=1.4, label="中心 $C(0,t)$")
    ax.plot(tt, Cavg, "-", color=C["teal"], lw=1.4, label="体积平均 $\\langle C\\rangle(t)$")
    ax.plot(tt, Cm[:, -1], "-", color=C["red"], lw=1.4, label="表面 $C(R,t)$")
    tt_fine = np.linspace(0, 1800, 600)
    ax.plot(tt_fine, env.C_arr(tt_fine), "--", color=C["orange"], lw=1.2,
            label="烘房 $C_\\infty(t)$")
    ax.annotate(f"$t=1800$ s：$C(R)/C_\\infty\\approx{ratio:.0f}$ 倍",
                xy=(1800, Cm[-1, -1]), xytext=(1050, 0.55), fontsize=7.5,
                arrowprops=dict(arrowstyle="->", color=GREY["dark"], lw=0.7))
    ax.set_xlabel("时间 $t$ (s)")
    ax.set_ylabel("水分浓度 $C$ (kg/kg)")
    ax.set_ylim(0, 2.75)
    ax.legend(loc="center right", ncol=2)
    ax.set_title("(c) 各层浓度演化与环境对比：仅表层脱湿，表面远未平衡", fontsize=8.5)

    fig.tight_layout()
    save(fig, "fig_q1_moist_results")


if __name__ == "__main__":
    main()
