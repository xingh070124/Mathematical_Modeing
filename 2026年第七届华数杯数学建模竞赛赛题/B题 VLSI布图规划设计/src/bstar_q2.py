"""第2层（L2）问题二主算法：B*-树 + 快速模拟退火（增量 HPWL + 自适应 γ）。

关键适配（相对问题一 bstar.py）：
  1. 代价 = ΣHPWL + γ·Σoverflow，γ 自适应调节（Chen-Chang）；
  2. 增量评估：仅重算"发生位置变化模块"所涉线网 O(deg·\bar d)，接受后以
     运行变量维护 HPWL，周期性全量校正避免浮点漂移；
  3. 邻域新增 Op5 终端引力移动：把关键模块移到所连引脚几何中心附近；
  4. 固定轮廓越界由罚函数处理，(C1) 无重叠由 B*-树表示内建。
"""
from __future__ import annotations

import time
import numpy as np

from bstar import BStarTree
from hpwl import overflow_of_module


class BStarTreeQ2(BStarTree):
    """B*-树 + 线网索引 + 固定轮廓；提供 Q2 版邻域与增量代价计算。"""

    def __init__(self, widths, heights, rot, root, parent, left, right,
                 bound_w, net, Lhat):
        super().__init__(widths, heights, rot, root, parent, left, right, bound_w)
        self.net = net
        self.Lhat = int(Lhat)
        self.netdeg = net.module_netdeg()
        self.termdeg = net.module_termdeg()
        self._grad = self.netdeg + 2.0 * self.termdeg   # 关键模块评分

    # ------------------------------------------------------------------ #
    # 邻域操作（Q2 版：rotate / swap / move / subtree-swap / gravity）
    # ------------------------------------------------------------------ #
    def perturb_q2(self, rng, xs, ys, rw, rh, p_gravity=0.25):
        """选择一个 Q2 邻域操作并执行，返回操作名。"""
        if rng.random() < p_gravity:
            return self.gravity_move(rng, xs, ys, rw, rh)
        op = rng.integers(0, 4)
        if op == 0:
            u = int(rng.integers(0, self.n))
            self.rot[u] ^= 1
            return "rotate"
        if op == 1:
            return self._try_swap(rng)
        if op == 2:
            return self._try_move(rng)
        return self._try_subtree_swap(rng)

    def _try_swap(self, rng):
        for _ in range(64):
            a = int(rng.integers(0, self.n))
            b = int(rng.integers(0, self.n))
            if a == b or self._is_ancestor(a, b) or self._is_ancestor(b, a):
                continue
            self._swap_nodes(a, b)
            return "swap"
        return "swap"

    def _try_move(self, rng):
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

    def _try_subtree_swap(self, rng):
        """Op4 子树交换：交换两棵子树根，保留各自子树结构（全局探索）。"""
        a = int(rng.integers(0, self.n))
        b = int(rng.integers(0, self.n))
        if a == b or self._is_ancestor(a, b) or self._is_ancestor(b, a):
            return "swap"
        self._swap_nodes(a, b)
        return "subtree_swap"

    def gravity_move(self, rng, xs, ys, rw, rh):
        """Op5 终端引力移动：把关键模块与其"理想位置最近"模块交换。

        关键模块 = 线网度 + 2×终端相连线网度 最大者（带随机扰动避免死锁）；
        理想位置 = 其相连引脚（终端固定坐标 + 已放模块中心）的几何中心。
        """
        n = self.n
        score = self._grad + rng.uniform(0, 0.5, size=n)
        u = int(np.argmax(score))
        pts = []
        for k in self.net.mod_nets[u]:
            for kind, ref in self.net.net_pins[k]:
                if kind == "m" and ref is not None:
                    pts.append((xs[ref] + rw[ref] / 2.0, ys[ref] + rh[ref] / 2.0))
                elif kind == "t" and ref is not None:
                    pts.append((float(ref[0]), float(ref[1])))
        if not pts:
            self.rot[u] ^= 1
            return "rotate"
        tx = sum(p[0] for p in pts) / len(pts)
        ty = sum(p[1] for p in pts) / len(pts)
        cx = xs + rw / 2.0
        cy = ys + rh / 2.0
        d = (cx - tx) ** 2 + (cy - ty) ** 2
        d[u] = np.inf
        best_v = int(np.argmin(d))
        if self._is_ancestor(u, best_v) or self._is_ancestor(best_v, u):
            self._swap_random(rng)
            return "swap"
        self._swap_nodes(u, best_v)
        return "gravity"

    def _swap_random(self, rng):
        for _ in range(64):
            a = int(rng.integers(0, self.n))
            b = int(rng.integers(0, self.n))
            if a != b and not self._is_ancestor(a, b) and not self._is_ancestor(b, a):
                self._swap_nodes(a, b)
                return

    # ------------------------------------------------------------------ #
    # 增量代价（核心：仅重算被扰动模块所涉线网）
    # ------------------------------------------------------------------ #
    def delta_cost(self, xs_old, ys_old, rw_old, rh_old, gamma):
        """解码当前树，返回 (delta_hpwl, ovf_old, ovf_new, 新位置, 扰动线网集)。"""
        xs, ys, rw, rh, W, H = self.decode()
        changed = np.nonzero(
            (xs != xs_old) | (ys != ys_old) | (rw != rw_old) | (rh != rh_old)
        )[0]
        touched = set()
        for i in changed:
            touched.update(self.net.mod_nets[i])
        delta = self.net.delta_hpwl(touched, xs, ys, rw, rh,
                                    xs_old, ys_old, rw_old, rh_old)
        ovf_new = 0
        ovf_old = 0
        L = self.Lhat
        for i in changed:
            ovf_new += max(0, int(xs[i]) + int(rw[i]) - L) \
                + max(0, int(ys[i]) + int(rh[i]) - L)
            ovf_old += max(0, int(xs_old[i]) + int(rw_old[i]) - L) \
                + max(0, int(ys_old[i]) + int(rh_old[i]) - L)
        return (delta, ovf_old, ovf_new, xs, ys, rw, rh, W, H, touched)

    # ------------------------------------------------------------------ #
    # B*-树基础操作复用
    # ------------------------------------------------------------------ #
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


