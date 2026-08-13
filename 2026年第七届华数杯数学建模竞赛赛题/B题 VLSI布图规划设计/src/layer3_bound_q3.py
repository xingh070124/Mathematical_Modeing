"""第3层（L3）问题三适配：边长下界 + 子集不可行证书 + gap 夹逼报告。

* 边长下界 L_lb = max(⌈√A⌉, max_i max(w_i,h_i))，对应 d_lb；
* 子集 CP-SAT 不可行证书：面积最大的 K 个模块（可 90° 旋转）能否放入
  L×L 正方形 —— 若不能则整实例不可行（大模块是装箱最难约束），快速抬升下界；
* gap = (L_ub² - L_lb²)/A，量化剩余压缩空间。
"""
from __future__ import annotations

import numpy as np


def lower_bound_L(ds) -> int:
    """理论边长下界：面积下界与最大模块边长取最大。"""
    A = ds.total_area
    sq = int(np.ceil(np.sqrt(A)))
    max_side = max(max(w, h) for w, h in zip(ds.widths, ds.heights))
    return max(sq, max_side)


def upper_bound_L(ds, dead_space_ratio=0.15) -> int:
    """已知可行上界：问题2（d=0.15）下必有可行布局。"""
    return int(np.ceil(np.sqrt(ds.total_area * (1.0 + dead_space_ratio))))


def d_of_L(ds, L: int) -> float:
    return L * L / ds.total_area - 1.0


def density(ds, L: int) -> float:
    return ds.total_area / float(L * L)


def gap_report_q3(ds, L_ub: int, L_lb: int) -> dict:
    A = ds.total_area
    return dict(
        L_lb=int(L_lb), L_ub=int(L_ub),
        d_lb=d_of_L(ds, int(L_lb)),
        d_ub=d_of_L(ds, int(L_ub)),
        gap_area=(int(L_ub) ** 2 - int(L_lb) ** 2) / A,
        density=density(ds, int(L_ub)),
    )


def cp_sat_subset_infeasible(ds, L: int, K: int = 20, time_limit: int = 60):
    """用 OR-Tools CP-SAT 判定"面积最大 K 个模块"能否放入 L×L（允许 90° 旋转）。

    返回 (status, count, elapsed)：
      'infeasible' —— 子集不可行 ⇒ 整实例不可行（不可行证书）；
      'feasible'   —— 子集可行（不构成任何结论）；
      'unknown'    —— 超时或求解器不可用。
    """
    try:
        from ortools.sat.python import cp_model
    except Exception:
        return "unknown", 0, 0.0

    idx = sorted(range(ds.n),
                 key=lambda i: -(ds.widths[i] * ds.heights[i]))[:K]
    model = cp_model.CpModel()
    ix, iy, xv, yv = [], [], [], []
    for a, i in enumerate(idx):
        w, h = ds.widths[i], ds.heights[i]
        o0 = model.NewBoolVar(f"o{a}_0")
        o1 = model.NewBoolVar(f"o{a}_1")
        model.AddBoolOr([o0, o1])
        # 朝向 0：(w,h)；朝向 1：(h,w)
        for orient, (wi, hi), ov in ((0, (w, h), o0), (1, (h, w), o1)):
            x = model.NewIntVar(0, max(0, L - wi), f"x{a}_{orient}")
            y = model.NewIntVar(0, max(0, L - hi), f"y{a}_{orient}")
            model.Add(x + wi <= L).OnlyEnforceIf(ov)
            model.Add(y + hi <= L).OnlyEnforceIf(ov)
            vx = model.NewOptionalIntervalVar(x, wi, x + wi, ov,
                                              f"ix{a}_{orient}")
            vy = model.NewOptionalIntervalVar(y, hi, y + hi, ov,
                                              f"iy{a}_{orient}")
            ix.append(vx)
            iy.append(vy)
            xv.append(x)
            yv.append(y)
    model.AddNoOverlap2D(ix, iy)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 1
    import time as _t
    t0 = _t.time()
    status = solver.Solve(model)
    elapsed = _t.time() - t0
    if status == cp_model.INFEASIBLE:
        return "infeasible", len(idx), elapsed
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return "feasible", len(idx), elapsed
    return "unknown", len(idx), elapsed
