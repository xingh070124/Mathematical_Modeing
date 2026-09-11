# -*- coding: utf-8 -*-
"""
q2_center_node.py -- r=0 节点: 行和集中质量矩阵与精确半控制体的差别及其影响.

发现
----
集中质量 (行和) FEM 在内部节点给出 M^L_ii = rho cp dr r_i, 与节点式有限体积的
控制体热容 rho cp V_i/(2 pi) 在**内部完全一致**; 但在 r=0 处两者不同:

        lumped  FEM : M^L_00 = rho cp dr^2 / 6   (r_0=0 的线性单元行和)
        半控制体 FV : V_0/(2 pi) = dr^2 / 8

且刚度项在两种口径下都是 k r_{1/2}/dr = k/2, 故 r=0 的等效系数为

        lumped FEM : dT_0/dt = 3 alpha (T_1 - T_0)/dr^2
        精确 (r->0): (1/r) d/dr (r dT/dr) = 2 d^2T/dr^2 -> 4 alpha (T_1-T_0)/dr^2

即**集中质量的 r=0 系数恰为精确值的 3/4**, 与 M 无关。这是集中质量 FEM 的一个
已知弱点: 节点 0 的方程不再一致逼近柱坐标算子。

本脚本定量回答: 这一局部不一致对**解**的影响有多大, 以及在什么网格下低于四位小数
阈值 5e-5。做法: 常数系数的线性 Robin 圆柱问题, 与 Bessel 特征函数级数解析解对比。

运行: python src/q2_center_node.py
输出: outputs/q2_center_node.log, outputs/registry_q2_center.csv
"""

from __future__ import annotations

import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = os.path.join(ROOT, "outputs")
CMD = "python src/q2_center_node.py"
LOG, REG = [], []
R = 0.02
T0K = 301.15
H = 25.0


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMD, CMD, note])


def _bessel(r, t, alpha, k, h, Tinf, T0, n_modes=400):
    from scipy.special import j0, j1
    from scipy.optimize import brentq
    Bi = h * R / k
    f = lambda lam: lam * j1(lam) - Bi * j0(lam)          # noqa: E731
    grid = np.linspace(1e-8, 800.0, 400001)
    v = f(grid)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    lam = np.array([brentq(f, grid[i], grid[i + 1], xtol=1e-15) for i in idx[:n_modes]])
    Cn = 2 * j1(lam) / (lam * (j0(lam) ** 2 + j1(lam) ** 2))
    rr = np.atleast_1d(r) / R
    th = (Cn[:, None] * np.exp(-(lam ** 2)[:, None] * alpha * t / R ** 2)) * j0(
        lam[:, None] * rr[None, :])
    return Tinf + (T0 - Tinf) * th.sum(axis=0)


def _job(cfg):
    from q2_solve import Par, march
    M, dt, bound = cfg["M"], cfg["dt"], cfg["bound"]
    par = Par(mode="app2", hevap="off", boundary=bound)
    t1 = np.array([0.0, 1.0e7])
    from q1_solve import Env
    env = Env(t1, np.array([50.0, 50.0]), np.array([0.0, 0.0]), method="pchip")
    t0 = time.time()
    o = march(M, dt, 600.0, env, par, out_idx=np.arange(M + 1))
    return (M, dt, bound), dict(T=o["T_snap"][-1], r=o["r"], wall=time.time() - t0)


