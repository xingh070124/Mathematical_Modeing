# -*- coding: utf-8 -*-
"""
q1_const_env_check.py -- 附录 A 的"常环境校核": 令 T_inf ≡ 50 degC 时的数值解与解析级数解之差.

引言: 附录 A 用一个常环境算例作补充校核 —— 此时不存在环境插值误差, 剩余偏差纯由
数值离散造成, 可与变环境结论对照。该数字此前只出现在论文里, 没有注册表来源;
本脚本把它算出来并登记, 同时如实记录实际使用的网格与步长。

问题一侧提供 `solve_q1(..., const_T_inf=...)`, 正是为此设计。

输出: outputs/registry_q1_const_env.csv
"""

from __future__ import annotations

import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q1_solve import solve_q1, load_attachment1          # noqa: E402
from q1_analytic_fit import eigen, series_T              # noqa: E402
from q2_solve import H_CONV                              # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

K2C = 273.15
T_TAB = [100.0, 300.0, 600.0, 900.0, 1200.0, 1500.0, 1800.0]
R_ALL = np.round(np.arange(0.0, 2.0001, 0.1), 10) / 100.0
COL5 = [0, 5, 10, 15, 20]
T_INF_C = 50.0


class ConstEnv:
    """常环境: T_inf 固定, C_inf 取附件1 末值 (仅温度校核用, C 不参与结论)."""

    def __init__(self, t1, C1, T_c=T_INF_C, C_c=None):
        self.Tbar = T_c + K2C
        self.Cbar = float(C1[-1]) if C_c is None else float(C_c)

    def T(self, t):
        return self.Tbar

    def C(self, t):
        return self.Cbar


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    t0 = time.time()
    t1, T1, C1 = load_attachment1()
    env = ConstEnv(t1, C1)
    print(f"常环境: T_inf = {T_INF_C} degC, C_inf = {env.Cbar:.4f} kg/kg")

    x, lam, c = eigen(H_CONV * 0.02 / 0.36, 400)    # Bi = hR/k, 400 模态
    # 解析侧: 常环境, 分段线性子步长 0.25 s (与附录 A 同口径)
    htau = 0.25
    tg = np.unique(np.concatenate([np.arange(0.0, 1800.0 + htau, htau),
                                   np.array(T_TAB)]))
    Tinf = np.full(tg.size, env.Tbar)
    Tsol = series_T(tg, Tinf, R_ALL, x, lam, c)
    idx = [int(np.where(np.isclose(tg, v))[0][0]) for v in T_TAB]
    T_ana = Tsol[idx]

    rows = []
    add = lambda k, q, v, u, s: rows.append((k, q, float(v), u, s))
    add("CE_Tinf", "常环境校核使用的环境温度", T_INF_C, "degC", "设定值")
    add("CE_Bi", "热 Biot 数", 5.0 * 0.02 / 0.36, "1", "附录2")
    add("CE_htau", "解析侧分段线性子步长", htau, "s", "设置")
    add("CE_nmodes", "解析侧模态数", 400.0, "1", "设置")

    for M, e_dt in ((3200, 8), (800, 11)):
        dt = 2.0 ** -e_dt
        if M == 800:
            print(f"  [skip] M={M}, dt=2^-{e_dt} 需 {1800/dt:.3e} 步, 不实现 (见论文说明)")
            continue
        T_num_snap = solve_q1(M, dt, 1800.0, env, corr=True,
                              probes_t=np.array(T_TAB),
                              const_T_inf=env.Tbar)
        sT = T_num_snap[3]
        dr = 0.02 / M
        qidx = np.round(R_ALL / dr).astype(int)
        T_num = sT[:, qidx]
        dmax = float(np.max(np.abs(T_num - T_ana)))
        dtab = float(np.max(np.abs(T_num[:, COL5] - T_ana[:, COL5])))
        print(f"  M={M}, dt=2^-{e_dt} s: 全场 max|dT| = {dmax:.4e} K; "
              f"表1 位形 (7x5) max|dT| = {dtab:.4e} K")
        add(f"CE_maxdT_M{M}", f"常环境校核 M={M} 全场最大温度差", dmax, "K",
            "q1_const_env_check.py")
        add(f"CE_maxdT_tab_M{M}", f"常环境校核 M={M} 表1 位形最大温度差", dtab, "K",
            "q1_const_env_check.py")
        add(f"CE_dt_M{M}", f"常环境校核 M={M} 的时间步长", dt, "s",
            "q1_const_env_check.py")

    path = os.path.join(OUTDIR, "registry_q1_const_env.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "source"])
        for r in rows:
            w.writerow([r[0], r[1], repr(r[2]), r[3], r[4]])
    print(f"写出: outputs/registry_q1_const_env.csv ({len(rows)} 行), "
          f"耗时 {time.time()-t0:.1f} s")


if __name__ == "__main__":
    main()
