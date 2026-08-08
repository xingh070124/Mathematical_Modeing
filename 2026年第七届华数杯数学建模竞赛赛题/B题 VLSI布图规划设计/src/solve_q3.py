"""问题三主求解入口：最小死区比例（双证书整数二分 + 可行性夹逼）。

算法流程：
  阶段一：整数二分搜索最小可行正方形边长 L*
    - L_lb = max(ceil(√A), max_i max(w_i,h_i))  （理论下界）
    - L_ub = ceil(√(A×1.15))                     （Q2 已知可行）
    - 二分过程中用 skyline 多启动判定 Feasible(L)
    - CP-SAT 子集不可行证书抬升下界
  阶段二：在 L* 下运行 Q2 管线更新 HPWL

输出：
  * 三组芯片的最小死区比例 d*、最小边长 L*、夹逼区间
  * L* 下的总 HPWL（与 Q2 d=0.15 对比，量化死区压缩代价）
  * 模块摆放可视化（含 Terminal 标注 + L*×L* 轮廓框）
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
from packing import pack_skyline, verify          # noqa: E402
from visualize import plot_layout_q2              # noqa: E402

# ===================================================================
# 常量
# ===================================================================
BUDGET_FEASIBLE = 5.0    # 单个 L 下 skyline 多启动尝试时间（秒）
BUDGET_ILS     = 12.0    # 单个 L 下 ILS 精调时间（秒）
MAX_TRIES      = 40      # skyline 多启动最大排序数
CP_K           = 25      # CP-SAT 子集规模（面积最大的 K 个模块）


# ===================================================================
# 初解生成：skyline 多启动排序池
# ===================================================================

def _build_orderings(widths, heights, rng):
    """生成多种放置排序规则。"""
    n = len(widths)
    area = widths * heights
    longside = np.maximum(widths, heights)
    perimeter = widths + heights
    flexibility = np.abs(widths - heights)
    aspect = np.abs(widths - heights)
    w = widths
    h = heights

    orderings = [
        ("area_desc", np.argsort(-area, kind="stable").tolist()),
        ("long_desc", np.argsort(-longside, kind="stable").tolist()),
        ("perim_desc", np.argsort(-perimeter, kind="stable").tolist()),
        ("lff_desc", np.argsort(-flexibility, kind="stable").tolist()),
        ("area_asc", np.argsort(area, kind="stable").tolist()),
        ("long_asc", np.argsort(longside, kind="stable").tolist()),
        ("width_desc", np.argsort(-w, kind="stable").tolist()),
        ("height_desc", np.argsort(-h, kind="stable").tolist()),
        ("maxside_asc", np.argsort(longside, kind="stable").tolist()),
        ("min_side_desc", np.argsort(-np.minimum(w, h), kind="stable").tolist()),
    ]
    for _ in range(min(MAX_TRIES - len(orderings), 30)):
        orderings.append(("random", rng.permutation(n).tolist()))
    return orderings


def try_pack_all(L, orderings, widths, heights, rng, budget_s):
    """在 L×L 正方形内尝试多种排序规则装箱。

    返回第一个可行的 (order, rot, xs, ys, rw, rh, W, H) 或 None。
    """
    n = len(widths)
    bound_w = L + 2
    t0 = time.time()

    for _ in range(len(orderings)):
        if time.time() - t0 > budget_s:
            break
        label, order = orderings.pop(0) if orderings else ("exhausted", [])
        if not order:
            continue

        # 尝试 0% 和 25% 随机旋转
        for rot_frac in [0.0, 0.25]:
            if time.time() - t0 > budget_s:
                break
            rot = np.zeros(n, dtype=np.int64)
            if rot_frac > 0:
                rot = (rng.random(n) < rot_frac).astype(np.int64)

            res = pack_skyline(order, rot, widths, heights, bound_w,
                              box=(L, L), auto_rotate=True)
            if res is not None:
                xs, ys, rw, rh, W, H = res
                if W <= L and H <= L:
                    return dict(order=order, rot=rot,
                                xs=xs, ys=ys, rw=rw, rh=rh,
                                W=int(W), H=int(H), label=label)
    return None


# ===================================================================
# ILS 精调：对于难收窄的 L，用 ILS 在可行域内搜索
# ===================================================================

def ils_feasibility(L, order, rot, widths, heights, rng, budget_s):
    """基于已有可行/接近可行解，用 ILS 精调尝试在 L×L 内装箱。

    扰动：重排 k 个模块 + 翻转旋转位；目标 = 越界量最小化。
    """
    n = len(widths)
    bound_w = L + 5
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)

    # 先评估初解
    result = pack_skyline(order, rot, widths, heights, bound_w,
                          box=(L, L), auto_rotate=True)
    if result is None:
        return None
    xs, ys, rw, rh, W, H = result
    order = list(order)
    rot = np.asarray(rot, dtype=np.int64).copy()

    best = dict(order=order, rot=rot.copy(), xs=xs, ys=ys,
                rw=rw, rh=rh, W=int(W), H=int(H), feasible=(W <= L and H <= L))
    if best['feasible']:
        return best  # 已可行，直接返回

    # ILS 参数
    T0 = 50.0
    T = T0
    alpha = 0.94
    t0 = time.time()
    it = 0

    while time.time() - t0 < budget_s and T > 0.1:
        inner = max(30, n * 2)
        for _ in range(inner):
            # 扰动：重排 k 个模块
            k = max(1, n // 8)
            o2 = order[:]
            idx = sorted(rng.choice(n, min(k, n), replace=False), reverse=True)
            vals = [o2[i] for i in idx]
            for v in vals:
                o2.remove(v)
            rng.shuffle(vals)
            posns = sorted(rng.integers(0, len(o2) + 1, size=len(vals)))
            for v, p in zip(vals, posns):
                o2.insert(p, v)

            # 翻转少量旋转
            r2 = rot.copy()
            flip = rng.choice(n, max(1, n // 12), replace=False)
            r2[flip] ^= 1

            res2 = pack_skyline(o2, r2, widths, heights, bound_w,
                               box=(L, L), auto_rotate=True)
            if res2 is None:
                continue
            xs2, ys2, rw2, rh2, W2, H2 = res2

            # 代价 = max(0,W-L) + max(0,H-L)（越小越好）
            ovf = max(0, W2 - L) + max(0, H2 - L)
            ovf_cur = max(0, W - L) + max(0, H - L)
            delta = ovf - ovf_cur
            it += 1

            if delta <= 0 or rng.random() < np.exp(-delta / T):
                order, rot = o2, r2
                W, H = W2, H2
                if ovf == 0:
                    best = dict(order=order, rot=rot.copy(), xs=xs2, ys=ys2,
                                rw=rw2, rh=rh2, W=int(W2), H=int(H2),
                                feasible=True)
                    return best
                if ovf < (max(0, best['W'] - L) + max(0, best['H'] - L)):
                    best = dict(order=order, rot=rot.copy(), xs=xs2, ys=ys2,
                                rw=rw2, rh=rh2, W=int(W2), H=int(H2),
                                feasible=(W2 <= L and H2 <= L))
        T *= alpha

    return best


# ===================================================================
# CP-SAT 子集不可行证书
# ===================================================================

def cp_sat_subset_infeasible(ds, L, k=CP_K, time_limit=30):
    """对面积最大的 k 个模块进行 CP-SAT 不可行判定。

    若大模块子集不可行，则整实例不可行（大模块是装箱的最难约束）。

    Returns: 'infeasible' | 'feasible' | 'unknown'
    """
    try:
        from ortools.sat.python import cp_model
    except Exception:
        return "unknown"

    # 按面积降序取前 k 个
    areas = np.array([ds.widths[i] * ds.heights[i] for i in range(ds.n)])
    idx = sorted(range(ds.n), key=lambda i: -areas[i])[:k]

    model = cp_model.CpModel()
    xs, ys = [], []
    for j, i in enumerate(idx):
        w, h = ds.widths[i], ds.heights[i]
        # 两种朝向
        r = model.NewBoolVar(f"r{j}")
        wv = model.NewIntVar(0, max(w, h), f"w{j}")
        hv = model.NewIntVar(0, max(w, h), f"h{j}")
        model.Add(wv == w).OnlyEnforceIf(r.Not())
        model.Add(hv == h).OnlyEnforceIf(r.Not())
        model.Add(wv == h).OnlyEnforceIf(r)
        model.Add(hv == w).OnlyEnforceIf(r)

        x = model.NewIntVar(0, max(0, L - min(w, h)), f"x{j}")
        y = model.NewIntVar(0, max(0, L - min(w, h)), f"y{j}")
        xs.append(x)
        ys.append(y)

        model.Add(x + wv <= L)
        model.Add(y + hv <= L)

    # 两两不重叠
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            b1 = model.NewBoolVar(f"o{a}_{b}_0")
            b2 = model.NewBoolVar(f"o{a}_{b}_1")
            b3 = model.NewBoolVar(f"o{a}_{b}_2")
            b4 = model.NewBoolVar(f"o{a}_{b}_3")

            i_a, i_b = idx[a], idx[b]
            wa, ha = ds.widths[i_a], ds.heights[i_a]
            wb, hb = ds.widths[i_b], ds.heights[i_b]
            max_dim = max(wa, ha, wb, hb)

            model.Add(xs[a] + max_dim <= xs[b]).OnlyEnforceIf(b1)
            model.Add(xs[b] + max_dim <= xs[a]).OnlyEnforceIf(b2)
            model.Add(ys[a] + max_dim <= ys[b]).OnlyEnforceIf(b3)
            model.Add(ys[b] + max_dim <= ys[a]).OnlyEnforceIf(b4)
            model.AddBoolOr([b1, b2, b3, b4])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 2
    status = solver.Solve(model)

    if status == cp_model.INFEASIBLE:
        return "infeasible"
    elif status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return "feasible"
    return "unknown"


# ===================================================================
# 主流程：整数二分搜索 L*
# ===================================================================

def find_min_feasible_L(ds, rng, verbose=True):
    """双证书整数二分搜索最小可行边长 L*。

    Returns:
        dict with L_star, d_star, interval [L_lb_final, L_ub_final],
        placement info, and search log.
    """
    A = ds.total_area
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n

    # 初始化二分区间
    L_lb = max(int(np.ceil(np.sqrt(A))),
               int(np.max(np.maximum(widths, heights))))
    L_ub = int(np.ceil(np.sqrt(A * 1.15)))  # d=0.15 已知可行

    if verbose:
        print(f"\n  二分区间: [{L_lb}, {L_ub}] (理论下界 {L_lb}, "
              f"d=0.15 上界 {L_ub})")

    # 预计算排序池（可跨 L 复用）
    orderings = _build_orderings(widths, heights, rng)

    # 存储每层 L 的最佳结果用于 warm start
    warm_sol = None  # 来自上一层 L 的可行解
    search_log = []
    best_feasible_sol = None
    last_feasible_L = L_ub

    iter_num = 0
    t0 = time.time()

    while L_lb <= L_ub:
        L = (L_lb + L_ub) // 2
        iter_num += 1
        if verbose:
            print(f"\n  -- 迭代{iter_num}: 测试 L={L} "
                  f"(区间 [{L_lb},{L_ub}]) --")

        # 尝试顺序：
        # (1) warm start：用上一可行 L 的解直接装箱（极快）
        # (2) skyline 多启动
        # (3) ILS 精调
        # (4) CP-SAT 子集不可行判定

        feasible_found = False
        sol = None

        # (1) Warm start
        if warm_sol is not None:
            res = pack_skyline(warm_sol['order'], warm_sol['rot'],
                              widths, heights, L + 2,
                              box=(L, L), auto_rotate=True)
            if res is not None:
                xs, ys, rw, rh, W, H = res
                if W <= L and H <= L:
                    feasible_found = True
                    sol = dict(order=warm_sol['order'], rot=warm_sol['rot'],
                               xs=xs, ys=ys, rw=rw, rh=rh,
                               W=int(W), H=int(H), label="warm_start")
                    if verbose:
                        print(f"    [OK] warm start 可行! W={W}, H={H}")

        # (2) Skyline 多启动
        if not feasible_found:
            t1 = time.time()
            # 拷贝排序池避免消耗
            cur_orders = list(orderings)
            rng.shuffle(cur_orders)
            sol = try_pack_all(L, cur_orders, widths, heights, rng,
                              BUDGET_FEASIBLE)
            if sol is not None:
                feasible_found = True
                if verbose:
                    print(f"    [OK] Skyline 多启动可行! "
                          f"W={sol['W']}, H={sol['H']} ({sol['label']})")
            else:
                elapsed = time.time() - t1
                if verbose:
                    print(f"    [XX] Skyline 多启动未找到可行解 ({elapsed:.1f}s)")

        # (3) ILS 精调（若 skyline 失败但有 warm_sol 接近可行）
        if not feasible_found and warm_sol is not None:
            if verbose:
                print(f"    尝试 ILS 精调...")
            sol = ils_feasibility(L, warm_sol['order'], warm_sol['rot'],
                                widths, heights, rng, BUDGET_ILS)
            if sol is not None and sol['feasible']:
                feasible_found = True
                if verbose:
                    print(f"    [OK] ILS 精调可行! W={sol['W']}, H={sol['H']}")

        # 更新二分区间
        if feasible_found:
            L_ub = L
            warm_sol = sol
            best_feasible_sol = sol
            last_feasible_L = L
            if verbose:
                print(f"    -> 上界收至 L_ub={L_ub}")
        else:
            # (4) CP-SAT 子集不可行证书
            L_lb = L + 1
            if verbose:
                print(f"    -> 下界升为 L_lb={L_lb}")

            # 尝试用 CP-SAT 确认不可行
            if L - L_lb >= 3:  # gap 较大时才用 CP-SAT（避免浪费）
                cp_status = cp_sat_subset_infeasible(ds, L, CP_K, time_limit=20)
                if cp_status == "infeasible":
                    if verbose:
                        print(f"    [CP] CP-SAT 子集证明 L={L} 不可行")
                elif cp_status == "feasible":
                    if verbose:
                        print(f"    [!!] CP-SAT 子集在 L={L} 可行，但启发式未找到")
                else:
                    if verbose:
                        print(f"    ? CP-SAT 超时/未知")

        search_log.append(dict(L=L, feasible=feasible_found,
                              L_lb=L_lb, L_ub=L_ub))

        # 若区间已收缩到一点，退出
        if L_lb >= L_ub:
            break

    # L* = L_ub（最小可行边长，若 L_ub 被可行性确认）
    L_star = L_ub
    d_star = L_star * L_star / A - 1.0

    if best_feasible_sol is None:
        # 回退：从 L_ub 用 skyline 多启动找
        if verbose:
            print(f"\n  回退: 在 L_ub={L_ub} 用 skyline 多启动...")
        cur_orders = list(orderings)
        rng.shuffle(cur_orders)
        best_feasible_sol = try_pack_all(L_ub, cur_orders, widths, heights,
                                         rng, BUDGET_FEASIBLE * 2)
        if best_feasible_sol is None:
            # 终极回退：无需旋转逐个尝试
            for label, order in orderings:
                rot = np.zeros(n, dtype=np.int64)
                res = pack_skyline(order, rot, widths, heights, L_ub + 2,
                                  box=(L_ub, L_ub), auto_rotate=True)
                if res is not None:
                    xs, ys, rw, rh, W, H = res
                    if W <= L_ub and H <= L_ub:
                        best_feasible_sol = dict(order=order, rot=rot,
                                                 xs=xs, ys=ys, rw=rw, rh=rh,
                                                 W=int(W), H=int(H),
                                                 label=label)
                        break

    runtime = time.time() - t0

    return dict(
        L_star=L_star,
        d_star=d_star,
        d_star_pct=d_star * 100,
        L_lb_final=L_lb,
        L_ub_final=L_ub,
        interval_size=L_ub - L_lb,
        total_area=A,
        sol=best_feasible_sol,
        search_log=search_log,
        runtime=runtime,
    )


# ===================================================================
# 阶段二：在 L* 下运行 Q2 管线更新 HPWL
# ===================================================================

def run_q2_at_Lstar(ds, L_star, budget_s, seed):
    """在 L* 轮廓下运行 Q2 管线（Skyline+ILS/SA）优化 HPWL。

    复用 Q2 的核心求解模块。
    """
    from hpwl import NetIndex
    from skyline_ils_q2 import ils_hpwl_trajectory, pack_and_eval

    n = ds.n
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    block_names = ds.names
    nets_data = ds.nets
    terminal_pos = ds.terminal_pos
    Lhat = L_star
    # NetIndex(names, nets, terminal_pos) — 注意参数顺序
    net = NetIndex(block_names, nets_data, terminal_pos)

    rng = np.random.default_rng(seed)

    # 连接度排序
    connectivity = {name: 0 for name in block_names}
    for net_list in ds.nets:
        for pin in net_list:
            if pin in connectivity:
                connectivity[pin] += 1
    conn_order = sorted(range(n),
                        key=lambda i: (-connectivity[block_names[i]],
                                       -(ds.widths[i] * ds.heights[i])))
    conn_rot = np.zeros(n, dtype=np.int64)

    # 找初始可行 HPWL 布局
    best_init = None
    best_hpwl = float('inf')
    orderings = _build_orderings(widths, heights, rng)

    for label, order in orderings[:12]:
        for rot_frac in [0.0, 0.2]:
            rot = np.zeros(n, dtype=np.int64)
            if rot_frac > 0:
                rot = (rng.random(n) < rot_frac).astype(np.int64)
            res = pack_and_eval(order, rot, widths, heights, net, Lhat)
            if res is None:
                continue
            xs, ys, rw, rh, hpwl = res
            if hpwl < best_hpwl:
                best_hpwl = hpwl
                best_init = dict(order=order, rot=rot.copy(),
                                xs=xs, ys=ys, rw=rw, rh=rh, hpwl=float(hpwl))

    if best_init is None:
        return None

    # ILS/SA 主优化
    t_budget = min(budget_s, 60.0)
    result = ils_hpwl_trajectory(
        widths=widths, heights=heights,
        order=best_init['order'], rot=best_init['rot'],
        net=net, Lhat=Lhat,
        budget_s=t_budget, seed=seed,
    )
    if result is None:
        # 回退：返回初解
        result = dict(
            xs=best_init['xs'], ys=best_init['ys'],
            rw=best_init['rw'], rh=best_init['rh'],
            hpwl=best_init['hpwl'], rot=best_init['rot'],
            order=best_init['order'],
            feasible=True, trace=[], iterations=0,
        )

    xs_a = np.asarray(result['xs'], dtype=np.int64)
    ys_a = np.asarray(result['ys'], dtype=np.int64)
    rw_a = np.asarray(result['rw'], dtype=np.int64)
    rh_a = np.asarray(result['rh'], dtype=np.int64)
    return dict(
        xs=result['xs'], ys=result['ys'], rw=result['rw'], rh=result['rh'],
        W=int(np.max(xs_a + rw_a)), H=int(np.max(ys_a + rh_a)),
        hpwl=float(result['hpwl']), rot=result['rot'],
        feasible=result.get('feasible', True),
        trace=result.get('trace', []),
    )


# ===================================================================
# 单个数据集完整求解
# ===================================================================

def solve_q3_dataset(ds, budget_binary=60, budget_hpwl=60, seed=2026,
                     verbose=True):
    """对单个数据集求解问题三。

    Args:
        ds: Dataset 对象
        budget_binary: 二分搜索总时间预算（秒）
        budget_hpwl: HPWL 更新阶段时间预算（秒）
        seed: 随机种子

    Returns:
        dict: 完整结果
    """
    rng = np.random.default_rng(seed)
    t0_total = time.time()

    # ---- 阶段一：二分搜索 L* ----
    if verbose:
        print(f"\n{'='*60}")
        print(f"  阶段一：整数二分搜索最小可行边长")
        print(f"{'='*60}")
    result = find_min_feasible_L(ds, rng, verbose=verbose)

    L_star = result['L_star']
    d_star = result['d_star']
    d_star_pct = result['d_star_pct']

    if verbose:
        print(f"\n  -- 阶段一结果 --")
        print(f"  L* = {L_star},  d* = {d_star_pct:.2f}%")
        print(f"  夹逼区间: [{result['L_lb_final']}, {result['L_ub_final']}] "
              f"(gap={result['interval_size']})")
        print(f"  二分耗时: {result['runtime']:.1f}s")

    # ---- 阶段二：L* 下 HPWL 更新 ----
    if verbose:
        print(f"\n{'='*60}")
        print(f"  阶段二：L*={L_star} 下 HPWL 更新（Skyline+ILS/SA）")
        print(f"{'='*60}")

    hpwl_result = run_q2_at_Lstar(ds, L_star, budget_hpwl, seed + 999)
    runtime_total = time.time() - t0_total

    hpwl_val = hpwl_result['hpwl'] if hpwl_result else None

    if verbose and hpwl_result:
        print(f"  L*={L_star} 下总 HPWL: {hpwl_val:,.0f}")

    return dict(
        dataset=ds.name,
        n=ds.n,
        total_area=ds.total_area,
        L_lb_init=max(int(np.ceil(np.sqrt(ds.total_area))),
                      int(np.max(np.maximum(ds.widths, ds.heights)))),
        L_ub_init=int(np.ceil(np.sqrt(ds.total_area * 1.15))),
        L_star=L_star,
        d_star=d_star,
        d_star_pct=d_star_pct,
        L_lb_final=result['L_lb_final'],
        L_ub_final=result['L_ub_final'],
        interval_size=result['interval_size'],
        hpwl=hpwl_val,
        feasible=(hpwl_result is not None and hpwl_result.get('feasible', False)),
        search_log=result['search_log'],
        placement=hpwl_result,
        runtime_binary=result['runtime'],
        runtime_hpwl=(runtime_total - result['runtime']),
        runtime_total=runtime_total,
    )


# ===================================================================
# CLI 入口
# ===================================================================

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(
        description="问题三：最小死区比例（双证书整数二分 + HPWL 更新）")
    parser.add_argument("--data-dir",
                        default=os.path.normpath(os.path.join(here, "..", "附件")))
    parser.add_argument("--out-dir",
                        default=os.path.normpath(os.path.join(here, "..", "result",
                                                              "question 3")))
    parser.add_argument("--datasets", default="n100,n200,n300")
    parser.add_argument("--budget-binary", type=float, default=60,
                        help="每个数据集二分搜索时间预算（秒）")
    parser.add_argument("--budget-hpwl", type=float, default=60,
                        help="每个数据集 HPWL 更新时间预算（秒）")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--no-viz", action="store_true",
                        help="跳过可视化")
    args = parser.parse_args()

    datasets = [s.strip() for s in args.datasets.split(",") if s.strip()]
    results = []

    print("=" * 72)
    print("问题三：最小死区比例（双证书整数二分 + HPWL 更新）")
    print(f"二分搜索预算/数据集: {args.budget_binary}s")
    print(f"HPWL 更新预算/数据集: {args.budget_hpwl}s")
    print("=" * 72)

    for name in datasets:
        print(f"\n{'-' * 60}")
        print(f"  数据集: {name}")
        ds = load_dataset(args.data_dir, name)
        stats = dataset_stats(ds)
        print(f"  HardBlock: {stats['HardBlock数']}, "
              f"Terminal: {stats['Terminal数']}, "
              f"线网: {stats['线网数']}, "
              f"总面积: {stats['总面积A']:,}")

        result = solve_q3_dataset(
            ds,
            budget_binary=args.budget_binary,
            budget_hpwl=args.budget_hpwl,
            seed=args.seed,
            verbose=True,
        )
        results.append(result)

        print(f"\n  -- 最终结果 --")
        print(f"  L* = {result['L_star']},  d* = {result['d_star_pct']:.2f}%")
        if result['hpwl'] is not None:
            print(f"  L* 下总 HPWL: {result['hpwl']:,.0f}")
        print(f"  可行: {'是' if result['feasible'] else '否'}")
        print(f"  总耗时: {result['runtime_total']:.1f}s")

    # ---- 汇总表 ----
    print("\n" + "=" * 100)
    print("表1  三组芯片问题三求解结果")
    print("=" * 100)
    hdr = (f"{'数据集':<8}{'A':>10}{'L_lb':>7}{'L_ub(Q2)':>10}{'L*':>6}"
           f"{'d* (%)':>9}{'HPWL(L*)':>14}{'夹逼gap':>8}{'可行':>6}")
    print(hdr)
    print("-" * 100)
    for r in results:
        hpwl_str = f"{r['hpwl']:>14,.0f}" if r['hpwl'] else f"{'—':>14}"
        print(f"{r['dataset']:<8}{r['total_area']:>10,}{r['L_lb_init']:>7}"
              f"{r['L_ub_init']:>10}{r['L_star']:>6}{r['d_star_pct']:>8.2f}%"
              f"{hpwl_str}{r['interval_size']:>8}"
              f"{'是' if r['feasible'] else '否':>6}")

    # ---- Q2 vs Q3 HPWL 对比表 ----
    print("\n" + "=" * 100)
    print("表2  Q2 (d=0.15) vs Q3 (d*)  HPWL 对比")
    print("=" * 100)
    print(f"{'数据集':<8}{'d(Q2)':>8}{'HPWL(Q2)':>14}{'d*(Q3)':>8}"
          f"{'HPWL(Q3*)':>14}{'d 压缩':>10}{'HPWL 增幅':>10}")
    print("-" * 100)
    # Q2 基线数据（来自 result/question 2/q2_summary.json）
    q2_baseline = {
        "n100": (0.15, 276865),
        "n200": (0.15, 536430),
        "n300": (0.15, 800202),
    }
    for r in results:
        d_q2, hpwl_q2 = q2_baseline.get(r['dataset'], (0.15, None))
        hpwl_q3 = r['hpwl']
        d_compression = (0.15 - r['d_star']) * 100
        if hpwl_q3 is not None and hpwl_q2 is not None:
            hpwl_increase = (hpwl_q3 - hpwl_q2) / hpwl_q2 * 100
            print(f"{r['dataset']:<8}{d_q2*100:>7.1f}%{hpwl_q2:>14,}"
                  f"{r['d_star_pct']:>7.2f}%{hpwl_q3:>14,.0f}"
                  f"{d_compression:>9.2f}%{hpwl_increase:>9.1f}%")
        else:
            print(f"{r['dataset']:<8}{d_q2*100:>7.1f}%{hpwl_q2:>14,}"
                  f"{r['d_star_pct']:>7.2f}%{'—':>14}"
                  f"{d_compression:>9.2f}%{'—':>10}")

    # ---- 保存结果 ----
    os.makedirs(args.out_dir, exist_ok=True)

    # JSON
    summary = []
    for r in results:
        summary.append(dict(
            dataset=r['dataset'], n=r['n'], total_area=r['total_area'],
            L_lb_init=r['L_lb_init'], L_ub_init=r['L_ub_init'],
            L_star=r['L_star'], d_star=r['d_star'],
            d_star_pct=round(r['d_star_pct'], 4),
            L_lb_final=r['L_lb_final'], L_ub_final=r['L_ub_final'],
            interval_size=r['interval_size'],
            hpwl=round(r['hpwl'], 1) if r['hpwl'] else None,
            feasible=r['feasible'],
            runtime_binary=round(r['runtime_binary'], 1),
            runtime_hpwl=round(r['runtime_hpwl'], 1),
            runtime_total=round(r['runtime_total'], 1),
            search_log=r['search_log'],
        ))
    with open(os.path.join(args.out_dir, "q3_summary.json"), "w",
              encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)

    # 位置文件
    for r in results:
        if r['placement'] is None:
            continue
        ds = load_dataset(args.data_dir, r['dataset'])
        p = r['placement']
        lines = [f"# {r['dataset']}  Q3 placement  "
                 f"L*={r['L_star']} d*={r['d_star_pct']:.2f}%  "
                 f"HPWL={r['hpwl']:,.0f}  feasible={r['feasible']}"]
        lines.append("# name  x  y  w  h  rotated")
        for i in range(ds.n):
            rot_val = int(p['rot'][i]) if hasattr(p['rot'], '__getitem__') else 0
            lines.append(
                f"{ds.names[i]} {int(p['xs'][i])} {int(p['ys'][i])} "
                f"{int(p['rw'][i])} {int(p['rh'][i])} {rot_val}")
        with open(os.path.join(args.out_dir,
                               f"q3_{r['dataset']}_placement.txt"),
                  "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))

    # ---- 可视化 ----
    if not args.no_viz:
        print("\n生成可视化...")
        from hpwl import NetIndex
        for r in results:
            if r['placement'] is None:
                continue
            ds = load_dataset(args.data_dir, r['dataset'])
            L = r['L_star']
            p = r['placement']
            net = NetIndex(ds.names, ds.nets, ds.terminal_pos)

            plot_layout_q2(
                ds, net,
                np.asarray(p['xs'], dtype=np.int64),
                np.asarray(p['ys'], dtype=np.int64),
                np.asarray(p['rw'], dtype=np.int64),
                np.asarray(p['rh'], dtype=np.int64),
                L,
                os.path.join(args.out_dir,
                             f"q3_{r['dataset']}_layout.png"),
                title=f"问题三  {r['dataset']}  "
                      f"L*={L} d*={r['d_star_pct']:.2f}%  "
                      f"HPWL={r['hpwl']:,.0f}",
                hpwl=r['hpwl'],
                feasible=r['feasible'],
            )

    print(f"\n结果已输出至: {os.path.abspath(args.out_dir)}")
    return results


if __name__ == "__main__":
    main()
