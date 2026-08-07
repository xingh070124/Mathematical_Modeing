"""可视化：模块摆放矩形图 + 芯片轮廓框 + 关键指标标注。"""
from __future__ import annotations

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle


def _setup_cjk_font():
    """配置中文字体（解决图表中文乱码/方块问题），并支持西文负号。"""
    wanted = ["Microsoft YaHei", "SimHei", "DengXian", "SimSun", "KaiTi",
              "Noto Sans CJK SC", "Source Han Sans SC", "WenQuanYi Micro Hei",
              "PingFang SC", "Heiti SC"]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in wanted:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name] + plt.rcParams.get(
                "font.sans-serif", [])
            break
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False


_setup_cjk_font()


def plot_layout(ds, xs, ys, rw, rh, W, H, path, title=None, density=None,
                aspect=None, dpi=150):
    xs = np.asarray(xs, dtype=np.int64)
    ys = np.asarray(ys, dtype=np.int64)
    rw = np.asarray(rw, dtype=np.int64)
    rh = np.asarray(rh, dtype=np.int64)
    cmap = plt.get_cmap("tab20")
    fig, ax = plt.subplots(figsize=(7.2, 7.2 * H / max(W, 1)))
    for i in range(ds.n):
        color = cmap(i % 20)
        ax.add_patch(Rectangle((xs[i], ys[i]), rw[i], rh[i], facecolor=color,
                               edgecolor="black", linewidth=0.5, alpha=0.85))
        if ds.n <= 60:
            ax.text(xs[i] + rw[i] / 2, ys[i] + rh[i] / 2, ds.names[i],
                    ha="center", va="center", fontsize=6)
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="crimson",
                           linewidth=2.2, linestyle="--"))
    ax.set_xlim(-W * 0.03, W * 1.03)
    ax.set_ylim(-H * 0.03, H * 1.03)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)
    info = (f"轮廓: {W} × {H}    面积: {W * H}"
            + (f"    密度: {density * 100:.2f}%" if density else "")
            + (f"    长宽比: {aspect:.3f}" if aspect else ""))
    ax.text(0.0, 1.012, info, transform=ax.transAxes, fontsize=9,
            verticalalignment="bottom")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def plot_convergence(traces, path):
    """多起点 vs 单起点收敛对比曲线。

    traces: 每条轨迹的 [(elapsed, best_area, aspect), ...]。
      * 多起点（累积最优）：全部轨迹在 t 时刻前各自已得最优面积的最小值；
      * 单起点·最佳初解：从最优初解出发的单条轨迹随时间的变化；
      * 单起点·中位初解：从初解质量中位数出发的典型单跑（代表"只跑一次"）。
    三者同一时间轴，直观体现多起点并行在收敛速度与终值上的优势。
    """
    if not traces:
        return
    tmax = max(tr[-1][0] for tr in traces)
    grid = np.linspace(0, tmax, 400)

    def best_of(tr, t):
        vals = [a for tt, a, _ in tr if tt <= t]
        return vals[-1] if vals else tr[0][1]

    def curve(tr):
        return [best_of(tr, t) for t in grid]

    multi = []
    cur = float("inf")
    for t in grid:
        cur = min(cur, min(best_of(tr, t) for tr in traces))
        multi.append(cur)

    sorted_tr = sorted(traces, key=lambda tr: tr[0][1])
    best_tr = sorted_tr[0]
    median_tr = sorted_tr[len(sorted_tr) // 2]

    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.plot(grid, multi,
            label=f"多起点（{len(traces)}条轨迹累积最优）", color="tab:red", lw=2.2)
    ax.plot(grid, curve(best_tr), label="单起点（最佳初解）",
            color="tab:blue", ls="--", lw=1.6)
    ax.plot(grid, curve(median_tr), label="单起点（中位初解·典型单跑）",
            color="tab:blue", ls=":", lw=1.6)
    ax.set_xlabel("时间（秒）")
    ax.set_ylabel("轮廓面积 W×H")
    ax.set_title("多起点与单起点收敛对比")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
