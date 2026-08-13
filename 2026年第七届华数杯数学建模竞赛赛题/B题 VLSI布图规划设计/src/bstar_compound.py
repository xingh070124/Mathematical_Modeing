"""问题四 L2 对照算法：复合形状 B*-树 + 快速模拟退火（咬合版）。

B*-树节点表示复合矩形模块（子块刚性链接）。解码时每个节点仍按
"左孩子贴父右侧、右孩子置父上方"的 B*-树规则定序，但**落位校验用复合
形状整模判定**（非包围盒），从而支持凹凸咬合、达到与精确解一致的密度。

解码算法：
  * 前序遍历 B*-树，顺序 = 放置顺序；
  * 逐模块在可行锚点域内按"最低、最左"落位，校验全部子块占用格空闲且
    不越界（刚性链接整体落位）；
  * 代价 = 字典序 (面积, |W/H-1|)，Metropolis 接受，快速降温 + 重启。
"""
from __future__ import annotations

import time
import numpy as np

from polyomino import pack_compound
from bstar import BStarTree


class CompoundBStar:
    """复合形状 B*-树：节点保存旋转，解码时复合形状整模落位。"""

    def __init__(self, modules, rot, root, parent, left, right):
        self.modules = modules
        self.n = len(modules)
        self.rot = np.asarray(rot, dtype=np.int64)
        self.root = int(root)
        self.parent = np.asarray(parent, dtype=np.int64)
        self.left = np.asarray(left, dtype=np.int64)
        self.right = np.asarray(right, dtype=np.int64)

    def preorder(self):
        """前序遍历：返回 (节点序列, 各节点在序列中的位置)。"""
        seq = []
        stack = [self.root]
        while stack:
            u = stack.pop()
            seq.append(u)
            if self.right[u] != -1:
                stack.append(self.right[u])
            if self.left[u] != -1:
                stack.append(self.left[u])
        return seq

    def decode(self, bound_w, bound_h):
        """按前序顺序复合装箱：返回 (xs, ys, rot, W, H) 或 None。"""
        seq = self.preorder()
        rot = [int(self.rot[u]) for u in seq]
        res = pack_compound(self.modules, seq, rot, bound_w, bound_h)
        if res is None:
            return None
        xs, ys, rot_used, W, H = res
        return xs, ys, rot_used, W, H

    def _snapshot(self):
        return (self.root, self.parent.copy(), self.left.copy(),
                self.right.copy(), self.rot.copy())

    def _restore(self, snap):
        self.root, self.parent, self.left, self.right, self.rot = snap

    def _swap_nodes(self, a, b):
        pa, pb = self.parent[a], self.parent[b]
        if pa == -1:
            self.root = b
        elif self.left[pa] == a:
            self.left[pa] = b
        else:
            self.right[pa] = b
        if pb == -1:
            self.root = a
        elif self.left[pb] == b:
            self.left[pb] = a
        else:
            self.right[pb] = a
        self.parent[a], self.parent[b] = pb, pa

    def perturb(self, rng):
        """邻域：旋转 / 交换节点 / 移动节点。"""
        op = rng.integers(0, 3)
        n = self.n
        if op == 0:
            u = int(rng.integers(0, n))
            self.rot[u] = (self.rot[u] + int(rng.integers(1, 4))) % 4
            return "rotate"
        if op == 1:
            for _ in range(64):
                a = int(rng.integers(0, n))
                b = int(rng.integers(0, n))
                if a == b or self._is_ancestor(a, b) or self._is_ancestor(b, a):
                    continue
                self._swap_nodes(a, b)
                return "swap"
            return "swap"
        # move：摘除 u 重插
        u = int(rng.integers(0, n))
        self._detach(u)
        for _ in range(64):
            p = int(rng.integers(0, n))
            if p == u or (self.left[p] != -1 and self.right[p] != -1):
                continue
            side = 0 if self.left[p] == -1 else 1
            if side == 0:
                self.left[p] = u
            else:
                self.right[p] = u
            self.parent[u] = p
            return "move"
        self.left[0 if self.root != 0 else 1] = u if self.root != 0 else u
        self.parent[u] = 0 if self.root != 0 else 1
        return "move"

    def _is_ancestor(self, a, b):
        while a != -1:
            if a == b:
                return True
            a = self.parent[a]
        return False

    def _detach(self, u):
        p = self.parent[u]
        l, r = self.left[u], self.right[u]
        if r != -1:
            lr = r
            while self.left[lr] != -1:
                lr = self.left[lr]
            if l != -1:
                self.left[lr] = l
                self.parent[l] = lr
            repl = r
        elif l != -1:
            repl = l
        else:
            repl = -1
        if p == -1:
            self.root = repl
        elif self.left[p] == u:
            self.left[p] = repl
        else:
            self.right[p] = repl
        if repl != -1:
            self.parent[repl] = p
        self.parent[u] = -1
        self.left[u] = -1
        self.right[u] = -1


