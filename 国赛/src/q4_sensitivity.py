# -*- coding: utf-8 -*-
"""
q4_sensitivity.py -- 问题四灵敏度与鲁棒性检验.

单因素 (OAT):
  G1 h_m, h            : 表面传质/换热系数 (附录2 未为问题四另给, 属假设 D5)
  G2 附录4 物性系数     : rho0,krho,cp0,kcp,k0,kk, D0,kD, EA 各 ±10%
  G3 汽化潜热 L_v      : ±10% (由热力学关系导出, 非题面给定)
  G4 收缩律 R(t)       : 整体幅值 ±10%, 冻结收缩 (已在 q4_verify V6)
  G5 收缩模式 eta      : 0(仿射) / 1(边缘收缩) / -1(除表面通量外忽略)
  G6 环境外推          : Tbar ±1 degC, Cbar ±10% 与 ±20%
  G7 阈值 C*           : 0.15 -> 0.10 / 0.20 (判据的口径不确定度)

蒙特卡洛 (9 个物性系数同时均匀 ±5%, 及 ±10%), 固定随机种子。

输出: outputs/q4_sensitivity.log 与 outputs/registry_q4_sens.csv
"""

from __future__ import annotations

import csv
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (solve_q4, P4, APP, PROD_M, PROD_RTOL, PROD_ATOL_T,   # noqa: E402
                      PROD_ATOL_C, PROD_MAX_STEP, Q4Radius, load_attachment2)
from q3_solve import TBAR_C, CBAR                                    # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
BASE = None
LOG = []
ROWS = []

P4_KEYS = ["rho0", "krho", "cp0", "kcp", "k0", "kk", "D0", "kD", "EA"]


def say(m):
    print(m, flush=True)
    LOG.append(m)


def run(tag, note, **kw):
    """跑一个配置, 返回 t_dry; 未达标返回 None."""
    t0 = time.time()
    try:
        r = solve_q4(M=PROD_M, **kw)
        td = r["t_dry"]
        add = "" if BASE is None else f"  ({td - BASE:+.1f} s = {(td-BASE)/3600:+.4f} h)"
        say(f"  {tag:34s} {td:14.4f} s = {td/3600:9.4f} h{add}")
        ROWS.append((tag, note, td, "s", f"{td/3600:.4f}", "outputs/q4_sensitivity.log"))
        return td
    except RuntimeError as e:
        say(f"  {tag:34s} 未达标 (3 天安全网内无终止事件)")
        ROWS.append((tag, note + " [未达标]", float("nan"), "s", "nan",
                     "outputs/q4_sensitivity.log"))
        return None


def scaled_p4(fac):
    """按倍率缩放全部 9 个物性系数."""
    return {k: P4[k] * fac for k in P4_KEYS}


