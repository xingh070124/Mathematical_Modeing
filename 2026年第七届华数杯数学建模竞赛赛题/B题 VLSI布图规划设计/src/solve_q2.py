"""问题二主求解入口：四层框架落地（L4 配置 Q2 适配）。

L1 终端感知初解池 → L2 并行元启发（Skyline+ILS/SA 主 / B*-树+SA、SP+AGA 对照）
→ L3 双向反馈定界（凸松弛下界 + 可行证书 + gap）→ L4 场景适配。

主算法说明：B*-树只能表示"左紧致"类 packing，是 Skyline 可达空间的真子集，
且从不可行货架种子出发浪费预算修复越界；Skyline+ILS/SA 将固定轮廓约束内建
于装箱，每次评估都是可行解，实测 HPWL 更优（统一 NetIndex 精确口径）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCENARIOS                      # noqa: E402
from data_io import load_dataset, dataset_stats   # noqa: E402
from hpwl import NetIndex, overflow                # noqa: E402
from layer1_pool_q2 import (                       # noqa: E402
    generate_initial_pool_q2, diversity_filter_q2,
)
from skyline_ils_q2 import ils_hpwl_trajectory     # noqa: E402
from bstar import BStarTree                        # noqa: E402
from bstar_q2 import bstar_hpwl_sa_solve           # noqa: E402
from sp_ga import sp_aga_solve                     # noqa: E402
from layer3_bound_q2 import (                      # noqa: E402
    lower_bound_hpwl, check_feasible_q2, gap_report_q2,
)
from refine_q2 import refine_hpwl                  # noqa: E402
from visualize import plot_layout_q2, plot_convergence_q2  # noqa: E402


def _worker_ils(task):
    from skyline_ils_q2 import ils_hpwl_trajectory
    return ils_hpwl_trajectory(**task)


def _worker_bstar(task):
    from bstar_q2 import bstar_hpwl_sa_solve
    return bstar_hpwl_sa_solve(**task)


def _worker_sp(task):
    from sp_ga import sp_aga_solve
    return sp_aga_solve(**task)


def build_seed_tree(widths, heights, order, rot, Lhat):
    """在 Lhat 附近扫描货架宽，取首个合法（无越界）的 B*-树作为初始解。

    货架宽越大则货架数越少、高度越低，故从 Lhat 向上扫描必能找到合法树
    （极端情形整行单货架宽=Σw，高=单模块高度，必然可行）。
    用二分在 [Lhat, Σw] 中找最小可行货架宽（该宽度下解码高度最小、越界最少）。
    """
    lo, hi = Lhat, int(np.sum(widths)) + 1
    if hi <= lo:
        hi = lo + 1
    best = None
    while lo <= hi:
        Wt = (lo + hi) // 2
        tree = BStarTree.from_shelf(widths, heights, order, rot, Wt)
        xs, ys, rw, rh, W, H = tree.decode()
        if overflow(xs, ys, rw, rh, Lhat) == 0:
            best = (tree, Wt)
            hi = Wt - 1
        else:
            lo = Wt + 1
    if best is not None:
        return best[0]
    return BStarTree.from_shelf(widths, heights, order, rot, Lhat)


def run_parallel(tasks, nproc):
    if nproc <= 1 or len(tasks) <= 1:
        return [fn(task) for fn, task in tasks]
    out = []
    with ProcessPoolExecutor(max_workers=nproc) as ex:
        futs = [ex.submit(fn, task) for fn, task in tasks]
        for f in futs:
            out.append(f.result())
    return out


def solve_dataset(ds, cfg, net):
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n
    A = ds.total_area
    Lhat = int(np.ceil(np.sqrt(A * (1.0 + 0.15))))
    t0 = time.time()

    # ---- L1 终端感知初解池 + 多样性粗筛 ----
    rng = np.random.default_rng(cfg.seed)
    pool = generate_initial_pool_q2(ds, net, Lhat, rng, prob_rot=0.3)
    pool = diversity_filter_q2(pool, cfg.kp)

    # ---- L2 主算法：Skyline + ILS/SA 多起点并行（可行域内直接优化 HPWL）----
    tasks = []
    for i, sol in enumerate(pool):
        tasks.append((
            _worker_ils,
            dict(widths=widths, heights=heights, order=sol["order"],
                 rot=np.asarray(sol["rot"], dtype=np.int64),
                 net=net, Lhat=Lhat,
                 budget_s=cfg.t_ils, seed=cfg.seed + i * 101 + 7)
        ))
    results = [r for r in run_parallel(tasks, cfg.nproc) if r is not None]

    # ---- L2 精英池 + 强扰动重启 ----
    elites = sorted(results, key=lambda r: r["hpwl"])[:3]
    rng2 = np.random.default_rng(cfg.seed + 999)
    restart_tasks = []
    for j, el in enumerate(elites):
        o2 = el["order"][:]
        r2 = el["rot"].copy()
        # 重排大片 + 翻转旋转（强扰动）
        k = max(2, n // 6)
        idx = sorted(rng2.choice(n, k, replace=False), reverse=True)
        vals = [o2[i] for i in idx]
        for v in vals:
            o2.remove(v)
        rng2.shuffle(vals)
        posns = sorted(rng2.integers(0, len(o2) + 1, size=len(vals)))
        for v, p in zip(vals, posns):
            o2.insert(p, v)
        flip = rng2.choice(n, max(1, n // 5), replace=False)
        r2[flip] ^= 1
        restart_tasks.append((
            _worker_ils,
            dict(widths=widths, heights=heights, order=o2, rot=r2,
                 net=net, Lhat=Lhat,
                 budget_s=cfg.t_restart, seed=cfg.seed + 5000 + j * 17)
        ))
    results += [r for r in run_parallel(restart_tasks, cfg.nproc) if r is not None]

    # ---- L2 对照算法 1：B*-树 + SA（增量 HPWL + 自适应γ）----
    bound_w = int(max(widths.sum(), heights.sum())) + 10
    bstar_tasks = []
    for i, sol in enumerate(pool[:2]):
        tree = build_seed_tree(widths, heights, sol["order"],
                               np.asarray(sol["rot"]), Lhat)
        bstar_tasks.append((
            _worker_bstar,
            dict(widths=widths, heights=heights, rot=tree.rot.tolist(),
                 root=int(tree.root), parent=tree.parent.tolist(),
                 left=tree.left.tolist(), right=tree.right.tolist(),
                 bound_w=bound_w, net=net, Lhat=Lhat,
                 budget_s=cfg.t_bstar, seed=cfg.seed + 3000 + i * 19,
                 init=sol)
        ))
    bstar_res = [r for r in run_parallel(bstar_tasks, cfg.nproc) if r is not None]

    # ---- L2 对照算法 2：SP + 自适应遗传算法 ----
    sp_task = (_worker_sp,
               dict(widths=widths, heights=heights, net=net, Lhat=Lhat,
                    budget_s=cfg.t_sp, seed=cfg.seed + 7000))
    sp_res = run_parallel([sp_task], cfg.nproc)[0]

    # ---- 取主算法最优可行解（主算法天然可行；补对照候选）----
    candidates = [dict(xs=p["xs"], ys=p["ys"], rw=p["rw"], rh=p["rh"],
                       W=p["W"], H=p["H"], hpwl=p["hpwl"], overflow=p["overflow"],
                       rot=np.asarray(p["rot"], dtype=np.int64))
                  for p in pool]
    for r in results:
        candidates.append(dict(xs=r["xs"], ys=r["ys"], rw=r["rw"], rh=r["rh"],
                               W=int((r["xs"] + r["rw"]).max()),
                               H=int((r["ys"] + r["rh"]).max()),
                               hpwl=r["hpwl"], overflow=0,
                               rot=r["rot"]))
    for r in bstar_res:
        if r["overflow"] == 0:
            candidates.append(r)
    feasible = [c for c in candidates if c["overflow"] == 0]
    if feasible:
        best = min(feasible, key=lambda r: r["hpwl"])
    else:
        best = min(candidates, key=lambda r: (r["overflow"], r["hpwl"]))

    # ---- L2b 终端引力合法化精调（PeF 后处理）----
    if best["overflow"] == 0:
        rxs, rys, rrw, rrh, rhp = refine_hpwl(
            net, best["xs"], best["ys"], best["rw"], best["rh"], Lhat,
            cfg.t_refine, seed=cfg.seed + 777)
        if rhp < best["hpwl"] - 1e-9:
            best = dict(xs=rxs, ys=rys, rw=rrw, rh=rrh,
                        W=int((rxs + rrw).max()), H=int((rys + rrh).max()),
                        hpwl=rhp, overflow=0, rot=best["rot"])

    # ---- L3 双向反馈定界 ----
    hpwl_lb = lower_bound_hpwl(ds, Lhat)
    ok, max_ov, ovf = check_feasible_q2(ds, net, best["xs"], best["ys"],
                                        best["rw"], best["rh"], Lhat)
    gap = gap_report_q2(best["hpwl"], hpwl_lb)
    runtime = time.time() - t0

    bstar_best = min(bstar_res, key=lambda r: (r["overflow"], r["hpwl"])) \
        if bstar_res else None

    return dict(
        dataset=ds.name, best=best, sp=sp_res, hpwl_lb=hpwl_lb,
        feasible=ok, max_overlap=max_ov, overflow=ovf, gap=gap,
        Lhat=Lhat, runtime=runtime,
        traces=[r["trace"] for r in results],
        pool_hpwl=min((s["hpwl"] for s in pool), default=None),
        results_hpwl=[(r["hpwl"], 0) for r in results],
        bstar=(None if bstar_best is None else
               (bstar_best["hpwl"], bstar_best["overflow"])),
        pool=[(s["key"], s["hpwl"], s["overflow"]) for s in pool],
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="问题二：固定轮廓内总 HPWL 最小化")
    parser.add_argument("--data-dir", default=os.path.normpath(os.path.join(here, "..", "附件")))
    parser.add_argument("--out-dir", default=os.path.normpath(os.path.join(here, "..", "result")))
    parser.add_argument("--datasets", default="n100,n200,n300")
    parser.add_argument("--nproc", type=int, default=6)
    parser.add_argument("--scale", type=float, default=1.0,
                        help="时间预算缩放系数（快速测试用）")
    args = parser.parse_args()

    cfg = SCENARIOS["Q2"]
    cfg.nproc = args.nproc
    cfg.out_dir = args.out_dir
    cfg.t_ils *= args.scale
    cfg.t_restart *= args.scale
    cfg.t_bstar *= args.scale
    cfg.t_sp *= args.scale
    cfg.t_refine *= args.scale
    cfg.kp = max(2, int(round(cfg.kp * args.scale)))
    out_root = os.path.join(args.out_dir, "question 2")
    os.makedirs(out_root, exist_ok=True)

    datasets = [s.strip() for s in args.datasets.split(",") if s.strip()]
    results = []
    for name in datasets:
        ds = load_dataset(args.data_dir, name)
        net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
        print(f"\n===== 数据集 {name}  {dataset_stats(ds)}  =====", flush=True)
        r = solve_dataset(ds, cfg, net)
        results.append(r)
        b = r["best"]
        print(f"  轮廓: {r['Lhat']} × {r['Lhat']}  "
              f"总HPWL: {b['hpwl']:,.0f}  越界: {b['overflow']}  "
              f"可行: {r['feasible']}  gap: {r['gap']['gap_pct']:.2f}%  "
              f"耗时: {r['runtime']:.1f}s", flush=True)

    # ---- 结果表 ----
    print("\n" + "=" * 110)
    print("表1  问题二求解结果（死区比例 0.15，固定轮廓）")
    print("=" * 110)
    print(f"{'数据集':<8}{'轮廓L':>7}{'总HPWL(上界)':>14}{'凸松弛下界':>14}"
          f"{'gap':>9}{'可行':>6}{'B*树+SA':>14}{'SP+GA':>14}")
    for r in results:
        b = r["best"]
        sp_hp = f"{r['sp']['hpwl']:,.0f}" if r["sp"] else "—"
        bs_hp = f"{r['bstar'][0]:,.0f}" if r["bstar"] else "—"
        print(f"{r['dataset']:<8}{r['Lhat']:>7}{b['hpwl']:>14,.0f}"
              f"{r['hpwl_lb']:>14,.0f}{r['gap']['gap_pct']:>8.2f}%"
              f"{'是' if r['feasible'] else '否':>6}{bs_hp:>14}{sp_hp:>14}")

    # ---- 多起点收敛表 ----
    print("\n" + "=" * 100)
    print("表2  多起点 Skyline+ILS/SA 各轨迹 HPWL 分布")
    print("=" * 100)
    for r in results:
        vals = ", ".join(f"{h:,.0f}" for h, _ in r["results_hpwl"])
        print(f"{r['dataset']:<8}  轨迹数 {len(r['results_hpwl'])}:  {vals}")

    # ---- L1 初解池 ----
    print("\n" + "=" * 100)
    print("表3  L1 初解池（机制 / HPWL / 越界）")
    print("=" * 100)
    for r in results:
        row = ", ".join(f"{k}:{h:,.0f}(ovf{o})" for k, h, o in r["pool"])
        print(f"{r['dataset']:<8}  {row}")

    # ---- 可视化 ----
    for r in results:
        ds = load_dataset(args.data_dir, r["dataset"])
        net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
        b = r["best"]
        plot_layout_q2(
            ds, net, b["xs"], b["ys"], b["rw"], b["rh"], r["Lhat"],
            os.path.join(out_root, f"q2_{r['dataset']}_layout.png"),
            title=f"问题二  {r['dataset']}  模块摆放（死区15% 固定轮廓）",
            hpwl=b["hpwl"], gap_pct=r["gap"]["gap_pct"],
            feasible=r["feasible"])
        plot_convergence_q2(r["traces"], r["hpwl_lb"],
                            os.path.join(out_root, f"q2_{r['dataset']}_convergence.png"),
                            pool_hpwl=r["pool_hpwl"])

    # ---- 保存结果 ----
    summary = []
    for r in results:
        b = r["best"]
        ds = load_dataset(args.data_dir, r["dataset"])
        lines = [f"# {r['dataset']} Q2 placement  L={r['Lhat']} "
                 f"HPWL={b['hpwl']:.0f}"]
        for i in range(ds.n):
            lines.append(f"{ds.names[i]} {b['xs'][i]} {b['ys'][i]} "
                         f"{b['rw'][i]} {b['rh'][i]} {int(b['rot'][i])}")
        with open(os.path.join(out_root, f"q2_{r['dataset']}_placement.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        summary.append(dict(
            dataset=r["dataset"], Lhat=r["Lhat"], hpwl=round(b["hpwl"], 1),
            hpwl_lb=round(r["hpwl_lb"], 1),
            gap_pct=round(r["gap"]["gap_pct"], 4),
            overflow=int(b["overflow"]), feasible=r["feasible"],
            bstar_hpwl=round(r["bstar"][0], 1) if r["bstar"] else None,
            sp_hpwl=round(r["sp"]["hpwl"], 1) if r["sp"] else None,
            runtime=round(r["runtime"], 1),
        ))
    with open(os.path.join(out_root, "q2_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"\n结果与可视化已输出至: {os.path.abspath(out_root)}")


if __name__ == "__main__":
    main()
