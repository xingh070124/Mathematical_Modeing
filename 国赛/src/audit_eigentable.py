"""Audit of the feishu.md §6.1 eigen table: are its values roots of the
eigencondition for ANY single Bi, and by how much do they deviate?

Produces outputs/registry_eigentable.csv so every number quoted in
model/建模方式对比.md §1.3 comes from a run rather than from the draft.

Run: python src/audit_eigentable.py
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.special import j0, j1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "registry_eigentable.csv")

BI = 25.0 * 0.02 / 0.36                 # hR/k = 1.388888...
TABLE = np.array([2.0, 5.0, 8.0, 11.0])  # feishu.md §6.1 placeholder table
_REG: list[dict] = []


def add(id_, quantity, value, unit, note=""):
    _REG.append(dict(id=id_, quantity=quantity, value="%.10e" % float(value),
                     unit=unit, uncertainty="机器精度", source="run audit_eigentable",
                     command="python src/audit_eigentable.py", note=note))


def eigen(Bi, n):
    f = lambda x: x * j1(x) - Bi * j0(x)
    grid = np.linspace(1e-8, 4.0 * n + 40.0, 300 * (n + 20))
    v = f(grid)
    xs = []
    for k in range(len(grid) - 1):
        if v[k] * v[k + 1] < 0:
            xs.append(brentq(f, grid[k], grid[k + 1], xtol=1e-15, rtol=8.9e-16))
        if len(xs) >= n:
            break
    return np.array(xs)


x = eigen(BI, 4)
print("Bi = %.12f" % BI)
print("true roots (k=1..4): " + ", ".join("%.10f" % t for t in x))
print("feishu table       : " + ", ".join("%.4f" % t for t in TABLE))
add("T00", "热 Biot 数 Bi = hR/k", BI, "-", "定义由附录2")

dev = (TABLE / x - 1.0) * 100.0
print("\n  k  table     true        deviation(table vs true)")
for k in range(4):
    print("  %d  %6.2f  %11.7f   %+8.4f %%" % (k + 1, TABLE[k], x[k], dev[k]))
    add("T01_%d" % (k + 1), "feishu §6.1 表值 x_%d" % (k + 1), TABLE[k], "-", "占位值")
    add("T02_%d" % (k + 1), "真实本征值 x_%d" % (k + 1), x[k], "-", "数值求根")
    add("T03_%d" % (k + 1), "表值相对真值偏差 (%%) x_%d" % (k + 1), dev[k], "%",
        "正 = 表值偏大")
print("  deviation range: %+.4f %% to %+.4f %%" % (dev.min(), dev.max()))
add("T04", "表值偏差下界 (最小)", float(dev.min()), "%", "表值偏大")
add("T05", "表值偏差上界 (最大)", float(dev.max()), "%", "表值偏大")

print("\nimplied Bi if each table value were a root:  Bi = x J1(x)/J0(x)")
imp = TABLE * j1(TABLE) / j0(TABLE)
for k in range(4):
    print("  x=%6.2f  ->  Bi = %9.4f" % (TABLE[k], imp[k]))
    add("T06_%d" % (k + 1), "表值 x=%g 反推的 Bi" % TABLE[k], imp[k], "-",
        "彼此相差近 2 倍 => 不属于同一 Bi")
add("T07", "反推 Bi 的极差 (max-min)", float(imp.max() - imp.min()), "-",
    "若表值同属一个 Bi 应为 0")

print("\nroot spacing (asymptotically pi = %.5f):" % np.pi)
sp = np.diff(x)
for k in range(3):
    print("  x_%d -> x_%d : %.4f" % (k + 1, k + 2, sp[k]))
    add("T08_%d" % (k + 1), "真根间隔 x_%d->x_%d" % (k + 1, k + 2), sp[k], "-", "趋于 pi")
add("T09", "真根间隔均值 (k=1..4)", float(sp.mean()), "-", "趋于 pi")
print("  table spacing: uniformly %.4f" % (TABLE[1] - TABLE[0]))
add("T10", "表值间隔 (均匀)", float(TABLE[1] - TABLE[0]), "-", "人为等距, 与真根间隔不符")

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["id", "quantity", "value", "unit",
                                      "uncertainty", "source", "command", "note"])
    w.writeheader()
    for r in _REG:
        w.writerow(r)
print("\nwrote %s" % OUT)
