"""第1层（L1）问题二适配：终端感知多源初解生成池。

问题二初解需把模块优先放到所连引脚附近，生成 K>=10 个初解：
  S1 树式贪心（HSA式）：评估函数引入 netdeg 项，线网度越大越早放；
  S2 Terminal 锚点贪心：以相连终端引脚几何中心为理想位置，按其分簇排序；
  S3 Skyline/BL 多规则：目标框固定为 (Lhat, Lhat)，优先放相连终端的模块；
  S4 随机/混合：随机排列 + 随机预选 90° 旋转（多样性保底）。

随后按"结构位置 + 旋转"多样性粗筛保留 K' 个代表初解（统一转为 B*-树）。
"""
from __future__ import annotations

import numpy as np

from packing import pack_skyline
from hpwl import NetIndex, overflow, hpwl_of_placement, convex_lb_with_centers


def pack_in_box(widths, heights, order, rot, Lhat, ideal_x=None):
    """在 (Lhat, Lhat) 内 Skyline 装箱（PeF：可选 ideal_x 合法化）；
    贪心失败时放宽至 2Lhat 保证有解。"""
    res = pack_skyline(order, rot, widths, heights, Lhat,
                       box=(Lhat, Lhat), auto_rotate=True, ideal_x=ideal_x)
    if res is None:
        B = 2 * Lhat + 10
        res = pack_skyline(order, rot, widths, heights, B,
                           box=(B, B), auto_rotate=True, ideal_x=ideal_x)
    return res


def hpwl_greedy_pack(net, widths, heights, order, Lhat):
    """HPWL 贪心构造（S1 终端感知树式贪心的核心加速版）。

    按 order 依次放模块，每个模块在等高线候选位置中，贪心选择"所涉线网
    增量 HPWL 最小"的合法落点（兼顾不越界）。这是把"放哪最省线"直接编码
    进构造过程，比纯面积/长边序更贴合 HPWL 目标。
    返回 (xs, ys, rw, rh, hpwl) 或 None。
    """
    from scipy.ndimage import maximum_filter1d
    n = len(order)
    widths = np.asarray(widths, dtype=np.int64)
    heights = np.asarray(heights, dtype=np.int64)
    Wmax = int(Lhat)
    contour = np.zeros(Wmax + 1, dtype=np.int64)
    xs = np.zeros(n, dtype=np.int64)
    ys = np.zeros(n, dtype=np.int64)
    rw = np.zeros(n, dtype=np.int64)
    rh = np.zeros(n, dtype=np.int64)
    for mid in order:
        wm, hm = int(widths[mid]), int(heights[mid])
        candidates = []
        for wi, hi in ((wm, hm), (hm, wm)):
            if wi > Wmax:
                continue
            M = maximum_filter1d(contour, size=wi, origin=-(wi - 1) // 2,
                                 mode="constant", cval=0)
            cand = M[: Wmax - wi + 1]
            ok_mask = np.arange(cand.size) <= Wmax - wi
            ok_mask &= cand <= Lhat - hi
            if not ok_mask.any():
                continue
            feasible = np.nonzero(ok_mask)[0]
            yv = cand[feasible]
            # 候选落点（最低若干）
            ymin = int(yv.min())
            xs_cand = feasible[yv == ymin]
            for x0 in xs_cand[:16]:
                candidates.append((int(x0), ymin, wi, hi))
        if not candidates:
            return None
        # 增量评估每个候选落点所涉线网 HPWL
        best_place, best_delta = None, float("inf")
        base = None
        for (x0, y0, wi, hi) in candidates:
            xs[mid], ys[mid], rw[mid], rh[mid] = x0, y0, wi, hi
            d = 0.0
            for k in net.mod_nets[mid]:
                d += net.net_hpwl(k, xs, ys, rw, rh)
            if base is None:
                base = d  # 第一个候选为参照（都是未放置前状态，无需减）
            if d < best_delta:
                best_delta = d
                best_place = (x0, y0, wi, hi)
        x0, y0, wi, hi = best_place
        xs[mid], ys[mid], rw[mid], rh[mid] = x0, y0, wi, hi
        contour[x0:x0 + wi] = y0 + hi
    hp = net.total_hpwl(xs, ys, rw, rh)
    return xs, ys, rw, rh, hp


