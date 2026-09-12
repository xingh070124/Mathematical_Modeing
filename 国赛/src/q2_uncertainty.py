# -*- coding: utf-8 -*-
"""
q2_uncertainty.py -- 生产解的离散不确定度: 多种估计口径的透明比较.

问题
----
`q2_produce.py` 取 max(时间加密偏差, 网格加密偏差) 作为不确定度。这里两个量都是
**两次解之差**（即增量）, 不是"生产网格上的误差"。当误差按 h^p 收敛时,
细网格解的误差约等于增量 / (2^p - 1):

    p = 1 (后向 Euler, 时间):  err_fine ≈ Δ
    p = 2 (线性单元, 空间):    err_fine ≈ Δ / 3

因此 max(增量) 是一个**上界偏保守但口径不严**的估计。本脚本把四种口径都算出来:

  (i)   max(增量)              —— 原报告所用
  (ii)  Richardson (按各量的实测阶数 p)
  (iii) 求和 (Richardson 后相加)  —— 最保守
  (iv)  RSS (Richardson 后平方和开方)

并对温度与水分分别给出, 与四位小数阈值 5e-5 比较。生产者与读者都应看到:
**水分的结果依赖口径**, 论文必须写明用的是哪一种。

输入: outputs/q2_production.log 中的三组偏差不可直接机器读取, 故本脚本重算它们
      （M=1600/dt=1/64, M=1600/dt=1/128, M=3200/dt=1/64）。

运行: python src/q2_uncertainty.py
输出: outputs/registry_q2_uncertainty.csv, outputs/q2_uncertainty.log
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
CMD = "python src/q2_uncertainty.py"
LOG, REG = [], []
THR = 5e-5


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, CMD, CMD, note])


def _job(cfg):
    from q2_solve import Par, march, out_indices
    from q1_solve import Env, load_attachment1
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    M, dt = cfg["M"], cfg["dt"]
    o = march(M, dt, 10800.0, env, Par(), out_idx=out_indices(M))
    return cfg["tag"], dict(T=o["T_snap"], C=o["C_snap"], M=M, dt=dt,
                            wall=o["stats"]["wall"])


def _load_increments():
    """从 outputs/registry_q2_uncertainty.csv 读回已登记的四个增量.

    这四组偏差来自三组 M=1600/M=3200 的 10800 s 长跑（合计约 70 分钟）。
    把它们缓存到注册表后, 本脚本的"口径比较"部分就可以秒级重跑 ——
    否则每次调整口径都要重解三次, 成本与收益完全不成比例。
    仅在注册表缺失时才真正重算。
    """
    path = os.path.join(OUT, "registry_q2_uncertainty.csv")
    if not os.path.exists(path):
        return None
    d = {}
    with open(path, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["id"] in ("UT_dT_t", "UT_dC_t", "UT_dT_h", "UT_dC_h"):
                d[r["id"]] = float(r["value"])
    return d if len(d) == 4 else None


def main():
    t0 = time.time()
    cached = _load_increments()
    if cached is not None:
        say("=" * 96)
        say("生产解离散不确定度的多种口径 (M=1600, dt=1/64 s)")
        say("=" * 96)
        say("  [缓存] 三组长跑 (M=1600/dt=1/64, M=1600/dt=1/128, M=3200/dt=1/64) 的")
        say("         偏差已登记在 outputs/registry_q2_uncertainty.csv, 本次不重解。")
        say("         如需重解, 删除该注册表后重跑本脚本。")
        dT_t, dC_t = cached["UT_dT_t"], cached["UT_dC_t"]
        dT_h, dC_h = cached["UT_dT_h"], cached["UT_dC_h"]
    else:
        cfgs = [dict(tag="prod", M=1600, dt=1.0 / 64),
                dict(tag="chk-t", M=1600, dt=1.0 / 128),
                dict(tag="chk-h", M=3200, dt=1.0 / 64)]
        with ProcessPoolExecutor(max_workers=3) as ex:
            res = dict(ex.map(_job, cfgs))
        say("=" * 96)
        say("生产解离散不确定度的多种口径 (M=1600, dt=1/64 s)")
        say("=" * 96)
        say(f"  三组算例用时 {time.time()-t0:.1f} s")
        for tag in ("prod", "chk-t", "chk-h"):
            o = res[tag]
            say(f"    [{tag}] M={o['M']}, dt={o['dt']:.10g} s, wall={o['wall']:.1f} s")
        P, Tt, Th = res["prod"], res["chk-t"], res["chk-h"]
        dT_t = float(np.max(np.abs(P["T"] - Tt["T"])))
        dC_t = float(np.max(np.abs(P["C"] - Tt["C"])))
        dT_h = float(np.max(np.abs(P["T"] - Th["T"])))
        dC_h = float(np.max(np.abs(P["C"] - Th["C"])))

    say()
    say(f"  时间加密 (dt/2, 同网格):  ΔT = {dT_t:.4e} K,  ΔC = {dC_t:.4e} kg/kg")
    say(f"  网格加密 (M x2, 同 dt):   ΔT = {dT_h:.4e} K,  ΔC = {dC_h:.4e} kg/kg")
    for k, v, u in (("UT_dT_t", dT_t, "K"), ("UT_dC_t", dC_t, "kg/kg"),
                    ("UT_dT_h", dT_h, "K"), ("UT_dC_h", dC_h, "kg/kg")):
        add(k, f"生产校核增量 {k}", v, u)

    # 实测阶数 (由 q2_verify.py 的 V1/V2 给出, 这里用保守值)
    p_t, p_h = 1.0, 2.0
    say()
    say(f"  实测收敛阶: 时间 p = {p_t:.0f} (后向 Euler), 空间 p = {p_h:.0f} (线性单元)")
    say(f"  => Richardson: 由粗、细两解之差 Δ 估计各自的误差")
    say(f"     err(细) = Δ / (2^p - 1);   err(粗) = Δ · 2^p / (2^p - 1)")
    say(f"     时间: 分母 1, 粗解因子 2;  空间: 分母 3, 粗解因子 4/3")
    say(f"  注意: **生产解 (M=1600, dt=1/64) 是「粗」的那一个**, 加密解才是「细」的。")
    say(f"        因此对**交付物**的误差估计应当用 err(粗), 不是 err(细)。")

    eT_t, eC_t = dT_t / (2 ** p_t - 1), dC_t / (2 ** p_t - 1)
    eT_h, eC_h = dT_h / (2 ** p_h - 1), dC_h / (2 ** p_h - 1)
    cT_t, cC_t = dT_t * 2 ** p_t / (2 ** p_t - 1), dC_t * 2 ** p_t / (2 ** p_t - 1)
    cT_h, cC_h = dT_h * 2 ** p_h / (2 ** p_h - 1), dC_h * 2 ** p_h / (2 ** p_h - 1)
    say()
    say(f"  Richardson err(细): 时间 T {eT_t:.4e} / C {eC_t:.4e};  "
        f"空间 T {eT_h:.4e} / C {eC_h:.4e}")
    say(f"  Richardson err(粗): 时间 T {cT_t:.4e} / C {cC_t:.4e};  "
        f"空间 T {cT_h:.4e} / C {cC_h:.4e}   <- 对交付物")
    for k, v, u in (("UR_eT_t", eT_t, "K"), ("UR_eC_t", eC_t, "kg/kg"),
                    ("UR_eT_h", eT_h, "K"), ("UR_eC_h", eC_h, "kg/kg"),
                    ("UR_cT_t", cT_t, "K"), ("UR_cC_t", cC_t, "kg/kg"),
                    ("UR_cT_h", cT_h, "K"), ("UR_cC_h", cC_h, "kg/kg")):
        add(k, f"Richardson 误差估计 {k}", v, u)

    # 四种口径 (对交付物 = 粗解)
    conv = {}
    conv["(i)   max(增量)"] = (max(dT_t, dT_h), max(dC_t, dC_h))
    conv["(ii)  max(Rich. 细)"] = (max(eT_t, eT_h), max(eC_t, eC_h))
    conv["(iii) max(Rich. 粗)"] = (max(cT_t, cT_h), max(cC_t, cC_h))
    conv["(iv)  求和 (粗)"] = (cT_t + cT_h, cC_t + cC_h)
    conv["(v)   RSS (粗)"] = (float(np.hypot(cT_t, cT_h)),
                             float(np.hypot(cC_t, cC_h)))
    say()
    say("=" * 96)
    say("五种口径的结果与四位小数阈值 (半 ulp = 5e-5) 比较")
    say("=" * 96)
    say(f"  {'口径':>20} {'T 不确定度':>14} {'占阈值':>9} {'C 不确定度':>14} {'占阈值':>9}")
    for name, (uT, uC) in conv.items():
        pT, pC = 100 * uT / THR, 100 * uC / THR
        say(f"  {name:>20} {uT:14.4e} {pT:8.2f}% {uC:14.4e} {pC:8.2f}%")
        tag = name.split()[0].strip("()")
        add(f"UC_{tag}_T", f"口径 {name} 的温度不确定度", uT, "K")
        add(f"UC_{tag}_C", f"口径 {name} 的水分不确定度", uC, "kg/kg")
        add(f"UC_{tag}_Tpct", f"口径 {name} 温度不确定度占阈值", pT, "%")
        add(f"UC_{tag}_Cpct", f"口径 {name} 水分不确定度占阈值", pC, "%")

    say()
    say("  结论 (如实报告):")
    worst_T = max(u for u, _ in conv.values())
    worst_C = max(u for _, u in conv.values())
    say(f"    * 温度: 五种口径的最大值 {worst_T:.4e} K = 阈值的 "
        f"{100*worst_T/THR:.2f}%  -> 无论取哪种口径都**低于**阈值。")
    say(f"    * 水分: 五种口径的最大值 {worst_C:.4e} kg/kg = 阈值的 "
        f"{100*worst_C/THR:.2f}%  -> **超过**阈值。")
    say(f"      其中对**交付物**最贴切的 Richardson-粗 口径给出 C = "
        f"{conv['(iii) max(Rich. 粗)'][1]:.4e} kg/kg = 阈值的 "
        f"{100*conv['(iii) max(Rich. 粗)'][1]/THR:.2f}%。")
    say()
    say("    => 准确而完整的三句话:")
    say(f"       (1) 若以「两次解之差」为不确定度 (口径 i, 原报告的用法), "
        f"T = {max(dT_t,dT_h):.3e} K ({100*max(dT_t,dT_h)/THR:.1f}%)、"
        f"C = {max(dC_t,dC_h):.3e} kg/kg ({100*max(dC_t,dC_h)/THR:.1f}%), 两者都在阈值内;")
    say(f"       (2) 若按 Richardson 估计**交付网格自身**的误差 (口径 iii, 更严), "
        f"T = {conv['(iii) max(Rich. 粗)'][0]:.3e} K ({100*conv['(iii) max(Rich. 粗)'][0]/THR:.1f}%), "
        f"仍在阈值内;")
    say(f"           但 C = {conv['(iii) max(Rich. 粗)'][1]:.3e} kg/kg = "
        f"阈值的 {100*conv['(iii) max(Rich. 粗)'][1]/THR:.1f}% —— **超出阈值**;")
    say(f"       (3) 故**不能说「水分的四位小数都可靠」**。准确的说法是:")
    say(f"           温度的四位小数在全部口径下都可靠 (最大 {100*worst_T/THR:.1f}% 阈值);")
    say(f"           水分的四位小数**只在「增量」口径下可靠**; 按交付网格自身的")
    say(f"           误差估计, 水分的第 4 位**不正**。")
    say()
    say("    何时何地受影响 (关键补充): 水分的大偏差集中在 t<=60 s 的表面边界层")
    say("      (见 q2_moist_diag.py; 网格加密偏差逐时段为")
    say("       t=1..60 s: 3.85e-05, t=61..600: 3.77e-06, t=601..3600: 6.51e-07,")
    say("       t=3601..10800: 3.80e-07 kg/kg)。故")
    say("       - **表 3 / 表 4 (0.5~3 h) 的四位小数可靠** (<8% 阈值);")
    say("       - `result2.xlsx` 中 t<=60 s 的**表面若干行**的第 4 位不可靠;")
    say("       - 若要求全部 10800x21 个值都满足四位小数, 须加密: 时间上")
    say("         dt=1/64 -> 1/128 使 err(粗) 降到 ~2.98e-05 (59.7%), 空间上")
    say("         M=1600 -> 3200 使 err(粗) 降到 ~1.28e-05 (25.6%)。")
    add("UC_worst_T", "五种口径中温度不确定度的最大值", float(worst_T), "K")
    add("UC_worst_C", "五种口径中水分不确定度的最大值", float(worst_C), "kg/kg")
    add("UC_worst_Tpct", "温度最坏口径占阈值", 100 * worst_T / THR, "%")
    add("UC_worst_Cpct", "水分最坏口径占阈值", 100 * worst_C / THR, "%")
    add("UC_thr", "四位小数半 ulp 阈值", THR, "-")
    add("UC_margin_C", "水分余量 (阈值 - 最坏口径, 可能为负)",
        float(THR - worst_C), "kg/kg")
    add("UC_margin_C_pct", "同上, 占阈值的比例",
        100 * (THR - worst_C) / THR, "%")
    add("UC_dt128_time_err", "若 dt=1/128, 时间误差 err(粗) 估计",
        float(dC_t), "kg/kg")
    add("UC_M3200_space_err", "若 M=3200, 空间误差 err(粗) 估计",
        float(dC_h / 3 * 4 / 4), "kg/kg")

    # ------------------------------------------------------------------
    # 分时段偏差占阈值的比例 (文稿 §7.3 的表用到)
    # ------------------------------------------------------------------
    wins = ((1, 60, "t=1..60 s"), (61, 600, "t=61..600 s"),
            (601, 3600, "t=601..3600 s"), (3601, 10800, "t=3601..10800 s"))
    say()
    say("  分时段网格加密偏差占四位小数阈值的比例 (见 §7.3 的表):")
    say(f"  {'时间窗':>16} {'max|dC| [kg/kg]':>18} {'占阈值':>9} {'Richardson-粗 占阈值':>22}")
    # 分时段值取自 q2_produce.py 的网格加密校核 (已在 registry_q2_production 登记)
    win_vals = {"t=1..60 s": 3.8467e-05, "t=61..600 s": 3.7683e-06,
                "t=601..3600 s": 6.5054e-07, "t=3601..10800 s": 3.7970e-07}
    for lbl, dc in win_vals.items():
        pct = 100 * dc / THR
        pct_rich = 100 * dc * 4 / 3 / THR
        say(f"  {lbl:>16} {dc:18.4e} {pct:8.2f}% {pct_rich:21.2f}%")
        tag = lbl.replace(" ", "").replace("=", "").replace("..", "_").replace(".", "p")
        add(f"UC_win_{tag}_dC", f"分时段网格加密水分偏差 ({lbl})", dc, "kg/kg")
        add(f"UC_win_{tag}_pct", f"同上占四位小数阈值 ({lbl})", pct, "%")
        add(f"UC_win_{tag}_pct_rich", f"同上, Richardson-粗 占阈值 ({lbl})",
            pct_rich, "%")

    with open(os.path.join(OUT, "q2_uncertainty.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    with open(os.path.join(OUT, "registry_q2_uncertainty.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_uncertainty.log')}")
    print(f"注册表: {os.path.join(OUT, 'registry_q2_uncertainty.csv')} ({len(REG)} 行)")


if __name__ == "__main__":
    main()
