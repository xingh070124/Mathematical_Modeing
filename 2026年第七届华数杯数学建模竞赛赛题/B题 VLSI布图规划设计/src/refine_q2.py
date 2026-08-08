"""第2层（L2b）问题二精调：终端引力合法化局部精调（PeF 后处理）。

在 B*-树+SA / 初解池提供的可行布局基础上，对每个模块计算其"理想中心"
= 相连引脚（终端固定坐标 + 其它模块当前中心）的几何中心，然后在"当前
位置 → 理想中心"连线上的若干候选落点中，尝试把模块移到"合法（不重叠、
不越界）且总 HPWL 下降最多"的位置（模拟退火式接受）。

这是 Op5 终端引力思想在位置层的实现：在紧凑固定轮廓内，模块未必能一步
到达理想中心，因此沿连线逐步逼近，只要每步合法且降低线长就采纳。
"""
from __future__ import annotations

import time
import numpy as np

from hpwl import overflow_of_module


def _legal(x, y, rw, rh, xs, ys, rws, rhs, Lhat, skip):
    if x < 0 or y < 0 or x + rw > Lhat or y + rh > Lhat:
        return False
    for j in range(len(xs)):
        if j == skip:
            continue
        if (x < xs[j] + rws[j] and xs[j] < x + rw
                and y < ys[j] + rhs[j] and ys[j] < y + rh):
            return False
    return True


def refine_hpwl(net, xs, ys, rw, rh, Lhat, budget_s, seed=0,
                rounds=10, steps_per_axis=10):
    """终端引力合法化精调：把可行布局进一步压低 HPWL。

    逐模块多轮扫描：对模块 i，沿"当前位置 → 理想中心"连线取 steps 个候选
    落点，每个落点验证合法并增量计算其相连线网 HPWL，取"合法且线长下降最多"
    者采纳；温度随轮次下降（模拟退火）。全程保持合法，返回精调结果。
    """
    rng = np.random.default_rng(seed)
    xs = np.asarray(xs, dtype=np.int64).copy()
    ys = np.asarray(ys, dtype=np.int64).copy()
    rw = np.asarray(rw, dtype=np.int64).copy()
    rh = np.asarray(rh, dtype=np.int64).copy()
    n = net.n
    Lhat = int(Lhat)
    t0 = time.time()

    def hpwl_total():
        return net.total_hpwl(xs, ys, rw, rh)

    best_hp = hpwl_total()
    best_state = (xs.copy(), ys.copy(), rw.copy(), rh.copy())
    t = max(10.0, best_hp / max(n, 1) * 0.02)

    mod_pins = []
    for i in range(n):
        pts = []
        for k in net.mod_nets[i]:
            for kind, ref in net.net_pins[k]:
                pts.append(("m" if kind == "m" else "t", ref))
        mod_pins.append(pts)

    for _ in range(rounds):
        order = rng.permutation(n)
        for i in order:
            if time.time() - t0 >= budget_s:
                break
            # 理想中心 = 相连引脚几何中心
            px = py = 0.0
            cnt = 0
            for kind, ref in mod_pins[i]:
                if kind == "m":
                    px += xs[ref] + rw[ref] / 2.0
                    py += ys[ref] + rh[ref] / 2.0
                else:
                    px += ref[0]
                    py += ref[1]
                cnt += 1
            if cnt == 0:
                continue
            px /= cnt
            py /= cnt
            # 理想左下角
            txi = int(px - rw[i] / 2.0)
            tyi = int(py - rh[i] / 2.0)
            txi = max(0, min(Lhat - rw[i], txi))
            tyi = max(0, min(Lhat - rh[i], tyi))
            # 沿连线取候选
            x0, y0 = int(xs[i]), int(ys[i])
            base_hp = sum(net.net_hpwl(k, xs, ys, rw, rh)
                          for k in net.mod_nets[i])
            best_place = None
            best_delta = 0
            for s in np.linspace(0.0, 1.0, steps_per_axis + 1):
                cx = int(round(x0 + (txi - x0) * s))
                cy = int(round(y0 + (tyi - y0) * s))
                if (cx, cy) == (x0, y0):
                    continue
                if not _legal(cx, cy, rw[i], rh[i], xs, ys, rw, rh,
                              Lhat, skip=i):
                    continue
                xs[i], ys[i] = cx, cy
                delta = sum(net.net_hpwl(k, xs, ys, rw, rh)
                            for k in net.mod_nets[i]) - base_hp
                xs[i], ys[i] = x0, y0
                if delta < best_delta:
                    best_delta = delta
                    best_place = (cx, cy)
            if best_place is not None and (best_delta < 0
                                           or rng.random()
                                           < np.exp(-best_delta / t)):
                xs[i], ys[i] = best_place
                hp = hpwl_total()
                if hp < best_hp - 1e-9:
                    best_hp = hp
                    best_state = (xs.copy(), ys.copy(), rw.copy(), rh.copy())
        t *= 0.85
        if time.time() - t0 >= budget_s:
            break

    xs, ys, rw, rh = best_state
    return xs, ys, rw, rh, hpwl_total()
