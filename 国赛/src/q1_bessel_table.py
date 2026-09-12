# -*- coding: utf-8 -*-
"""
q1_bessel_table.py -- 附录 A 表 11 的数据源: Bessel 特征展开的前五阶根、展开系数与衰减率.

论文附录 A 表 11 给出特征方程 x J1(x) = Bi J0(x) 的前五阶正根 x_k、展开系数 c_k
与衰减率 mu_k = alpha x_k^2 / R^2。本脚本把这 15 个数字算出来并写进注册表,
使附录表格逐项可追溯。

物性取附录 2: h=25 W/(m^2K), k=0.36 W/(mK), rho=820 kg/m^3, cp=2600 J/(kg K),
R=0.02 m。故 Bi = hR/k, alpha = k/(rho cp)。

输出: outputs/registry_q1_bessel.csv
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np
from scipy.optimize import brentq
from scipy.special import j0, j1

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q2_solve import H_CONV, R as R0        # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

RHO, CP, K = 820.0, 2600.0, 0.36          # 附录 2
ALPHA = K / (RHO * CP)
BI = H_CONV * R0 / K


def roots(n=5):
    """x J1(x) = Bi J0(x) 的前 n 个正根."""
    f = lambda x: x * j1(x) - BI * j0(x)
    out, x = [], 1e-6 + 1e-3
    while len(out) < n:
        x_lo, x_hi = x, x + 0.05
        while np.sign(f(x_lo)) == np.sign(f(x_hi)):
            x_lo, x_hi = x_hi, x_hi + 0.05
        out.append(brentq(f, x_lo, x_hi, xtol=1e-14, rtol=1e-15))
        x = x_hi
    return np.array(out)


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    xk = roots(5)
    # 均匀初值下的展开系数: c_k = 2 J1(x_k) / (x_k (J0(x_k)^2 + J1(x_k)^2))
    ck = 2.0 * j1(xk) / (xk * (j0(xk) ** 2 + j1(xk) ** 2))
    muk = ALPHA * xk ** 2 / R0 ** 2

    rows = [("BS_alpha", "问题一热扩散率 alpha=k/(rho cp)", ALPHA, "m^2/s",
             "附录2"),
            ("BS_Bi", "热 Biot 数 Bi=hR/k", BI, "1", "附录2/定义")]
    print(f"alpha = {ALPHA:.10e} m^2/s   Bi = {BI:.10f}")
    print(f"{'k':>2} {'x_k':>16} {'c_k':>14} {'mu_k / 1/s':>16}")
    for i in range(5):
        print(f"{i+1:>2} {xk[i]:>16.10f} {ck[i]:>14.7f} {muk[i]:>16.10e}")
        rows.append((f"BS_x{i+1}", f"表11 第{i+1}阶特征根 x_{i+1}", float(xk[i]), "1",
                     "推导"))
        rows.append((f"BS_c{i+1}", f"表11 第{i+1}阶展开系数 c_{i+1}", float(ck[i]),
                     "1", "推导"))
        rows.append((f"BS_mu{i+1}", f"表11 第{i+1}阶衰减率 mu_{i+1}", float(muk[i]),
                     "1/s", "推导"))

    path = os.path.join(OUTDIR, "registry_q1_bessel.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "source"])
        for r in rows:
            w.writerow([r[0], r[1], repr(r[2]), r[3], r[4]])
    print(f"\n写出: outputs/registry_q1_bessel.csv ({len(rows)} 行)")


if __name__ == "__main__":
    main()
