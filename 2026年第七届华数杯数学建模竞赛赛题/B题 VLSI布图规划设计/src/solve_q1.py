"""问题一主求解入口：四层框架落地。

L1 多源初解池 → L2 并行多目标元启发（Skyline+ILS 主 / B*-树+SA 对照）
→ L3 双向反馈定界（密度 gap / CP-SAT 子集证书）→ L4 配置适配。

输出：
  * 三组芯片的轮廓面积、长宽比、密度与摆放可视化；
  * "多起点 vs 单起点"收敛对比表与曲线；
  * "密度 gap"表（上界证书 / 下界）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCENARIOS                     # noqa: E402
from data_io import load_dataset, dataset_stats  # noqa: E402
from layer1_pool import generate_initial_pool, diversity_filter  # noqa: E402
from layer2_search import (                       # noqa: E402
    width_bounds, width_grid, ils_trajectory, final_width_sweep,
    strong_perturb, run_parallel, _worker_area, _worker_bstar,
)
from layer3_bound import (                        # noqa: E402
    lower_bounds, gap_report, check_feasible, cp_sat_subset_feasible,
)
from bstar import BStarTree                        # noqa: E402
from visualize import plot_layout, plot_convergence  # noqa: E402


def solve_dataset(ds, cfg):
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n
    A = ds.total_area
    w_lb, w_ub = width_bounds(widths, heights)
    wgrid = width_grid(widths, heights, n=max(5, min(8, cfg.kp)))
    W0 = int(round(np.sqrt(A)))
    t0 = time.time()

    # ---- L1 多源初解生成池 + 多样性粗筛 ----
    rng = np.random.default_rng(cfg.seed)
    pool = generate_initial_pool(ds, rng, prob_rot=0.3, strip_w=W0)
    pool = diversity_filter(pool, cfg.kp)

    # ---- L2 主算法：Skyline+ILS 多起点并行（固定条带宽，覆盖宽度网格）----
    tasks = [
        (_worker_area, dict(widths=widths, heights=heights, order=sol["order"],
                            rot=sol["rot"].tolist(),
                            W=wgrid[i % len(wgrid)], budget_s=cfg.t_ils,
                            seed=cfg.seed + i * 101 + 7, phase="area"))
        for i, sol in enumerate(pool)
    ]
    results = [r for r in run_parallel(tasks, cfg.nproc) if r is not None]

    # ---- L2 精英池 + 扰动重启（在精英解宽度邻域内）----
    elites = sorted(results, key=lambda r: (r["area"], r["asp"]))[:3]
    rng2 = np.random.default_rng(cfg.seed + 999)
    restart_tasks = []
    for j, el in enumerate(elites):
        o2, r2 = strong_perturb(el["order"], np.asarray(el["rot"]), n, rng2)
        Wr = max(w_lb, min(w_ub, el["W"] + (j - 1) * 3))
        restart_tasks.append(
            (_worker_area, dict(widths=widths, heights=heights, order=o2,
                                rot=r2.tolist(), W=Wr, budget_s=cfg.t_restart,
                                seed=cfg.seed + 5000 + j * 17, phase="area"))
        )
    results += [r for r in run_parallel(restart_tasks, cfg.nproc) if r is not None]

    # ---- L2 长宽比精调（字典序第二级：面积不增，压 |W/H-1|）----
    s_area = min(r["area"] for r in results)
    aspect_tasks = []
    for j, el in enumerate(elites):
        Wasp = max(w_lb, min(w_ub, el["W"] + (j - 1) * 2))
        aspect_tasks.append(
            (_worker_area, dict(widths=widths, heights=heights, order=el["order"],
                                rot=el["rot"], W=Wasp, budget_s=cfg.t_aspect,
                                seed=cfg.seed + 10000 + j * 13, phase="aspect",
                                s_area=s_area))
        )
    results += [r for r in run_parallel(aspect_tasks, cfg.nproc) if r is not None]

    # ---- L2 对照算法：B*-树 + 模拟退火 ----
    bound_b = int(max(widths.sum(), heights.sum())) + 10
    bstar_tasks = []
    for j, el in enumerate(elites[:2]):
        tree = BStarTree.from_shelf(widths, heights, el["order"],
                                    np.asarray(el["rot"]), int(el["W"]))
        bstar_tasks.append(
            (_worker_bstar, dict(widths=widths, heights=heights, rot=tree.rot.tolist(),
                                 root=int(tree.root), parent=tree.parent.tolist(),
                                 left=tree.left.tolist(), right=tree.right.tolist(),
                                 bound_w=bound_b, budget=cfg.t_bstar,
                                 seed=cfg.seed + 7000 + j * 19))
        )
    bstar_results = [r for r in run_parallel(bstar_tasks, cfg.nproc) if r is not None]

    # ---- 全局条带宽全扫：落实字典序（面积最小 → 长宽比最接近1）----
    top = sorted(results, key=lambda r: (r["area"], r["asp"]))[:5]
    finals = []
    for r in top:
        f = final_width_sweep(r["order"], r["rot"], widths, heights, w_lb, w_ub,
                              phase="area")
        if f is not None:
            finals.append(f)
    if bstar_results:
        bb = min(bstar_results, key=lambda r: (r["area"], r["asp"]))
        finals.append(bb)
    final = min(finals, key=lambda r: (r["area"], r["asp"]))

    # ---- L3 校验与定界 ----
    ok, _ = check_feasible(ds, final["xs"], final["ys"], final["rw"], final["rh"],
                           final["W"], final["H"])
    lb = lower_bounds(ds)
    gap = gap_report(ds, final["W"], final["H"])
    cp = cp_sat_subset_feasible(ds, final["W"], final["H"], cfg.cp_subset,
                                cfg.cp_timeout)
    runtime = time.time() - t0

    bstar_best = min(bstar_results, key=lambda r: (r["area"], r["asp"])) \
        if bstar_results else None
    return dict(
        dataset=ds.name, final=final, feasible=ok, bounds=lb, gap=gap, cp=cp,
        runtime=runtime, traces=[r["trace"] for r in results],
        results_area=[(r["area"], r["asp"]) for r in results],
        bstar=(None if bstar_best is None else
               (bstar_best["W"], bstar_best["H"], bstar_best["area"],
                bstar_best["asp"])),
        pool=[(s["key"], s["W"], s["H"], s["area"], s["cost"]) for s in pool],
    )


def _fmt_area_table(results):
    rows = []
    for r in results:
        A = r["bounds"]["A"]
        rows.append((r["dataset"], r["final"]["W"], r["final"]["H"],
                     r["final"]["area"], A, r["gap"]["density"],
                     r["gap"]["gap_pct"], r["final"]["asp"], r["feasible"]))
    return rows


def _save_placement(ds, final, out_dir):
    """保存模块摆放结果文件（名称 x y w h 是否旋转）。"""
    lines = [f"# {ds.name}  Q1 placement  W={final['W']} H={final['H']}"]
    for i in range(ds.n):
        lines.append(f"{ds.names[i]} {final['xs'][i]} {final['ys'][i]} "
                     f"{final['rw'][i]} {final['rh'][i]} {int(final['rot'][i])}")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f"q1_{ds.name}_placement.txt"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="问题一：最小面积/长宽比 Packing")
    parser.add_argument("--data-dir", default=os.path.normpath(os.path.join(here, "..", "附件")))
    parser.add_argument("--out-dir", default=os.path.normpath(os.path.join(here, "..", "result")))
    parser.add_argument("--datasets", default="n100,n200,n300")
    parser.add_argument("--nproc", type=int, default=6)
    parser.add_argument("--scale", type=float, default=1.0,
                        help="时间预算缩放系数（快速测试用）")
    parser.add_argument("--cp", action="store_true", help="启用 CP-SAT 子集证书")
    args = parser.parse_args()

    cfg = SCENARIOS["Q1"]
    cfg.nproc = args.nproc
    cfg.out_dir = args.out_dir
    cfg.t_ils *= args.scale
    cfg.t_bstar *= args.scale
    cfg.t_aspect *= args.scale
    cfg.t_restart *= args.scale
    if not args.cp:
        cfg.cp_timeout = 0
    cfg.kp = max(2, int(round(cfg.kp * args.scale)))

    datasets = [s.strip() for s in args.datasets.split(",") if s.strip()]
    results = []
    for name in datasets:
        ds = load_dataset(args.data_dir, name)
        print(f"\n===== 数据集 {name}  {dataset_stats(ds)} =====", flush=True)
        r = solve_dataset(ds, cfg)
        results.append(r)
        f = r["final"]
        print(f"  轮廓: {f['W']} × {f['H']}  面积: {f['area']}  "
              f"密度: {r['gap']['density']*100:.2f}%  "
              f"长宽比: {f['asp']:.3f}  可行: {r['feasible']}", flush=True)

    # ---- 结果表 ----
    rows = _fmt_area_table(results)
    print("\n" + "=" * 82)
    print("表1  三组芯片问题一求解结果")
    print("=" * 82)
    print(f"{'数据集':<8}{'轮廓W':>7}{'轮廓H':>7}{'面积S':>9}{'总面积A':>10}"
          f"{'密度ρ':>9}{'gap(1-ρ)':>10}{'长宽比':>9}{'可行':>6}")
    for row in rows:
        ds, W, H, S, A, rho, gpct, asp, ok = row
        print(f"{ds:<8}{W:>7}{H:>7}{S:>9}{A:>10}{rho*100:>8.2f}%{gpct:>9.2f}%"
              f"{asp:>9.3f}{'是' if ok else '否':>6}")

    lb_rows = [(r["dataset"], r["bounds"]["A"], r["bounds"]["S_lb"],
                r["final"]["area"], r["final"]["area"] / r["bounds"]["S_lb"])
               for r in results]
    print("\n" + "=" * 82)
    print("表2  密度 gap 表（下界与可行证书）")
    print("=" * 82)
    print(f"{'数据集':<8}{'面积下界S_lb':>14}{'上界(证书)S_ub':>16}{'gap':>10}")
    for name, A, S_lb, S_ub, _ in lb_rows:
        print(f"{name:<8}{S_lb:>14}{S_ub:>16}{(S_ub/S_lb-1)*100:>9.2f}%")

    # ---- 多起点 vs 单起点收敛表 ----
    print("\n" + "=" * 100)
    print("表3  多起点与单起点收敛对比（各时间点已得最优面积，越小越好）")
    print("=" * 100)
    hdr = f"{'数据集':<8}{'起点数':>6}{'t=25%':>12}{'t=50%':>12}{'t=75%':>12}{'t=100%':>12}"
    print(hdr + "   (多起点累积最优)         " + "单起点(最优轨迹)")
    for r in results:
        traces = r["traces"]
        tmax = max((tr[-1][0] for tr in traces), default=1.0)
        fracs = (0.25, 0.5, 0.75, 1.0)
        multi = []
        for frac in fracs:
            t = frac * tmax
            best = min((a for tr in traces for tt, a, _ in tr if tt <= t),
                       default=float("inf"))
            multi.append(best)
        single_row = []
        if traces:
            sorted_tr = sorted(traces, key=lambda tr: tr[0][1])
            tr = sorted_tr[len(sorted_tr) // 2]      # 中位初解（典型单跑）
            for frac in fracs:
                vals = [a for tt, a, _ in tr if tt <= frac * tmax]
                single_row.append(vals[-1] if vals else tr[0][1])
        def fmt(v):
            return "—" if v == float("inf") else f"{v:>12,}"
        print(f"{r['dataset']:<8}{len(traces):>6}"
              f"{fmt(multi[0])}{fmt(multi[1])}{fmt(multi[2])}{fmt(multi[3])}"
              f"   |  {fmt(single_row[0])}{fmt(single_row[1])}{fmt(single_row[2])}{fmt(single_row[3])}")

    # ---- 主算法 vs 对照算法（B*-树+SA） ----
    print("\n" + "=" * 100)
    print("表4  主算法 Skyline+ILS 与 对照算法 B*-树+SA 结果对比")
    print("=" * 100)
    print(f"{'数据集':<8}{'ILS 轮廓':>12}{'ILS 面积':>12}{'ILS 密度':>10}"
          f"{'B*树 轮廓':>12}{'B*树 面积':>12}{'B*树 密度':>10}")
    for r in results:
        f = r["final"]
        bb = r["bstar"]
        bstr = f"{bb[0]}×{bb[1]}" if bb else "—"
        barea = f"{bb[2]:,}" if bb else "—"
        bd = f"{r['bounds']['A'] / bb[2] * 100:.2f}%" if bb else "—"
        print(f"{r['dataset']:<8}{f'{f['W']}×{f['H']}':>12}{f['area']:>12,}"
              f"{r['gap']['density'] * 100:>9.2f}%{bstr:>12}{barea:>12}{bd:>10}")

    # ---- CP-SAT 子集证书 ----
    if args.cp:
        print("\n" + "=" * 100)
        print("表5  CP-SAT 小规模子集可行性证书（L3 定界验证）")
        print("=" * 100)
        for r in results:
            status, cnt, el = r["cp"]
            print(f"{r['dataset']:<8} 子集规模(面积最大块数): {cnt:>3}  状态: {status:<10}  "
                  f"耗时: {el:.1f}s")

    # ---- 可视化 ----
    for r in results:
        ds_name = r["dataset"]
        f = r["final"]
        plot_layout(
            load_dataset(args.data_dir, ds_name), f["xs"], f["ys"], f["rw"], f["rh"],
            f["W"], f["H"],
            os.path.join(args.out_dir, f"q1_{ds_name}_layout.png"),
            title=f"问题一  {ds_name}  模块摆放",
            density=r["gap"]["density"], aspect=f["asp"])
        plot_convergence(r["traces"],
                         os.path.join(args.out_dir, f"q1_{ds_name}_convergence.png"))

    # ---- 保存结果文件 ----
    summary = []
    for r in results:
        f = r["final"]
        ds = load_dataset(args.data_dir, r["dataset"])
        _save_placement(ds, f, args.out_dir)
        summary.append(dict(
            dataset=r["dataset"], n=ds.n, A=r["bounds"]["A"],
            S_lb=r["bounds"]["S_lb"], W=f["W"], H=f["H"], area=f["area"],
            density=round(r["gap"]["density"], 6),
            gap=round(r["gap"]["gap_pct"], 4), aspect=round(f["asp"], 6),
            feasible=r["feasible"], runtime=round(r["runtime"], 1),
            bstar=(dict(W=r["bstar"][0], H=r["bstar"][1], area=r["bstar"][2])
                   if r["bstar"] else None),
        ))
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "q1_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"\n结果与可视化已输出至: {os.path.abspath(args.out_dir)}")


if __name__ == "__main__":
    main()
