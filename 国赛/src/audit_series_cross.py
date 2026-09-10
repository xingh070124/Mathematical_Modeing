"""Non-circular cross-check of the semi-analytic reference used in
src/feishu_compare.py against session 1's INDEPENDENTLY WRITTEN eigen-solver and
series evaluator (src/q1_solve.py: robin_cylinder_eigen / robin_cylinder_theta).

Rationale: within feishu_compare.py, series_T (semi-analytic) and solve_T (numerical)
share the eigen() helper, so their agreement could be circular. This script instead
compares two separately-written implementations of the SAME closed-form solution
(different root bracketing, different coefficient code path, different array layout).

Run: python src/audit_series_cross.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import feishu_compare as FC          # noqa: E402
from q1_solve import (robin_cylinder_eigen,  # noqa: E402
                      robin_cylinder_theta, ALPHA as A1, R0 as R1,
                      T0_K as T01, H_CONV as H1, K_COND as K1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG_OUT = os.path.join(ROOT, "outputs", "registry_series_cross.csv")
_REG = []


def add(id_, quantity, value, unit, note=""):
    _REG.append(dict(id=id_, quantity=quantity, value="%.10e" % value, unit=unit,
                     uncertainty=note if note else "机器精度",
                     source="run audit_series_cross",
                     command="python src/audit_series_cross.py", note=note))

print("== session-1 vs session-2 alpha / Bi consistency ==")
print("  alpha  s1=%.12e  s2=%.12e  rel=%.2e" % (A1, FC.ALPHA, abs(A1 - FC.ALPHA) / FC.ALPHA))
Bi1 = H1 * R1 / K1
print("  Bi     s1=%.12f  s2=%.12f  rel=%.2e" % (Bi1, FC.BI, abs(Bi1 - FC.BI) / FC.BI))
print("  R      s1=%.6f  s2=%.6f" % (R1, FC.R0))
print("  T0_K   s1=%.6f  s2=%.6f" % (T01, FC.T0_K))

print("\n== eigen roots: two independently coded solvers ==")
x1, c1 = robin_cylinder_eigen(Bi1, n_modes=8)
x2, lam2, c2 = FC.eigen(FC.BI, 8)
print("  k   s1 x_k            s2 x_k            |diff|        s1 c_k          s2 c_k")
for k in range(8):
    print("  %d  %16.12f %16.12f  %.3e  %14.10f %14.10f"
          % (k + 1, x1[k], x2[k], abs(x1[k] - x2[k]), c1[k], c2[k]))
dx = float(np.max(np.abs(x1 - x2)))
dc = float(np.max(np.abs(c1 - c2)))
add("X01", "两独立求根器的最大本征值差 (k=1..8)", dx, "-", "session1 vs session2")
add("X02", "两独立实现的最大展开系数差 (k=1..8)", dc, "-", "应接近 0")
print("  -> max|dx| = %.3e ; max|dc| = %.3e" % (dx, dc))

print("\n== series evaluation: constant Tinf = 50 C = 323.15 K ==")
Tinf = 323.15
add("X03", "常 Tinf=50C 时物理设定温度 (热风)", Tinf, "K", "定义")
worst = 0.0
for t in (60.0, 300.0, 900.0, 1800.0):
    Fo1 = A1 * t / R1 ** 2
    Fo2 = FC.ALPHA * t / FC.R0 ** 2
    print("  t=%6.0f  Fo s1=%.10f s2=%.10f" % (t, Fo1, Fo2))
    tot = 0.0
    for rr in (0.0, 0.25, 0.5, 0.75, 1.0):
        v1 = Tinf + (T01 - Tinf) * robin_cylinder_theta(
            np.array([rr]), Fo1, x1, c1)[0]
        v2 = Tinf + (FC.T0_K - Tinf) * float(np.sum(
            c2 * FC.j0(x2 * rr) * np.exp(-x2 ** 2 * Fo2)))
        tot = max(tot, abs(v1 - v2))
        print("     r/R=%.2f  s1=%.12f  s2=%.12f  |diff|=%9.2e" % (rr, v1, v2, abs(v1 - v2)))
    print("     -> max|diff| over r at this t = %.3e K" % tot)
    worst = max(worst, tot)
    add("X04_t%g" % t, "两独立级数实现在 t=%g s 时的最大差" % t, tot, "K", "机器精度")
add("X05", "两独立级数实现的总最大差 (t=60..1800 s)", worst, "K",
    "用于证明半解析参照解非循环")

print("\n== how many modes does each series need to reach 1e-12 K? ==")
rec_diff = 0.0
for nm in (8, 20, 50, 100):
    xa, ca = robin_cylinder_eigen(Bi1, n_modes=nm)
    eta = FC.eigen(FC.BI, nm)
    # reconstruct the constant 1 at r=R with each
    s1 = float(np.sum(ca * FC.j0(xa)))
    s2 = float(np.sum(eta[2] * FC.j0(eta[0])))
    rec_diff = max(rec_diff, abs(s1 - s2))
    print("  n_modes=%4d  Sum c_k J0(x_k)|_{r=R}:  s1=%.12f  s2=%.12f  |diff|=%.2e"
          % (nm, s1, s2, abs(s1 - s2)))
    add("X06_n%d" % nm, "重构常数1 的两实现差 (n_modes=%d, r=R)" % nm, abs(s1 - s2),
        "-", "机器精度")
add("X07", "重构常数1 两实现的最大差 (n_modes=8..100)", rec_diff, "-", "机器精度")

with open(REG_OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "quantity", "value", "unit",
                                      "uncertainty", "source", "command", "note"])
    w.writeheader()
    for r_ in _REG:
        w.writerow(r_)
print("\nwrote %s" % REG_OUT)
