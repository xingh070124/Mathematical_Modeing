"""问题四主求解入口：L/T 型异形模块最小包围盒 Packing（矩形切割 + 刚性链接）。

沿用问题一四层框架（L4 配置 Q4：shape=polyomino, rotation=C4, outline=free,
objective=area），第 1-3 层复用主线，仅把"放置单个矩形"改为"放置带刚性链接
的复合矩形对象"：
  L1 多源初解（复合形状 Skyline/BL）→ L2 并行元启发（复合 Skyline-ILS 主 ·
     B*-树-包围盒近似对照）→ L3 双向反馈定界（面积下界 + 因子枚举 + 精确 DFS）
  → L4 场景适配。

验证实例（图3 四模块，A=24）：精确 DFS 在面积 24 的因子对上检验可铺砌性，
预期 S*=24（6×4，密度 100%，凹凸咬合消除死区）。
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SCENARIOS                      # noqa: E402
from polyomino import (                            # noqa: E402
    CompoundModule, pack_compound, bbox_of_modules,
)
from exact_q4 import factor_pairs, exact_pack, find_optimal  # noqa: E402
from bstar import BStarTree                        # noqa: E402
from bstar import bstar_sa_solve                   # noqa: E402
from visualize import plot_layout_q4               # noqa: E402


# --------------------------------------------------------------------------- #
# 验证实例：四模块（图3）定义（《问题4_数学建模.md》第六节）
# --------------------------------------------------------------------------- #
def build_instance():
    """返回 4 个复合模块列表（b1 T型、b2 L型、b3/b4 矩形）。"""
    return [
        CompoundModule("b1", [(4, 2, 0, 2), (2, 2, 1, 0)]),   # T型：顶杆4×2@(0,2)+中杆2×2@(1,0)
        CompoundModule("b2", [(1, 4, 0, 0), (1, 2, 1, 0)]),   # L型：左条1×4@(0,0)+右下块1×2@(1,0)
        CompoundModule("b3", [(2, 1, 0, 0)]),                 # 矩形 2×1
        CompoundModule("b4", [(1, 4, 0, 0)]),                 # 矩形 1×4
    ]


# --------------------------------------------------------------------------- #
# L1：多源初解生成池（复合形状 Skyline/BL）
# --------------------------------------------------------------------------- #
def _orders(widths, heights, rng):
    n = len(widths)
    area = widths * heights
    longside = np.maximum(widths, heights)
    orders = {
        "area_desc": np.argsort(-area, kind="stable").tolist(),
        "long_desc": np.argsort(-longside, kind="stable").tolist(),
        "perim_desc": np.argsort(-(widths + heights), kind="stable").tolist(),
        "lff": np.argsort(-np.abs(widths - heights), kind="stable").tolist(),
        "area_asc": np.argsort(area, kind="stable").tolist(),
        "width_desc": np.argsort(-widths, kind="stable").tolist(),
    }
    for j in range(8):
        orders[f"rand_{j}"] = rng.permutation(n).tolist()
    return orders


def generate_pool(modules, cfg, seed):
    """L1：多排序规则 + auto_rotate 贪心，生成初解池（保留可行者）。"""
    rng = np.random.default_rng(seed)
    widths = np.array([m.bbox[0] for m in modules], dtype=np.int64)
    heights = np.array([m.bbox[1] for m in modules], dtype=np.int64)
    orders = _orders(widths, heights, rng)
    bound_w = int(sum(max(m.bbox[0], m.bbox[1]) for m in modules)) + 10
    bound_h = bound_w
    pool = []
    for key, order in orders.items():
        res = pack_compound(modules, order, None, bound_w, bound_h,
                            auto_rotate=True)
        if res is None:
            continue
        xs, ys, rot, W, H = res
        pool.append(dict(key=key, order=order, rot=rot, xs=xs, ys=ys,
                         W=int(W), H=int(H), area=int(W) * int(H),
                         asp=abs(W / H - 1.0)))
    return pool


# --------------------------------------------------------------------------- #
# L2 主算法：复合 Skyline-ILS（字典序面积 → 长宽比）
# --------------------------------------------------------------------------- #
def _perturb(order, rot, n, rng):
    order2 = list(order)
    rot2 = rot.copy()
    k = max(1, min(3, n // 4))
    idx = sorted(rng.choice(n, k, replace=False), reverse=True)
    vals = [order2[i] for i in idx]
    for v in vals:
        order2.remove(v)
    rng.shuffle(vals)
    posns = sorted(rng.integers(0, len(order2) + 1, size=len(vals)))
    for v, p in zip(vals, posns):
        order2.insert(p, v)
    for _ in range(int(rng.integers(1, 3))):
        m = int(rng.integers(0, n))
        rot2[m] = (rot2[m] + int(rng.integers(1, 4))) % 4
    if rng.random() < 0.3:
        a = int(rng.integers(0, n))
        b = int(rng.integers(0, n))
        lo, hi = min(a, b), max(a, b)
        order2[lo:hi + 1] = order2[lo:hi + 1][::-1]
    return order2, rot2


def ils_trajectory(modules, order, rot, budget_s, seed):
    """单条复合 Skyline-ILS 轨迹：字典序目标 (面积, |W/H-1|)。"""
    rng = np.random.default_rng(seed)
    n = len(modules)
    widths = np.array([m.bbox[0] for m in modules], dtype=np.int64)
    heights = np.array([m.bbox[1] for m in modules], dtype=np.int64)
    bound_w = int(sum(max(m.bbox[0], m.bbox[1]) for m in modules)) + 10
    bound_h = bound_w

    def eval_sol(o, r):
        res = pack_compound(modules, o, r, bound_w, bound_h)
        if res is None:
            return None
        xs, ys, rot, W, H = res
        return dict(order=o, rot=rot, xs=xs, ys=ys, W=int(W), H=int(H),
                    area=int(W) * int(H), asp=abs(W / H - 1.0))

    cur = eval_sol(list(order), np.asarray(rot, dtype=np.int64).copy())
    if cur is None:
        return None
    best = dict(cur)
    T = 200.0
    alpha = 0.96
    start = time.time()
    it = 0
    trace = [(0.0, best["area"], best["asp"])]
    while time.time() - start < budget_s:
        o2, r2 = _perturb(cur["order"], cur["rot"], n, rng)
        cand = eval_sol(o2, r2)
        if cand is None:
            continue
        it += 1
        delta = (cand["area"], cand["asp"]) < (cur["area"], cur["asp"])
        cost_delta = (cand["area"] - cur["area"]) * 10_000_000 \
            + (cand["asp"] - cur["asp"]) * 1_000_000
        if delta or rng.random() < np.exp(-max(cost_delta, 0) / T):
            cur = cand
            if (cand["area"], cand["asp"]) < (best["area"], best["asp"]):
                best = dict(cand)
        T = max(T * alpha, 1.0)
        if it % 300 == 0:
            trace.append((time.time() - start, best["area"], best["asp"]))
    best["iterations"] = it
    best["trace"] = trace
    return best


# --------------------------------------------------------------------------- #
# L2 对照：B*-树-包围盒近似
# --------------------------------------------------------------------------- #
def bstar_bbox_solve(modules, budget_s, seed):
    """把异形模块按包围盒矩形做 B*-树+SA（明确局限：无法咬合，密度 < 100%）。"""
    n = len(modules)
    widths = np.array([m.bbox[0] for m in modules], dtype=np.int64)
    heights = np.array([m.bbox[1] for m in modules], dtype=np.int64)
    order = list(range(n))
    rng = np.random.default_rng(seed)
    rng.shuffle(order)
    rot = np.zeros(n, dtype=np.int64)
    bound_w = int(max(widths.sum(), heights.sum())) + 10
    tree = BStarTree.from_shelf(widths, heights, order, rot, int(bound_w // 2))
    res = bstar_sa_solve(widths, heights, tree.rot.tolist(), int(tree.root),
                         tree.parent.tolist(), tree.left.tolist(),
                         tree.right.tolist(), bound_w,
                         budget_s, seed=seed)
    return dict(W=res["W"], H=res["H"], area=res["W"] * res["H"],
                asp=abs(res["W"] / res["H"] - 1.0))


# --------------------------------------------------------------------------- #
# 主流程
# --------------------------------------------------------------------------- #
def solve_dataset(cfg, seed):
    modules = build_instance()
    A = sum(m.area for m in modules)
    t0 = time.time()

    # ---- L1 初解池 ----
    pool = generate_pool(modules, cfg, seed)

    # ---- L2 主算法：多起点复合 Skyline-ILS ----
    results = []
    for i, sol in enumerate(pool[:cfg.kp]):
        r = ils_trajectory(modules, sol["order"], sol["rot"],
                           cfg.t_ils, seed + i * 101 + 7)
        if r is not None:
            results.append(r)
    if results:
        best = min(results, key=lambda r: (r["area"], r["asp"]))
    else:
        best = None

    # ---- L2 对照：B*-树-包围盒 ----
    bstar_res = bstar_bbox_solve(modules, cfg.t_bstar, seed + 7000)

    # ---- L3 精确验证：因子枚举 + 首空位 DFS ----
    S_star, W_star, H_star, exact_sol, trials = find_optimal(modules)

    # 用精确解作为最终答案（可证明最优）
    if exact_sol is not None:
        final = dict(W=W_star, H=H_star, area=W_star * H_star,
                     asp=abs(W_star / H_star - 1.0), sol=exact_sol,
                     source="exact")
    elif best is not None:
        final = dict(W=best["W"], H=best["H"], area=best["area"],
                     asp=best["asp"], sol=dict(zip(range(len(modules)),
                                                   zip(best["xs"], best["ys"],
                                                       best["rot"]))),
                     source="heuristic")
    else:
        final = None

    runtime = time.time() - t0
    return dict(
        dataset="q4", A=A, modules=modules, pool=pool, ils=results,
        bstar=bstar_res, exact=(S_star, W_star, H_star, exact_sol, trials),
        final=final, runtime=runtime,
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="问题四：L/T 型异形模块最小包围盒")
    parser.add_argument("--out-dir", default=os.path.normpath(os.path.join(here, "..", "result")))
    parser.add_argument("--nproc", type=int, default=4)
    parser.add_argument("--scale", type=float, default=1.0,
                        help="时间预算缩放系数（快速测试用）")
    args = parser.parse_args()

    cfg = SCENARIOS["Q4"]
    cfg.nproc = args.nproc
    cfg.t_ils *= args.scale
    cfg.t_bstar *= args.scale
    cfg.kp = max(2, int(round(cfg.kp * args.scale)))
    out_root = os.path.join(args.out_dir, "question 4")
    os.makedirs(out_root, exist_ok=True)

    r = solve_dataset(cfg, cfg.seed)
    modules = r["modules"]
    A = r["A"]

    # ---- 结果打印 ----
    print("\n" + "=" * 76)
    print("问题四：L/T 型异形模块最小包围盒 Packing")
    print("=" * 76)
    print(f"模块总面积 A = {A}")
    for m in modules:
        print(f"  {m.name}: 子块 {m.subblocks}  面积={m.area}  包围盒={m.bbox}")

    print("\n-- L3 精确验证：面积因子枚举 --")
    S_star, W_star, H_star, exact_sol, trials = r["exact"]
    for W, H, ok in trials:
        print(f"  {W}*{H}: {'可行' if ok else '不可行'}")
    if exact_sol is not None:
        print(f"最小面积 S* = {S_star}  ({W_star}×{H_star})  密度 = "
              f"{A / (W_star * H_star) * 100:.1f}%")
        print("最优摆放（旋转 / 锚点）：")
        for m in range(len(modules)):
            x, y, rr = exact_sol[m]
            print(f"  {modules[m].name}: r={rr*90}° 锚点=({x},{y})")

    print("\n-- L2 主算法（复合 Skyline-ILS）vs 对照（B*-树包围盒） --")
    if r["ils"]:
        b = min(r["ils"], key=lambda x: (x["area"], x["asp"]))
        print(f"  Skyline-ILS: {b['W']}×{b['H']}  面积={b['area']}  "
              f"密度={A / b['area'] * 100:.1f}%")
    if r["bstar"]:
        bb = r["bstar"]
        print(f"  B*-树(包围盒): {bb['W']}×{bb['H']}  面积={bb['area']}  "
              f"密度={A / bb['area'] * 100:.1f}%  （无法咬合，面积偏大）")

    print(f"\n耗时 {r['runtime']:.1f}s")

    # ---- 可视化 ----
    if r["final"] is not None:
        plot_layout_q4(
            modules, r["final"]["sol"], r["final"]["W"], r["final"]["H"],
            os.path.join(out_root, "q4_layout.png"),
            title=f"问题四  4 模块最小包围盒  S*={r['final']['area']} "
                  f"({r['final']['W']}×{r['final']['H']})",
            area=r["final"]["area"], density=A / r["final"]["area"],
            aspect=r["final"]["asp"])

    # ---- 保存 ----
    exact_placements = None
    if exact_sol is not None:
        exact_placements = [
            dict(module=modules[m].name, rot=int(exact_sol[m][2]),
                 anchor=[int(exact_sol[m][0]), int(exact_sol[m][1])])
            for m in range(len(modules))
        ]
    summary = dict(
        dataset="q4", total_area=A, S_star=int(S_star) if S_star else None,
        W=int(W_star) if W_star else None, H=int(H_star) if H_star else None,
        density=round(A / (W_star * H_star), 6) if W_star else None,
        trials=[{"W": int(W), "H": int(H), "ok": bool(ok)} for W, H, ok in trials],
        exact_placements=exact_placements,
        bstar_area=r["bstar"]["area"] if r["bstar"] else None,
        runtime=round(r["runtime"], 1),
    )
    with open(os.path.join(out_root, "q4_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
    print(f"\n结果与可视化已输出至: {os.path.abspath(out_root)}")


if __name__ == "__main__":
    main()