def main():
    global BASE
    os.makedirs(OUTDIR, exist_ok=True)
    say("=" * 78)
    say("问题四灵敏度与鲁棒性检验 (q4_sensitivity.py)")
    say("=" * 78)
    say(f"基准配置: M={PROD_M}, rtol={PROD_RTOL:g}, max_step={PROD_MAX_STEP:g} s, 附录4, R(t)=附件2")

    say("\n[基准]")
    BASE = run("BASE", "生产基准")
    say(f"  -> t_dry = {BASE:.4f} s = {BASE/3600:.4f} h")

    # ---------------- G1 h_m / h ----------------
    say("\n[G1] 表面传质系数 h_m 与换热系数 h (假设 D5)")
    for f in (0.5, 0.8, 1.2, 2.0, 1.0e3):
        run(f"G1_hm_x{f:g}", f"h_m x {f:g}", hm=8.0e-7 * f)
    for f in (0.5, 0.8, 1.2, 2.0):
        run(f"G1_h_x{f:g}", f"h x {f:g}", hc=25.0 * f)

    # ---------------- G2 物性系数单因素 ----------------
    say("\n[G2] 附录4 物性系数单因素 ±10%")
    for k in P4_KEYS:
        for f, lab in ((1.1, "+10%"), (0.9, "-10%")):
            p = dict(P4)
            p[k] = P4[k] * f
            run(f"G2_{k}_{lab}", f"附录4 {k} {lab}", params=p)

    # ---------------- G3 汽化潜热 ----------------
    say("\n[G3] 汽化潜热 L_v")
    for f in (0.9, 1.1):
        run(f"G3_Lv_x{f:g}", f"L_v x {f:g}", lv_mult=f)
    run("G3_Lv_off", "L_v = 0 (忽略蒸发吸热)", hevap=False)

    # ---------------- G4 收缩律幅值 ----------------
    say("\n[G4] 收缩律 R(t) 幅值")
    for f in (0.9, 0.95, 1.05, 1.1):
        run(f"G4_R_x{f:g}", f"R(t) x {f:g}", rad_scale=f)
    run("G4_R_const", "R = const (冻结收缩)", rad_mode="const")

    # ---------------- G5 收缩模式 ----------------
    say("\n[G5] 收缩模式参数 eta  (几何增强因子 phi=(R0/R)^(2 eta))")
    t5 = {}
    for tag, lab, e in (("G5_eta_0", "eta = 0 (仿射收缩, 本文模型)", 0.0),
                        ("G5_eta_p1", "eta = +1 (边缘收缩)", 1.0),
                        ("G5_eta_m1", "eta = -1 (除表面通量外忽略收缩)", -1.0)):
        t5[tag] = run(tag, lab, eta=e)
        if t5[tag] is not None:
            ROWS.append((f"{tag}_h", lab + " 的 t_dry", t5[tag] / 3600.0, "h",
                         f"{t5[tag]/3600:.4f}", "outputs/q4_sensitivity.log"))

    # ---------------- G6 环境外推 ----------------
    say("\n[G6] 环境长期外推")
    for dT in (-1.0, 1.0):
        run(f"G6_Tbar{dT:+.0f}", f"Tbar {dT:+.0f} degC", Tbar_C=TBAR_C + dT)
    for f in (0.8, 0.9, 1.1, 1.2):
        run(f"G6_Cbar_x{f:g}", f"Cbar x {f:g}", Cbar=CBAR * f)

    # ---------------- G7 阈值 ----------------
    say("\n[G7] 达标阈值口径")
    for c in (0.10, 0.12, 0.18, 0.20):
        run(f"G7_Cstar_{c:g}", f"C* = {c:g} kg/kg", cstar=c)

    # ---------------- 蒙特卡洛 ----------------
    # 注意: 积分上界放宽到 10 天, 使绝大多数样本都能触达终止事件,
    # 从而给出**未被 3 天安全网截断**的分布; 同时报告超过 3 天的比例.
    say("\n[MC] 蒙特卡洛: 9 个附录4 系数同时均匀扰动 (积分上界 10 天)")
    TMAX_MC = 864000.0
    for lev, N, seed in ((0.05, 100, 2026), (0.10, 100, 2026)):
        rng = np.random.default_rng(seed)
        ts, over3 = [], 0
        for i in range(N):
            f = 1.0 + lev * (2.0 * rng.random(len(P4_KEYS)) - 1.0)
            p = {k: P4[k] * fi for k, fi in zip(P4_KEYS, f)}
            try:
                r = solve_q4(M=PROD_M, params=p, t_max=TMAX_MC)
                ts.append(r["t_dry"])
                if r["t_dry"] > 259200.0:
                    over3 += 1
            except RuntimeError:
                pass
        ts = np.array(ts)
        q = np.percentile(ts, [2.5, 50, 97.5])
        # 自助法给出分位数自身的抽样不确定度 (审计意见: N=100 时 95% 区间是
        # 有噪声的样本分位区间, 不应作为精确的 95% 区间陈述)
        rngb = np.random.default_rng(seed + 1)
        B = 2000
        boot = np.array([np.percentile(rngb.choice(ts, size=ts.size, replace=True),
                                       [2.5, 97.5]) for _ in range(B)])
        lo_ci = np.percentile(boot[:, 0], [2.5, 97.5])
        hi_ci = np.percentile(boot[:, 1], [2.5, 97.5])
        say(f"  ±{lev*100:.0f}%: {ts.size}/{N} 在 10 天内达标; 其中 {over3} 个超过 3 天"
            f" ({100.0*over3/N:.0f} % 的样本)")
        say(f"        均值 {ts.mean()/3600:.3f} h, 标准差 {ts.std(ddof=1)/3600:.3f} h,"
            f" 中位数 {q[1]/3600:.3f} h")
        say(f"        样本分位区间 [{q[0]/3600:.3f}, {q[2]/3600:.3f}] h"
            f" (N={N}, 右删失上界 10 天)")
        say(f"        其中上分位的自助法 95% 置信区间 "
            f"[{hi_ci[0]/3600:.3f}, {hi_ci[1]/3600:.3f}] h  <- 分位数自身的不确定度")
        ROWS.append((f"MC{int(lev*100)}_p97p5_lo", f"MC ±{lev*100:.0f}% 上分位的自助下界",
                     float(hi_ci[0]), "s", f"{hi_ci[0]/3600:.4f}",
                     "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_p97p5_hi", f"MC ±{lev*100:.0f}% 上分位的自助上界",
                     float(hi_ci[1]), "s", f"{hi_ci[1]/3600:.4f}",
                     "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_n", f"MC ±{lev*100:.0f}% 达标样本数",
                     float(ts.size), "1", "-", "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_over3", f"MC ±{lev*100:.0f}% 超过 3 天的样本数",
                     float(over3), "1", "-", "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_mean", f"MC ±{lev*100:.0f}% 均值", ts.mean(),
                     "s", f"{ts.mean()/3600:.4f}", "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_median", f"MC ±{lev*100:.0f}% 中位数", q[1],
                     "s", f"{q[1]/3600:.4f}", "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_std", f"MC ±{lev*100:.0f}% 标准差",
                     ts.std(ddof=1), "s", f"{ts.std(ddof=1)/3600:.4f}",
                     "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_p2p5", f"MC ±{lev*100:.0f}% 2.5% 分位",
                     float(q[0]), "s", f"{q[0]/3600:.4f}", "outputs/q4_sensitivity.log"))
        ROWS.append((f"MC{int(lev*100)}_p97p5", f"MC ±{lev*100:.0f}% 97.5% 分位",
                     float(q[2]), "s", f"{q[2]/3600:.4f}", "outputs/q4_sensitivity.log"))

    # ---------------- 汇总 ----------------
    say("\n[汇总] 相对基准的影响幅度 (只统计已达标的单因素扰动)")
    sens = {}
    for tag, note, val, *_ in ROWS:
        if not tag.startswith(("G1_", "G2_", "G3_", "G4_", "G5_", "G6_", "G7_")):
            continue
        if tag.endswith("_h") or np.isnan(val):
            continue
        sens[tag] = abs(val - BASE) / 3600.0
    for k, v in sorted(sens.items(), key=lambda x: -x[1])[:12]:
        say(f"  {k:34s} |dt_dry| = {v:8.4f} h")
    if sens:
        say(f"  单因素最大影响: {max(sens.values()):.4f} h "
            f"({max(sens, key=sens.get)})")

    with open(os.path.join(OUTDIR, "registry_q4_sens.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "value_h", "source"])
        w.writerow(["BASE", "基准 t_dry", repr(float(BASE)), "s",
                    f"{BASE/3600:.4f}", "outputs/q4_sensitivity.log"])
        for r in ROWS:
            w.writerow([r[0], r[1], repr(float(r[2])), r[3], r[4], r[5]])
    say(f"\n写出: outputs/registry_q4_sens.csv ({len(ROWS)+1} 行)")
    with open(os.path.join(OUTDIR, "q4_sensitivity.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
