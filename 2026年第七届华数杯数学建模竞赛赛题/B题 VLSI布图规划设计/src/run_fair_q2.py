"""Q2 统一时间预算公平对比（评审建议 15/28/29）。

在相同墙钟预算下比较三种算法：Skyline-ILS/SA（主） vs B*-树-SA vs SP-AGA。
每种算法独立运行、等时预算 t，报告各自 Best HPWL。
输出 result/question 2/q2_fair.json 与 q2_fair.png。
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
from layer1_pool_q2 import generate_initial_pool_q2, diversity_filter_q2  # noqa: E402
from skyline_ils_q2 import ils_hpwl_trajectory      # noqa: E402
from sp_ga import sp_aga_solve                      # noqa: E402
from bstar import BStarTree                         # noqa: E402
from bstar_q2 import bstar_hpwl_sa_solve            # noqa: E402


def build_seed_tree(widths, heights, order, rot, Lhat):
    from solve_q2 import build_seed_tree as _b
    return _b(widths, heights, order, rot, Lhat)


def fair_run(name, budget, seed=2026):
    ds = load_dataset(DATA, name)
    net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    Lhat = int(math.ceil(math.sqrt(ds.total_area * 1.15)))
    rng = np.random.default_rng(seed)
    cfg = SCENARIOS["Q2"]
    pool = generate_initial_pool_q2(ds, net, Lhat, rng, prob_rot=0.3)
    pool = diversity_filter_q2(pool, cfg.kp)

    # 主算法 Skyline-ILS/SA：K' 条轨迹，等时预算
    ilses = []
    for i, sol in enumerate(pool):
        res = ils_hpwl_trajectory(widths, heights, sol["order"],
                                  np.asarray(sol["rot"], dtype=np.int64),
                                  net, Lhat, budget, seed=seed + i * 101 + 7)
        if res is not None:
            ilses.append(float(res["hpwl"]))
    main_best = float(min(ilses))

    # B*-树-SA：种子树 + L1 可行解 init，等时预算
    tree = build_seed_tree(widths, heights, pool[0]["order"],
                           np.asarray(pool[0]["rot"]), Lhat)
    bound_w = int(max(widths.sum(), heights.sum())) + 10
    feas_pool = [s for s in pool if s["overflow"] == 0]
    init = feas_pool[0] if feas_pool else None
    bs = bstar_hpwl_sa_solve(widths, heights, tree.rot.tolist(),
                             int(tree.root), tree.parent.tolist(),
                             tree.left.tolist(), tree.right.tolist(),
                             bound_w, net, Lhat, budget, seed=seed + 3000,
                             init=init)
    bstar_best = float(bs["hpwl"]) if bs.get("overflow", 1) == 0 else None

    # SP-AGA：等时预算
    sp = sp_aga_solve(widths, heights, net, Lhat, budget, seed=seed + 7000)
    sp_best = float(sp["hpwl"]) if sp.get("overflow", 1) == 0 else None

    return dict(dataset=name, budget=budget,
                skyline_ils=main_best, bstar=bstar_best, sp_aga=sp_best)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="n100,n200,n300")
    ap.add_argument("--budget", type=float, default=15.0,
                    help="各算法统一墙钟预算（秒）")
    args = ap.parse_args()
    names = [s.strip() for s in args.datasets.split(",") if s.strip()]
    rows = []
    for name in names:
        print(f"[fair] {name} budget={args.budget}s", flush=True)
        r = fair_run(name, args.budget)
        rows.append(r)
        print(f"   {r}", flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "q2_fair.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    _plot(rows)
    print("saved q2_fair.json / q2_fair.png")


def _plot(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    names = {f.name for f in font_manager.fontManager.ttflist}
    cjk = next((n for n in ["Microsoft YaHei", "SimHei", "SimSun"] if n in names),
               "sans-serif")
    plt.rcParams.update({"font.sans-serif": [cjk, "Arial"],
                         "axes.unicode_minus": False})
    labels = ["Skyline-ILS/SA", "B*-树-SA", "SP-AGA"]
    keys = ["skyline_ils", "bstar", "sp_aga"]
    x = np.arange(len(rows))
    w = 0.26
    colors = ["#4C72B0", "#DD8452", "#C44E52"]
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    for j, (lab, key) in enumerate(zip(labels, keys)):
        vals = [r[key] for r in rows]
        ax.bar(x + (j - 1) * w, [v if v is not None else 0 for v in vals],
               w, label=lab, color=colors[j])
        for xi, v in zip(x + (j - 1) * w, vals):
            if v is None:
                ax.text(xi, 0, "未达可行", ha="center", va="bottom", fontsize=6.5)
            else:
                ax.text(xi, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=6.5)
    ax.set_xticks(x)
    ax.set_xticklabels([r["dataset"] for r in rows])
    ax.set_ylabel("总 HPWL（越低越好）")
    ax.set_title(f"问题二 统一时间预算公平对比（每算法 {rows[0]['budget']:.0f}s）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "q2_fair.png"), dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    main()
