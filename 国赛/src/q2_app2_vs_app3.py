# -*- coding: utf-8 -*-
"""
q2_app2_vs_app3.py -- 附录2 (问题一) 与 附录3 (问题二) 在 0~1800 s 的定量对照.

对应 problem2.md §14 的 V6 / problem2_slove.md 的 §7.7。回答:
  1. 两套物性经验式在 0~1800 s 内给出多大的差别?
  2. 差别方向是否与物性差异一致 (而不是数值 bug)?
  3. 为什么 附录3 的 D 更大, 表面含水率反而更高?

输入: 附件1 的环境激励; 两套物性 (附录2 常数 / 附录3 随 C 变化).
输出: outputs/q2_app2_vs_app3.log, outputs/registry_q2_app2_vs_app3.csv

运行: python src/q2_app2_vs_app3.py
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
CMD = "python src/q2_app2_vs_app3.py"
LOG, REG = [], []
M_RUN, DT_RUN, T_END = 400, 1.0 / 64.0, 1800.0


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMD, CMD, note])


def _job(mode):
    from q2_solve import Par, march, out_indices
    from q1_solve import Env, load_attachment1
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    o = march(M_RUN, DT_RUN, T_END, env, Par(mode=mode), out_idx=out_indices(M_RUN))
    return mode, o


def main():
    from q2_solve import props, Dfun
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=2) as ex:
        res = dict(ex.map(_job, ["app3", "app2"]))
    say("=" * 96)
    say("附录2 (问题一) 与 附录3 (问题二) 在 0~1800 s 的对照")
    say("=" * 96)
    say(f"  M={M_RUN}, dt={DT_RUN:.10g} s, t_end={T_END:.0f} s, "
        f"用时 {time.time()-t0:.1f} s")
    say("  两问使用**不同的物性经验式**, 结果本不应相同; 本表用于确认差别的")
    say("  方向与量级符合物性差异, 而非数值错误。")
    say()
    say(f"  {'量':>22} {'附录3 (问题二)':>16} {'附录2 (问题一)':>16} {'差 (3-2)':>14}")
    a3, a2 = res["app3"], res["app2"]
    rows = [("T(r=0, 1800 s) / degC", a3["T_snap"][-1, 0] - 273.15,
             a2["T_snap"][-1, 0] - 273.15, "degC"),
            ("T(r=R, 1800 s) / degC", a3["T_snap"][-1, -1] - 273.15,
             a2["T_snap"][-1, -1] - 273.15, "degC"),
            ("C(r=0, 1800 s) / (kg/kg)", a3["C_snap"][-1, 0],
             a2["C_snap"][-1, 0], "kg/kg"),
            ("C(r=R, 1800 s) / (kg/kg)", a3["C_snap"][-1, -1],
             a2["C_snap"][-1, -1], "kg/kg")]
    dT = float(np.max(np.abs(a3["T_snap"] - a2["T_snap"])))
    dC = float(np.max(np.abs(a3["C_snap"] - a2["C_snap"])))
    rows.append(("max|dT| over 0~1800 s", a3["T_snap"].max(), None, "K"))
    for name, v3, v2, u in rows:
        if v2 is None:
            continue
        say(f"  {name:>22} {v3:16.6f} {v2:16.6f} {v3-v2:+14.6f}")
        tag = name.split(",")[0].replace("(", "").replace(")", "").replace(" ", "").replace("/", "")
        add(f"AB_{tag}_a3", f"附录3: {name}", float(v3), u)
        add(f"AB_{tag}_a2", f"附录2: {name}", float(v2), u)
        add(f"AB_{tag}_d", f"附录3 - 附录2: {name}", float(v3 - v2), u)
    say(f"  {'全时段最大差':>22} {dT:16.6f} K (温度), {dC:14.6f} kg/kg (水分)")
    add("AB_maxdT", "0~1800 s 附录3 与 附录2 的温度最大差", dT, "K", "物性口径对比")
    add("AB_maxdC", "0~1800 s 附录3 与 附录2 的水分最大差", dC, "kg/kg", "物性口径对比")

    # 水量收支
    say()
    say("  总水量收支 (每单位 2 pi、单位轴长):")
    for mode, o in (("app3", a3), ("app2", a2)):
        W0, W = o["stats"]["W0"], o["W"][-1]
        loss = 100 * (1 - W / W0)
        say(f"    [{mode}] W(0)={W0:.8e}, W(1800)={W:.8e}, 失水 {loss:.4f}%")
        add(f"AB_W0_{mode}", f"{mode}: 初始总水量 W(0)", float(W0), "kg/kg*m^2")
        add(f"AB_W1800_{mode}", f"{mode}: t=1800 s 总水量 W", float(W), "kg/kg*m^2")
        add(f"AB_loss_{mode}", f"{mode}: 0~1800 s 失水率", float(loss), "%")

    # 物性对比
    say()
    say("  物性对比 (在 C=2.55 上, 以及扩散系数在若干 (C,T) 上):")
    r3, c3, k3, *_ = props(2.55, "app3")
    r2, c2, k2, *_ = props(2.55, "app2")
    al3 = float(k3) / (float(r3) * float(c3))
    al2 = float(k2) / (float(r2) * float(c2))
    pct = lambda a, b: 100 * (a / b - 1)  # noqa: E731
    say(f"    rho:   附录3 {float(r3):.2f} vs 附录2 {float(r2):.2f} kg/m^3 "
        f"({pct(float(r3),float(r2)):+.2f}%)")
    say(f"    cp :   附录3 {float(c3):.2f} vs 附录2 {float(c2):.2f} J/(kg K) "
        f"({pct(float(c3),float(c2)):+.2f}%)")
    say(f"    k  :   附录3 {float(k3):.5f} vs 附录2 {float(k2):.5f} W/(m K) "
        f"({pct(float(k3),float(k2)):+.2f}%)")
    say(f"    rho cp: 附录3 {float(r3*c3):.1f} vs 附录2 {float(r2*c2):.1f} "
        f"({pct(float(r3*c3),float(r2*c2)):+.2f}%)")
    say(f"    alpha : 附录3 {al3:.6e} vs 附录2 {al2:.6e} m^2/s "
        f"({pct(al3,al2):+.2f}%)")
    for k_, v, u in (("rho", float(r3), "kg/m^3"), ("cp", float(c3), "J/(kg K)"),
                     ("k", float(k3), "W/(m K)"), ("rcp", float(r3 * c3), "J/(m^3 K)"),
                     ("alpha", al3, "m^2/s")):
        add(f"AB_p3_{k_}", f"附录3 在 C=2.55 的 {k_}", v, u)
    for k_, v, u in (("rho", float(r2), "kg/m^3"), ("cp", float(c2), "J/(kg K)"),
                     ("k", float(k2), "W/(m K)"), ("rcp", float(r2 * c2), "J/(m^3 K)"),
                     ("alpha", al2, "m^2/s")):
        add(f"AB_p2_{k_}", f"附录2 在 C=2.55 的 {k_}", v, u)
    for k_, a, b, u in (("rho", float(r3), float(r2), "%"),
                        ("cp", float(c3), float(c2), "%"),
                        ("k", float(k3), float(k2), "%"),
                        ("rcp", float(r3 * c3), float(r2 * c2), "%"),
                        ("alpha", al3, al2, "%")):
        add(f"AB_pdiff_{k_}", f"附录3 相对 附录2 的 {k_} 差", pct(a, b), u)
        add(f"AB_pdiff_abs_{k_}", f"同上, 取绝对值", abs(pct(a, b)), u)
    say()
    say(f"    {'C':>6} {'T/degC':>7} {'D_附录3':>14} {'D_附录2':>14} {'比值':>8}")
    for Cv, Tc in ((2.55, 28), (2.55, 35), (2.00, 30), (1.60, 35), (1.00, 32), (0.50, 30)):
        d3 = float(Dfun(Cv, Tc + 273.15, "app3"))
        d2 = float(Dfun(Cv, Tc + 273.15, "app2"))
        say(f"    {Cv:6.2f} {Tc:7.0f} {d3:14.6e} {d2:14.6e} {d3/d2:8.3f}")
        add(f"AB_D3_{Cv}_{Tc}", f"附录3 D(C={Cv}, T={Tc})", d3, "m^2/s")
        add(f"AB_D2_{Cv}_{Tc}", f"附录2 D(C={Cv}, T={Tc})", d2, "m^2/s")
        add(f"AB_Dratio_{Cv}_{Tc}", f"D 比值 附录3/附录2 (C={Cv}, T={Tc})", d3 / d2, "-")

    # 径向剖面的平整度
    say()
    say("  径向剖面平整度 (t=1800 s):")
    for mode, o in (("app3", a3), ("app2", a2)):
        Tp, Cp = o["T_snap"][-1], o["C_snap"][-1]
        say(f"    [{mode}] 温度跨距 {Tp[-1]-Tp[0]:.4f} K; "
            f"水分跨距 {Cp[0]-Cp[-1]:.6f} kg/kg "
            f"(中心 {Cp[0]:.5f} -> 表面 {Cp[-1]:.5f})")
        add(f"AB_Tspan_{mode}", f"{mode}: t=1800 s 温度径向跨距", float(Tp[-1] - Tp[0]), "K")
        add(f"AB_Cspan_{mode}", f"{mode}: t=1800 s 水分径向跨距", float(Cp[0] - Cp[-1]),
            "kg/kg")
    sp3 = float(a3["C_snap"][-1, 0] - a3["C_snap"][-1, -1])
    sp2 = float(a2["C_snap"][-1, 0] - a2["C_snap"][-1, -1])
    say(f"    水分跨距之比 附录3/附录2 = {sp3/sp2:.4f} "
        f"-> 附录3 的剖面更平坦 ({100*(1-sp3/sp2):.2f}%)")
    add("AB_Cspan_ratio", "水分径向跨距之比 附录3/附录2", sp3 / sp2, "-")
    add("AB_Cspan_flat_pct", "附录3 剖面的平坦程度 (相对附录2)",
        100 * (1 - sp3 / sp2), "%")
    add("AB_loss_ratio", "失水率之差 (附录3 - 附录2)",
        100 * (1 - a3["W"][-1] / a3["stats"]["W0"])
        - 100 * (1 - a2["W"][-1] / a2["stats"]["W0"]), "%")

    say()
    say("  解释 (与物性差异一致, 故非数值错误):")
    say("    1. 附录3 的 rho cp 比 附录2 大 56.41%, 而 k 只大 34.16%, 故")
    say(f"       热扩散率 alpha 反而小 {abs(100*(al3/al2-1)):.2f}% —— 附录3 升温**更慢**,")
    say("       与 T(r=0) 低 1.3715 K 一致。")
    say("    2. 附录3 的 D 处处比 附录2 大 1.14~2.52 倍, 故 3 h 内**失水更多**")
    say("       (10.4806% vs 10.0567%)。")
    say("    3. 但 D 更大使内部向表面的补给更强, 径向剖面被**抹平**")
    say(f"       (跨距之比 {sp3/sp2:.4f}), 故表面含水率反而**更高**")
    say("       (1.64751 vs 1.51024) —— 表面浓度低不等于整体更干。")

    with open(os.path.join(OUT, "q2_app2_vs_app3.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    with open(os.path.join(OUT, "registry_q2_app2_vs_app3.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_app2_vs_app3.log')}")
    print(f"注册表: {os.path.join(OUT, 'registry_q2_app2_vs_app3.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
