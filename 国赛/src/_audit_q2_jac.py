# -*- coding: utf-8 -*-
"""Audit of src/q2_solve.py assemble(): independent element-wise finite-difference
check of the analytic Jacobian, with per-entry (not global) normalisation.

Also: does the frozen=True (Picard) branch's analytic Jacobian match the frozen
residual?  And is the `dHev*hm*R*(C_M-Cinf)` term in the right block?

Outputs outputs/_audit_q2_jac.log and _audit_q2_jac.csv
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q2_solve import (Par, assemble, geometry, hevap_of, residual,  # noqa: E402
                      C0, T0K, R, HM, HEVAP_28, HEVAP_SLOPE)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
ROWS = []


def dense_from_ab(ab, n2):
    d = np.zeros((n2, n2))
    for j in range(n2):
        for dd in range(4):
            if j + dd < n2:
                d[j + dd, j] = ab[3 + dd, j]
            if dd > 0 and j - dd >= 0:
                d[j - dd, j] = ab[3 - dd, j]
    return d


def fd_dense(x, xold, dt, g, par, Tinf, Cinf, eps=1e-7):
    n2 = x.size
    fd = np.zeros((n2, n2))
    for j in range(n2):
        xp = x.copy(); xp[j] += eps
        xm = x.copy(); xm[j] -= eps
        fd[:, j] = (residual(xp, xold, dt, g, par, Tinf, Cinf)
                    - residual(xm, xold, dt, g, par, Tinf, Cinf)) / (2 * eps)
    return fd


def make_state(M, par, seed=7):
    g = geometry(M, par.boundary)
    n = g["n"]
    rng = np.random.default_rng(seed)
    x = np.empty(2 * n)
    x[0::2] = T0K + rng.uniform(0.0, 3.0, n)
    x[1::2] = C0 - rng.uniform(0.0, 0.4, n)
    xold = x.copy()
    xold[0::2] = x[0::2] - 0.5
    xold[1::2] = x[1::2] + 0.02
    return g, x, xold, n


def main():
    M, dt = 12, 0.05
    Tinf, Cinf = 320.0, 0.045
    cases = [("default (H_evap(T))", Par()),
             ("H_evap = const", Par(hevap="const")),
             ("H_evap = 0", Par(hevap="off")),
             ("conserv", Par(energy="conserv")),
             ("frozen (Picard)", Par(frozen=True)),
             ("frozen + app2", Par(frozen=True, mode="app2")),
             ]
    csv_rows = []
    for lbl, par in cases:
        g, x, xold, n = make_state(M, par)
        _, ab, _ = assemble(x, xold, dt, g, par, Tinf, Cinf)
        n2 = 2 * n
        Ja = dense_from_ab(ab, n2)
        Jf = fd_dense(x, xold, dt, g, par, Tinf, Cinf)
        glob = float(np.max(np.abs(Ja - Jf))) / float(np.max(np.abs(Jf)))
        # per-entry relative error, restricted to entries of practical size
        scale = float(np.max(np.abs(Jf)))
        mask = np.abs(Jf) > 1e-6 * scale
        per = np.abs(Ja - Jf)[mask] / np.abs(Jf)[mask]
        print(f"{lbl:22s}  global max rel = {glob:.3e}   "
              f"per-entry (|J|>1e-6 max) max rel = {per.max():.3e}  "
              f"median = {np.median(per):.2e}")
        csv_rows.append([lbl, glob, float(per.max())])
        if per.max() > 1e-5:
            k = np.unravel_index(np.argmax(np.abs(Ja - Jf) * mask), Ja.shape)
            print(f"    worst entry A[{k[0]},{k[1]}]: analytic={Ja[k]!r} "
                  f"fd={Jf[k]!r}  absdiff={Ja[k]-Jf[k]:.3e}  "
                  f"Jmax={scale:.3e}")
            # list the largest 5 discrepancies
            dd = np.abs(Ja - Jf) * mask
            for kk in np.argsort(dd.ravel())[::-1][:5]:
                i, j = np.unravel_index(kk, dd.shape)
                print(f"      A[{i:3d},{j:3d}] ana={Ja[i,j]: .8e} "
                      f"fd={Jf[i,j]: .8e} diff={Ja[i,j]-Jf[i,j]: .3e} "
                      f"relerr={abs(Ja[i,j]-Jf[i,j])/max(abs(Jf[i,j]),1e-300):.3e}")
            ROWS.extend([[lbl, i, j, Ja[i, j], Jf[i, j]] for (i, j) in
                         [np.unravel_index(kk, dd.shape)
                          for kk in np.argsort(dd.ravel())[::-1][:5]]])

    print()
    print("=" * 100)
    print("定向检验: 表面 T 行的 TT 与 TC 对角元")
    print("=" * 100)
    for lbl, par in [("default (H_evap(T))", Par()),
                     ("H_evap = const", Par(hevap="const"))]:
        g, x, xold, n = make_state(M, par)
        _, ab, aux = assemble(x, xold, dt, g, par, Tinf, Cinf)
        Ja = dense_from_ab(ab, 2 * n)
        Jf = fd_dense(x, xold, dt, g, par, Tinf, Cinf)
        Hev, dHev = hevap_of(x[2 * M], par)
        s = 2 * M
        print(f"  {lbl}: T_M = {x[s]-273.15:.3f} degC, C_M = {x[s+1]:.4f}, "
              f"Cinf = {Cinf}")
        print(f"    Hev = {Hev:.4f},  dHev = {dHev:.4f}")
        print(f"    dHev*hm*R*(C_M-Cinf) = {dHev*par.hm*R*(x[s+1]-Cinf):.6e}   "
              f"(hm*R = {par.hm*R:.3e})")
        print(f"    analytic A[T_M,T_M] = {Ja[s, s]:.10f}   "
              f"fd = {Jf[s, s]:.10f}   diff = {Ja[s,s]-Jf[s,s]:.3e}")
        print(f"    analytic A[T_M,C_M] = {Ja[s, s+1]:.10f}   "
              f"fd = {Jf[s, s+1]:.10f}   diff = {Ja[s,s+1]-Jf[s,s+1]:.3e}")
        print(f"    hc*R = {par.hc*R:.6f}; Hev*hm*R = {Hev*par.hm*R:.8f}")

    print()
    print("=" * 100)
    print("冻结分支: 解析 Jacobian 是否与冻结残差一致 (逐元)")
    print("=" * 100)
    par = Par(frozen=True)
    g, x, xold, n = make_state(M, par)
    Ja = dense_from_ab(assemble(x, xold, dt, g, par, Tinf, Cinf)[1], 2 * n)
    Jf = fd_dense(x, xold, dt, g, par, Tinf, Cinf)
    ratio = np.abs(Ja - Jf) / np.maximum(np.abs(Jf), 1e-12)
    print(f"  max|Ja-Jf| = {np.max(np.abs(Ja-Jf)):.3e}, "
          f"max|Jf| = {np.max(np.abs(Jf)):.3e}, "
          f"global rel = {np.max(np.abs(Ja-Jf))/np.max(np.abs(Jf)):.3e}")
    print(f"  逐元相对偏差 (仅 |Jf|>1e-3*max): "
          f"{ratio[np.abs(Jf) > 1e-3*np.max(np.abs(Jf))].max():.3e}")
    # the counterfactual: the term that used to be added unconditionally
    from q2_solve import props  # noqa: E402
    rho, cp, k, drho, dcp, dk = props(xold[1::2], par.mode)
    drcp = drho * cp + rho * dcp
    term = g["MLg"] * drcp * (x[0::2] - xold[0::2]) / dt
    print(f"  被移出冻结分支的项 MLg*drcp*(T-Told)/dt: "
          f"max|term| = {np.max(np.abs(term)):.4e}, "
          f"占 max|J| 的比例 = {np.max(np.abs(term))/np.max(np.abs(Jf)):.3e} "
          f"(q2_solve 自检记录的 9.667e-2)")
    print(f"  残差对当前 C 的数值导数 (冻结, T 行) 最大绝对值 = "
          f"{np.max(np.abs(Jf[0::2, 1::2])):.3e}  "
          f"(应只有表面蒸发项 Hev*hm*R = {HM*R*HEVAP_28:.6e} 量级)")
    print(f"  冻结分支 T 行对内部 C 的数值导数 max = "
          f"{np.max(np.abs(Jf[0:2*M:2, 1:2*M:2])):.3e} (应为 0)")

    print()
    print("=" * 100)
    print("逐元相对偏差最大的 5 个条目 (默认配置, |Jf|>1e-6 max|Jf|)")
    print("=" * 100)
    par = Par()
    g, x, xold, n = make_state(M, par)
    Ja = dense_from_ab(assemble(x, xold, dt, g, par, Tinf, Cinf)[1], 2 * n)
    Jf = fd_dense(x, xold, dt, g, par, Tinf, Cinf)
    scale = np.max(np.abs(Jf))
    dd = np.abs(Ja - Jf) / np.maximum(np.abs(Jf), 1e-300)
    dd[np.abs(Jf) <= 1e-6 * scale] = 0.0
    for kk in np.argsort(dd.ravel())[::-1][:5]:
        i, j = np.unravel_index(kk, dd.shape)
        print(f"  A[{i:3d},{j:3d}] ana={Ja[i,j]: .10e} fd={Jf[i,j]: .10e} "
              f"relerr={dd[i,j]:.3e}  占 max|J| 的比例="
              f"{abs(Ja[i,j]-Jf[i,j])/scale:.3e}")
    print(f"  q2_solve.check_jacobian 使用 max|Ja-Jf|/max|Jf| = "
          f"{np.max(np.abs(Ja-Jf))/scale:.4e}")

    with open(os.path.join(OUT, "_audit_q2_jac.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["case", "global_rel", "per_entry_max_rel"])
        w.writerows(csv_rows)
    print(f"\n写出 {os.path.join(OUT, '_audit_q2_jac.csv')}")


if __name__ == "__main__":
    main()
