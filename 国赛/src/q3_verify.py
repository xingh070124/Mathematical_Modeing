# -*- coding: utf-8 -*-
"""
q3_verify.py -- 问题三数值验证 (problem3.md §12 的 W1~W10).

    W1  空间收敛性      M=100/200/400 (rtol=1e-9) -> 收敛阶 + Richardson 外推
    W2  时间容限收敛性  rtol=1e-7 vs 1e-9 (M=200 与 M=400)
    W3  步长上界敏感性  max_step = 600/1800/3600 s
    W4  与问题二交叉验证 0~14400 s 上 BDF vs 问题二后向 Euler (M=200, dt=0.25/0.125)
    W5  Jacobian 提供方式 解析稀疏 vs jac_sparsity 分组差分 vs 全稠密差分
    W6  积分器交叉验证  Radau / LSODA vs BDF
    W7  环境外推敏感性  Tbar +/-1 degC; Cbar +/-10%; 过渡段 0/600/1800 s
    W8  极值原理与守恒  C 包络 / 单调性 / 水量收支残差
    W9  最大值位置诊断  argmax_i C_i(t) 全过程
    W10 阈值附近行为    g(t) 单调性 / 单根 / 条件数 |dt/dC|

输出: outputs/q3_verify.log, outputs/registry_q3_verify.csv
运行: python src/q3_verify.py
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q3_solve import (PROD_ATOL_C, PROD_ATOL_T, PROD_MAX_STEP, PROD_M,     # noqa: E402
                      PROD_RTOL, run_case, run_parallel, write_registry)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

T6H = [21600.0 * k for k in range(1, 10)]          # 6..54 h 的公共采样时刻

LOG = []
REG = []


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def radd(id_, q, v, u, unc="", note=""):
    REG.append([id_, q, v, u, unc, "outputs/q3_verify.log",
                "python src/q3_verify.py", note])


def _job_q2(cfg):
    """子进程: 问题二求解器 (后向 Euler) 独立求解 0~14400 s."""
    from q1_solve import Env, load_attachment1
    from q2_solve import Par, march, out_indices
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    t0 = time.time()
    o = march(cfg["M"], cfg["dt"], cfg["t_end"], env, Par(),
              out_idx=out_indices(cfg["M"]),
              out_every_s=cfg.get("out_every", 600.0))
    return dict(tag=cfg["tag"], t=o["t_snap"], C=o["C_snap"], T=o["T_snap"],
                wall=time.time() - t0, nsteps=o["stats"]["nsteps"],
                dt=cfg["dt"])


def _fake_pool(cfgs):
    """--dry 模式: 合成 run_parallel 的返回 (取自真实运行值), 走通后处理代码路径."""
    n60 = 500
    t60 = 60.0 * np.arange(1, n60 + 1)
    tfin = np.linspace(2.0e5, 2.0672e5, 7201)
    base_extra = dict(C60=np.linspace(2.0, 0.05, 21)[None, :] * np.linspace(
        1.0, 0.1, n60)[:, None],
        maxC60=np.linspace(2.5, 0.15, n60), argmax60=np.zeros(n60, dtype=int),
        n60=n60, t60=t60, C_dry=np.linspace(0.15, 0.05, 21),
        T_dry=np.full(21, 323.0), maxC_dry=0.15, argmax_dry=0,
        W0=5.1e-4, W_dry=1.7e-5,
        W60=np.linspace(5.1e-4, 1.7e-5, n60),
        t_flux=np.linspace(0.0, 2.0672e5, 20000),
        flux_w=np.linspace(1.0e-5, 1e-9, 20000),
        t_fin=tfin, maxC_fin=np.linspace(0.16, 0.15, 7201),
        C60_min=0.04, C60_max=2.55)
    tdr = dict(base200=206720.413, M100=206397.931, M400=206857.296,
               M200r7=206720.584, M400r7=206857.473, ms600=206720.382,
               ms1800=206720.397, jac_dense=206720.584, jac_sparse=206720.413,
               radau=206720.382, lsoda=206720.374, w4q3=206720.421,
               s_Tm1=213431.732, s_Tp1=200302.315, s_Cm10=206300.257,
               s_Cp10=207191.838, s_tau0=206720.421, s_tau1800=206720.483)
    out = {}
    for cfg in cfgs:
        d = dict(tag=cfg["tag"], M=cfg.get("M", 200),
                 t_dry=tdr.get(cfg["tag"], 206720.413),
                 nsteps=3299, nfev=8477, njev=326, nlu=1001,
                 wall=2.0, method=cfg.get("method", "BDF"),
                 jac_mode=cfg.get("jac_mode", "analytic"),
                 rtol=cfg.get("rtol", 1e-9), max_step=cfg.get("max_step", 3600.0),
                 status=1)
        if cfg.get("sample", False):
            d.update(base_extra)
        st = cfg.get("sample_times")
        if st is not None:
            d["C_ts"] = np.linspace(2.0, 0.05, 21)[None, :] * np.ones((len(st), 1))
            d["T_ts"] = np.full((len(st), 21), 323.0)
        out[cfg["tag"]] = d
    return out


def main():
    import scipy
    dry = "--dry" in sys.argv
    t_all = time.time()
    say("=" * 96)
    say("问题三数值验证 (W1~W10, problem3.md §12)")
    say(f"环境: python {sys.version.split()[0]}, scipy {scipy.__version__}, "
        f"numpy {np.__version__}")
    say(f"生产配置: M={PROD_M}, rtol={PROD_RTOL:g}, atol=({PROD_ATOL_T:g} K, "
        f"{PROD_ATOL_C:g}), max_step={PROD_MAX_STEP:g} s, tau=600 s")
    say("=" * 96)

    # ------------------------------------------------------------------
    # 阶段 A: 全部 q3 求解 (并行)
    # ------------------------------------------------------------------
    say("")
    say("[阶段 A] BDF 求解组 (12 组并行)")
    base_cfg = dict(tag="base200", M=200, rtol=1e-9, sample=True,
                    sample_times=T6H)
    cfgs = [
        base_cfg,
        dict(tag="M100", M=100, rtol=1e-9, sample_times=T6H),
        dict(tag="M400", M=400, rtol=1e-9, sample_times=T6H),
        dict(tag="M200r7", M=200, rtol=1e-7),
        dict(tag="M400r7", M=400, rtol=1e-7),
        dict(tag="ms600", M=200, rtol=1e-9, max_step=600.0),
        dict(tag="ms1800", M=200, rtol=1e-9, max_step=1800.0),
        dict(tag="jac_dense", M=200, rtol=1e-7, jac_mode="dense"),
        dict(tag="jac_sparse", M=200, rtol=1e-9, jac_mode="sparsity"),
        dict(tag="radau", M=200, rtol=1e-9, method="Radau", max_step=1800.0),
        dict(tag="lsoda", M=200, rtol=1e-9, method="LSODA", max_step=1800.0,
             jac_mode="none"),
        dict(tag="w4q3", M=200, rtol=1e-9, tau=0.0, sample_times=[600.0 * k for k in range(1, 25)]),
        dict(tag="s_Tm1", M=200, rtol=1e-9, Tbar_C=49.0),
        dict(tag="s_Tp1", M=200, rtol=1e-9, Tbar_C=51.0),
        dict(tag="s_Cm10", M=200, rtol=1e-9, Cbar=0.045),
        dict(tag="s_Cp10", M=200, rtol=1e-9, Cbar=0.055),
        dict(tag="s_tau0", M=200, rtol=1e-9, tau=0.0),
        dict(tag="s_tau1800", M=200, rtol=1e-9, tau=1800.0),
    ]
    if dry:
        say("  [--dry 干跑模式: 合成求解结果, 只走后处理代码路径]")
        res = _fake_pool(cfgs)
    else:
        res = run_parallel(cfgs, workers=4)
    base = res["base200"]

    # ------------------------------------------------------------------
    # 阶段 B: W4 的问题二侧 (并行)
    # ------------------------------------------------------------------
    say("")
    say("[阶段 B] 问题二后向 Euler 交叉验证组 (0~14400 s, M=200)")
    q2 = {}
    if not dry:
        from concurrent.futures import ProcessPoolExecutor
        q2cfgs = [dict(tag="q2_dt025", M=200, dt=0.25, t_end=14400.0),
                  dict(tag="q2_dt0125", M=200, dt=0.125, t_end=14400.0)]
        with ProcessPoolExecutor(max_workers=2) as ex:
            for o in ex.map(_job_q2, q2cfgs):
                q2[o["tag"]] = o
                say(f"  [{o['tag']}] dt={o['dt']} s, {o['nsteps']} 步, "
                    f"用时 {o['wall']:.1f} s")
    else:
        from q1_solve import Env as _E  # noqa: F401  (仅为保持 import 一致)
        tq = 600.0 * np.arange(1, 25)
        for tag in ("q2_dt025", "q2_dt0125"):
            q2[tag] = dict(tag=tag, t=tq, C=res["w4q3"]["C_ts"] * 1.0001,
                           T=res["w4q3"]["T_ts"] * 1.0001, wall=90.0,
                           nsteps=57600, dt=0.25 if tag.endswith("025") else 0.125)

    # ------------------------------------------------------------------
    say("")
    say("=" * 96)
    say("W1  空间收敛性 (rtol=1e-9)")
    say("=" * 96)
    t1h, t2h, t4h = (res["M100"]["t_dry"], base["t_dry"], res["M400"]["t_dry"])
    d1, d2 = t2h - t1h, t4h - t2h
    ratio = d1 / d2
    p = np.log2(ratio)
    rich = t4h + d2 / (2.0 ** p - 1.0)
    rich_p1 = t4h + d2
    say(f"  {'M':>5} {'t_dry [s]':>16} {'t_dry [h]':>14} {'步数':>8} {'用时 [s]':>10}")
    for tag, rr in (("100", res["M100"]), ("200", base), ("400", res["M400"])):
        say(f"  {tag:>5} {rr['t_dry']:>16.3f} {rr['t_dry'] / 3600.0:>14.5f} "
            f"{rr['nsteps']:>8d} {rr['wall']:>10.1f}")
    say(f"  d1 (M100->200) = {d1:.3f} s, d2 (M200->400) = {d2:.3f} s")
    say(f"  d1/d2 = {ratio:.4f}  =>  实测收敛阶 p = log2(d1/d2) = {p:.4f}")
    say(f"  Richardson 外推 t* = t(400) + d2/(2^p - 1) = {rich:.1f} s = "
        f"{rich / 3600.0:.4f} h")
    say(f"  保守 p=1 外推       t* = {rich_p1:.1f} s = {rich_p1 / 3600.0:.4f} h")
    # 公共 6 h 时刻的场偏差 (M=200 vs 400)
    C2, C4 = base["C_ts"], res["M400"]["C_ts"]
    T2, T4 = base["T_ts"], res["M400"]["T_ts"]
    dC6 = float(np.max(np.abs(C2 - C4)))
    dT6 = float(np.max(np.abs(T2 - T4)))
    say(f"  6 h 采样时刻 (6..54 h x 21 半径) 的相邻网格最大偏差: "
        f"max|dC| = {dC6:.4e} kg/kg, max|dT| = {dT6:.4e} K")
    for tag, rr in (("M100", res["M100"]), ("M200", base), ("M400", res["M400"])):
        if rr.get("maxC_dry") is not None:
            say(f"  事件一致性 [{tag}]: max_i C_i(t_dry) - C* = "
                f"{rr['maxC_dry'] - 0.15:.2e}")
    for i, (id_, v, u) in enumerate([
            ("V1_M100", t1h, "s"), ("V1_M200", t2h, "s"), ("V1_M400", t4h, "s"),
            ("V1_M100_h", t1h / 3600, "h"), ("V1_M200_h", t2h / 3600, "h"),
            ("V1_M400_h", t4h / 3600, "h"),
            ("V1_d1", d1, "s"), ("V1_d2", d2, "s"), ("V1_ratio", ratio, "-"),
            ("V1_order", p, "-"), ("V1_richardson", rich, "s"),
            ("V1_richardson_h", rich / 3600, "h"),
            ("V1_richardson_p1", rich_p1, "s"),
            ("V1_dC_200_400", dC6, "kg/kg"), ("V1_dT_200_400", dT6, "K")]):
        radd(id_, "W1 " + ["t_dry M=100", "t_dry M=200(生产)", "t_dry M=400",
                           "t_dry M=100", "t_dry M=200(生产)", "t_dry M=400",
                           "相邻网格差 d1", "相邻网格差 d2", "差分比 d1/d2",
                           "实测空间收敛阶", "Richardson 外推 t_dry",
                           "Richardson 外推 t_dry", "p=1 保守外推 t_dry",
                           "6h 时刻 M200-400 最大水分偏差",
                           "6h 时刻 M200-400 最大温度偏差"][i], v, u)

    say("")
    say("=" * 96)
    say("W2  时间容限收敛性 (rtol=1e-7 vs 1e-9)")
    say("=" * 96)
    dt2 = res["M200r7"]["t_dry"] - base["t_dry"]
    dt4 = res["M400r7"]["t_dry"] - res["M400"]["t_dry"]
    say(f"  M=200: rtol=1e-7 -> {res['M200r7']['t_dry']:.3f} s, "
        f"rtol=1e-9 -> {base['t_dry']:.3f} s, 差 {dt2:+.3f} s")
    say(f"  M=400: rtol=1e-7 -> {res['M400r7']['t_dry']:.3f} s, "
        f"rtol=1e-9 -> {res['M400']['t_dry']:.3f} s, 差 {dt4:+.3f} s")
    say(f"  通过标准 (差 < 1 s): {'OK' if max(abs(dt2), abs(dt4)) < 1.0 else '!!'}")
    radd("V2_M200_diff", "W2 M=200 rtol 1e-7 与 1e-9 的 t_dry 差", dt2, "s")
    radd("V2_M400_diff", "W2 M=400 rtol 1e-7 与 1e-9 的 t_dry 差", dt4, "s")

    say("")
    say("=" * 96)
    say("W3  步长上界敏感性 (max_step = 600/1800/3600 s, M=200, rtol=1e-9)")
    say("=" * 96)
    for tag, ms in (("ms600", 600.0), ("ms1800", 1800.0)):
        dms = res[tag]["t_dry"] - base["t_dry"]
        say(f"  max_step={ms:>6.0f} s: t_dry = {res[tag]['t_dry']:.3f} s "
            f"({res[tag]['nsteps']} 步), 与 3600 s 差 {dms:+.3f} s")
        radd(f"V3_{tag}_diff", f"W3 max_step={ms:g}s 与 3600s 的 t_dry 差",
             dms, "s")
        radd(f"V3_{tag}_steps", f"W3 max_step={ms:g}s 步数",
             res[tag]["nsteps"], "-")
    say(f"  max_step=3600 s: t_dry = {base['t_dry']:.3f} s ({base['nsteps']} 步)")
    radd("V3_base_steps", "W3 max_step=3600s 步数", base["nsteps"], "-")

    say("")
    say("=" * 96)
    say("W4  与问题二交叉验证 (0~14400 s, M=200: BDF vs 后向 Euler)")
    say("=" * 96)
    Cq3, Tq3 = res["w4q3"]["C_ts"], res["w4q3"]["T_ts"]
    tq3 = 600.0 * np.arange(1, 25)
    for tag in ("q2_dt025", "q2_dt0125"):
        dC = np.abs(Cq3 - q2[tag]["C"])
        dT = np.abs(Tq3 - q2[tag]["T"])
        wins = [(0, 3, "0~1.8e3 s"), (3, 12, "1.8e3~7.2e3 s"),
                (12, 24, "7.2e3~1.44e4 s")]
        say(f"  [{tag}] (dt={q2[tag]['dt']} s)")
        say(f"    全时段 max|dC| = {dC.max():.4e} kg/kg @ t="
            f"{tq3[np.unravel_index(dC.argmax(), dC.shape)[0]]:.0f} s, "
            f"r={np.unravel_index(dC.argmax(), dC.shape)[1] * 0.1:.1f} cm; "
            f"max|dT| = {dT.max():.4e} K")
        for lo, hi, lbl in wins:
            say(f"      {lbl:>16}: max|dC| = {dC[lo:hi].max():.4e}, "
                f"max|dT| = {dT[lo:hi].max():.4e}")
        radd(f"V4_{tag}_dC", f"W4 {tag} 全时段最大水分偏差", float(dC.max()),
             "kg/kg")
        radd(f"V4_{tag}_dT", f"W4 {tag} 全时段最大温度偏差", float(dT.max()), "K")
        for lo, hi, lbl in wins:
            t = lbl.replace("~", "_").replace(".", "p")
            radd(f"V4_{tag}_dC_w{t}", f"W4 {tag} {lbl} 最大水分偏差",
                 float(dC[lo:hi].max()), "kg/kg")
            radd(f"V4_{tag}_dT_w{t}", f"W4 {tag} {lbl} 最大温度偏差",
                 float(dT[lo:hi].max()), "K")
    r4a = float(np.abs(Cq3 - q2["q2_dt025"]["C"]).max())
    r4b = float(np.abs(Cq3 - q2["q2_dt0125"]["C"]).max())
    say(f"  归因: 时间步减半 (dt 0.25->0.125) 后最大偏差 {r4a:.4e} -> {r4b:.4e} "
        f"(比值 {r4a / r4b:.3f}, 后向 Euler 一阶 => 应约 2)")
    radd("V4_ratio", "W4 时间步减半的偏差比 (应约 2, 一阶归因)", r4a / r4b, "-")

    say("")
    say("=" * 96)
    say("W5  Jacobian 提供方式 (M=200)")
    say("=" * 96)
    say(f"  {'方式':>22} {'rtol':>8} {'步数':>8} {'nfev':>8} {'njev':>6} "
        f"{'用时 [s]':>10} {'t_dry [s]':>16}")
    for tag, lbl in (("jac_dense", "全稠密差分"), ("jac_sparse", "jac_sparsity"),
                     ("base200", "解析稀疏")):
        rr = res[tag]
        say(f"  {lbl:>22} {rr['rtol']:>8g} {rr['nsteps']:>8d} {rr['nfev']:>8d} "
            f"{rr['njev']:>6d} {rr['wall']:>10.1f} {rr['t_dry']:>16.3f}")
    d_sp = res["jac_sparse"]["t_dry"] - base["t_dry"]
    say(f"  解析 vs jac_sparsity: 差 {d_sp:+.3f} s")
    radd("V5_sparse_diff", "W5 解析 Jacobian 与 jac_sparsity 的 t_dry 差", d_sp,
         "s")
    radd("V5_sparse_steps", "W5 jac_sparsity 步数", res["jac_sparse"]["nsteps"],
         "-")
    radd("V5_dense_tdry", "W5 全稠密差分 t_dry (rtol=1e-7)",
         res["jac_dense"]["t_dry"], "s")
    radd("V5_dense_nfev", "W5 全稠密差分 nfev", res["jac_dense"]["nfev"], "-")

    say("")
    say("=" * 96)
    say("W6  积分器交叉验证 (M=200, rtol=1e-9)")
    say("=" * 96)
    for tag, lbl in (("radau", "Radau"), ("lsoda", "LSODA")):
        rr = res[tag]
        dif = rr["t_dry"] - base["t_dry"]
        say(f"  {lbl:>6}: t_dry = {rr['t_dry']:.3f} s ({rr['nsteps']} 步, "
            f"用时 {rr['wall']:.1f} s), 与 BDF 差 {dif:+.3f} s")
        radd(f"V6_{tag}", f"W6 {lbl} t_dry", rr["t_dry"], "s")
        radd(f"V6_{tag}_diff", f"W6 {lbl} 与 BDF 的 t_dry 差", dif, "s")

    say("")
    say("=" * 96)
    say("W7  环境外推敏感性 (M=200, rtol=1e-9; 基准 Tbar=50.00, Cbar=0.0500, tau=600)")
    say("=" * 96)
    say(f"  {'变体':>22} {'t_dry [s]':>16} {'t_dry [h]':>14} {'dt_dry [h]':>14}")
    for tag, lbl in (("s_Tm1", "Tbar = 49 degC"), ("s_Tp1", "Tbar = 51 degC"),
                     ("s_Cm10", "Cbar = 0.045 (-10%)"),
                     ("s_Cp10", "Cbar = 0.055 (+10%)"),
                     ("s_tau0", "tau = 0 s"), ("s_tau1800", "tau = 1800 s")):
        rr = res[tag]
        dh = (rr["t_dry"] - base["t_dry"]) / 3600.0
        say(f"  {lbl:>22} {rr['t_dry']:>16.3f} {rr['t_dry'] / 3600.0:>14.4f} "
            f"{dh:>+14.4f}")
        radd(f"V7_{tag}", f"W7 {lbl} t_dry", rr["t_dry"], "s")
        radd(f"V7_{tag}_dh", f"W7 {lbl} 的 t_dry 变化", dh, "h")
    dtdT = (res["s_Tp1"]["t_dry"] - res["s_Tm1"]["t_dry"]) / 2.0 / 3600.0
    dtdC = (res["s_Cp10"]["t_dry"] - res["s_Cm10"]["t_dry"]) / 0.01 / 3600.0
    say(f"  敏感性系数: dt_dry/dTbar = {dtdT:+.3f} h/degC "
        f"(problem3.md §6.4(d) 先验: 约 -2), "
        f"dt_dry/dCbar = {dtdC:+.1f} h/(kg/kg)")
    say(f"  => Cbar +/-10% (0.005) 对应 dt_dry 约 {dtdC * 0.005:+.2f} h "
        f"(先验: 约 -/+4.8 h)")
    radd("V7_dtdT", "W7 dt_dry/dTbar 敏感性系数", dtdT, "h/degC")
    radd("V7_dtdC", "W7 dt_dry/dCbar 敏感性系数", dtdC, "h/(kg/kg)")

    say("")
    say("=" * 96)
    say("W8  极值原理与守恒 (生产配置 M=200)")
    say("=" * 96)
    C60 = base["C60"]
    dCmono = float(np.max(np.diff(C60, axis=0)))
    dmaxmono = float(np.max(np.diff(base["maxC60"])))
    budget = abs(base["W_dry"] - base["W0"]
                 + float(np.trapezoid(base["flux_w"], base["t_flux"])))
    fluxI = abs(float(np.trapezoid(base["flux_w"], base["t_flux"])))
    resW = budget / fluxI
    loss = 100.0 * (1.0 - base["W_dry"] / base["W0"])
    say(f"  含水率范围: [{C60.min():.6f}, {C60.max():.6f}] kg/kg "
        f"(环境 C_inf 全程下界 0.019636, 初值 2.55)")
    say(f"  C(r,t) 单调不增: 最大正增量 = {dCmono:.3e} kg/kg "
        f"{'OK' if dCmono < 1e-12 else '!!'}")
    say(f"  max_i C_i 单调不增: 最大正增量 = {dmaxmono:.3e} kg/kg "
        f"{'OK' if dmaxmono < 1e-12 else '!!'}")
    say(f"  水量收支: W(0) = {base['W0']:.6e}, W(t_dry) = {base['W_dry']:.6e} "
        f"(per 2 pi), 失水率 {loss:.4f}%")
    say(f"  水量收支相对残差 = {resW:.3e} {'OK' if resW < 1e-6 else '!!'} (<1e-6)")
    radd("V8_C_min", "W8 含水率最小值", float(C60.min()), "kg/kg")
    radd("V8_C_max", "W8 含水率最大值", float(C60.max()), "kg/kg")
    radd("V8_C_mono", "W8 C 时间单调性最大正增量", dCmono, "kg/kg")
    radd("V8_maxC_mono", "W8 maxC 单调性最大正增量", dmaxmono, "kg/kg")
    radd("V8_W0", "W8 初始总水量 W(0) (per 2 pi)", base["W0"], "m^2")
    radd("V8_W_dry", "W8 终态总水量 W(t_dry) (per 2 pi)", base["W_dry"], "m^2")
    radd("V8_loss", "W8 全程失水率", loss, "%")
    radd("V8_budget", "W8 水量收支相对残差", resW, "-")

    say("")
    say("=" * 96)
    say("W9  最大值位置诊断 (argmax_i C_i, 生产配置)")
    say("=" * 96)
    am = base["argmax60"]
    n_nz = int((am != 0).sum())
    last_nz = int(np.max(np.nonzero(am)[0])) if n_nz else -1
    say(f"  60 s 采样网格 ({base['n60']} 点): argmax != 0 的点数 = {n_nz}, "
        f"最后一个非零位置 t = {base['t60'][last_nz]:.0f} s" if n_nz else
        f"  60 s 采样网格 ({base['n60']} 点): argmax 恒为 0 (轴心)")
    say(f"  终态 argmax = 节点 {base['argmax_dry']} (r="
        f"{base['argmax_dry'] * 0.01:.2f} cm), max_i C_i(t_dry) = "
        f"{base['maxC_dry']:.12f}")
    radd("V9_argmax_nz", "W9 argmax 非 0 的 60s 采样点数", n_nz, "-")
    radd("V9_maxC_dry", "W9 终态 max_i C_i 与 C* 之差",
         base["maxC_dry"] - 0.15, "kg/kg")

    say("")
    say("=" * 96)
    say("W10 阈值附近行为 (g(t) = max_i C_i - C*)")
    say("=" * 96)
    g60 = base["maxC60"] - 0.15
    n_below60 = int(np.sum(g60 < 0))
    mfin = base["maxC_fin"]
    gfin = mfin - 0.15
    gpre_min = float(gfin[:-1].min())
    g_end = abs(float(gfin[-1]))
    dfin = np.diff(mfin)
    k = 120
    slope = (mfin[-1] - mfin[-1 - k]) / (base["t_fin"][-1] - base["t_fin"][-1 - k])
    cond = 1.0 / abs(slope)
    say(f"  60 s 网格 ({base['n60']} 点): 低于阈值的样本数 = {n_below60} (应为 0 —— "
        f"事件位于最后一个采样间隔内: 末样本 t = {base['t60'][-1]:.0f} s, "
        f"t_dry = {base['t_dry']:.1f} s)")
    say(f"  末 2 h (1 s 采样): t < t_dry 段 g 恒正: "
        f"{'OK' if gpre_min > 0 else '!!'} (最小值 {gpre_min:.3e}), "
        f"终点 |g(t_dry)| = {g_end:.3e} (应为 0)")
    say(f"  结合 maxC 全程单调不增 (W8) => g 在 (0, t_dry] 上恰有一个零点, "
        f"事件 direction=-1 定位无歧义")
    say(f"  maxC 单调性: 最大正增量 = {dfin.max():.3e} kg/kg")
    say(f"  终点下降速率 |dC0/dt| = {abs(slope):.4e} kg/(kg s) "
        f"(problem3.md §11.4 先验 2.92e-7)")
    say(f"  条件数 |dt_dry/dC| = 1/|dC0/dt| = {cond:.3e} s")
    say(f"  => 报告精度 1e-5 (四位小数) 的阈值解释差异对应 dt_dry 约 "
        f"{cond * 1e-5:.0f} s")
    radd("V10_nbelow60", "W10 60s 网格低于阈值的样本数", n_below60, "-")
    radd("V10_gpre_min", "W10 末 2h 内 t<t_dry 段 g 的最小值", gpre_min, "kg/kg")
    radd("V10_g_end", "W10 终点 |g(t_dry)|", g_end, "kg/kg")
    radd("V10_fin_mono", "W10 末 2h maxC 最大正增量", float(dfin.max()), "kg/kg")
    radd("V10_slope", "W10 终点下降速率 |dC0/dt|", float(abs(slope)),
         "kg/(kg s)")
    radd("V10_cond", "W10 条件数 |dt_dry/dC|", float(cond), "s")

    # ------------------------------------------------------------------
    rp = os.path.join(OUT, "registry_q3_verify.csv")
    if dry:
        say("")
        say("[--dry] 跳过写注册表与日志")
        say(f"总用时 {time.time() - t_all:.1f} s")
        return
    write_registry(rp, REG)
    with open(os.path.join(OUT, "q3_verify.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    say("")
    say(f"注册表: {rp} ({len(REG)} 行)")
    say(f"总用时 {time.time() - t_all:.1f} s")


if __name__ == "__main__":
    main()
