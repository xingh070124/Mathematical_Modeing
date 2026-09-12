# -*- coding: utf-8 -*-
"""
q2_convergence.py -- 问题二离散格式的收敛阶与求解器一致性核验 (独立注册表).

为什么单独一个脚本: q2_verify.py 只在整轮跑完后一次性写出注册表, 若用 --only
只跑收敛项会覆盖掉 V3~V11 的全部行. 这里独立产出一个注册表, 供论文引用.

包含:
  * 时间收敛: 固定 M, 把 dt 逐次减半, 取相邻两次解的最大偏差之比;
             比值 -> 2 表示一阶, -> 4 表示二阶 (后向 Euler 预期一阶).
  * 空间收敛: 用常数系数 Robin 圆柱的 Bessel 解析解作基准 (q2_center_node.py
             已跑出的 CN_halfcv_M* 行), 取相邻网格误差之比.
              直接比较变物性问题的 M 与 2M 解会被时间误差污染 ——
              见 registry_q2_verify 的 V2 (dt 减半仅使偏差减半, 说明 dt=1/32 时
              时间误差 2.76e-5 K 大于 M 由 400 到 800 的空间偏差 1.86e-5 K),
              故空间阶数只取"时间误差被压到可忽略"的 Bessel 基准.
  * 求解器一致性: q2_solve 退化到 (附录2 + 半控制体 + 系数冻结 + 无相变) 后与
             独立的 q1_solve 比较.
  * 解析 Jacobian vs 有限差分 (六种配置).

运行: python src/q2_convergence.py [--workers 6]
输出: outputs/q2_convergence.log, outputs/registry_q2_conv.csv
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from q1_solve import Env, load_attachment1, solve_q1  # noqa: E402
from q2_solve import (Par, check_jacobian, march, out_indices)  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
STEP_LOG = os.path.join(OUT, "q2_convergence.log")
REG = []
CMD = "python src/q2_convergence.py"
T_END = 10800.0


def say(s=""):
    print(s, flush=True)
    with open(STEP_LOG, "a", encoding="utf-8") as f:
        f.write(str(s) + "\n")


def add(id_, q, v, u="", unc="", note=""):
    vs = f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v)
    REG.append([id_, q, vs, u, unc, "q2_convergence.py", CMD, note])
    return v


def _worker(cfg):
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    par = Par(**cfg.get("par", {}))
    M = cfg["M"]
    idx = (np.arange(M + 1) if cfg.get("full_idx") else out_indices(M))
    o = march(M, cfg["dt"], cfg["t_end"], env, par, out_idx=idx)
    return cfg["tag"], o


def run_jobs(cfgs, workers=6):
    from concurrent.futures import ProcessPoolExecutor
    t0 = time.time()
    res = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for tag, o in ex.map(_worker, cfgs):
            res[tag] = o
    say(f"  [并行 {len(cfgs)} 个算例, {workers} 进程, 用时 {time.time()-t0:.1f} s]")
    return res


def read_reg(path):
    d = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            try:
                d[r["id"]] = float(r["value"])
            except (TypeError, ValueError):
                pass
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    open(STEP_LOG, "w", encoding="utf-8").close()

    say("=" * 92)
    say("问题二: 收敛阶 / 求解器一致性 / Jacobian 核验")
    say("=" * 92)
    say(f"Python {sys.version.split()[0]}, numpy {np.__version__}, "
        f"t_end={T_END:.0f} s, 输出 21 个半径")

    # ---------------- 时间收敛 ----------------
    dts = [1.0 / 8, 1.0 / 16, 1.0 / 32]
    cfgs = [dict(tag=f"t{int(round(1/dt))}", M=400, dt=dt, t_end=T_END) for dt in dts]
    res = run_jobs(cfgs, args.workers)
    say("")
    say("V-T  时间收敛阶 (固定 M=400, t_end=10800 s, 后向 Euler 预期一阶)")
    say("     相邻两次解之差 |U(dt/2)-U(dt)|, 以及相邻两个差之比 -> 2 即一阶")
    say(f"  {'dt / s':>10s} {'max|dT| / K':>16s} {'max|dC| / kg/kg':>20s} "
        f"{'比 T':>8s} {'比 C':>8s}")
    diffs = []
    prevT = prevC = None
    for dt in dts:
        o = res[f"t{int(round(1/dt))}"]
        if prevT is None:
            say(f"  {dt:10.6f} {'-':>16s} {'-':>20s} {'-':>8s} {'-':>8s}")
            add(f"VT_ref_dt{int(round(1/dt))}", "时间收敛的最粗网格基准解",
                f"dt=1/{int(round(1/dt))} s", "-", "-", "作为下一次比较的基准")
        else:
            dT = float(np.max(np.abs(o["T_snap"] - prevT)))
            dC = float(np.max(np.abs(o["C_snap"] - prevC)))
            diffs.append((dt, dT, dC))
            rT = diffs[-2][1] / dT if len(diffs) > 1 else float("nan")
            rC = diffs[-2][2] / dC if len(diffs) > 1 else float("nan")
            say(f"  {dt:10.6f} {dT:16.6e} {dC:20.6e} {rT:8.4f} {rC:8.4f}")
            tag = int(round(1 / dt))
            add(f"VT_dT_{tag}", f"dt 减半到 1/{tag} s 时的温度最大偏差", dT, "K",
                "时间收敛")
            add(f"VT_dC_{tag}", f"dt 减半到 1/{tag} s 时的水分最大偏差", dC, "kg/kg",
                "时间收敛")
            if len(diffs) > 1:
                add(f"VT_ratio_T_{tag}", "温度偏差之比 (相邻 dt)", rT, "-",
                    "时间收敛", "比值 -> 2 为一阶")
                add(f"VT_ratio_C_{tag}", "水分偏差之比 (相邻 dt)", rC, "-",
                    "时间收敛", "比值 -> 2 为一阶")
                add(f"VT_order_T_{tag}", "温度观测阶 log2(比值)", float(np.log2(rT)),
                    "-", "时间收敛")
                add(f"VT_order_C_{tag}", "水分观测阶 log2(比值)", float(np.log2(rC)),
                    "-", "时间收敛")
        prevT, prevC = o["T_snap"], o["C_snap"]

    # ---------------- 空间收敛 (Bessel 基准) ----------------
    say("")
    say("V-S  空间收敛阶 (常数系数 Robin 圆柱 + Bessel 解析解, 由 q2_center_node.py 产生)")
    say("     直接比较变物性问题的 M 与 2M 会被时间误差污染 (见 q2_verify 的 V2),")
    say("     故空间阶数只取时间误差可忽略的 Bessel 基准.")
    cen = read_reg(os.path.join(OUT, "registry_q2_center.csv"))
    ms = [25, 50, 100, 200, 400, 800]
    say(f"  {'M':>6s} {'max|dT| / K':>16s} {'比 (M/2 -> M)':>16s} {'观测阶':>10s}")
    prev_e = None
    for M in ms:
        key = f"CN_halfcv_M{M}"
        if key not in cen:
            continue
        e = cen[key]
        if prev_e is None:
            say(f"  {M:6d} {e:16.6e} {'-':>16s} {'-':>10s}")
        else:
            r = prev_e / e
            say(f"  {M:6d} {e:16.6e} {r:16.4f} {np.log2(r):10.4f}")
            add(f"VS_ratio_{M}", f"Bessel 基准: M 由 {M//2} 加密到 {M} 的误差之比",
                r, "-", "空间收敛", "比值 -> 4 为二阶")
            add(f"VS_order_{M}", f"Bessel 基准观测阶 (M={M})", float(np.log2(r)), "-",
                "空间收敛")
        add(f"VS_err_M{M}", f"Bessel 基准 M={M} 的最大温度偏差", e, "K",
            "空间收敛", "来源 registry_q2_center")
        prev_e = e

    # ---------------- 与问题一求解器的一致性 ----------------
    say("")
    say("V-0  求解器一致性: q2_solve 退化 (附录2 + 半控制体 + 冻结 + 无相变) vs q1_solve")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    M0, dt0, te0 = 100, 0.01, 600.0
    o = _worker(dict(tag="v0", M=M0, dt=dt0, t_end=te0, full_idx=True,
                     par=dict(mode="app2", boundary="halfcv", frozen=True,
                              hevap="off")))[1]
    r1, Tq1, Cq1, _, _ = solve_q1(M0, dt0, te0, env, corr=True)
    dT0 = float(np.max(np.abs(o["T_snap"][-1] - Tq1)))
    dC0 = float(np.max(np.abs(o["C_snap"][-1] - Cq1)))
    say(f"  M={M0}, dt={dt0} s, t_end={te0:.0f} s (同时刻全场 {M0+1} 个节点)")
    say(f"  max|dT| = {dT0:.6e} K,  max|dC| = {dC0:.6e} kg/kg")
    add("V0_dT", "两套独立实现退化解的最大温度差", dT0, "K", "求解器一致性")
    add("V0_dC", "两套独立实现退化解的最大水分差", dC0, "kg/kg", "求解器一致性")

    # ---------------- Jacobian ----------------
    say("")
    say("V-J  解析 Jacobian vs 有限差分 (M=12)")
    cases = [("default", "默认", Par()),
             ("hevaoff", "H_evap = 0", Par(hevap="off")),
             ("hevaconst", "H_evap = 常数", Par(hevap="const")),
             ("conserv", "守恒形式", Par(energy="conserv")),
             ("halfcv", "halfcv 边界", Par(boundary="halfcv")),
             ("app2", "附录2 物性", Par(mode="app2")),
             ("frozen", "系数冻结", Par(frozen=True))]
    mx = 0.0
    for tag, lbl, p in cases:
        rel = check_jacobian(par=p)
        mx = max(mx, rel)
        say(f"  {lbl:24s} 最大相对偏差 = {rel:.4e}")
        add(f"VJ_{tag}", f"解析 Jacobian vs 有限差分 ({lbl})", float(rel), "-",
            "Jacobian 核验")
    add("VJ_max", "六种配置的最大相对偏差", float(mx), "-", "Jacobian 核验")

    # ---------------- 论文中引用的派生量 ----------------
    say("")
    say("V-M  论文引用的派生量 (可复算)")
    R_U = 8.314462618          # CODATA 2018 通用气体常数 J/(mol K)
    M_W = 0.01801528           # 水的摩尔质量 kg/mol
    R_V = R_U / M_W
    say(f"  水蒸气比气体常数 R_v = R_u/M_w = {R_U}/{M_W} = {R_V:.4f} J/(kg K)")
    add("VM_Ru", "通用气体常数 R_u (CODATA 2018)", R_U, "J/(mol K)", "定义值")
    add("VM_Mw", "水的摩尔质量 M_w", M_W, "kg/mol", "定义值")
    add("VM_Rv", "水蒸气比气体常数 R_v = R_u/M_w", R_V, "J/(kg K)", "解析")

    # 轴向热影响穿透深度 (与问题一同一判据)
    k0, rho0, cp0 = 0.48295774647887, 976.4, 3415.2957746479
    alpha0 = k0 / (rho0 * cp0)
    for te, uq in ((1800.0, "问题一"), (10800.0, "问题二")):
        dz = np.sqrt(alpha0 * te) * 100.0
        say(f"  alpha(C0)={alpha0:.6e} m^2/s, t={te:.0f} s ({uq}) 时 "
            f"sqrt(alpha t) = {dz:.4f} cm")
        add(f"VM_zpen_{int(te)}", f"sqrt(alpha(C0)*t) @ t={te:.0f} s ({uq})", float(dz),
            "cm", "解析", "轴向热影响穿透深度")
    add("VM_alpha_C0", "heat alpha(C0) = k/(rho cp), 附录3", float(alpha0), "m^2/s",
        "解析", "与 registry_q2_model 的 A_alpha_2.55 一致")

    # 3 h 时表面与环境的浓度比
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(OUT, "result2.xlsx"), data_only=True, read_only=True)
    rows = list(wb["水分浓度"].iter_rows(values_only=True))
    wb.close()
    C_R_end = float(rows[-1][-1])
    C_inf_end = env.C(T_END)
    say(f"  3 h: C(R)={C_R_end:.6f} kg/kg, C_inf={C_inf_end:.6f} kg/kg, "
        f"比值 = {C_R_end/C_inf_end:.4f}")
    add("VM_CR_end", "t=10800 s 表面含水率 (result2.xlsx)", C_R_end, "kg/kg",
        "生产解", "与 X_C_10800_2 一致")
    add("VM_Cinf_end", "t=10800 s 环境含水率", float(C_inf_end), "kg/kg", "附件1")
    add("VM_CR_over_Cinf", "3 h 表面含水率与环境含水率之比", float(C_R_end / C_inf_end),
        "-", "解析")

    # 表面对流驱动力 (说明蒸发份额上升的原因)
    wb = load_workbook(os.path.join(OUT, "result2.xlsx"), data_only=True, read_only=True)
    rowsT = list(wb["温度"].iter_rows(values_only=True))
    wb.close()
    say(f"  {'t / s':>8s} {'T_inf / C':>11s} {'T_R / C':>10s} {'驱动 / K':>10s}")
    for tsec in (1800, 3600, 5400, 7200, 9000, 10800):
        TinC = env.T(float(tsec)) - 273.15
        TR = float(rowsT[tsec][-1])
        say(f"  {tsec:8d} {TinC:11.5f} {TR:10.5f} {TinC-TR:10.5f}")
        add(f"VM_drive_{tsec}", f"t={tsec} s 表面对流驱动力 T_inf-T_R", float(TinC - TR),
            "K", "由 result2 与附件1")
    add("VM_qconv_decay", "q_conv 由 0.5 h 到 3 h 的衰减倍数",
        3.09995 / 0.1531, "-", "解析", "取自 registry_q2_figures 的 FG_qconv_*")

    # 论文明细表中引用的比值与派生量 (由既有注册表复算)
    ver = read_reg(os.path.join(OUT, "registry_q2_verify.csv"))
    fig = read_reg(os.path.join(OUT, "registry_q2_figures.csv"))
    cen = read_reg(os.path.join(OUT, "registry_q2_center.csv"))
    mdl = read_reg(os.path.join(OUT, "registry_q2_model.csv"))
    pairs = [("V1_T_200_400", "V1_T_400_800", "空间加密温度偏差之比 (200->400 vs 400->800)"),
             ("V1_C_200_400", "V1_C_400_800", "空间加密水分偏差之比 (200->400 vs 400->800)")]
    for a, b, q in pairs:
        if a in ver and b in ver:
            r = ver[a] / ver[b]
            say(f"  {q} = {r:.6f}")
            add(f"VM_ratio_{a}", q, float(r), "-", "由注册表复算")
    for a, b, q in (("V2_T_0.0625_0.03125", "V2_T_0.03125_0.015625",
                     "时间加密温度偏差之比 (1/16 vs 1/32 s)"),
                    ("V2_C_0.0625_0.03125", "V2_C_0.03125_0.015625",
                     "时间加密水分偏差之比 (1/16 vs 1/32 s)")):
        if a in ver and b in ver:
            r = ver[a] / ver[b]
            say(f"  {q} = {r:.6f}")
            add(f"VM_ratio_{a}", q, float(r), "-", "由注册表复算")
    if "V0_dT" in read_reg(os.path.join(OUT, "registry_q2_conv.csv")):
        pass
    # 守恒形式与非保守形式的中心温度之差
    if "FG_T0_cs" in fig and "FG_T0_nc" in fig:
        d = fig["FG_T0_cs"] - fig["FG_T0_nc"]
        say(f"  守恒与非保守的中心温度之差 (t=10800 s) = {d:.6f} K")
        add("VM_dT0_conserv", "守恒与非保守形式的中心温度之差 (t=10800 s, M=200)",
            float(d), "K", "由注册表复算")
    # 求解器一致性所用节点数
    add("VM_V0_nodes", "求解器一致性比较所用节点数 (M=100)", 101, "-", "结构")
    # 集中质量 vs 半控制体的误差比 (Bessel 基准)
    for M in (25, 50, 100, 200, 400, 800):
        k1, k2 = f"CN_lumped_M{M}", f"CN_halfcv_M{M}"
        if k1 in cen and k2 in cen:
            r = cen[k1] / cen[k2]
            add(f"VM_lump_ratio_M{M}", f"集中质量/半控制体 的 Bessel 偏差之比 (M={M})",
                float(r), "-", "由注册表复算")
    if all(f"CN_halfcv_M{m}" in cen for m in (25, 200)):
        r1 = cen["CN_lumped_M25"] / cen["CN_halfcv_M25"]
        r2 = cen["CN_lumped_M200"] / cen["CN_halfcv_M200"]
        say(f"  集中质量/半控制体 误差比: M=25 时 {r1:.2f}, M=200 时 {r2:.2f}")
        add("VM_lump_range_lo", "集中质量/半控制体 误差比的下界 (M=200)", float(r2), "-",
            "由注册表复算")
        add("VM_lump_range_hi", "集中质量/半控制体 误差比的上界 (M=25)", float(r1), "-",
            "由注册表复算")
    # 3 h / 湿分特征时间
    if "C_tauC" in mdl:
        r = T_END / mdl["C_tauC"]
        say(f"  3 h / R^2/D(C0,T0) = {r:.6f}")
        add("VM_frac_tauC", "3 h 占湿分特征时间 R^2/D(C0,T0) 的比例", float(r), "-",
            "由注册表复算")
    # 干燥前沿判别值
    add("VM_Cfront", "干燥前沿判别值 C = 0.9*C0", 0.9 * 2.55, "kg/kg", "解析")

    # M=3200 上 t=1 s 的表面剖面 (说明水分边界层的网格跨越度)
    say("")
    say("V-P  M=3200, t=1 s 的表面剖面 (节点序号自 0=表面 起算)")
    o = march(3200, 1.0 / 64, 1.0, env, Par(), out_idx=np.arange(3201))
    prof = o["C_snap"][-1]
    for k in range(9):
        say(f"   k={k}  C = {prof[3200 - k]:.7f}")
        add(f"VP_M3200_k{k}", f"M=3200, t=1 s, 自表面向内第 {k} 号节点的 C",
            float(prof[3200 - k]), "kg/kg", "剖面复算")
    md = read_reg(os.path.join(OUT, "registry_q2_moist_diag.csv"))
    for k in (0, 8):
        key = f"MD_prof_M3200_k{k}"
        if key in md:
            dd = abs(prof[3200 - k] - md[key])
            say(f"   与 {key} ({md[key]:.7f}) 之差 = {dd:.3e} kg/kg")
            add(f"VP_M3200_k{k}_vs_diag", f"k={k} 与 q2_moist_diag 之差 (时间步口径不同)",
                float(dd), "kg/kg", "口径对照")
    add("VP_M3200_k0_k8_gap", "M=3200, t=1 s: 表面到第 8 号节点的 C 落差",
        float(prof[3200] - prof[3192]), "kg/kg", "剖面复算")

    with open(os.path.join(OUT, "registry_q2_conv.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source",
                    "command", "note"])
        w.writerows(REG)
    say("")
    say(f"注册表: outputs/registry_q2_conv.csv ({len(REG)} 行)")


if __name__ == "__main__":
    main()
