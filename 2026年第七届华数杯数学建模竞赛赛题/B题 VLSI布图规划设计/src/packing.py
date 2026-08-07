"""核心几何算子：Skyline 装箱、字典序目标、合法性校验。

数据结构采用"稠密等高线数组 + 滑动窗口最大滤波"：
  * 轮廓线 contour[x] 表示 x 列当前的最高占用高度；
  * 放置 w×h 矩形时，滑动窗口最大滤波给出所有候选 x 处窗口内最大高度，
    取"最低、最左"位置放置（即经典 Skyline/Bottom-Left 准则），整体向量化。
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d

BIG = 10_000_000  # 字典序中面积项的放大系数，使面积差严格支配长宽比差


def lex_cost(W: int, H: int) -> int:
    """字典序目标 cost = WH*BIG + round(1e6*|W/H-1|)。"""
    return W * H * BIG + int(round(abs(W / H - 1.0) * 1e6))


def lex_key(W: int, H: int) -> tuple[int, int]:
    """字典序比较键：(面积, 长宽比惩罚)。"""
    return W * H, round(abs(W / H - 1.0) * 1e6)


def pack_skyline(
    order: list[int],
    rot: list[int] | np.ndarray,
    widths: np.ndarray,
    heights: np.ndarray,
    bound_w: int,
    box: tuple[int, int | None] | None = None,
    auto_rotate: bool = False,
):
    """按给定放置顺序与旋转，用 Skyline 准则装箱。

    放置准则：在"最低"可行位置中，选取"该矩形下方残留空白面积最小"者（填平凹凸），
    并列时取最左，从而在经典 BL 基础上显著提升密度。

    Args:
        order: 模块序号放置顺序（长度 n）。
        rot:   per-module 是否 90° 旋转（0/1，长度 n）。
        widths/heights: 按模块序号索引的宽/高。
        bound_w: 等高线数组宽度上界（需 >= 任意可行轮廓宽）。
        box: 可选 (W0, H0)，要求最终轮廓不超界；超界则返回 infeasible。
        auto_rotate: 若 True，放置每个模块时贪心选择更优朝向并同步更新 rot。

    Returns:
        (xs, ys, rw, rh, W, H) 或 None（box 下不可行）。
    """
    n = len(order)
    Wmax = int(bound_w)
    contour = np.zeros(Wmax + 1, dtype=np.int64)
    xs = np.zeros(n, dtype=np.int64)
    ys = np.zeros(n, dtype=np.int64)
    rw = np.zeros(n, dtype=np.int64)
    rh = np.zeros(n, dtype=np.int64)
    rot = np.asarray(rot, dtype=np.int64)

    for i, mid in enumerate(order):
        orientations = [(widths[mid], heights[mid]), (heights[mid], widths[mid])]
        if not auto_rotate:
            orientations = [orientations[int(rot[mid])]]
        best_place = None
        for wi, hi in orientations:
            if wi > Wmax:
                continue
            M = maximum_filter1d(contour, size=wi, origin=-(wi - 1) // 2,
                                 mode="constant", cval=0)
            cand = M[: Wmax - wi + 1]
            if box is not None:
                W0, H0 = box
                ok_mask = np.arange(cand.size) <= W0 - wi
                if H0 is not None:
                    ok_mask &= cand <= H0 - hi
                if not ok_mask.any():
                    continue
                feasible = np.nonzero(ok_mask)[0]
                cand = cand[feasible]
            else:
                feasible = np.arange(cand.size)
            y = int(cand.min())
            x = int(feasible[int(np.argmax(cand == y))])
            if best_place is None or (y, x) < (best_place[0], best_place[1]):
                best_place = (y, x, wi, hi)
        if best_place is None:
            return None
        y, x, wi, hi = best_place
        rot[mid] = 1 if (wi, hi) == (heights[mid], widths[mid]) else 0
        xs[mid] = x
        ys[mid] = y
        rw[mid] = wi
        rh[mid] = hi
        contour[x : x + wi] = y + hi

    W = int(np.max(xs + rw))
    H = int(np.max(ys + rh))
    return xs, ys, rw, rh, W, H


def verify(block_area: np.ndarray, xs: np.ndarray, ys: np.ndarray,
           rw: np.ndarray, rh: np.ndarray, W: int, H: int) -> tuple[bool, int]:
    """合法性与重叠检查（O(n^2)）。返回 (合法, 最大重叠面积)。"""
    n = len(xs)
    if n == 0:
        return True, 0
    if xs.min() < 0 or ys.min() < 0 or int((xs + rw).max()) > W or int((ys + rh).max()) > H:
        return False, -1
    max_overlap = 0
    for i in range(n):
        for j in range(i + 1, n):
            ox = min(xs[i] + rw[i], xs[j] + rw[j]) - max(xs[i], xs[j])
            oy = min(ys[i] + rh[i], ys[j] + rh[j]) - max(ys[i], ys[j])
            if ox > 0 and oy > 0:
                max_overlap = max(max_overlap, ox * oy)
    return max_overlap == 0, max_overlap


def total_area(block_area: np.ndarray) -> int:
    return int(block_area.sum())
