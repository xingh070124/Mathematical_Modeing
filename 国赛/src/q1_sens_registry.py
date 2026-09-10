"""
从灵敏度/鲁棒性实验产物生成数字注册表, 供 q1_reconcile.py 对账使用.

来源: outputs/q1_sensitivity_oat.csv, outputs/q1_sensitivity_mc.csv
      (由 python src/q1_sensitivity.py 生成); E5 网格/插值数值现算 (快速).
输出: outputs/registry_q1_sensitivity.csv
运行: python src/q1_sens_registry.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
OAT = os.path.join(OUT, "q1_sensitivity_oat.csv")
MC = os.path.join(OUT, "q1_sensitivity_mc.csv")
REG = os.path.join(OUT, "registry_q1_sensitivity.csv")

CMD = "python src/q1_sensitivity.py"
SRC = "outputs/q1_sensitivity_*.csv"


def main():
    rows = []

    def add(id_, q, v, u, unc, note=""):
        rows.append([id_, q, v, u, unc, SRC, CMD, note])

    # ---- OAT 灵敏度系数 ----
    with open(OAT, encoding="utf-8-sig") as f:
        oat = list(csv.DictReader(f))
    for r in oat:
        add(f"OAT_{r['param']}_{r['qoi'][:3]}",
            f"灵敏度 S(中心差分) {r['qoi']} <- {r['param']}(±10%)",
            r["S_central"], "-", "OAT ±10%", "")
    add("OAT_note", "温度QoI对hm/D0/C0灵敏度最大绝对值",
        max(abs(float(r["S_central"])) for r in oat
            if r["param"] in ("hm", "D0", "C0") and r["qoi"].startswith("T")),
        "-", "OAT ±10%", "严格为0: 热湿解耦数值证据")
    add("OAT_note2", "水分QoI对h/k/rho/cp/T0灵敏度最大绝对值",
        max(abs(float(r["S_central"])) for r in oat
            if r["param"] in ("h", "k", "rho", "cp", "T0") and not r["qoi"].startswith("T")),
        "-", "OAT ±10%", "严格为0: 热湿解耦数值证据")

    # ---- MC 分布 ----
    e3, e4 = [], []
    with open(MC, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            v = [float(r["T_center_1800s_K"]), float(r["T_surface_1800s_K"]),
                 float(r["C_surface_1800s_kgkg"]), float(r["C_avg_1800s_kgkg"])]
            (e3 if r["experiment"] == "E3_noise" else e4).append(v)
    e3, e4 = np.array(e3), np.array(e4)
    base = np.array([306.726129, 309.935961, 1.510266, 2.293556])
    names = ["T中心", "T表面", "C表面", "C平均"]
    for j, nm in enumerate(names):
        add(f"E3_{nm}_std", f"噪声MC {nm}(1800s) 标准差", f"{e3[:, j].std(ddof=1):.3e}",
            "K" if j < 2 else "kg/kg", "N=100", f"均值 {e3[:, j].mean():.6f}")
        add(f"E3_{nm}_max", f"噪声MC {nm}(1800s) 最大绝对偏差",
            f"{np.abs(e3[:, j] - base[j]).max():.3e}", "K" if j < 2 else "kg/kg",
            "N=100", "")
    for j, nm in enumerate(names):
        add(f"E4_{nm}_std", f"参数MC {nm}(1800s) 标准差", f"{e4[:, j].std(ddof=1):.3e}",
            "K" if j < 2 else "kg/kg", "N=100", f"均值 {e4[:, j].mean():.6f}")
        add(f"E4_{nm}_max", f"参数MC {nm}(1800s) 最大绝对偏差",
            f"{np.abs(e4[:, j] - base[j]).max():.3e}", "K" if j < 2 else "kg/kg",
            "N=100", "")
    rel4 = max(np.abs((e4[:, j] - base[j]) / base[j]).max() for j in range(4))
    add("E4_rel_max", "参数MC QoI 最大相对偏差", f"{rel4:.4f}", "-", "N=100",
        "参数物理不确定性的传导")
    add("E3_sigT", "附件1 T_inf 噪声标准差(二阶差分MAD估计)", 0.152528, "degC",
        "稳健估计", "")
    add("E3_sigC", "附件1 C_inf 噪声标准差(二阶差分MAD估计)", 1.271e-4, "kg/kg",
        "稳健估计", "")

    # ---- E5 网格收敛 / 插值方法 (现算) ----
    from q1_sensitivity import solve_fast
    from q1_solve import Env, load_attachment1
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    dt = 0.25
    tg = np.arange(1, int(round(1800.0 / dt)) + 1) * dt
    grid = {}
    for M in (100, 200, 400, 800):
        Tg, Cg, Cag = solve_fast(M, dt, env.T_arr(tg), env.C_arr(tg))
        grid[M] = np.array([Tg[0], Tg[-1], Cg[-1], Cag])
    ref = grid[800]
    for M in (100, 200, 400):
        dev = np.abs(grid[M] - ref)
        add(f"E5_M{M}", f"网格收敛 M={M} vs M=800 四QoI最大偏差",
            f"{dev.max():.3e}", "-", "vs M=800", "")
    dtb = 0.5
    nsb = int(round(1800.0 / dtb))
    tgb = np.arange(1, nsb + 1) * dtb
    ip = {}
    for meth in ("linear", "pchip", "cubic"):
        ev = Env(t1, T1, C1, method=meth)
        Ti, Ci, Cai = solve_fast(400, dtb, ev.T_arr(tgb), ev.C_arr(tgb))
        ip[meth] = np.array([Ti[0], Ti[-1], Ci[-1], Cai])
    for meth in ("linear", "cubic"):
        dev = np.abs(ip[meth] - ip["pchip"])
        add(f"E5_interp_{meth}", f"插值方法 {meth} vs pchip 四QoI最大偏差",
            f"{dev.max():.3e}", "-", "M=400, dt=0.5s", "")

    with open(REG, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(rows)
    print(f"注册表: {REG}  ({len(rows)} 行)")


if __name__ == "__main__":
    main()
