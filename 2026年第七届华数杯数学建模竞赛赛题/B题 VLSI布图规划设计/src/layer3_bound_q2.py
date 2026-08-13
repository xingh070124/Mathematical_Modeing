"""第3层（L3）问题二适配：双向反馈定界校验层。

* 反向反馈（搜索→定界）：L2 任一可行布局（无重叠 + 在 Lhat×Lhat 内）
  即为可行证书，给出总 HPWL 上界；
* 正向反馈（定界→搜索）：凸松弛下界 HPWL_lb（无重叠松弛，加权中位数坐标
  下降），实时回馈 gap = (HPWL_ub - HPWL_lb) / HPWL_lb 判断剩余优化空间；
* CP-SAT 小规模子集证书（可选，与问题一 L3 同构）。
"""
from __future__ import annotations

import numpy as np

from packing import verify
from hpwl import convex_lb, overflow, hpwl_of_placement


def lower_bound_hpwl(ds, Lhat: int) -> float:
    """凸松弛下界（无重叠松弛 + 加权中位数坐标下降）。"""
    return convex_lb(ds, Lhat)


def check_feasible_q2(ds, net, xs, ys, rw, rh, Lhat: int):
    """问题二可行性：无重叠 + 全部在固定轮廓内（Terminal 不参与）。"""
    xs = np.asarray(xs, dtype=np.int64)
    ys = np.asarray(ys, dtype=np.int64)
    rw = np.asarray(rw, dtype=np.int64)
    rh = np.asarray(rh, dtype=np.int64)
    if xs.min() < 0 or ys.min() < 0:
        return False, -1, int(overflow(xs, ys, rw, rh, Lhat))
    if int((xs + rw).max()) > Lhat or int((ys + rh).max()) > Lhat:
        return False, -1, int(overflow(xs, ys, rw, rh, Lhat))
    areas = np.asarray([w * h for w, h in zip(ds.widths, ds.heights)],
                       dtype=np.int64)
    ok, max_overlap = verify(areas, xs, ys, rw, rh, Lhat, Lhat)
    ovf = int(overflow(xs, ys, rw, rh, Lhat))
    return ok, int(max_overlap), ovf


def gap_report_q2(hpwl_ub: float, hpwl_lb: float) -> dict:
    lb = float(hpwl_lb)
    ub = float(hpwl_ub)
    return dict(hpwl_lb=lb, hpwl_ub=ub,
                gap=(ub - lb) / lb if lb > 0 else 0.0,
                gap_pct=(ub - lb) / lb * 100.0 if lb > 0 else 0.0,
                ub_lb_ratio=ub / lb if lb > 0 else 0.0)


def hpwl_of_solution(net, xs, ys, rw, rh) -> float:
    return hpwl_of_placement(net, xs, ys, rw, rh)