def compound_bstar_sa(modules, budget_s, seed=0, init_rot=None):
    """复合形状 B*-树 + 快速模拟退火。

    Returns: dict(xs, ys, rot, W, H, area, asp, iterations, trace)。
    """
    rng = np.random.default_rng(seed)
    n = len(modules)
    bound_w = int(sum(max(m.bbox[0], m.bbox[1]) for m in modules)) + 10
    bound_h = bound_w

    # 初始树：链式（左孩子链）
    parent = np.full(n, -1, dtype=np.int64)
    left = np.full(n, -1, dtype=np.int64)
    right = np.full(n, -1, dtype=np.int64)
    root = 0
    for k in range(1, n):
        left[k - 1] = k
        parent[k] = k - 1
    rot = np.zeros(n, dtype=np.int64)
    if init_rot is not None:
        rot = np.asarray(init_rot, dtype=np.int64).copy()

    tree = CompoundBStar(modules, rot, root, parent, left, right)

    def eval_tree():
        res = tree.decode(bound_w, bound_h)
        if res is None:
            return None
        xs, ys, rot_used, W, H = res
        return dict(xs=xs, ys=ys, rot=rot_used, W=int(W), H=int(H),
                    area=int(W) * int(H), asp=abs(W / H - 1.0))

    cur = eval_tree()
    if cur is None:
        return None
    best = dict(cur)
    T = 300.0
    alpha = 0.95
    tmin = 1.0
    start = time.time()
    it = 0
    trace = [(0.0, best["area"], best["asp"])]
    while time.time() - start < budget_s:
        snap = tree._snapshot()
        op = tree.perturb(rng)
        cand = eval_tree()
        if cand is None:
            tree._restore(snap)
            continue
        it += 1
        delta = (cand["area"] * 10_000_000 + cand["asp"] * 1_000_000) \
            - (cur["area"] * 10_000_000 + cur["asp"] * 1_000_000)
        if delta <= 0 or rng.random() < np.exp(-delta / T):
            cur = cand
            if (cand["area"], cand["asp"]) < (best["area"], best["asp"]):
                best = dict(cand)
        else:
            tree._restore(snap)
        T = max(T * alpha, tmin)
        if it % 200 == 0:
            trace.append((time.time() - start, best["area"], best["asp"]))
    best["iterations"] = it
    best["trace"] = trace
    return best


def exhaustive_search(modules):
    """全枚举：所有排列 (n!) × 旋转 (C4^n) 组合，返回最优解。

    Returns: (best, total_combinations, all_achieved)
      best: dict(xs,ys,rot,W,H,area,asp) 或 None
      all_achieved: {area: count} 各面积达成的组合数。
    """
    from itertools import permutations, product
    n = len(modules)
    bound_w = int(sum(max(m.bbox[0], m.bbox[1]) for m in modules)) + 10
    bound_h = bound_w
    best = None
    achieved = {}
    total = 0
    for order in permutations(range(n)):
        for rots in product(range(4), repeat=n):
            res = pack_compound(modules, list(order), list(rots),
                                bound_w, bound_h)
            if res is None:
                continue
            xs, ys, rot_used, W, H = res
            area = int(W) * int(H)
            asp = abs(W / H - 1.0)
            achieved[area] = achieved.get(area, 0) + 1
            total += 1
            if best is None or (area, asp) < (best["area"], best["asp"]):
                best = dict(xs=xs, ys=ys, rot=rot_used, W=int(W), H=int(H),
                            area=area, asp=asp)
    return best, total, achieved
