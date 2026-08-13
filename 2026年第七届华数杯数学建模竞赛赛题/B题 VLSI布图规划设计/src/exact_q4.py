"""问题四 L3：精确验证 —— 面积下界 + 因子枚举 + 首空位精确 DFS（4 模块实例）。

思路（《问题4_算法.md》第五节）：
  * 面积下界 S* >= A；在 A 的整数因子对 (W,H) 上检验可铺砌性；
  * 首空位规范序 DFS：始终把下一模块放在"最左下首空闲格"，锚点置于
    覆盖该格子的子块对应位置（整体落位，刚性链接天然满足）；
  * 剪枝：剩余模块面积 > 当前空格数则回溯；旋转/镜像等价剪枝。
"""
from __future__ import annotations

import math


def factor_pairs(A: int):
    """返回 A 的所有整数因子对 (W,H)，按"面积升序、长宽比接近1"排序。"""
    pairs = []
    for w in range(1, int(math.isqrt(A)) + 1):
        if A % w == 0:
            h = A // w
            pairs.append((w, h))
            pairs.append((h, w))
    pairs = list(dict.fromkeys(pairs))
    pairs.sort(key=lambda p: (p[0] * p[1], abs(p[0] / p[1] - 1.0)))
    return pairs


def _first_free_cell(occ, W, H):
    for y in range(H):
        for x in range(W):
            if (x, y) not in occ:
                return x, y
    return None


def exact_pack(modules, W, H):
    """首空位规范序 DFS：判定 modules 能否铺满 W×H。

    Returns: (ok, solution)  solution = {m: (x, y, r)} 或 None。
    """
    n = len(modules)
    total_area = sum(m.area for m in modules)
    if total_area > W * H:
        return False, None

    occ = set()
    placed = [False] * n
    sol = {}
    result = [False, None]

    def dfs(n_placed):
        if result[0]:
            return True
        if n_placed == n:
            result[0] = True
            result[1] = dict(sol)
            return True
        cell = _first_free_cell(occ, W, H)
        if cell is None:
            return False
        cx, cy = cell
        # 剩余面积剪枝
        remain = sum(modules[m].area for m in range(n) if not placed[m])
        if remain > W * H - len(occ):
            return False
        for m in range(n):
            if placed[m]:
                continue
            mod = modules[m]
            for r in range(4):
                for w, h, a, b in mod.rotated(r):
                    # 锚点 = cell 相对子块 (a,b) 的反推
                    ax, ay = cx - a, cy - b
                    if not (0 <= ax and 0 <= ay and ax + w <= W and ay + h <= H):
                        continue
                    if not mod.fits(r, ax, ay, occ, W, H):
                        continue
                    placed[m] = True
                    sol[m] = (ax, ay, r)
                    mod.place(r, ax, ay, occ)
                    if dfs(n_placed + 1):
                        return True
                    # 回退
                    mod.unplace(r, ax, ay, occ)
                    placed[m] = False
                    del sol[m]
        return False

    dfs(0)
    return result[0], result[1]


def find_optimal(modules):
    """因子枚举 + 精确 DFS：返回 (S*, W, H, solution, trials)。

    trials: [(W,H,可行?)] 尝试历史。
    """
    A = sum(m.area for m in modules)
    trials = []
    for W, H in factor_pairs(A):
        ok, sol = exact_pack(modules, W, H)
        trials.append((W, H, ok))
        if ok:
            return W * H, W, H, sol, trials
    # 无完美铺砌：放宽到最小面积 > A（本实例不会走到）
    for W in range(1, A + 1):
        for H in range(W, A + 1):
            if W * H < A:
                continue
            ok, sol = exact_pack(modules, W, H)
            trials.append((W, H, ok))
            if ok:
                return W * H, W, H, sol, trials
    return None, None, None, None, trials
