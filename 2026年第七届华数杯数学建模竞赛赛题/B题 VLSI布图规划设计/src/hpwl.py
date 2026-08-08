"""问题二共享核心：线网索引 + HPWL 评估（全量/增量）+ 凸松弛下界。

模块划分：
  * NetIndex     —— 线网→引脚、模块→线网两级索引；全量 HPWL 与"仅重算被扰
                    模块所涉线网"的增量评估 O(deg(i)·\bar d)；
  * overflow     —— 固定轮廓越界量（L2 罚函数用）；
  * convex_lb    —— 无重叠凸松弛下界（加权中位数坐标下降，L3 定界证书）。
"""
from __future__ import annotations

import numpy as np


class NetIndex:
    """维护线网与模块/终端的关联关系。

    引脚命名约定（与附件一致）：模块引脚名以 'b' 开头，终端引脚名以 'p' 开头。
    模块引脚位于模块几何中心（随摆放位置变化）；终端引脚坐标固定（.pl 给出）。
    """

    def __init__(self, names: list[str], nets: list[list[str]],
                 terminal_pos: dict[str, tuple[int, int]]):
        self.names = list(names)
        self.n = len(self.names)
        self.name2idx = {nm: i for i, nm in enumerate(self.names)}
        self.terminal_pos = terminal_pos
        self.nets = nets
        # net_pins[k] = [(kind, idx), ...]  kind in {'m'|'t'}
        #   'm' -> 模块下标；'t' -> 终端固定坐标 (x, y)
        self.net_pins: list[list[tuple[str, object]]] = []
        # mod_nets[i] = 与模块 i 相连的线网下标
        self.mod_nets: list[list[int]] = [[] for _ in range(self.n)]
        for k, net in enumerate(nets):
            pins = []
            for pid in net:
                if pid.startswith("b"):
                    pins.append(("m", self.name2idx.get(pid)))
                else:
                    pins.append(("t", self.terminal_pos.get(pid)))
            self.net_pins.append(pins)
            for kind, ref in pins:
                if kind == "m" and ref is not None:
                    self.mod_nets[ref].append(k)

    # ------------------------------------------------------------------ #
    # 引脚坐标收集
    # ------------------------------------------------------------------ #
    def pin_coords(self, k: int, xs, ys, rw, rh):
        """返回线网 k 的全部引脚 (x, y) 坐标列表。"""
        pts = []
        for kind, ref in self.net_pins[k]:
            if kind == "m":
                if ref is None:
                    continue
                pts.append((xs[ref] + rw[ref] / 2.0, ys[ref] + rh[ref] / 2.0))
            else:
                if ref is None:
                    continue
                pts.append((float(ref[0]), float(ref[1])))
        return pts

    # ------------------------------------------------------------------ #
    # 全量 / 单线网 HPWL
    # ------------------------------------------------------------------ #
    def net_hpwl(self, k: int, xs, ys, rw, rh) -> float:
        xs_p = []
        ys_p = []
        for kind, ref in self.net_pins[k]:
            if kind == "m":
                if ref is None:
                    continue
                xs_p.append(xs[ref] + rw[ref] / 2.0)
                ys_p.append(ys[ref] + rh[ref] / 2.0)
            else:
                if ref is None:
                    continue
                xs_p.append(float(ref[0]))
                ys_p.append(float(ref[1]))
        if not xs_p:
            return 0.0
        return (max(xs_p) - min(xs_p)) + (max(ys_p) - min(ys_p))

    def total_hpwl(self, xs, ys, rw, rh) -> float:
        return sum(self.net_hpwl(k, xs, ys, rw, rh) for k in range(len(self.nets)))

    # ------------------------------------------------------------------ #
    # 增量 HPWL（核心加速：只重算被扰动模块所涉线网）
    # ------------------------------------------------------------------ #
    def delta_hpwl(self, touched_nets, xs, ys, rw, rh,
                   xs_old, ys_old, rw_old, rh_old) -> float:
        """给定被扰动线网集合，计算新旧布局 HPWL 之差。

        touched_nets 由调用方根据"发生变化的模块"推导（见 bstar_q2）。
        """
        delta = 0.0
        for k in touched_nets:
            delta += (self.net_hpwl(k, xs, ys, rw, rh)
                      - self.net_hpwl(k, xs_old, ys_old, rw_old, rh_old))
        return delta

    # ------------------------------------------------------------------ #
    # 启发式辅助：线网度 / 终端相连线网
    # ------------------------------------------------------------------ #
    def module_netdeg(self) -> np.ndarray:
        return np.asarray([len(v) for v in self.mod_nets], dtype=np.int64)

    def module_termdeg(self) -> np.ndarray:
        """每模块相连线网中"含终端"的线网数（Terminal 引力强度近似）。"""
        term = np.zeros(self.n, dtype=np.int64)
        for i in range(self.n):
            for k in self.mod_nets[i]:
                if any(kind == "t" for kind, _ in self.net_pins[k]):
                    term[i] += 1
        return term


