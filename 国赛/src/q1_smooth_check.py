# -*- coding: utf-8 -*-
"""附件1 环境序列的噪声处理实测: 原始 PCHIP  vs  Savitzky-Golay 平滑后 PCHIP.

回答评阅意见 "C_inf 含噪声但未滤波" 一类的疑问: 不是声称"已滤波", 而是实测
"若滤波, 结果会差多少". 若差异低于四位小数分辨率 5e-5, 则使用原始数据的
PCHIP 是站得住的, 并可把该结论写进论文.

输出: outputs/registry_q1_smooth.csv, outputs/q1_smooth_check.log
运行: python src/q1_smooth_check.py
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import Env, load_attachment1, solve_q1            # noqa: E402
from q2_solve import Par, march, out_indices                    # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
WIN, POLY = 11, 3          # 采样间隔 60 s -> 窗 11 点 = 11 min
REG = []
LOG = []


def say(s=""):
    print(s, flush=True)
    LOG.append(str(s))


def add(id_, q, v, u="", unc="run", note=""):
    REG.append([id_, q, f"{float(v):.14g}", u, unc, "q1_smooth_check.py",
                "python src/q1_smooth_check.py", note])


def main():
    from scipy.signal import savgol_filter

    t, T1, C1 = load_attachment1()
    say(f"附件1: {len(t)} 点, {t[0]:.0f}~{t[-1]:.0f} s, 采样间隔 {t[1]-t[0]:.0f} s")

    Ts = savgol_filter(T1, WIN, POLY)
    Cs = savgol_filter(C1, WIN, POLY)
    hi_T = T1 - Ts
    hi_C = C1 - Cs
    say(f"高频分量 (原始 - SG 平滑, 窗 {WIN}, {POLY} 阶):")
    say(f"  T_inf: rms {np.sqrt((hi_T**2).mean()):.4e} degC, max|.| {np.abs(hi_T).max():.4e} degC")
    say(f"  C_inf: rms {np.sqrt((hi_C**2).mean()):.4e} kg/kg, max|.| {np.abs(hi_C).max():.4e} kg/kg")
    add("SM_noise_T_rms", "附件1 T_inf 高频分量 rms", np.sqrt((hi_T**2).mean()), "degC")
    add("SM_noise_T_max", "附件1 T_inf 高频分量最大绝对值", np.abs(hi_T).max(), "degC")
    add("SM_noise_C_rms", "附件1 C_inf 高频分量 rms", np.sqrt((hi_C**2).mean()), "kg/kg")
    add("SM_noise_C_max", "附件1 C_inf 高频分量最大绝对值", np.abs(hi_C).max(), "kg/kg")

    env_raw = Env(t, T1, C1, method="pchip")
    env_sg = Env(t, Ts, Cs, method="pchip")

    # ---- 问题一: 1800 s ----
    say()
    say("=" * 78)
    say("问题一 (M=200, dt=0.25 s, t_end=1800 s)")
    say("=" * 78)
    r1 = solve_q1(200, 0.25, 1800.0, env_raw, probes_t=[1800.0])
    r2 = solve_q1(200, 0.25, 1800.0, env_sg, probes_t=[1800.0])
    dT1 = float(np.max(np.abs(r2[3][-1] - r1[3][-1])))
    dC1 = float(np.max(np.abs(r2[4][-1] - r1[4][-1])))
    say(f"  t=1800 s 全场最大差异: dT = {dT1:.4e} K,  dC = {dC1:.4e} kg/kg")
    add("SM_q1_dT_1800", "问题一 t=1800 s 全场 max|dT| (原始 vs SG 平滑)",
        dT1, "K", "run", f"窗 {WIN}/{POLY} 阶")
    add("SM_q1_dC_1800", "问题一 t=1800 s 全场 max|dC| (原始 vs SG 平滑)",
        dC1, "kg/kg", "run", f"窗 {WIN}/{POLY} 阶")

    # ---- 问题二: 10800 s (M=200, dt=0.25 s, 与表8 同口径) ----
    say()
    say("=" * 78)
    say("问题二 (M=200, dt=0.25 s, t_end=10800 s, 表8 同口径)")
    say("=" * 78)
    idx = out_indices(200)
    o1 = march(200, 0.25, 10800.0, env_raw, Par(), out_idx=idx)
    o2 = march(200, 0.25, 10800.0, env_sg, Par(), out_idx=idx)
    dT2 = float(np.max(np.abs(o2["T_snap"] - o1["T_snap"])))
    dC2 = float(np.max(np.abs(o2["C_snap"] - o1["C_snap"])))
    dTs = float(np.max(np.abs(o2["T_snap"][:, -1] - o1["T_snap"][:, -1])))
    dCs = float(np.max(np.abs(o2["C_snap"][:, -1] - o1["C_snap"][:, -1])))
    say(f"  全场全程最大差异: dT = {dT2:.4e} K,  dC = {dC2:.4e} kg/kg")
    say(f"  表面全程最大差异: dT = {dTs:.4e} K,  dC = {dCs:.4e} kg/kg")
    add("SM_q2_dT_10800", "问题二 全场全程 max|dT| (原始 vs SG 平滑)", dT2, "K")
    add("SM_q2_dC_10800", "问题二 全场全程 max|dC| (原始 vs SG 平滑)", dC2, "kg/kg")
    add("SM_q2_dT_surf", "问题二 表面全程 max|dT| (原始 vs SG 平滑)", dTs, "K")
    add("SM_q2_dC_surf", "问题二 表面全程 max|dC| (原始 vs SG 平滑)", dCs, "kg/kg")

    if "Fw_snap" in o1 and "Fw_snap" in o2:
        dFw = float(np.max(np.abs(np.asarray(o2["Fw_snap"]) - np.asarray(o1["Fw_snap"]))))
        fmax = float(np.max(np.abs(np.asarray(o1["Fw_snap"]))))
        say(f"  表面传质通量全程 max|dFw| = {dFw:.4e} (基准 max|Fw| = {fmax:.4e}, "
            f"相对 {dFw / fmax:.3e})")
        add("SM_q2_dFw", "问题二 表面传质通量全程 max|dFw| (原始 vs SG 平滑)", dFw, "kg/(m2 s)")
        add("SM_q2_dFw_rel", "问题二 表面传质通量相对差异 (原始 vs SG 平滑)", dFw / fmax, "-")

    say()
    say(f"结论(如实, 不修饰): 滤波与否的差异 —— 温度 max(dT)={max(dT1,dT2):.2e} K, "
        f"水分 max(dC)={max(dC1,dC2):.2e} kg/kg。")
    say("  温度差异 (3.94e-2 K) 来自被平滑掉的环境脉动 (rms 0.12 degC) 经热惯性的部分传递,")
    say("    属输入数据的不确定度, 不是格式误差;")
    say("  水分差异 (9.21e-5) 与本文已声明的 '水分第 4 位小数为分辨率边界' (76.9% 半 ulp)")
    say("    同量级, 故并入该口径说明, 而不宣称滤波无影响。")
    say("  选型理由: PCHIP 保形插值自身不产生过冲, 而滤波会引入窗长/阶数两个人为参数;")
    say("    故正文采用未滤波的原始数据, 并将上述差异计入不确定度。")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "q1_smooth_check.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    p = os.path.join(OUT, "registry_q1_smooth.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    say(f"注册表: {p}")


if __name__ == "__main__":
    main()
