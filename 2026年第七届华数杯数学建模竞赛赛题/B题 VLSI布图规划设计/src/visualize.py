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


def plot_layout_q2(ds, net, xs, ys, rw, rh, Lhat, path, title=None,
                   hpwl=None, gap_pct=None, dpi=150, feasible=True):
    """问题二布局可视化：矩形模块 + Terminal 点标注 + 固定轮廓框。

    额外信息标注：总 HPWL（上界证书）、gap（相对凸松弛下界）。
    """
    xs = np.asarray(xs, dtype=np.int64)
    ys = np.asarray(ys, dtype=np.int64)
    rw = np.asarray(rw, dtype=np.int64)
    rh = np.asarray(rh, dtype=np.int64)
    cmap = plt.get_cmap("tab20")
    fig, ax = plt.subplots(figsize=(7.2, 7.2))
    for i in range(ds.n):
        color = cmap(i % 20)
        ax.add_patch(Rectangle((xs[i], ys[i]), rw[i], rh[i], facecolor=color,
                               edgecolor="black", linewidth=0.5, alpha=0.85))
    # Terminal 引脚标注（固定坐标，不占面积）
    tx = [p[0] for p in ds.terminal_pos.values()]
    ty = [p[1] for p in ds.terminal_pos.values()]
    if tx:
        ax.scatter(tx, ty, s=10, c="red", marker="o", zorder=3,
                   edgecolors="black", linewidths=0.3, label="Terminal")
    # 固定轮廓框
    ax.add_patch(Rectangle((0, 0), Lhat, Lhat, fill=False,
                           edgecolor="crimson", linewidth=2.2, linestyle="--"))
    ax.set_xlim(-Lhat * 0.03, Lhat * 1.03)
    ax.set_ylim(-Lhat * 0.03, Lhat * 1.03)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    if title:
        ax.set_title(title)
    info = f"轮廓: {Lhat} × {Lhat}"
    if hpwl is not None:
        info += f"    总HPWL: {hpwl:,.0f}"
    if gap_pct is not None:
        info += f"    gap: {gap_pct:.2f}%"
    info += "    可行" if feasible else "    不可行"
    ax.text(0.0, -0.09, info, transform=ax.transAxes, fontsize=9,
            verticalalignment="top")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)


def plot_convergence_q2(traces, hpwl_lb, path, pool_hpwl=None):
    """问题二收敛曲线：多起点 B*-树+SA 各轨迹搜索进程 + 累积最优 + 参考线。

    traces: 每条 SA 轨迹的 [(elapsed, best_hpwl, overflow), ...]（字典序最优）。
      * 细线 = 各轨迹自身最优（从种子树状态下降，展示搜索进程）；
      * 粗红线 = 多起点累积最优可行 HPWL（t=0 起锚定 L1 初解池最优）；
      * 参考线 = 凸松弛下界 与 L1 初解池最优。
    """
    if not traces:
        return
    traces = [tr for tr in traces if len(tr) > 0]
    if not traces:
        return
    tmax = max(tr[-1][0] for tr in traces)
    grid = np.linspace(0, tmax, 400)

    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    # 各轨迹自身最优（细线）
    cmap = plt.get_cmap("Set2")
    for ci, tr in enumerate(traces):
        yy = [h for tt, h, _ in tr]
        xx = [tt for tt, _, _ in tr]
        ax.plot(xx, yy, color=cmap(ci % 8), lw=1.1, alpha=0.8,
                label=f"轨迹{ci + 1}（自身最优）")
    # 多起点累积最优可行解
    def best_feasible_so_far(tr, t):
        vals = [h for tt, h, ov in tr if tt <= t and ov == 0]
        return vals[-1] if vals else None

    multi = []
    cur = float(pool_hpwl) if pool_hpwl is not None else float("inf")
    for t in grid:
        vals = [best_feasible_so_far(tr, t) for tr in traces]
        vals = [v for v in vals if v is not None]
        if vals:
            cur = min(cur, min(vals))
        multi.append(cur)
    ax.plot(grid, multi, label="多起点累积最优（可行）",
            color="tab:red", lw=2.6)
    if pool_hpwl is not None:
        ax.axhline(pool_hpwl, color="tab:blue", ls=":", lw=1.6,
                   label=f"L1 初解池最优 HPWL={pool_hpwl:,.0f}")
    ax.axhline(hpwl_lb, color="tab:green", ls="--", lw=1.6,
               label=f"凸松弛下界 HPWL_lb={hpwl_lb:,.0f}")
    ax.set_xlabel("时间（秒）")
    ax.set_ylabel("总 HPWL")
    ax.set_title("问题二 多起点 B*-树+SA 收敛与下界对比")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
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


def plot_layout_q4(modules, solution, W, H, path, title=None,
                   area=None, density=None, aspect=None, dpi=150):
    """问题四布局可视化：异形模块按子块绘制 + 轮廓框 + 指标标注。

    modules: list[CompoundModule]
    solution: {m: (x, y, r)}
    """
    cmap = plt.get_cmap("tab10")
    fig, ax = plt.subplots(figsize=(7.2, 7.2 * H / max(W, 1)))
    for m, (x, y, r) in solution.items():
        mod = modules[m]
        color = cmap(m % 10)
        for w, h, a, b in mod.rotated(r):
            ax.add_patch(Rectangle((x + a, y + b), w, h, facecolor=color,
                                   edgecolor="black", linewidth=1.0, alpha=0.85))
        ax.text(x + mod.bbox[0] / 2.0, y + mod.bbox[1] / 2.0, mod.name,
                ha="center", va="center", fontsize=11, fontweight="bold")
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="crimson",
                           linewidth=2.2, linestyle="--"))
    ax.set_xlim(-W * 0.05, W * 1.05)
    ax.set_ylim(-H * 0.05, H * 1.05)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(alpha=0.3, linewidth=0.5)
    if title:
        ax.set_title(title)
    info = f"轮廓: {W} × {H}    面积: {W * H}"
    if density is not None:
        info += f"    密度: {density * 100:.2f}%"
    if aspect is not None:
        info += f"    长宽比: {W / H:.3f}"
    ax.text(0.0, -0.09, info, transform=ax.transAxes, fontsize=10,
            verticalalignment="top")
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
