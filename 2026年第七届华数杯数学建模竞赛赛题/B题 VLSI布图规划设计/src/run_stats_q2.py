"""Q2 多次独立运行统计 + 三级消融实验（评审建议 14/15/28/29）。

多次独立运行：每数据集运行 n_runs 次（不同种子），报告 Best/Mean/Std/Worst/Time，
并以箱线图展示分布（证明结果非单次碰巧）。

三级消融：
  L1 贪心构造（初解池最优） -> 多起点 Skyline-ILS（不含精英池/重启） -> 完整四层流水线
输出 result/question 2/q2_stats.json 与 q2_stats_boxplot.png / q2_ablation.png。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "附件")
OUT = os.path.join(BASE, "result", "question 2")
sys.path.insert(0, HERE)

from config import SCENARIOS                       # noqa: E402
from data_io import load_dataset                    # noqa: E402
from hpwl import NetIndex                           # noqa: E402
from solve_q2 import solve_dataset                  # noqa: E402
from layer1_pool_q2 import generate_initial_pool_q2, diversity_filter_q2  # noqa: E402
from skyline_ils_q2 import ils_hpwl_trajectory      # noqa: E402


def _cfg(scale):
    from dataclasses import replace
    cfg = replace(SCENARIOS["Q2"])
    cfg.nproc = 6
    for attr in ("t_ils", "t_restart", "t_bstar", "t_sp", "t_refine"):
        setattr(cfg, attr, getattr(cfg, attr) * scale)
    return cfg


def run_stats(name, n_runs, scale):
    ds = load_dataset(DATA, name)
    net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
    cfg = _cfg(scale)
    hpwls, times = [], []
    for k in range(n_runs):
        cfg.seed = 2026 + k * 101
        r = solve_dataset(ds, cfg, net)
        hpwls.append(float(r["best"]["hpwl"]))
        times.append(round(r["runtime"], 1))
    hpwls = np.asarray(hpwls)
    return dict(
        dataset=name, n=n_runs, best=float(hpwls.min()),
        mean=float(hpwls.mean()), std=float(hpwls.std()),
        worst=float(hpwls.max()), times=times, all=hpwls.tolist(),
    )


def run_ablation(name, scale, seed=1531):
    ds = load_dataset(DATA, name)
    net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
    cfg = _cfg(scale)
    cfg.seed = seed
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    Lhat = int(math.ceil(math.sqrt(ds.total_area * 1.15)))
    rng = np.random.default_rng(cfg.seed)
    pool = generate_initial_pool_q2(ds, net, Lhat, rng, prob_rot=0.3)
    pool = diversity_filter_q2(pool, cfg.kp)
    greedy = float(min(s["hpwl"] for s in pool))
    ilses = []
    for sol in pool:
        res = ils_hpwl_trajectory(widths, heights, sol["order"],
                                  np.asarray(sol["rot"], dtype=np.int64),
                                  net, Lhat, cfg.t_ils, seed=cfg.seed)
        if res is not None:
            ilses.append(float(res["hpwl"]))
    ils_multi = float(min(ilses))
    full = float(solve_dataset(ds, cfg, net)["best"]["hpwl"])
    return dict(dataset=name, greedy=greedy, ils_multi=ils_multi, full=full)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="n100,n200,n300")
    ap.add_argument("--n-runs", type=int, default=6)
    ap.add_argument("--scale", type=float, default=0.2,
                    help="时间预算缩放（快速实验用，全量取 1.0）")
    ap.add_argument("--no-ablation", action="store_true")
    args = ap.parse_args()

    names = [s.strip() for s in args.datasets.split(",") if s.strip()]
    stats = []
    for name in names:
        print(f"[stats] {name} x{args.n_runs} (scale={args.scale})", flush=True)
        stats.append(run_stats(name, args.n_runs, args.scale))
        print(f"   {stats[-1]}", flush=True)

    abl = []
    if not args.no_ablation:
        for name in names:
            print(f"[ablation] {name} (scale={args.scale})", flush=True)
            abl.append(run_ablation(name, args.scale))
            print(f"   {abl[-1]}", flush=True)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "q2_stats.json"), "w", encoding="utf-8") as f:
        json.dump(dict(stats=stats, ablation=abl, scale=args.scale,
                       n_runs=args.n_runs), f, ensure_ascii=False, indent=2)
    _plot_box(stats)
    if abl:
        _plot_ablation(abl)
    print("saved q2_stats.json / q2_stats_boxplot.png / q2_ablation.png")


def _plot_box(stats):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names = {f.name for f in font_manager.fontManager.ttflist}
    cjk = next((n for n in ["Microsoft YaHei", "SimHei", "SimSun"] if n in names),
               "sans-serif")
    plt.rcParams.update({"font.sans-serif": [cjk, "Arial"],
                         "axes.unicode_minus": False})
    data = [s["all"] for s in stats]
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    bp = ax.boxplot(data, tick_labels=[s["dataset"] for s in stats], widths=0.5)
    for i, s in enumerate(stats):
        ax.scatter(i + 1, s["mean"], color="tab:red", zorder=3, s=22,
                   label="均值" if i == 0 else None)
    ax.set_ylabel("总 HPWL")
    ax.set_xlabel("数据集")
    ax.set_title(f"问题二 多次独立运行总HPWL分布（n={stats[0]['n']}次）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q2_stats_boxplot.png"), dpi=300)
    plt.close(fig)


def _plot_ablation(abl):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names = {f.name for f in font_manager.fontManager.ttflist}
    cjk = next((n for n in ["Microsoft YaHei", "SimHei", "SimSun"] if n in names),
               "sans-serif")
    plt.rcParams.update({"font.sans-serif": [cjk, "Arial"],
                         "axes.unicode_minus": False})
    levels = ["L1贪心构造", "多起点Skyline-ILS", "完整四层流水线"]
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    x = np.arange(len(abl))
    width = 0.28
    colors = ["#7f8c8d", "#4C72B0", "#C44E52"]
    for j, lv in enumerate(levels):
        vals = [a[["greedy", "ils_multi", "full"][j]] for a in abl]
        ax.bar(x + (j - 1) * width, vals, width, label=lv, color=colors[j])
        for xi, v in zip(x + (j - 1) * width, vals):
            ax.text(xi, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=6.5)
    ax.set_xticks(x)
    ax.set_xticklabels([a["dataset"] for a in abl])
    ax.set_ylabel("总 HPWL")
    ax.set_title("问题二 三级消融实验（HPWL，越低越好）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q2_ablation.png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
