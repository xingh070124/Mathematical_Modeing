"""第2层（L2）问题二对照算法：序列对（SP）+ 自适应遗传算法（AGA）。

表示完备：双排列 (Γ⁺, Γ⁻) 经最长公共子序列解码为无重叠 packing（FAST-SP O(n log n)）。
代价与主算法一致：ΣHPWL + γ·Σoverflow（γ 取固定大值保证先找可行解）。
进化：OX 交叉、swap/inverse 变异、精英保留；交叉/变异率随适应度方差自适应。
作用：与 B*-树+SA 互为对照，验证主算法在 HPWL 指标上的优势。
"""
from __future__ import annotations

import time
import numpy as np

from hpwl import overflow


def sp_decode(pos_p, pos_n, rot, widths, heights):
    """序列对 (Γ⁺, Γ⁻) 解码。pos_p[i]/pos_n[i] 为模块 i 在两条序列中的下标。

    规则：i 在两条序列中都先于 j → i 在 j 左；i 在 Γ⁺ 中后于 j 且 Γ⁻ 中先于 j
          → i 在 j 下。由最长公共子序列 DP 得到 x/y 坐标，天然无重叠。
    返回 (xs, ys, rw, rh, W, H)。
    """
    n = len(widths)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    pos_p = np.asarray(pos_p, dtype=np.int64)
    pos_n = np.asarray(pos_n, dtype=np.int64)
    rw = np.where(rot == 1, heights, widths).astype(np.int64)
    rh = np.where(rot == 1, widths, heights).astype(np.int64)
    xs = np.zeros(n, dtype=np.int64)
    ys = np.zeros(n, dtype=np.int64)
    # x：按 Γ⁺ 序 DP，x_i = max over j 在 i 之前(两序均) 的 x_j + w_j
    order_p = np.argsort(pos_p)
    for i in order_p:
        mask = (pos_p < pos_p[i]) & (pos_n < pos_n[i])
        if mask.any():
            xs[i] = int((xs + rw)[mask].max())
    # y：按 Γ⁻ 序 DP，y_i = max over j(Γ⁺后、Γ⁻先) 的 y_j + h_j
    order_n = np.argsort(pos_n)
    for i in order_n:
        mask = (pos_n < pos_n[i]) & (pos_p > pos_p[i])
        if mask.any():
            ys[i] = int((ys + rh)[mask].max())
    W = int(np.max(xs + rw))
    H = int(np.max(ys + rh))
    return xs, ys, rw, rh, W, H


def _ox(a, b, rng):
    """顺序交叉（OX）：子代继承 a 的一段，其余位置按 b 的顺序补全（保持合法排列）。"""
    n = len(a)
    a = np.asarray(a, dtype=np.int64).tolist()
    b = np.asarray(b, dtype=np.int64).tolist()
    p, q = sorted(rng.choice(n, 2, replace=False))
    segment = a[p:q]
    child = [None] * n
    child[p:q] = segment
    rest = [x for x in b if x not in segment]
    idx = 0
    for k in list(range(q, n)) + list(range(0, p)):
        child[k] = rest[idx]
        idx += 1
    assert None not in child, "OX 交叉失败"
    return np.asarray(child, dtype=np.int64)


def _individual(n, rng):
    perm = rng.permutation(n)
    pos = np.argsort(perm)
    perm2 = rng.permutation(n)
    pos2 = np.argsort(perm2)
    rot = (rng.random(n) < 0.5).astype(np.int64)
    return pos, pos2, rot


def _fitness(pos_p, pos_n, rot, widths, heights, net, Lhat, gamma):
    xs, ys, rw, rh, W, H = sp_decode(pos_p, pos_n, rot, widths, heights)
    hpwl = net.total_hpwl(xs, ys, rw, rh)
    ovf = overflow(xs, ys, rw, rh, Lhat)
    return hpwl, ovf, xs, ys, rw, rh, W, H


