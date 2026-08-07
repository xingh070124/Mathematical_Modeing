"""第3层（L3）：双向反馈定界校验层。

* 反向反馈（搜索→定界）：L2 产生的可行布局 = 可行证书，给出轮廓面积上界 S_ub 与密度 ρ=A/S；
* 正向反馈（定界→搜索）：由面积下界 S_lb=ceil(A) 与整数性引理计算密度 gap δ=1-ρ，
  反馈 L2 判断剩余优化空间；
* CP-SAT（OR-Tools）可选：小规模子集上验证下界 / 可行性证书。
"""
from __future__ import annotations

import numpy as np

from packing import verify


def lower_bounds(ds):
    A = ds.total_area
    sq = int(np.ceil(np.sqrt(A)))
    return dict(
        A=A,
        S_lb=ceil_int(A),
        W_lb=sq, H_lb=sq,
        L_lb=max(sq, max(max(w, h) for w, h in zip(ds.widths, ds.heights))),
    )


def ceil_int(x):
    return int(np.ceil(x))


def gap_report(ds, W, H):
    A = ds.total_area
    S = W * H
    rho = A / S
    return dict(area=A, outline_area=S, density=rho, gap=1.0 - rho,
                gap_pct=(1.0 - rho) * 100.0)


def check_feasible(ds, xs, ys, rw, rh, W, H):
    xs = np.asarray(xs, dtype=np.int64)
    ys = np.asarray(ys, dtype=np.int64)
    rw = np.asarray(rw, dtype=np.int64)
    rh = np.asarray(rh, dtype=np.int64)
    areas = np.asarray([w * h for w, h in zip(ds.widths, ds.heights)], dtype=np.int64)
    ok, max_overlap = verify(areas, xs, ys, rw, rh, int(W), int(H))
    return ok, int(max_overlap)


def cp_sat_subset_feasible(ds, W, H, subset_size=15, time_limit=60):
    """用 OR-Tools CP-SAT 对"面积最大的 subset_size 个模块"在 (W,H) 内做可行性验证。

    返回 (status, count, elapsed)。status ∈ {'feasible','infeasible','unknown'}。
    仅作为小规模子集的可证明性证书；不可用时返回 ('unavailable', 0, 0)。
    """
    try:
        from ortools.sat.python import cp_model
    except Exception:
        return "unavailable", 0, 0.0
    idx = sorted(range(ds.n), key=lambda i: -(ds.widths[i] * ds.heights[i]))[:subset_size]
    model = cp_model.CpModel()
    xs, ys = [], []
    for i in idx:
        w, h = ds.widths[i], ds.heights[i]
        x = model.NewIntVar(0, max(0, W - w), f"x{i}")
        y = model.NewIntVar(0, max(0, H - h), f"y{i}")
        xs.append(x)
        ys.append(y)
        model.Add(x + w <= W)
        model.Add(y + h <= H)
    for a in range(len(idx)):
        for b in range(a + 1, len(idx)):
            wa, wb = ds.widths[idx[a]], ds.widths[idx[b]]
            ha, hb = ds.heights[idx[a]], ds.heights[idx[b]]
            b1 = model.NewBoolVar(f"o{a}_{b}_0")
            b2 = model.NewBoolVar(f"o{a}_{b}_1")
            b3 = model.NewBoolVar(f"o{a}_{b}_2")
            b4 = model.NewBoolVar(f"o{a}_{b}_3")
            model.Add(xs[a] + wa <= xs[b]).OnlyEnforceIf(b1)
            model.Add(xs[b] + wb <= xs[a]).OnlyEnforceIf(b2)
            model.Add(ys[a] + ha <= ys[b]).OnlyEnforceIf(b3)
            model.Add(ys[b] + hb <= ys[a]).OnlyEnforceIf(b4)
            model.AddBoolOr([b1, b2, b3, b4])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_workers = 1
    import time as _t
    t0 = _t.time()
    status = solver.Solve(model)
    elapsed = _t.time() - t0
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return "feasible", len(idx), elapsed
    if status == cp_model.INFEASIBLE:
        return "infeasible", len(idx), elapsed
    return "unknown", len(idx), elapsed
