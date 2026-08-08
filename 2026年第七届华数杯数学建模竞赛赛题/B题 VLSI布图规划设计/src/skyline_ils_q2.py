"""第2层（L2）问题二主算法：Skyline 装箱 + 迭代局部搜索/模拟退火（ILS/SA）。

关键设计（针对固定轮廓 + HPWL 目标）：
  * Skyline 装箱 box=(Lhat,Lhat) 约束内建 —— 每次评估都是可行解，不浪费
    迭代去"修复越界"，全部预算用于压低总 HPWL；
  * 解表示 = (放置顺序, 旋转)，扰动算子（轻/中/重三档）重排顺序、翻转旋转；
  * Metropolis 接受准则（SA 降温）跳出局部最优；
  * HPWL 评估统一走 NetIndex 精确半坐标口径（与 L1/L3 一致）。

B*-树只能表示"左紧致"类 packing，是 Skyline 可达空间的真子集；
本算法在可行域内直接搜索，三组数据实测 HPWL 优于 B*-树+SA。
"""
from __future__ import annotations

import time
import numpy as np

from packing import pack_skyline
from hpwl import NetIndex


def pack_and_eval(order, rot, widths, heights, net: NetIndex, Lhat):
    """在固定轮廓内 Skyline 装箱（auto_rotate=True）并返回 (xs,ys,rw,rh,hpwl)。

    装箱失败（轮廓内放不下）返回 None。
    """
    res = pack_skyline(order, rot, widths, heights, Lhat,
                       box=(Lhat, Lhat), auto_rotate=True)
    if res is None:
        return None
    xs, ys, rw, rh, W, H = res
    hpwl = net.total_hpwl(xs, ys, rw, rh)
    return xs, ys, rw, rh, hpwl


def perturb_order_rot(order, rot, n, rng, strength="medium"):
    """扰动放置顺序与旋转（light/medium/heavy 三档强度）。"""
    order2 = list(order)
    rot2 = np.asarray(rot, dtype=np.int64).copy()

    if strength == "light":
        k = max(2, n // 20)
        n_flip = max(1, n // 15)
    elif strength == "heavy":
        k = max(3, n // 6)
        n_flip = max(2, n // 5)
    else:
        k = max(2, n // 10)
        n_flip = max(1, n // 8)

    idx = sorted(rng.choice(n, min(k, n), replace=False), reverse=True)
    vals = [order2[i] for i in idx]
    for v in vals:
        order2.remove(v)
    rng.shuffle(vals)
    posns = sorted(rng.integers(0, len(order2) + 1, size=len(vals)))
    for v, p in zip(vals, posns):
        order2.insert(p, v)

    flip_idx = rng.choice(n, min(n_flip, n), replace=False)
    rot2[flip_idx] ^= 1

    if strength in ("medium", "heavy") and rng.random() < 0.5:
        a = int(rng.integers(0, n))
        b = int(rng.integers(0, n))
        lo, hi = min(a, b), max(a, b)
        order2[lo:hi + 1] = order2[lo:hi + 1][::-1]

    return order2, rot2


def ils_hpwl_trajectory(widths, heights, order, rot, net, Lhat, budget_s,
                        seed=0, trace_interval=1.0):
    """单条 Skyline+ILS/SA 轨迹：从 (order, rot) 出发优化 HPWL。

    返回 dict(xs, ys, rw, rh, hpwl, order, rot, iterations, trace, feasible)。
    trace = [(t, best_hpwl, overflow=0), ...]。
    """
    rng = np.random.default_rng(seed)
    n = len(widths)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)

    init = pack_and_eval(order, rot, widths, heights, net, Lhat)
    if init is None:
        # 初序在 (Lhat,Lhat) 内放不下：尝试找可行初解，仍失败则放弃该轨迹
        from packing import pack_skyline
        found = None
        for _ in range(40):
            o2, r2 = perturb_order_rot(order, rot, n, rng, "heavy")
            res = pack_skyline(o2, r2, widths, heights, Lhat,
                               box=(Lhat, Lhat), auto_rotate=True)
            if res is not None:
                xs0, ys0, rw0, rh0, W0, H0 = res
                found = (o2, r2, xs0, ys0, rw0, rh0,
                         net.total_hpwl(xs0, ys0, rw0, rh0))
                break
        if found is None:
            return None
        order, rot = list(found[0]), np.asarray(found[1], dtype=np.int64).copy()
        xs, ys, rw, rh, hpwl = found[2], found[3], found[4], found[5], found[6]
    else:
        xs, ys, rw, rh, hpwl = init
        order = list(order)
        rot = np.asarray(rot, dtype=np.int64).copy()

    best = dict(xs=xs, ys=ys, rw=rw, rh=rh, hpwl=hpwl,
                order=order, rot=rot.copy())

    # 自适应初温：估计典型 HPWL 变化量
    deltas = []
    for _ in range(30):
        o2, r2 = perturb_order_rot(order, rot, n, rng, "medium")
        r2_res = pack_and_eval(o2, r2, widths, heights, net, Lhat)
        if r2_res is not None:
            deltas.append(abs(r2_res[-1] - hpwl))
    T0 = float(np.mean(deltas)) * 2.0 + 1.0 if deltas else float(hpwl) * 0.01 + 100.0

    T = T0
    T_min = 1e-2
    alpha = 0.96
    it = 0
    stagnant = 0
    max_stagnant = 400

    trace = [(0.0, best["hpwl"], 0)]
    last_trace = 0.0
    start = time.time()

    while time.time() - start < budget_s and T > T_min:
        inner = max(50, n * 3)
        improved_inner = False
        for _ in range(inner):
            strength = ("heavy" if rng.random() < 0.08 else
                        "light" if rng.random() < 0.3 else "medium")
            o2, r2 = perturb_order_rot(order, rot, n, rng, strength)
            r2_res = pack_and_eval(o2, r2, widths, heights, net, Lhat)
            if r2_res is None:
                continue
            hpwl2 = r2_res[-1]
            delta = hpwl2 - hpwl
            it += 1
            if delta <= 0 or rng.random() < np.exp(-delta / T):
                order, rot = o2, r2
                hpwl = hpwl2
                if hpwl2 < best["hpwl"]:
                    best = dict(xs=r2_res[0], ys=r2_res[1], rw=r2_res[2],
                                rh=r2_res[3], hpwl=hpwl2,
                                order=list(order), rot=rot.copy())
                    improved_inner = True
        T *= alpha
        if improved_inner:
            stagnant = 0
        else:
            stagnant += 1
        if stagnant >= max_stagnant:
            T = T0 * 0.4
            stagnant = 0
            for _ in range(max(5, n // 8)):
                o2, r2 = perturb_order_rot(order, rot, n, rng, "heavy")
                r2_res = pack_and_eval(o2, r2, widths, heights, net, Lhat)
                if r2_res is not None:
                    order, rot = o2, r2
                    hpwl = r2_res[-1]
        now = time.time() - start
        if now - last_trace >= trace_interval:
            last_trace = now
            trace.append((now, best["hpwl"], 0))
    trace.append((time.time() - start, best["hpwl"], 0))

    best["iterations"] = it
    best["trace"] = trace
    best["feasible"] = True
    return best
