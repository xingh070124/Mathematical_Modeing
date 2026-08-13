"""第2层（L2）：并行多目标元启发优化层。

主算法 Skyline + ILS：以"固定条带宽 W"的轨迹为基本单元（每条轨迹优化高度 H，
area=W·H 随之下降），轨迹宽度分布在 sqrt(A) 附近的网格上，多起点并行；
精英池 + 强扰动重启 + 长宽比精调阶段（字典序第二级）；
最终以"全局条带宽全扫"落实字典序（面积最小 → 长宽比最接近 1）。
对照算法 B*-树 + 模拟退火见 bstar.py。
"""
from __future__ import annotations

import time
import numpy as np
from concurrent.futures import ProcessPoolExecutor

from packing import pack_skyline


def strip_pack(order, rot, widths, heights, W):
    """在条带宽 W 下 Skyline 装箱（贪心自动选朝向）；
    返回 (xs, ys, rw, rh, Wout, H) 或 None。"""
    return pack_skyline(order, rot, widths, heights, W, box=(W, None),
                        auto_rotate=True)


def outline_of(res):
    _, _, _, _, W, H = res
    return int(W), int(H)


def _better(a_area, a_asp, b_area, b_asp, phase, s_area):
    if phase == "aspect":
        if s_area is not None and a_area > s_area:
            return False
        return (a_asp, a_area) < (b_asp, b_area)
    return (a_area, a_asp) < (b_area, b_asp)


def width_bounds(widths, heights):
    area = int(np.sum(widths * heights))
    sq = int(np.ceil(np.sqrt(area)))
    w_lb = max(sq, int(np.max(np.minimum(widths, heights))))
    w_ub = max(int(np.ceil(1.6 * np.sqrt(area))),
               int(np.max(np.maximum(widths, heights)))) + 10
    return w_lb, w_ub


def width_grid(widths, heights, n=6):
    """在 sqrt(A) 附近的条带宽网格（含边界），供多起点轨迹使用。"""
    w_lb, w_ub = width_bounds(widths, heights)
    sq = float(np.sqrt(int(np.sum(widths * heights))))
    factors = np.linspace(0.92, 1.35, n)
    grid = [w_lb] + [int(round(sq * f)) for f in factors] + [w_ub]
    return sorted(set(max(w_lb, min(w_ub, g)) for g in grid))


def eval_order(order, rot, widths, heights, W, phase="area", s_area=None):
    """在固定条带宽 W 下评估 (order, rot)。返回 outline 字典或 None。"""
    res = strip_pack(order, rot, widths, heights, W)
    if res is None:
        return None
    Wout, H = outline_of(res)
    return dict(order=list(order), rot=np.asarray(rot, dtype=np.int64).copy(),
                W=Wout, H=H, area=Wout * H, asp=abs(Wout / H - 1.0),
                xs=res[0], ys=res[1], rw=res[2], rh=res[3])