def _hsa_net_order(widths, heights, netdeg, lam1, lam2, lam3, rng):
    """HSA 贪心：V_i = λ1·area/(WH) + λ2·(w+h)/(W+H) + λ3·netdeg_i 动态选块。"""
    n = len(widths)
    rem = list(range(n))
    order = []
    W, H = 1.0, 1.0
    areas = widths * heights
    netdeg = netdeg.astype(float)
    while rem:
        vals = []
        for i in rem:
            v = (lam1 * areas[i] / (W * H)
                 + lam2 * (widths[i] + heights[i]) / (W + H)
                 + lam3 * netdeg[i])
            vals.append((v, i))
        vals.sort(key=lambda t: (-t[0], t[1]))
        _, mid = vals[0]
        order.append(mid)
        rem.remove(mid)
        W += widths[mid]
        H += heights[mid]
    return order


def _term_centroid_order(ds, net, Lhat):
    """S2 Terminal 锚点贪心：按相连终端引脚几何中心分簇排序。"""
    n = ds.n
    cx = np.zeros(n)
    cy = np.zeros(n)
    cnt = np.zeros(n)
    for i in range(n):
        for k in net.mod_nets[i]:
            for kind, ref in net.net_pins[k]:
                if kind == "t":
                    cx[i] += ref[0]
                    cy[i] += ref[1]
                    cnt[i] += 1
    for i in range(n):
        if cnt[i] > 0:
            cx[i] /= cnt[i]
            cy[i] /= cnt[i]
        else:
            cx[i], cy[i] = Lhat / 2.0, Lhat / 2.0
    # 以终端中心所在网格分簇，簇内按面积降序
    g = max(1, Lhat // 4)
    key = [(int(cx[i] // g), int(cy[i] // g), -(ds.widths[i] * ds.heights[i]), i)
           for i in range(n)]
    key.sort()
    return [i for *_, i in key]


def _lb_center_orders(ds, net, Lhat, centers):
    """S5 松弛中心排序（PeF）：按凸松弛理想中心的位置分簇排序。

    centers[i] = 模块 i 的无重叠松弛理想中心。按该中心空间分簇（网格 + 行），
    使合法化（skyline 装箱）后相连模块仍彼此邻近，压低 HPWL。
    """
    n = ds.n
    g = max(1, Lhat // 5)
    keys = {
        "lb_grid":  [(int(centers[i][0] // g), int(centers[i][1] // g),
                      -max(ds.widths[i], ds.heights[i]), i) for i in range(n)],
        "lb_snake": [(int(centers[i][1] // g), i) for i in range(n)],
        "lb_x":     [(int(centers[i][0] // g), int(centers[i][1] // g),
                      -(ds.widths[i] * ds.heights[i]), i) for i in range(n)],
    }
    out = {}
    for k, key in keys.items():
        key.sort()
        out[k] = [i for *_, i in key]
    return out


def _order_candidates(ds, net, Lhat, rng):
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n
    netdeg = net.module_netdeg()
    orders = {}

    orders["netdeg_hsa_1"] = _hsa_net_order(widths, heights, netdeg, 0.5, 0.2, 0.3, rng)
    orders["netdeg_hsa_2"] = _hsa_net_order(widths, heights, netdeg, 0.4, 0.3, 0.3, rng)

    orders["term_anchor"] = _term_centroid_order(ds, net, Lhat)

    orders["area_desc"] = np.argsort(-(widths * heights), kind="stable").tolist()
    longside = np.maximum(widths, heights)
    orders["long_desc"] = np.argsort(-longside, kind="stable").tolist()
    orders["perim_desc"] = np.argsort(-(widths + heights), kind="stable").tolist()

    orders["random_1"] = rng.permutation(n).tolist()
    orders["random_2"] = rng.permutation(n).tolist()
    orders["random_3"] = rng.permutation(n).tolist()
    return orders


def generate_initial_pool_q2(ds, net, Lhat, rng=None, prob_rot=0.3):
    """生成 K>=10 个终端感知初解，含 HPWL / 越界量 / 布局信息。"""
    if rng is None:
        rng = np.random.default_rng(0)
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n
    orders = _order_candidates(ds, net, Lhat, rng)
    # S5：凸松弛中心排序（PeF 范式），复用 L3 下界求解器
    _, centers = convex_lb_with_centers(ds, Lhat)
    for k, order in _lb_center_orders(ds, net, Lhat, centers).items():
        orders[k] = order
    ideal_x = np.asarray([c[0] for c in centers], dtype=np.int64)
    pool = []
    for key, order in orders.items():
        rot = np.zeros(n, dtype=np.int64)
        if key.startswith("random") or rng.random() < prob_rot:
            rot = (rng.random(n) < prob_rot).astype(np.int64)
        res = pack_in_box(widths, heights, order, rot, Lhat, ideal_x=ideal_x)
        if res is None:
            continue
        xs, ys, rw, rh, W, H = res
        hp = hpwl_of_placement(net, xs, ys, rw, rh)
        ovf = overflow(xs, ys, rw, rh, Lhat)
        pool.append(dict(key=key, mech=("random" if key.startswith("random") else "greedy"),
                         order=list(order), rot=rot, xs=xs, ys=ys,
                         rw=rw, rh=rh, W=int(W), H=int(H),
                         hpwl=hp, overflow=ovf))
    # S6：HPWL 贪心构造（线网增量最小化落点），对高质量初解再加一档
    for key in ["netdeg_hsa_1", "lb_grid", "term_anchor"]:
        if key not in orders:
            continue
        res = hpwl_greedy_pack(net, widths, heights, orders[key], Lhat)
        if res is None:
            continue
        xs, ys, rw, rh, hp = res
        ovf = overflow(xs, ys, rw, rh, Lhat)
        pool.append(dict(key=f"{key}_hpwl", mech="hpwl_greedy",
                         order=list(orders[key]), rot=np.zeros(n, dtype=np.int64),
                         xs=xs, ys=ys, rw=rw, rh=rh,
                         W=int((xs + rw).max()), H=int((ys + rh).max()),
                         hpwl=hp, overflow=ovf))
    return pool


def diversity_filter_q2(pool, kp):
    """按"结构位置 + 旋转"多样性粗筛，保留 K' 个代表初解。"""
    if len(pool) <= kp:
        return pool
    sols = sorted(pool, key=lambda s: (s["overflow"], s["hpwl"]))
    L = max((max(s["W"], s["H"]) for s in sols), default=1.0)
    selected = [sols[0]]
    rest = sols[1:]
    while len(selected) < kp and rest:
        best, best_score = None, -1.0
        for cand in rest:
            dmin = min(_diversity_q2(cand, s, L) for s in selected)
            score = dmin - cand["hpwl"] * 1e-12
            if score > best_score:
                best, best_score = cand, score
        if best is None:
            break
        selected.append(best)
        rest = [r for r in rest if r is not best]
    return selected


def _diversity_q2(a, b, L):
    dx = np.abs(a["xs"] / max(a["W"], 1) - b["xs"] / max(b["W"], 1))
    dy = np.abs(a["ys"] / max(a["H"], 1) - b["ys"] / max(b["H"], 1))
    d_pos = float((dx + dy).mean())
    d_rot = float(np.mean(a["rot"] != b["rot"]))
    return d_pos + 0.5 * d_rot
