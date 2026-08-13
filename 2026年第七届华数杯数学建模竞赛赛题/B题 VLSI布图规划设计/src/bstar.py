"""B*-树表示与解码（对照算法，L2）。

B*-树性质：
  * 根对应左下角模块；左孩子在父模块右侧（x = x_u + w_u），右孩子在父模块上方（x = x_u）；
  * 解码天然无重叠：x 由左孩子链累加确定，y 由"等高线数组"在 DFS 中确定；
  * 邻域操作：旋转 / 交换子树 / 移动子树，配合 Metropolis 接受准则做模拟退火。
"""
from __future__ import annotations

import time
import numpy as np

from packing import lex_cost


class BStarTree:
    def __init__(self, widths, heights, rot, root, parent, left, right, bound_w):
        self.widths = np.asarray(widths, dtype=np.int64)
        self.heights = np.asarray(heights, dtype=np.int64)
        self.n = len(self.widths)
        self.rot = np.asarray(rot, dtype=np.int64)
        self.root = int(root)
        self.parent = np.asarray(parent, dtype=np.int64)
        self.left = np.asarray(left, dtype=np.int64)
        self.right = np.asarray(right, dtype=np.int64)
        self.bound_w = int(bound_w)

    @classmethod
    def from_chain(cls, widths, heights, order, rot, bound_w):
        """按放置顺序构建一棵左孩子链（解码即从左到右一行摆放，保证合法）。"""
        n = len(widths)
        parent = np.full(n, -1, dtype=np.int64)
        left = np.full(n, -1, dtype=np.int64)
        right = np.full(n, -1, dtype=np.int64)
        root = order[0]
        for k in range(1, n):
            u, v = order[k - 1], order[k]
            left[u] = v
            parent[v] = u
        return cls(widths, heights, rot, root, parent, left, right, bound_w)

    @classmethod
    def from_positions(cls, widths, heights, rot, xs, ys, rw, rh, bound_w):
        """从"左下压缩"型 packing 重建 B*-树（标准重建算法，失败则回退为链式）。"""
        n = len(widths)
        parent = np.full(n, -1, dtype=np.int64)
        left = np.full(n, -1, dtype=np.int64)
        right = np.full(n, -1, dtype=np.int64)
        contour = np.zeros(bound_w + 1, dtype=np.int64)
        order = sorted(range(n), key=lambda i: (ys[i], xs[i]))
        placed = []
        root = order[0]
        for m in order:
            xm, ym = int(xs[m]), int(ys[m])
            wm = int(rw[m])
            if m == root:
                placed.append(m)
                contour[xm : xm + wm] = ym + rh[m]
                continue
            parent_u, is_left = -1, False
            for u in placed:
                if xs[u] + rw[u] == xm and ys[u] == ym and left[u] == -1:
                    parent_u, is_left = u, True
                    break
            if parent_u == -1:
                for u in placed:
                    if xs[u] == xm and ys[u] + rh[u] == ym and right[u] == -1:
                        parent_u, is_left = u, False
                        break
            if parent_u == -1:
                u = max(placed, key=lambda i: (ys[i], xs[i]))
                if left[u] == -1:
                    parent_u, is_left = u, True
                elif right[u] == -1:
                    parent_u, is_left = u, False
                else:
                    u = next(v for v in placed if left[v] == -1 or right[v] == -1)
                    parent_u, is_left = u, left[u] == -1
            parent[m] = parent_u
            if is_left:
                left[parent_u] = m
            else:
                right[parent_u] = m
            placed.append(m)
            contour[xm : xm + wm] = ym + rh[m]
        return cls(widths, heights, rot, root, parent, left, right, bound_w)

    @classmethod
    def from_shelf(cls, widths, heights, order, rot, W_target):
        """按"货架式"构造一棵初始 B*-树：每层货架为一条左孩子链，
        下一层货架首模块挂接为上一层首模块的右孩子（置于其上方）。
        解码天然合法，且初始布局接近目标宽度。"""
        n = len(widths)
        rot = np.asarray(rot, dtype=np.int64)
        widths = np.asarray(widths, dtype=np.int64)
        heights = np.asarray(heights, dtype=np.int64)
        shelves = []
        cur = []
        cur_w = 0
        for m in order:
            w = widths[m] if rot[m] == 0 else heights[m]
            if cur and cur_w + w > W_target:
                shelves.append(cur)
                cur = []
                cur_w = 0
            cur.append(m)
            cur_w += w
        if cur:
            shelves.append(cur)
        parent = np.full(n, -1, dtype=np.int64)
        left = np.full(n, -1, dtype=np.int64)
        right = np.full(n, -1, dtype=np.int64)
        root = shelves[0][0]
        for si in range(len(shelves)):
            shelf = shelves[si]
            for k in range(len(shelf) - 1):
                left[shelf[k]] = shelf[k + 1]
                parent[shelf[k + 1]] = shelf[k]
            if si + 1 < len(shelves):
                right[shelf[0]] = shelves[si + 1][0]
                parent[shelves[si + 1][0]] = shelf[0]
        bound_w = int(max(np.sum(widths), np.sum(heights))) + 10
        return cls(widths, heights, rot, root, parent, left, right, bound_w)

    def decode(self):
        """解码得到 (xs, ys, rw, rh, W, H)，保证无重叠。

        x 由前序遍历累加（左孩子 x = x_u + w_u，右孩子 x = x_u）；
        y 用等高线数组在"父→左→右"前序中确定（右孩子置于父模块上方）。
        """
        n = self.n
        rw = np.where(self.rot == 1, self.heights, self.widths).astype(np.int64)
        rh = np.where(self.rot == 1, self.widths, self.heights).astype(np.int64)
        xs = np.zeros(n, dtype=np.int64)
        ys = np.zeros(n, dtype=np.int64)
        contour = np.zeros(self.bound_w + 1, dtype=np.int64)
        stack = [(self.root, 0)]
        while stack:
            u, xu = stack.pop()
            x0, w0 = xu, int(rw[u])
            xs[u] = x0
            y = int(contour[x0 : x0 + w0].max())
            ys[u] = y
            contour[x0 : x0 + w0] = y + int(rh[u])
            if self.right[u] != -1:
                stack.append((self.right[u], x0))
            if self.left[u] != -1:
                stack.append((self.left[u], x0 + w0))
        W = int(np.max(xs + rw))
        H = int(np.max(ys + rh))
        return xs, ys, rw, rh, W, H

    def _snapshot(self):
        return (self.root, self.parent.copy(), self.left.copy(),
                self.right.copy(), self.rot.copy())

    def _restore(self, snap):
        self.root, self.parent, self.left, self.right, self.rot = snap

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

    def _insert(self, u, p, side):
        self.parent[u] = p
        if side == 0:
            self.left[p] = u
        else:
            self.right[p] = u

    def _is_ancestor(self, a, b):
        while a != -1:
            if a == b:
                return True
            a = self.parent[a]
        return False

    def perturb(self, rng):
        """随机选择并执行一个邻域操作。返回操作名供统计。"""
        op = rng.integers(0, 3)
        if op == 0:
            u = int(rng.integers(0, self.n))
            self.rot[u] ^= 1
            return "rotate"
        if op == 1:
            for _ in range(64):
                a = int(rng.integers(0, self.n))
                b = int(rng.integers(0, self.n))
                if a == b:
                    continue
                if self._is_ancestor(a, b) or self._is_ancestor(b, a):
                    continue
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
                return "swap"
            return "swap"
        u = int(rng.integers(0, self.n))
        self._detach(u)
        for _ in range(64):
            p = int(rng.integers(0, self.n))
            if p == u or (self.left[p] != -1 and self.right[p] != -1):
                continue
            side = 0 if self.left[p] == -1 else 1
            self._insert(u, p, side)
            return "move"
        self._insert(u, 0, 0)
        return "move"