def perturb(order, rot, n, rng):
    order2 = order[:]
    rot2 = rot.copy()
    k = int(rng.integers(1, min(6, n // 12 + 2)))
    idx = sorted(rng.choice(n, k, replace=False), reverse=True)
    vals = [order2[i] for i in idx]
    for v in vals:
        order2.remove(v)
    posns = sorted(rng.integers(0, len(order2) + 1, size=len(vals)))
    for v, p in zip(vals, posns):
        order2.insert(p, v)
    for _ in range(int(rng.integers(0, 3))):
        m = int(rng.integers(0, n))
        rot2[m] ^= 1
    if rng.random() < 0.15:
        a = int(rng.integers(0, n))
        b = int(rng.integers(0, n))
        lo, hi = min(a, b), max(a, b)
        order2[lo : hi + 1] = order2[lo : hi + 1][::-1]
    return order2, rot2


def strong_perturb(order, rot, n, rng):
    """精英解强扰动（重启用）：重排大片、翻转较多旋转。"""
    order2 = order[:]
    rot2 = rot.copy()
    k = max(1, n // 5)
    idx = sorted(rng.choice(n, k, replace=False), reverse=True)
    vals = [order2[i] for i in idx]
    for v in vals:
        order2.remove(v)
    rng.shuffle(vals)
    posns = sorted(rng.integers(0, len(order2) + 1, size=len(vals)))
    for v, p in zip(vals, posns):
        order2.insert(p, v)
    flip = rng.choice(n, int(n * 0.3), replace=False)
    rot2[flip] ^= 1
    if rng.random() < 0.3:
        order2.reverse()
    return order2, rot2


def ils_trajectory(widths, heights, order, rot, W, budget_s, seed,
                   phase="area", s_area=None, trace_interval=0.5):
    """单条 Skyline+ILS 轨迹（固定条带宽 W）。返回 best 解与收敛轨迹。"""
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    n = len(widths)
    rng = np.random.default_rng(seed)
    W = int(W)

    cur = eval_order(order, rot, widths, heights, W, phase, s_area)
    if cur is None:
        return None
    best = cur
    order, rot = best["order"], best["rot"]
    if phase == "aspect":
        T = 5e-3          # 长宽比尺度温度
    else:
        T = 400.0         # 面积尺度温度（W·H 单位）
    T0 = T
    it = 0
    start = time.time()
    last_trace = 0.0
    trace = [(0.0, best["area"], best["asp"])]
    while time.time() - start < budget_s:
        order2, rot2 = perturb(order, rot, n, rng)
        cand = eval_order(order2, rot2, widths, heights, W, phase, s_area)
        if cand is None:
            continue
        it += 1
        if phase == "aspect":
            if s_area is not None and cand["area"] > s_area:
                continue
            delta = cand["asp"] - cur["asp"]
        else:
            delta = cand["area"] - cur["area"]
        if delta <= 0:
            accept = True
        elif rng.random() < np.exp(-delta / T):
            accept = True
        else:
            accept = False
        if accept:
            order, rot = order2, rot2
            cur = cand
            if _better(cur["area"], cur["asp"], best["area"], best["asp"],
                       phase, s_area):
                best = cur
        if it % 300 == 0:
            T = max(T0 * 0.02, T * 0.9)
        if it % 900 == 0:
            T = T0
        now = time.time() - start
        if now - last_trace >= trace_interval:
            last_trace = now
            trace.append((now, best["area"], best["asp"]))
    res = dict(best)
    res["order"] = list(best["order"])
    res["rot"] = best["rot"].tolist()
    res["trace"] = trace
    res["iterations"] = it
    return res


def final_width_sweep(order, rot, widths, heights, w_lb, w_ub, phase="area",
                      s_area=None):
    """对给定 (order, rot) 在全部整数条带宽上全扫，取字典序最优轮廓。"""
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    best = None
    for W in range(w_lb, w_ub + 1):
        res = strip_pack(order, rot, widths, heights, W)
        if res is None:
            continue
        Wout, H = outline_of(res)
        a, s = Wout * H, abs(Wout / H - 1.0)
        if phase == "aspect" and s_area is not None and a > s_area:
            continue
        if best is None or _better(a, s, best["area"], best["asp"], phase, s_area):
            best = dict(order=list(order), rot=np.asarray(rot, dtype=np.int64).copy(),
                        W=Wout, H=H, area=a, asp=s,
                        xs=res[0], ys=res[1], rw=res[2], rh=res[3])
    return best


def _worker_area(task):
    return ils_trajectory(**task)


def _worker_bstar(task):
    from bstar import bstar_sa_solve, BStarTree
    widths = np.asarray(task["widths"], dtype=np.int64)
    heights = np.asarray(task["heights"], dtype=np.int64)
    res = bstar_sa_solve(widths, heights, task["rot"], task["root"],
                         task["parent"], task["left"], task["right"],
                         task["bound_w"], task["budget"], seed=task["seed"])
    return dict(name="bstar", W=res["W"], H=res["H"], area=res["W"] * res["H"],
                asp=abs(res["W"] / res["H"] - 1.0),
                xs=res["xs"], ys=res["ys"], rw=res["rw"], rh=res["rh"],
                rot=res["rot"].tolist(), trace=res["trace"])


def run_parallel(tasks, nproc):
    if nproc <= 1 or len(tasks) <= 1:
        return [fn(task) for fn, task in tasks]
    out = []
    with ProcessPoolExecutor(max_workers=nproc) as ex:
        futs = [ex.submit(fn, task) for fn, task in tasks]
        for f in futs:
            out.append(f.result())
    return out
