"""第1层（L1）：多源初解生成池与多样性粗筛。

四种初解生成机制：
  (1) HSA 贪心构造：按评估函数 V_i = λ1·area_i/(WH) + λ2·(w_i+h_i)/(W+H) 降序装箱；
  (2) BL/Skyline 多规则：面积降序 / 长边降序 / 周长降序 / 随机排序；
  (3) LFF：灵活性小者优先（|w-h| 越大越不灵活 → 先放）；
  (4) 随机预选 90° 旋转打破对称性（叠加于各机制）。
随后以"轮廓差异 + 结构差异 + 旋转差异"构造多样性指标，粗筛保留 K' 个代表初解。
"""
from __future__ import annotations

import numpy as np

from packing import pack_skyline, lex_cost


def _hsa_order(widths, heights, lam1, lam2, rng):
    """HSA 贪心：按 V_i 动态评估函数逐模块挑选装箱顺序。"""
    n = len(widths)
    rem = list(range(n))
    order = []
    W, H = 1, 1
    areas = widths * heights
    while rem:
        vals = []
        for i in rem:
            v = lam1 * areas[i] / (W * H) + lam2 * (widths[i] + heights[i]) / (W + H)
            vals.append((v, i))
        vals.sort(key=lambda t: (-t[0], t[1]))
        _, mid = vals[0]
        order.append(mid)
        rem.remove(mid)
        W += widths[mid]
        H += heights[mid]
    return order


def _gen_order_rot(widths, heights, rng):
    """生成 (order, rot) 对：返回 None 表示使用机制默认顺序。"""
    n = len(widths)
    orders = {}

    orders["hsa_1"] = (_hsa_order(widths, heights, 0.6, 0.4, rng), "hsa")
    orders["hsa_2"] = (_hsa_order(widths, heights, 0.35, 0.65, rng), "hsa")
    orders["hsa_3"] = (_hsa_order(widths, heights, 0.8, 0.2, rng), "hsa")

    orders["area_desc"] = (np.argsort(-(widths * heights)).tolist(), "skyline")
    longside = np.maximum(widths, heights)
    orders["long_desc"] = (np.argsort(-longside, kind="stable").tolist(), "skyline")
    orders["perim_desc"] = (np.argsort(-(widths + heights), kind="stable").tolist(), "skyline")
    orders["random_1"] = (rng.permutation(n).tolist(), "skyline")

    lff = np.abs(widths - heights)
    orders["lff"] = (np.argsort(-lff, kind="stable").tolist(), "lff")

    orders["random_2"] = (rng.permutation(n).tolist(), "skyline")
    orders["random_3"] = (rng.permutation(n).tolist(), "skyline")
    return orders


def _pack_solution(ds, order, rot, strip_w):
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    res = pack_skyline(order, rot, widths, heights, strip_w, box=(strip_w, None),
                       auto_rotate=True)
    if res is None:
        return None
    xs, ys, rw, rh, W, H = res
    return dict(order=order, rot=np.asarray(rot, dtype=np.int64), xs=xs, ys=ys,
                rw=rw, rh=rh, W=int(W), H=int(H), area=int(W) * int(H),
                asp=abs(W / H - 1.0), cost=lex_cost(W, H))


def generate_initial_pool(ds, rng=None, prob_rot=0.3, strip_w=None):
    """生成 K >= 10 个初始布局（含机制标签），并计算各自轮廓。

    以固定条带宽 strip_w 做 Skyline 装箱（默认取 sqrt(A)）。
    """
    if rng is None:
        rng = np.random.default_rng(0)
    widths = np.asarray(ds.widths, dtype=np.int64)
    heights = np.asarray(ds.heights, dtype=np.int64)
    n = ds.n
    if strip_w is None:
        strip_w = int(np.sqrt(ds.total_area))
    spec = _gen_order_rot(widths, heights, rng)
    pool = []
    for key, (order, mech) in spec.items():
        rot = np.zeros(n, dtype=np.int64)
        if key.startswith("random") or rng.random() < prob_rot:
            rot = (rng.random(n) < prob_rot).astype(np.int64)
        sol = _pack_solution(ds, order, rot, strip_w)
        if sol is not None:
            sol["mech"] = mech
            sol["key"] = key
            pool.append(sol)
    return pool


def diversity_filter(pool, kp):
    """以"轮廓尺寸 + 结构位置 + 旋转"多样性指标粗筛，保留 K' 个代表初解。"""
    if len(pool) <= kp:
        return pool
    sols = sorted(pool, key=lambda s: s["cost"])
    Wmax = max(s["W"] for s in sols)
    Hmax = max(s["H"] for s in sols)
    selected = [sols[0]]
    rest = sols[1:]
    while len(selected) < kp and rest:
        best = None
        best_score = -1.0
        for cand in rest:
            dmin = min(_diversity(cand, s, Wmax, Hmax) for s in selected)
            score = dmin - cand["area"] * 1e-12
            if score > best_score:
                best_score = score
                best = cand
        if best is None:
            break
        selected.append(best)
        rest = [r for r in rest if r is not best]
    return selected


def _diversity(a, b, Wmax, Hmax):
    n = len(a["xs"])
    d_outline = abs(a["W"] - b["W"]) / Wmax + abs(a["H"] - b["H"]) / Hmax
    dx = np.abs(a["xs"] / max(a["W"], 1) - b["xs"] / max(b["W"], 1))
    dy = np.abs(a["ys"] / max(a["H"], 1) - b["ys"] / max(b["H"], 1))
    d_pos = float((dx + dy).mean())
    d_rot = float(np.mean(a["rot"] != b["rot"]))
    return d_outline + d_pos + 0.5 * d_rot