def bstar_hpwl_sa_solve(widths, heights, rot, root, parent, left, right,
                        bound_w, net, Lhat, budget_s, seed=0,
                        gamma0=5e5, gamma_min=1e3, gamma_max=1e8,
                        p_gravity=0.25, t0=None,
                        init=None):
    """B*-树 + 快速模拟退火求解问题二。

    代价 cost = ΣHPWL + γ·Σoverflow，γ 每 window 次接受按可行性比例自适应
    （Chen-Chang）：可行占比高→γ 降（倾向线长），低→γ 升（强制回轮廓）。
    init 可选：L1 的可行布局 (xs,ys,rw,rh,hpwl,overflow)，作为最优解的种子，
    保证算法至少返回该可行解。

    返回 dict(best_xs, best_ys, best_rw, best_rh, hpwl, overflow, W, H,
              feasible, iterations, trace, gamma)
    """
    rng = np.random.default_rng(seed)
    tree = BStarTreeQ2(widths, heights, rot, root, parent, left, right,
                       bound_w, net, Lhat)
    xs, ys, rw, rh, W, H = tree.decode()
    hpwl = net.total_hpwl(xs, ys, rw, rh)
    ovf = sum(overflow_of_module(i, xs, ys, rw, rh, Lhat) for i in range(tree.n))
    gamma = float(gamma0)

    if init is not None:
        # L1 可行布局作为最优种子（保证可行性下界）
        best = dict(xs=np.asarray(init["xs"], dtype=np.int64),
                    ys=np.asarray(init["ys"], dtype=np.int64),
                    rw=np.asarray(init["rw"], dtype=np.int64),
                    rh=np.asarray(init["rh"], dtype=np.int64),
                    W=int(init.get("W", 0)), H=int(init.get("H", 0)),
                    hpwl=float(init["hpwl"]), overflow=int(init["overflow"]),
                    rot=tree.rot.copy())
        # 若当前树布局比种子更优且可行，则更新种子
        if ovf == 0 and hpwl < best["hpwl"]:
            best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                        hpwl=hpwl, overflow=ovf, rot=tree.rot.copy())
    else:
        best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                    hpwl=hpwl, overflow=ovf, rot=tree.rot.copy())
    # 搜索轨迹记录"本轨迹自身"的收敛过程（不含 init 种子）：按字典序
    # (overflow, hpwl) 记录迄今最优状态，从种子树初始状态出发随搜索单调下降，
    # 避免收敛曲线被初解种子瞬间压平为一条直线。
    search_best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                       hpwl=hpwl, overflow=ovf)

    if t0 is None:
        t0 = max(500.0, (hpwl + gamma * ovf) / max(tree.n, 1))
    t = float(t0)
    alpha = 0.995
    tmin = 1e-2

    it = 0
    acc = 0
    feas_acc = 0
    window = 300
    trace = []
    start = time.time()
    while time.time() - start < budget_s:
        if it % 400 == 0:
            t = max(t * alpha, tmin)
        snap = tree._snapshot()
        op = tree.perturb_q2(rng, xs, ys, rw, rh, p_gravity=p_gravity)
        (delta, ovf_old, ovf_new, xs2, ys2, rw2, rh2, W2, H2,
         touched) = tree.delta_cost(xs, ys, rw, rh, gamma)
        it += 1
        dcost = delta + gamma * (ovf_new - ovf_old)
        if dcost <= 0 or rng.random() < np.exp(-dcost / t):
            xs, ys, rw, rh, W, H = xs2, ys2, rw2, rh2, W2, H2
            hpwl += delta
            ovf += ovf_new - ovf_old
            acc += 1
            if ovf == 0:
                feas_acc += 1
                if hpwl < best["hpwl"] - 1e-9 or best["overflow"] > 0:
                    best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                                hpwl=hpwl, overflow=0, rot=tree.rot.copy())
            elif best["overflow"] > 0 and (ovf, hpwl) < (best["overflow"], best["hpwl"]):
                best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                            hpwl=hpwl, overflow=ovf, rot=tree.rot.copy())
            # 更新本轨迹搜索最优（字典序 (ovf,hpwl)，可行优先再比 HPWL）
            if (ovf, hpwl) < (search_best["overflow"], search_best["hpwl"]):
                search_best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                                   hpwl=hpwl, overflow=ovf, rot=tree.rot.copy())
            if acc % 400 == 0:
                # 周期性全量校正（消除增量累积漂移）
                hpwl = net.total_hpwl(xs, ys, rw, rh)
                ovf = sum(overflow_of_module(i, xs, ys, rw, rh, Lhat)
                          for i in range(tree.n))
                if ovf == 0 and hpwl < best["hpwl"] - 1e-9:
                    best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                                hpwl=hpwl, overflow=0, rot=tree.rot.copy())
                if (ovf, hpwl) < (search_best["overflow"], search_best["hpwl"]):
                    search_best = dict(xs=xs, ys=ys, rw=rw, rh=rh, W=W, H=H,
                                       hpwl=hpwl, overflow=ovf,
                                       rot=tree.rot.copy())
        else:
            tree._restore(snap)
        if acc >= window:
            ratio = feas_acc / acc
            if ratio > 0.85:
                gamma = max(gamma_min, gamma * 0.7)
            elif ratio < 0.45:
                gamma = min(gamma_max, gamma * 2.0)
            acc, feas_acc = 0, 0
        if it % 500 == 0:
            trace.append((time.time() - start, search_best["hpwl"],
                          search_best["overflow"]))
    best["iterations"] = it
    best["trace"] = trace
    best["gamma"] = gamma
    return best