def sp_aga_solve(widths, heights, net, Lhat, budget_s, seed=0,
                 pop=24, elite=4, gamma=5e5):
    """序列对 + 自适应遗传算法求解问题二（对照算法）。

    适应度 = ΣHPWL + γ·Σoverflow（γ 大 → 先保证可行，再压低线长）。
    返回 best dict（含 xs/ys/rw/rh/W/H/hpwl/overflow/iterations/trace）。
    """
    rng = np.random.default_rng(seed)
    n = len(widths)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    Lhat = int(Lhat)

    pop_pos, pop_pos2, pop_rot, pop_fit, pop_sol = [], [], [], [], []
    for _ in range(pop):
        pp, pn, r = _individual(n, rng)
        hp, ovf, xs, ys, rw, rh, W, H = _fitness(pp, pn, r, widths, heights,
                                                 net, Lhat, gamma)
        pop_pos.append(pp)
        pop_pos2.append(pn)
        pop_rot.append(r)
        pop_fit.append(hp + gamma * ovf)
        pop_sol.append(dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                            hpwl=hp, overflow=ovf))

    order = np.argsort(pop_fit)
    best = pop_sol[order[0]]
    it = 0
    trace = []
    start = time.time()
    while time.time() - start < budget_s:
        order = np.argsort(pop_fit)
        new_pos = [pop_pos[order[k]] for k in range(elite)]
        new_pos2 = [pop_pos2[order[k]] for k in range(elite)]
        new_rot = [pop_rot[order[k]] for k in range(elite)]
        new_fit = [pop_fit[order[k]] for k in range(elite)]
        new_sol = [pop_sol[order[k]] for k in range(elite)]

        var = float(np.var([f for f in pop_fit]))
        scale = max(0.0, min(1.0, var / (max(best["hpwl"], 1) ** 2)))
        pc = 0.9 - 0.3 * scale
        pm = 0.1 + 0.2 * scale

        def _tournament():
            idxs = rng.choice(pop, 2, replace=False)
            return idxs[0] if pop_fit[idxs[0]] <= pop_fit[idxs[1]] else idxs[1]

        while len(new_pos) < pop:
            ia, ib = _tournament(), _tournament()
            if rng.random() < pc:
                c1 = _ox(pop_pos[ia], pop_pos[ib], rng)
                c2 = _ox(pop_pos2[ia], pop_pos2[ib], rng)
                c3 = pop_rot[ia].copy()
                mask = rng.random(n) < 0.5
                c3[mask] = pop_rot[ib][mask]
            else:
                c1, c2, c3 = pop_pos[ia], pop_pos2[ia], pop_rot[ia].copy()
            if rng.random() < pm:
                a, b = sorted(rng.choice(n, 2, replace=False))
                c1[a], c1[b] = c1[b], c1[a]
                c2[a], c2[b] = c2[b], c2[a]
            if rng.random() < pm:
                a, b = sorted(rng.choice(n, 2, replace=False))
                c1[a:b] = c1[a:b][::-1]
                c2[a:b] = c2[a:b][::-1]
            if rng.random() < pm:
                c3[rng.integers(0, n)] ^= 1
            hp, ovf, xs, ys, rw, rh, W, H = _fitness(
                c1, c2, c3, widths, heights, net, Lhat, gamma)
            new_pos.append(c1)
            new_pos2.append(c2)
            new_rot.append(c3)
            new_fit.append(hp + gamma * ovf)
            new_sol.append(dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                                hpwl=hp, overflow=ovf))
        pop_pos, pop_pos2, pop_rot, pop_fit, pop_sol = \
            new_pos, new_pos2, new_rot, new_fit, new_sol

        order = np.argsort(pop_fit)
        cand = pop_sol[order[0]]
        if (cand["overflow"], cand["hpwl"]) <= (best["overflow"], best["hpwl"]):
            best = dict(cand)
        it += 1
        if it % 50 == 0:
            trace.append((time.time() - start, best["hpwl"], best["overflow"]))
    best["iterations"] = it
    best["trace"] = trace
    return best