def bstar_sa_solve(
    widths,
    heights,
    rot,
    root,
    parent,
    left,
    right,
    bound_w,
    budget_s,
    seed=0,
    t0=None,
    min_iter=500,
):
    """B*-树 + 模拟退火：字典序目标 (WH, |W/H-1|)。

    返回 dict(best_xs, best_ys, best_rw, best_rh, W, H, cost,
              best_rot, iterations, trace)
    """
    rng = np.random.default_rng(seed)
    tree = BStarTree(widths, heights, rot, root, parent, left, right, bound_w)
    xs, ys, rw, rh, W, H = tree.decode()
    best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                rot=tree.rot.copy(), cost=lex_cost(W, H))
    n = tree.n
    if t0 is None:
        t0 = 500.0
    t = float(t0)
    alpha = 0.995
    tmin = 1e-4
    it = 0
    trace = []
    start = time.time()
    while time.time() - start < budget_s:
        if it % 100 == 0:
            t = max(t * alpha, tmin)
        snap = tree._snapshot()
        tree.perturb(rng)
        xs2, ys2, rw2, rh2, W2, H2 = tree.decode()
        delta = (W2 * H2) - (W * H)
        it += 1
        if delta < 0 or rng.random() < np.exp(-delta / t):
            W, H = W2, H2
            c2 = lex_cost(W2, H2)
            if c2 < best["cost"]:
                best = dict(xs=xs2, ys=ys2, rw=rw2, rh=rh2, W=W2, H=H2,
                            rot=tree.rot.copy(), cost=c2)
            continue
        tree._restore(snap)
        if it % 200 == 0:
            trace.append((time.time() - start, best["W"] * best["H"],
                          best["W"], best["H"]))
    best["iterations"] = it
    best["trace"] = trace
    return best