def main():
    alpha = 0.36 / (820.0 * 2600.0)
    k = 0.36
    say("=" * 96)
    say("r=0 节点的一致性: 行和集中质量 FEM vs 精确半控制体")
    say("=" * 96)
    say(f"  模型: 常数系数 (附录2) Robin 圆柱, 初值 28 degC, 常 T_inf=50 degC")
    say(f"  alpha = {alpha:.10e} m2/s, k = {k}, h = {H}, t_end = 600 s")
    say()
    say("  (a) r=0 的等效扩散系数 (解析)")
    for M in (100, 400, 1600):
        dr = R / M
        # dT0/dt = c * alpha (T1-T0)/dr^2
        MLl = dr * dr / 6.0
        MLh = dr * dr / 8.0
        cl = (k * dr / 2.0) / (820.0 * 2600.0 * MLl * dr)     # (k/2)/(rcp ML00)
        ch = (k * dr / 2.0) / (820.0 * 2600.0 * MLh * dr)
        say(f"    M={M:5d}  集中质量: {cl*dr*dr/alpha:.6f} alpha/dr^2 ; "
            f"半控制体: {ch*dr*dr/alpha:.6f} alpha/dr^2 ; 比值 = {cl/ch:.6f}")
    add("CN_coef_lumped", "集中质量 r=0 的等效系数 (单位 alpha/dr^2)", 3.0, "-",
        "解析: (k/2)/(rho cp dr^2/6)")
    add("CN_coef_halfcv", "半控制体 r=0 的等效系数 (单位 alpha/dr^2)", 4.0, "-",
        "解析: 精确柱坐标算子")
    add("CN_coef_ratio", "集中质量 / 半控制体 的 r=0 系数之比", 0.75, "-", "解析")

    say()
    say("  (b) 与 Bessel 解析解的对比 (dt = 1/400 s, 时间误差底 < 1e-5 K)")
    cfgs = []
    for M in (25, 50, 100, 200, 400, 800):
        for bound in ("lumped", "halfcv"):
            cfgs.append(dict(M=M, dt=1.0 / 400.0, bound=bound))
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=12) as ex:
        res = dict(ex.map(_job, cfgs))
    say(f"    [并行 {len(cfgs)} 个算例, 用时 {time.time()-t0:.1f} s]")
    say(f"    {'M':>5} {'口径':>8} {'max|dT| [K]':>14} {'中心':>13} {'表面':>13} "
        f"{'最大偏差位置/cm':>16} {'比值':>8}")
    prev = {"lumped": None, "halfcv": None}
    for M in (25, 50, 100, 200, 400, 800):
        for bound in ("lumped", "halfcv"):
            o = res[(M, 1.0 / 400.0, bound)]
            ex = _bessel(o["r"], 600.0, alpha, k, H, 323.15, T0K)
            e = np.abs(o["T"] - ex)
            ratio = "" if prev[bound] is None else f"{prev[bound]/e.max():.3f}"
            say(f"    {M:5d} {bound:>8} {e.max():14.4e} {e[0]:13.4e} {e[-1]:13.4e} "
                f"{o['r'][int(np.argmax(e))]*100:16.4f} {ratio:>8}")
            add(f"CN_{bound}_M{M}", f"{bound} 口径 M={M} 的最大温度偏差",
                float(e.max()), "K", "Bessel 解析解")
            add(f"CN_{bound}_M{M}_c", f"{bound} 口径 M={M} 的中心温度偏差",
                float(e[0]), "K", "Bessel 解析解")
            prev[bound] = float(e.max())

    say()
    say("  结论:")
    say("    * 内部节点两种口径的控制体热容完全一致 (dr r_i), 故差别只在 r=0 附近的")
    say("      一层网格; 最大偏差确实出现在 r=0。")
    say("    * 集中质量在 r=0 的系数是精确值的 3/4, 属**局部不一致**; 其误差随 M 下降,")
    say("      但收敛常数大于半控制体, 需要更细网格才能达到同样的精度。")
    say("    * 生产设置 M=800 下, 两种口径的绝对偏差见表; 若低于 5e-5 则四位小数报告")
    say("      对该选择稳健。")

    # 非线性生产问题上的实际影响
    say()
    say("  (c) 非线性生产问题 (附录3, 含蒸发) 上两种口径的差别")
    from q2_solve import Par, march, out_indices
    from q1_solve import Env, load_attachment1
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    idx = out_indices(800)
    a = march(800, 1.0 / 16, 10800.0, env, Par(boundary="lumped"), out_idx=idx)
    b = march(800, 1.0 / 16, 10800.0, env, Par(boundary="halfcv"), out_idx=idx)
    dT = float(np.max(np.abs(a["T_snap"] - b["T_snap"])))
    dC = float(np.max(np.abs(a["C_snap"] - b["C_snap"])))
    say(f"    M=800, dt=1/16 s: max|dT| = {dT:.4e} K, max|dC| = {dC:.4e} kg/kg")
    add("CN_prod_dT", "生产问题 M=800/dt=1/16 下两种 r=0 口径的温度最大差", dT, "K",
        "口径对照")
    add("CN_prod_dC", "同上, 水分最大差", dC, "kg/kg", "口径对照")

    with open(os.path.join(OUT, "q2_center_node.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    with open(os.path.join(OUT, "registry_q2_center.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_center_node.log')}")
    print(f"注册表: {os.path.join(OUT, 'registry_q2_center.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