# --------------------------------------------------------------------------- #
# 固定轮廓越界量（L2 罚函数）
# --------------------------------------------------------------------------- #
def overflow(xs, ys, rw, rh, Lhat: int) -> int:
    """越界量 = Σ_i [max(0, x+w-Lhat) + max(0, y+h-Lhat)]。"""
    xs = np.asarray(xs, dtype=np.int64)
    ys = np.asarray(ys, dtype=np.int64)
    rw = np.asarray(rw, dtype=np.int64)
    rh = np.asarray(rh, dtype=np.int64)
    return int(np.maximum(0, xs + rw - Lhat).sum()
               + np.maximum(0, ys + rh - Lhat).sum())


def overflow_of_module(i, xs, ys, rw, rh, Lhat: int) -> int:
    return (max(0, int(xs[i]) + int(rw[i]) - Lhat)
            + max(0, int(ys[i]) + int(rh[i]) - Lhat))


def hpwl_of_placement(net: NetIndex, xs, ys, rw, rh) -> float:
    return net.total_hpwl(xs, ys, rw, rh)


# --------------------------------------------------------------------------- #
# L3：凸松弛下界（无重叠松弛 + 加权中位数坐标下降）
# --------------------------------------------------------------------------- #
def convex_lb(ds, Lhat: int, max_iter: int = 300, tol: float = 1e-6) -> float:
    """无重叠凸松弛问题 min Σ HPWL_k（只保留固定轮廓约束）的全局下界。

    理论依据（问题2建模性质3）：对单模块横坐标 x_i，其贡献为若干 hinge 函数
    max(0, x-h, l-x) 之和，最优值在断点加权中位数处取得；坐标下降收敛到全局最优。
    返回松弛问题最优值（原问题总 HPWL 的全局下界）。
    """
    return _convex_lb_impl(ds, Lhat, max_iter, tol)[0]


def convex_lb_with_centers(ds, Lhat: int, max_iter: int = 300,
                           tol: float = 1e-6):
    """返回 (lb_value, centers)。centers[i] = 模块 i 的松弛理想中心 (x, y)。

    该理想中心被 L1 用于构建"终端感知/松弛中心排序"初解（PeF 范式：
    松弛放置 → 合法化），使合法化后的布局天然贴近 HPWL 最优。
    """
    return _convex_lb_impl(ds, Lhat, max_iter, tol)


def _convex_lb_impl(ds, Lhat, max_iter, tol):
    names = list(ds.names)
    name2idx = {nm: i for i, nm in enumerate(names)}
    n = ds.n
    L = float(Lhat)

    # 模块初始中心放在轮廓中心
    cx = np.full(n, L / 2.0)
    cy = np.full(n, L / 2.0)

    # 每个模块：相连线网 -> 每线网的其它引脚坐标
    mod_nets: dict[int, list[int]] = {i: [] for i in range(n)}
    net_pins: list[list[tuple[str, object]]] = []
    for net in ds.nets:
        pins = []
        for pid in net:
            if pid.startswith("b"):
                j = name2idx.get(pid)
                if j is None:
                    continue
                pins.append(("m", j))
            else:
                pos = ds.terminal_pos.get(pid)
                if pos is None:
                    continue
                pins.append(("t", pos))
        k = len(net_pins)
        net_pins.append(pins)
        for kind, ref in pins:
            if kind == "m":
                mod_nets[ref].append(k)

    def _others_x(k, exclude):
        xs_p = []
        for kind, ref in net_pins[k]:
            if kind == "m":
                if ref == exclude:
                    continue
                xs_p.append(cx[ref])
            else:
                xs_p.append(float(ref[0]))
        return xs_p

    def _others_y(k, exclude):
        ys_p = []
        for kind, ref in net_pins[k]:
            if kind == "m":
                if ref == exclude:
                    continue
                ys_p.append(cy[ref])
            else:
                ys_p.append(float(ref[1]))
        return ys_p

    def total():
        tot = 0.0
        for pins in net_pins:
            xs_p = [cx[r] if t == "m" else float(r[0]) for t, r in pins]
            ys_p = [cy[r] if t == "m" else float(r[1]) for t, r in pins]
            if xs_p:
                tot += (max(xs_p) - min(xs_p)) + (max(ys_p) - min(ys_p))
        return tot

    # 加权中位数坐标下降（Gauss-Seidel 扫描，x/y 交替）
    for _ in range(max_iter):
        prev = total()
        for axis in (0, 1):
            for i in range(n):
                bps = []
                for k in mod_nets[i]:
                    others = _others_x(k, i) if axis == 0 else _others_y(k, i)
                    if others:
                        bps.append(min(others))
                        bps.append(max(others))
                if not bps:
                    c = L / 2.0
                else:
                    bps.sort()
                    c = bps[len(bps) // 2]
                c = min(max(c, 0.0), L)
                if axis == 0:
                    cx[i] = c
                else:
                    cy[i] = c
        if abs(total() - prev) < tol:
            break
    centers = [(cx[i], cy[i]) for i in range(n)]
    return total(), centers
