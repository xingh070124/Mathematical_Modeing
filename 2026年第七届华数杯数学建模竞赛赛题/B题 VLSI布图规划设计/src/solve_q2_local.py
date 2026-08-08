"""问题二主求解入口：固定正方形轮廓 + HPWL 最小化。

算法：Skyline + 迭代局部搜索 (ILS) + 模拟退火 (SA)
  - Skyline 装箱直接满足固定轮廓约束（box constraint）
  - ILS 扰动放置顺序与旋转方向探索解空间
  - SA/Metropolis 接受准则跳出局部最优
  - 多起点并行 + 精英解邻域精修

输出：
  * 三组芯片的总 HPWL
  * 模块摆放可视化（含 Terminal 标注）
  * JSON 结果汇总
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
from packing import pack_skyline                 # noqa: E402
from layer3_bound import check_feasible           # noqa: E402
from visualize import plot_layout_q2              # noqa: E402


# ===================================================================
# HPWL 计算
# ===================================================================

def compute_hpwl(nets, block_centers, terminal_pos):
    """计算全部线网的总半周长线长。

    HPWL_i = (Xmax_i - Xmin_i) + (Ymax_i - Ymin_i)
    总 HPWL = Σ_i HPWL_i
    """
    total = 0
    for net in nets:
        xs, ys = [], []
        for pin in net:
            if pin in block_centers:
                x, y = block_centers[pin]
            elif pin in terminal_pos:
                x, y = terminal_pos[pin]
            else:
                continue
            xs.append(x)
            ys.append(y)
        if xs:
            total += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return int(total)


def make_centers(block_names, xs, ys, rw, rh):
    """由左下坐标与宽高计算模块中心坐标字典。"""
    return {
        block_names[i]: (int(xs[i] + rw[i] // 2), int(ys[i] + rh[i] // 2))
        for i in range(len(block_names))
    }


# ===================================================================
# Skyline 装箱 + HPWL 评估
# ===================================================================

def pack_and_eval(order, rot, widths, heights, block_names,
                  W_chip, H_chip, nets, terminal_pos):
    """在固定轮廓内 Skyline 装箱并计算 HPWL。

    Returns:
        (xs, ys, rw, rh, W, H, hpwl) 或 None（装箱失败）
    """
    bound_w = W_chip + 10
    res = pack_skyline(order, rot, widths, heights, bound_w,
                       box=(W_chip, H_chip), auto_rotate=True)
    if res is None:
        return None
    xs, ys, rw, rh, W, H = res
    if W > W_chip or H > H_chip:
        return None
    centers = make_centers(block_names, xs, ys, rw, rh)
    hpwl = compute_hpwl(nets, centers, terminal_pos)
    return xs, ys, rw, rh, int(W), int(H), hpwl


# ===================================================================
# 初始可行解搜索
# ===================================================================

def find_feasible_initial(widths, heights, block_names,
                          W_chip, H_chip, nets, terminal_pos,
                          rng, max_tries=30):
    """使用多种排序规则寻找一个可行的初始布局。

    尝试的排序规则：面积降序、长边降序、周长降序、LFF、
    面积升序、长边升序，以及若干随机排序。
    每种规则尝试无旋转和 25% 随机旋转。

    Returns:
        dict(order, rot, xs, ys, rw, rh, W, H, hpwl, label) 或 None
    """
    n = len(widths)
    area = widths * heights
    longside = np.maximum(widths, heights)
    perimeter = widths + heights
    flexibility = np.abs(widths - heights)

    orderings = [
        ("area_desc", np.argsort(-area, kind="stable").tolist()),
        ("long_desc", np.argsort(-longside, kind="stable").tolist()),
        ("perim_desc", np.argsort(-perimeter, kind="stable").tolist()),
        ("lff_desc", np.argsort(-flexibility, kind="stable").tolist()),
        ("area_asc", np.argsort(area, kind="stable").tolist()),
        ("long_asc", np.argsort(longside, kind="stable").tolist()),
    ]
    for _ in range(min(max_tries - len(orderings), 20)):
        orderings.append(("random", rng.permutation(n).tolist()))

    best = None
    for label, order in orderings:
        for use_rot in [False, True]:
            if use_rot:
                rot = (rng.random(n) < 0.25).astype(np.int64)
            else:
                rot = np.zeros(n, dtype=np.int64)

            result = pack_and_eval(order, rot, widths, heights, block_names,
                                   W_chip, H_chip, nets, terminal_pos)
            if result is not None:
                xs, ys, rw, rh, W, H, hpwl = result
                sol = dict(order=order, rot=rot,
                           xs=xs, ys=ys, rw=rw, rh=rh,
                           W=W, H=H, hpwl=int(hpwl), label=label)
                if best is None or hpwl < best['hpwl']:
                    best = sol
    return best


# ===================================================================
# 连接度驱动的初序构造
# ===================================================================

def build_connectivity_order(ds):
    """按模块在网表中的参与度降序排列。

    高度连接的模块优先放置 → 有利于减小 HPWL。
    """
    block_names = ds.names
    n = len(block_names)
    connectivity = {name: 0 for name in block_names}
    for net in ds.nets:
        for pin in net:
            if pin in connectivity:
                connectivity[pin] += 1

    areas = {name: ds.widths[i] * ds.heights[i]
             for i, name in enumerate(block_names)}
    order = sorted(range(n),
                   key=lambda i: (-connectivity[block_names[i]],
                                  -areas[block_names[i]]))
    rot = np.zeros(n, dtype=np.int64)
    return order, rot


# ===================================================================
# ILS 扰动算子
# ===================================================================

def perturb_order_rot(order, rot, n, rng, strength='medium'):
    """扰动放置顺序和旋转方向。

    strength:
      'light'  — 小范围调序 + 少量旋转翻转
      'medium' — 中等范围移除重插 + 中度旋转翻转
      'heavy'  — 大块逆转 + 大量旋转翻转
    """
    order2 = order[:]
    rot2 = rot.copy()

    if strength == 'light':
        k = max(2, n // 20)
        n_flip = max(1, n // 15)
    elif strength == 'heavy':
        k = max(3, n // 6)
        n_flip = max(2, n // 5)
    else:  # medium
        k = max(2, n // 10)
        n_flip = max(1, n // 8)

    # 移除 k 个随机模块，随机重插
    idx = sorted(rng.choice(n, min(k, n), replace=False), reverse=True)
    vals = [order2[i] for i in idx]
    for v in vals:
        order2.remove(v)
    rng.shuffle(vals)
    posns = sorted(rng.integers(0, len(order2) + 1, size=len(vals)))
    for v, p in zip(vals, posns):
        order2.insert(p, v)

    # 翻转部分旋转
    flip_idx = rng.choice(n, min(n_flip, n), replace=False)
    rot2[flip_idx] ^= 1

    # 中等/重度：随机逆转一个子段
    if strength in ('medium', 'heavy') and rng.random() < 0.5:
        a = int(rng.integers(0, n))
        b = int(rng.integers(0, n))
        lo, hi = min(a, b), max(a, b)
        order2[lo:hi + 1] = order2[lo:hi + 1][::-1]

    return order2, rot2


# ===================================================================
# Skyline + ILS/SA 主优化器
# ===================================================================

def skyline_ils_hpwl(widths, heights, block_names,
                     W_chip, H_chip, nets, terminal_pos,
                     budget_s, seed, init_order, init_rot):
    """Skyline 装箱 + ILS/SA 优化 HPWL。

    在固定轮廓内维持可行布局，通过扰动顺序/旋转来降低 HPWL。
    使用 Metropolis 接受准则（SA）。

    Returns:
        dict(xs, ys, rw, rh, W, H, hpwl, rot, feasible,
             trace, iterations, runtime)
    """
    rng = np.random.default_rng(seed)
    n = len(widths)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)

    # ---- 初始解 ----
    result = pack_and_eval(init_order, init_rot, widths, heights, block_names,
                           W_chip, H_chip, nets, terminal_pos)
    if result is None:
        # 初始解不可行：尝试找一个可行的
        feas = find_feasible_initial(widths, heights, block_names,
                                     W_chip, H_chip, nets, terminal_pos, rng)
        if feas is None:
            return None  # 找不到任何可行解
        init_order, init_rot = feas['order'], feas['rot']
        result = pack_and_eval(init_order, init_rot, widths, heights,
                               block_names, W_chip, H_chip, nets, terminal_pos)
        if result is None:
            return None

    xs, ys, rw, rh, W, H, hpwl = result
    order = list(init_order)
    rot = np.asarray(init_rot, dtype=np.int64).copy()

    best = dict(xs=xs.copy(), ys=ys.copy(), rw=rw.copy(), rh=rh.copy(),
                W=W, H=H, hpwl=int(hpwl), rot=rot.copy(),
                feasible=True)

    # ---- 自适应初温（估计典型 HPWL 变化量）----
    deltas = []
    for _ in range(30):
        o2, r2 = perturb_order_rot(order, rot, n, rng, 'medium')
        r2_res = pack_and_eval(o2, r2, widths, heights, block_names,
                               W_chip, H_chip, nets, terminal_pos)
        if r2_res is not None:
            deltas.append(abs(r2_res[-1] - hpwl))
    if deltas:
        T0 = float(np.mean(deltas)) * 2.0 + 1.0
    else:
        T0 = float(hpwl) * 0.01 + 100.0

    T = T0
    T_min = 1e-2
    alpha = 0.96
    it = 0
    stagnant = 0
    max_stagnant = 400   # 连续未改进的最大温阶数

    trace = [(0.0, hpwl, W, H)]
    t_start = time.time()

    while time.time() - t_start < budget_s and T > T_min:
        inner = max(50, n * 3)
        improved_inner = False

        for _ in range(inner):
            strength = 'heavy' if rng.random() < 0.08 else \
                       'light' if rng.random() < 0.3 else 'medium'
            o2, r2 = perturb_order_rot(order, rot, n, rng, strength)
            r2_res = pack_and_eval(o2, r2, widths, heights, block_names,
                                   W_chip, H_chip, nets, terminal_pos)
            if r2_res is None:
                continue
            _, _, _, _, _, _, hpwl2 = r2_res

            delta = hpwl2 - hpwl
            it += 1

            if delta <= 0 or rng.random() < np.exp(-delta / T):
                order, rot = o2, r2
                hpwl = hpwl2
                xs2, ys2, rw2, rh2, W2, H2, _ = r2_res

                if hpwl2 < best['hpwl']:
                    best = dict(xs=xs2.copy(), ys=ys2.copy(),
                                rw=rw2.copy(), rh=rh2.copy(),
                                W=W2, H=H2, hpwl=int(hpwl2), rot=rot.copy(),
                                feasible=True)
                    stagnant = 0
                    improved_inner = True

        T *= alpha

        if not improved_inner:
            stagnant += 1
        else:
            stagnant = 0

        # 停滞震荡
        if stagnant >= max_stagnant:
            T = T0 * 0.4
            stagnant = 0
            # 强扰动
            for _ in range(max(5, n // 8)):
                o2, r2 = perturb_order_rot(order, rot, n, rng, 'heavy')
                r2_res = pack_and_eval(o2, r2, widths, heights, block_names,
                                       W_chip, H_chip, nets, terminal_pos)
                if r2_res is not None:
                    order, rot = o2, r2
                    hpwl = r2_res[-1]

        if it % 300 == 0:
            trace.append((time.time() - t_start, best['hpwl'],
                          best['W'], best['H']))

    runtime = time.time() - t_start
    trace.append((runtime, best['hpwl'], best['W'], best['H']))

    best['iterations'] = it
    best['trace'] = trace
    best['runtime'] = runtime
    return best


# ===================================================================
# B*-树 SA（备选精修器）
# ===================================================================

def bstar_refine(widths, heights, block_names,
                 W_chip, H_chip, nets, terminal_pos,
                 budget_s, seed, init_order, init_rot):
    """B*-树 + SA 精修：从 from_shelf 出发，优化 HPWL。

    仅接受严格可行解（无轮廓越界）。
    若 SA 结束时未找到可行解，返回途中最佳可行解。
    """
    from bstar import BStarTree

    rng = np.random.default_rng(seed)
    n = len(widths)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    bound_w = int(max(W_chip * 2, np.sum(np.maximum(widths, heights))) + 200)

    rot = np.asarray(init_rot, dtype=np.int64).copy()
    tree = BStarTree.from_shelf(widths, heights, init_order, rot, int(W_chip))

    xs, ys, rw, rh, W, H = tree.decode()
    feasible_init = (W <= W_chip and H <= H_chip)

    if feasible_init:
        centers = make_centers(block_names, xs, ys, rw, rh)
        hpwl = compute_hpwl(nets, centers, terminal_pos)
    else:
        hpwl = 10**12  # 不可行初始

    best_feasible = None
    if feasible_init:
        best_feasible = dict(xs=xs.copy(), ys=ys.copy(),
                             rw=rw.copy(), rh=rh.copy(),
                             W=W, H=H, hpwl=int(hpwl))

    # 自适应初温
    deltas = []
    for _ in range(20):
        snap = tree._snapshot()
        tree.perturb(rng)
        xs2, ys2, rw2, rh2, W2, H2 = tree.decode()
        if np.max(xs2 + rw2) <= bound_w:
            feasible2 = (W2 <= W_chip and H2 <= H_chip)
            if feasible2:
                centers2 = make_centers(block_names, xs2, ys2, rw2, rh2)
                hpwl2 = compute_hpwl(nets, centers2, terminal_pos)
                deltas.append(abs(hpwl2 - hpwl) if feasible_init else 1000)
        tree._restore(snap)

    T0 = float(np.mean(deltas)) * 2.0 + 100.0 if deltas else 1000.0
    T = T0
    alpha = 0.96
    T_min = 1e-1
    it = 0
    t_start = time.time()

    while time.time() - t_start < budget_s and T > T_min:
        inner = max(50, n * 3)
        for _ in range(inner):
            snap = tree._snapshot()
            tree.perturb(rng)
            xs2, ys2, rw2, rh2, W2, H2 = tree.decode()
            it += 1

            if np.max(xs2 + rw2) > bound_w:
                tree._restore(snap)
                continue

            feasible2 = (W2 <= W_chip and H2 <= H_chip)
            if not feasible2:
                # 不可行：概率接受（仅当当前也不可行时）
                if not feasible_init and rng.random() < 0.3:
                    W, H = W2, H2
                    feasible_init = False
                else:
                    tree._restore(snap)
                continue

            centers2 = make_centers(block_names, xs2, ys2, rw2, rh2)
            hpwl2 = compute_hpwl(nets, centers2, terminal_pos)
            delta = hpwl2 - hpwl

            if not feasible_init or delta <= 0 or \
               rng.random() < np.exp(-delta / T):
                W, H = W2, H2
                hpwl = hpwl2
                feasible_init = True

                if best_feasible is None or hpwl2 < best_feasible['hpwl']:
                    best_feasible = dict(xs=xs2.copy(), ys=ys2.copy(),
                                         rw=rw2.copy(), rh=rh2.copy(),
                                         W=W2, H=H2, hpwl=int(hpwl2),
                                         rot=tree.rot.copy())
            else:
                tree._restore(snap)

        T *= alpha

    if best_feasible is not None:
        best_feasible['feasible'] = True
        best_feasible['iterations'] = it
        best_feasible['runtime'] = time.time() - t_start
        best_feasible['trace'] = [(best_feasible['runtime'],
                                   best_feasible['hpwl'],
                                   best_feasible['W'], best_feasible['H'])]
        return best_feasible
    return None


# ===================================================================
# 单个数据集求解
# ===================================================================

def solve_q2_dataset(ds, dead_space_ratio=0.15, budget_s=120,
                     seed=2026, n_restarts=3):
    """对单个数据集求解问题二。

    策略：
      1. 多起点 Skyline + ILS/SA 优化 HPWL（主算法）
      2. B*-树 + SA 备选精修（从 ILS 最优解的 order/rot 出发）
      3. 取两阶段最优解

    Args:
        ds: Dataset 对象
        dead_space_ratio: 死区比例（默认 0.15）
        budget_s: 总时间预算（秒）
        seed: 随机种子
        n_restarts: 多起点数

    Returns:
        dict: 完整求解结果
    """
    A = ds.total_area
    W_chip = int(np.ceil(np.sqrt(A * (1 + dead_space_ratio))))
    H_chip = W_chip

    n = ds.n
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    block_names = ds.names
    nets = ds.nets
    terminal_pos = ds.terminal_pos

    rng = np.random.default_rng(seed)

    # ---- 寻找初始可行解 ----
    t0 = time.time()
    feas_init = find_feasible_initial(widths, heights, block_names,
                                      W_chip, H_chip, nets, terminal_pos,
                                      rng, max_tries=30)
    if feas_init is not None:
        print(f"  初始可行解: {feas_init['W']}x{feas_init['H']}, "
              f"HPWL={feas_init['hpwl']:,} ({feas_init['label']})")
    else:
        print(f"  [警告] 未找到初始可行解！将尝试随机搜索")

    # ---- 构造连接度排序 ----
    conn_order, conn_rot = build_connectivity_order(ds)

    # ---- 主算法：多起点 Skyline + ILS/SA ----
    budget_per_restart = budget_s * 0.65 / n_restarts
    best_overall = None

    for restart in range(n_restarts):
        if feas_init is not None and restart == 0:
            o_i, r_i = feas_init['order'], feas_init['rot']
        elif restart == 1:
            o_i, r_i = conn_order, conn_rot
        else:
            o_i = list(range(n))
            rng.shuffle(o_i)
            r_i = (rng.random(n) < 0.25).astype(np.int64)

        result = skyline_ils_hpwl(
            widths, heights, block_names,
            W_chip, H_chip, nets, terminal_pos,
            budget_s=budget_per_restart,
            seed=seed + restart * 101,
            init_order=o_i, init_rot=r_i,
        )

        if result is None:
            continue

        if best_overall is None or result['hpwl'] < best_overall['hpwl']:
            best_overall = result

    # ---- 备选：B*-树 SA 精修 ----
    if best_overall is not None:
        bstar_budget = budget_s * 0.25
        bstar_res = bstar_refine(
            widths, heights, block_names,
            W_chip, H_chip, nets, terminal_pos,
            budget_s=bstar_budget,
            seed=seed + 9999,
            init_order=conn_order,
            init_rot=best_overall['rot'],
        )
        if bstar_res is not None and bstar_res['hpwl'] < best_overall['hpwl']:
            print(f"  B*-树精修改进: {best_overall['hpwl']:,} -> "
                  f"{bstar_res['hpwl']:,}")
            best_overall = bstar_res

    if best_overall is None:
        # 最终回退：使用初始可行解
        if feas_init is not None:
            best_overall = dict(
                xs=feas_init['xs'], ys=feas_init['ys'],
                rw=feas_init['rw'], rh=feas_init['rh'],
                W=feas_init['W'], H=feas_init['H'],
                hpwl=feas_init['hpwl'], rot=feas_init['rot'],
                feasible=True, trace=[], iterations=0, runtime=0)
        else:
            raise RuntimeError(f"无法为 {ds.name} 找到任何可行布局")

    # ---- 合法性校验 ----
    ok, max_ov = check_feasible(
        ds, best_overall['xs'], best_overall['ys'],
        best_overall['rw'], best_overall['rh'],
        W_chip, H_chip)

    runtime_total = time.time() - t0

    return dict(
        dataset=ds.name,
        n_blocks=n,
        n_terminals=len(ds.terminal_names),
        n_nets=len(nets),
        total_block_area=A,
        dead_space_ratio=dead_space_ratio,
        W_chip=W_chip,
        H_chip=H_chip,
        chip_area=W_chip * H_chip,
        actual_dead_space=(W_chip * H_chip - A) / A,
        hpwl=int(best_overall['hpwl']),
        feasible=ok,
        max_overlap=int(max_ov) if max_ov > 0 else 0,
        xs=best_overall['xs'].tolist(),
        ys=best_overall['ys'].tolist(),
        rw=best_overall['rw'].tolist(),
        rh=best_overall['rh'].tolist(),
        rot=best_overall['rot'].tolist(),
        W_layout=int(best_overall['W']),
        H_layout=int(best_overall['H']),
        trace=best_overall.get('trace', []),
        iterations=best_overall.get('iterations', 0),
        runtime=best_overall.get('runtime', 0),
        runtime_total=runtime_total,
    )


# ===================================================================
# CLI 入口
# ===================================================================

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="问题二：固定正方形轮廓 + HPWL 最小化")
    parser.add_argument("--data-dir",
                        default=os.path.normpath(os.path.join(here, "..", "附件")))
    parser.add_argument("--out-dir",
                        default=os.path.normpath(os.path.join(here, "..", "result")))
    parser.add_argument("--datasets", default="n100,n200,n300")
    parser.add_argument("--dead-space-ratio", type=float, default=0.15,
                        help="死区比例（默认 0.15）")
    parser.add_argument("--budget", type=float, default=180,
                        help="每个数据集时间预算（秒），默认 180")
    parser.add_argument("--n-restarts", type=int, default=3,
                        help="多起点数量，默认 3")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--no-viz", action="store_true",
                        help="跳过可视化")
    args = parser.parse_args()

    datasets = [s.strip() for s in args.datasets.split(",") if s.strip()]
    results = []

    print("=" * 72)
    print("问题二：固定正方形轮廓 + HPWL 最小化")
    print(f"死区比例: {args.dead_space_ratio}")
    print(f"时间预算/数据集: {args.budget}s")
    print(f"多起点数: {args.n_restarts}")
    print("=" * 72)

    for name in datasets:
        print(f"\n{'─' * 60}")
        print(f"  数据集: {name}")
        ds = load_dataset(args.data_dir, name)
        stats = dataset_stats(ds)
        print(f"  HardBlock: {stats['HardBlock数']}, "
              f"Terminal: {stats['Terminal数']}, "
              f"线网: {stats['线网数']}, "
              f"总面积: {stats['总面积A']:,}")

        result = solve_q2_dataset(
            ds,
            dead_space_ratio=args.dead_space_ratio,
            budget_s=args.budget,
            seed=args.seed,
            n_restarts=args.n_restarts,
        )
        results.append(result)

        print(f"  ── 求解结果 ──")
        print(f"  芯片尺寸: {result['W_chip']} x {result['H_chip']} "
              f"(实际死区: {result['actual_dead_space']*100:.2f}%)")
        print(f"  总 HPWL: {result['hpwl']:,}")
        print(f"  布局尺寸: {result['W_layout']} x {result['H_layout']}")
        feasible_str = "是" if result['feasible'] else "否"
        print(f"  可行: {feasible_str}")
        print(f"  迭代次数: {result['iterations']:,}"
              f"  优化耗时: {result['runtime']:.1f}s"
              f"  总耗时: {result['runtime_total']:.1f}s")

    # ---- 汇总表 ----
    print("\n" + "=" * 90)
    print("表1  三组芯片问题二求解结果（死区比例 = {:.0%}）".format(
        args.dead_space_ratio))
    print("=" * 90)
    header = (f"{'数据集':<8}{'n_blocks':>8}{'芯片尺寸':>12}{'芯片面积':>10}"
              f"{'总HPWL':>14}{'布局WxH':>14}{'可行':>6}{'实际死区':>10}")
    print(header)
    print("-" * 90)
    for r in results:
        print(f"{r['dataset']:<8}{r['n_blocks']:>8}"
              f"{r['W_chip']}x{r['H_chip']:>12}"
              f"{r['chip_area']:>10,}"
              f"{r['hpwl']:>14,}"
              f"{r['W_layout']}x{r['H_layout']:>14}"
              f"{'是' if r['feasible'] else '否':>6}"
              f"{r['actual_dead_space']*100:>9.2f}%")

    # ---- 保存结果 ----
    os.makedirs(args.out_dir, exist_ok=True)

    summary = []
    for r in results:
        summary.append(dict(
            dataset=r['dataset'],
            n_blocks=r['n_blocks'],
            n_terminals=r['n_terminals'],
            n_nets=r['n_nets'],
            total_block_area=r['total_block_area'],
            dead_space_ratio=r['dead_space_ratio'],
            W_chip=r['W_chip'],
            H_chip=r['H_chip'],
            chip_area=r['chip_area'],
            actual_dead_space=round(r['actual_dead_space'], 6),
            hpwl=r['hpwl'],
            feasible=r['feasible'],
            W_layout=r['W_layout'],
            H_layout=r['H_layout'],
            iterations=r['iterations'],
            runtime_sa=round(r['runtime'], 2),
            runtime_total=round(r['runtime_total'], 2),
        ))
    with open(os.path.join(args.out_dir, "q2_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    # 位置文件
    for result in results:
        ds = load_dataset(args.data_dir, result['dataset'])
        lines = [f"# {result['dataset']}  Q2 placement  "
                 f"W_chip={result['W_chip']} H_chip={result['H_chip']}  "
                 f"HPWL={result['hpwl']}  feasible={result['feasible']}"]
        lines.append("# name  x  y  w  h  rotated")
        for i in range(ds.n):
            lines.append(
                f"{ds.names[i]} {result['xs'][i]} {result['ys'][i]} "
                f"{result['rw'][i]} {result['rh'][i]} {result['rot'][i]}")
        with open(os.path.join(args.out_dir,
                               f"q2_{result['dataset']}_placement.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    # ---- 可视化 ----
    if not args.no_viz:
        print("\n生成可视化...")
        for result in results:
            ds = load_dataset(args.data_dir, result['dataset'])
            chip_W, chip_H = result['W_chip'], result['H_chip']

            plot_layout_q2(
                ds,
                np.asarray(result['xs'], dtype=np.int64),
                np.asarray(result['ys'], dtype=np.int64),
                np.asarray(result['rw'], dtype=np.int64),
                np.asarray(result['rh'], dtype=np.int64),
                result['W_layout'], result['H_layout'],
                chip_W, chip_H,
                ds.terminal_pos,
                os.path.join(args.out_dir,
                             f"q2_{result['dataset']}_layout.png"),
                title=f"问题二  {result['dataset']}  "
                      f"HPWL={result['hpwl']:,}  "
                      f"芯片 {chip_W}x{chip_H}",
                hpwl=result['hpwl'],
                feasible=result['feasible'],
            )

            plot_convergence_q2(
                result['trace'],
                os.path.join(args.out_dir,
                             f"q2_{result['dataset']}_convergence.png"),
            )

    print(f"\n结果已输出至: {os.path.abspath(args.out_dir)}")
    return results


# ===================================================================
# Q2 收敛曲线可视化
# ===================================================================

def plot_convergence_q2(trace, path):
    """绘制 HPWL 收敛曲线。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not trace:
        return

    times = [t[0] for t in trace]
    hpwls = [t[1] for t in trace]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(times, hpwls, 'b-', lw=1.5)
    ax.set_xlabel("时间 (s)")
    ax.set_ylabel("HPWL")
    ax.set_title("HPWL 收敛曲线")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    main()
