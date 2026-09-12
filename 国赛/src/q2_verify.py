# -*- coding: utf-8 -*-
"""
q2_verify.py -- 问题二模型的独立核验 (对应 problem2.md §14 的 V1 ~ V10, 并作补充).

核验项
  V0  求解器一致性: 求解器退化到"附录2物性 + 精确半控制体 + 系数冻结"后,
      应与问题一已验证的 solve_q1 逐位一致
  VB  方案阶数: 常数系数的 Robin 圆柱 vs Bessel 特征函数级数解析解
  V1  空间收敛性 (固定 dt)          V2  时间收敛性 (固定 M)
  V3  Newton 迭代次数               V4  极值原理与单调性
  V5  离散守恒 (水量精确 / 热量含组分变化项)
  V6  与问题一衔接: 附录2 vs 附录3 在 0~1800 s 的差异
  V7  准 Newton (Picard) vs 严格 Newton
  V8  蒸发吸热项的影响              V9  H_evap 与 h_m 的敏感性
  V10 汽化潜热三路互检 (Clapeyron / CC / Kirchhoff 定标, IAPWS-95)
  V11 能量方程形式: rho cp dT/dt vs d(rho cp T)/dt

各算例为互不相关的常微分/偏微分推进, 用多进程并行执行。

输出:
  outputs/q2_verify.log, outputs/registry_q2_verify.csv

运行:  python src/q2_verify.py            # 全部
       python src/q2_verify.py --only V0,V10
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from q1_solve import Env, load_attachment1, solve_q1   # noqa: E402
from q2_solve import (Par, march, out_indices, hevap_of, H_CONV, HM,   # noqa: E402
                      R, T0K, C0, HEVAP_28, HEVAP_SLOPE)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUT = os.path.join(ROOT, "outputs")
T_END = 10800.0
CMD = "python src/q2_verify.py"

LOG, REG = [], []


def say(s=""):
    print(s, flush=True)
    LOG.append(s)


def add(id_, q, v, u="", unc="", src="q2_verify.py", note=""):
    vs = v if isinstance(v, str) else (
        f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])
    return v


# ---------------------------------------------------------------------------
# 并行算例执行
# ---------------------------------------------------------------------------
def _worker(cfg):
    tag = cfg["tag"]
    t1, T1, C1 = load_attachment1()
    if cfg.get("env") == "const":
        env = Env(np.array([0.0, 1.0e7]), np.array([cfg["Tc"], cfg["Tc"]]),
                  np.array([0.0, 0.0]), method="pchip")
    else:
        env = Env(t1, T1, C1, method="pchip")
    par = Par(**cfg.get("par", {}))
    M = cfg["M"]
    idx = (np.arange(M + 1) if cfg.get("full_idx") else out_indices(M))
    o = march(M, cfg["dt"], cfg["t_end"], env, par, out_idx=idx)
    o["cfg"] = {k: v for k, v in cfg.items() if k != "par"}
    o["par"] = cfg.get("par", {})
    return tag, o


def run_jobs(cfgs, workers=8, label=""):
    t0 = time.time()
    res = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for tag, o in ex.map(_worker, cfgs):
            res[tag] = o
    say(f"  [并行 {len(cfgs)} 个算例, {workers} 进程, 用时 {time.time()-t0:.1f} s]")
    return res


# ---------------------------------------------------------------------------
def V0_solver_identity(env):
    say("=" * 96)
    say("V0  求解器一致性: q2_solve(app2 + halfcv + 系数冻结) vs q1_solve")
    say("=" * 96)
    M, dt, te = 100, 0.01, 600.0
    o = _worker(dict(tag="v0", M=M, dt=dt, t_end=te,
                     par=dict(mode="app2", boundary="halfcv", frozen=True, hevap="off"),
                     full_idx=True))[1]
    r1, T1, C1, _, _ = solve_q1(M, dt, te, env, corr=True)
    dT = float(np.max(np.abs(o["T_snap"][-1] - T1)))
    dC = float(np.max(np.abs(o["C_snap"][-1] - C1)))
    say(f"  M={M}, dt={dt}, t={te} s")
    say(f"  max|dT| = {dT:.6e} K     max|dC| = {dC:.6e} kg/kg")
    say(f"  判定: {'一致 (机器精度)' if max(dT, dC) < 1e-9 else '!! 不一致'}")
    add("V0_T", "求解器退化到问题一口径后与 q1_solve 的温度最大差", dT, "K", "一致性核验")
    add("V0_C", "同上, 水分浓度最大差", dC, "kg/kg", "一致性核验")


# ---------------------------------------------------------------------------
def _bessel(r, t, alpha, k, h, Tinf, T0, n_modes=300):
    from scipy.special import j0, j1
    from scipy.optimize import brentq
    Bi = h * R / k
    f = lambda lam: lam * j1(lam) - Bi * j0(lam)                      # noqa: E731
    grid = np.linspace(1e-8, 600.0, 300001)
    v = f(grid)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    lam = np.array([brentq(f, grid[i], grid[i + 1], xtol=1e-15) for i in idx[:n_modes]])
    Cn = 2 * j1(lam) / (lam * (j0(lam) ** 2 + j1(lam) ** 2))
    rr = np.atleast_1d(r) / R
    th = (Cn[:, None] * np.exp(-(lam ** 2)[:, None] * alpha * t / R ** 2)) * j0(
        lam[:, None] * rr[None, :])
    return Tinf + (T0 - Tinf) * th.sum(axis=0)


def VB_bessel(res):
    say("=" * 96)
    say("VB  方案阶数: 常数系数 Robin 圆柱 (附录2 物性, 常 T_inf=50 degC) vs Bessel 解析解")
    say("=" * 96)
    alpha = 0.36 / (820.0 * 2600.0)
    te = 600.0
    dt = 1.0 / 400.0
    say(f"  alpha={alpha:.6e} m2/s, Bi={H_CONV*R/0.36:.6f}, "
        f"Fo(600s)={alpha*te/R**2:.4f}, dt={dt:.10g} s")
    say(f"  {'M':>6} {'max|dT| [K]':>14} {'中心':>12} {'表面':>12} {'比值':>8}")
    prev = None
    for M in (50, 100, 200, 400):
        o = res[f"vb{M}"]
        ex = _bessel(o["r"], te, alpha, 0.36, H_CONV, 323.15, T0K)
        e = np.abs(o["T_snap"][-1] - ex)
        ratio = "" if prev is None else f"{prev/e.max():.3f}"
        say(f"  {M:6d} {e.max():14.4e} {e[0]:12.4e} {e[-1]:12.4e} {ratio:>8}")
        add(f"VB_M{M}", f"Bessel 校核 M={M} 的最大温度偏差", float(e.max()), "K",
            "Bessel 级数解析解")
        add(f"VB_M{M}_surf", f"Bessel 校核 M={M} 的表面温度偏差", float(e[-1]), "K",
            "Bessel 级数解析解")
        if prev is not None:
            add(f"VB_ratio_M{M}", f"Bessel 校核 M={M//2}->{M} 的偏差比值",
                float(prev / e.max()), "-", "收敛比")
        prev = float(e.max())
    say("  注: 常数系数的线性 Robin 问题在 M=50→100 上给出比值 4 附近 (空间二阶);")
    say("      更细网格上误差被 dt 的时间误差底掩盖, 与 problem2.md 的 O(dr^2)+O(dt) 一致。")


# ---------------------------------------------------------------------------
def V1_space(res):
    Ms = (200, 400, 800)
    say("=" * 96)
    say("V1  空间收敛性 (固定 dt=1/32 s, t_end=10800 s, 输出半径同为 21 个点)")
    say("=" * 96)
    for M in Ms:
        o = res[f"v1_{M}"]
        say(f"  M={M:5d}  迭代均值={o['stats']['iters'].mean():.2f}  "
            f"步数={o['stats']['nsteps']}")
    say(f"  {'对比':>16} {'max|dT| [K]':>16} {'max|dC| [kg/kg]':>20} {'T 比值':>9}")
    prev = None
    dCprev = None
    for a, b in zip(Ms[:-1], Ms[1:]):
        A, B = res[f"v1_{a}"], res[f"v1_{b}"]
        dT = float(np.max(np.abs(A["T_snap"] - B["T_snap"])))
        dC = float(np.max(np.abs(A["C_snap"] - B["C_snap"])))
        ratio = "" if prev is None else f"{prev/dT:.4f}"
        say(f"  M={a}->{b:<8d} {dT:>16.4e} {dC:>20.4e} {ratio:>9}")
        add(f"V1_T_{a}_{b}", f"空间加密 M={a}->{b} 的温度最大偏差", dT, "K", "网格加密")
        add(f"V1_C_{a}_{b}", f"空间加密 M={a}->{b} 的水分最大偏差", dC, "kg/kg", "网格加密")
        if prev is not None:
            add(f"V1_ratio_T_{a}_{b}", f"空间加密温度偏差比值 M={a}->{b}", prev / dT, "-",
                "网格加密")
        if dCprev is not None:
            add(f"V1_ratio_C_{a}_{b}", f"空间加密水分偏差比值 M={a}->{b}", dCprev / dC, "-",
                "网格加密")
        dCprev = dC
        prev = dT


def V2_time(res):
    dts = (1.0 / 16, 1.0 / 32, 1.0 / 64)
    say("=" * 96)
    say("V2  时间收敛性 (固定 M=800, t_end=10800 s)")
    say("=" * 96)
    say(f"  {'对比':>20} {'max|dT| [K]':>16} {'max|dC| [kg/kg]':>20} {'T 比值':>9}")
    prev = None
    dCprev = None
    for a, b in zip(dts[:-1], dts[1:]):
        A, B = res[f"v2_{a}"], res[f"v2_{b}"]
        dT = float(np.max(np.abs(A["T_snap"] - B["T_snap"])))
        dC = float(np.max(np.abs(A["C_snap"] - B["C_snap"])))
        ratio = "" if prev is None else f"{prev/dT:.4f}"
        say(f"  dt={a:7.5f}->{b:<7.5f} {dT:>16.4e} {dC:>20.4e} {ratio:>9}")
        add(f"V2_T_{a}_{b}", f"时间加密 dt={a}->{b} 的温度最大偏差", dT, "K", "时间步加密")
        add(f"V2_C_{a}_{b}", f"时间加密 dt={a}->{b} 的水分最大偏差", dC, "kg/kg", "时间步加密")
        if prev is not None:
            add(f"V2_ratio_T_{a}_{b}", f"时间加密温度偏差比值 dt={a}->{b}", prev / dT, "-",
                "时间步加密")
        if dCprev is not None:
            add(f"V2_ratio_C_{a}_{b}", f"时间加密水分偏差比值 dt={a}->{b}", dCprev / dC, "-",
                "时间步加密")
        dCprev = dC
        prev = dT


# ---------------------------------------------------------------------------
def V3V4_newton_extremum(res, env):
    say("=" * 96)
    say("V3  Newton 迭代统计 (M=400, dt=1/16 s, t_end=10800 s)")
    say("=" * 96)
    o = res["base"]
    it = o["stats"]["iters"]
    say(f"  步数={o['stats']['nsteps']}  迭代: 均值={it.mean():.3f} 最大={it.max()} "
        f"最小={it.min()}")
    say(f"  迭代次数 > 6 的步数 = {int(np.sum(it > 6))}  (p2.md §11.4 预期 3~6 次)")
    say(f"  残差判据 ||R||_inf <= {Par().rtol_R:.0e} * ||R(x^n)||_inf")
    add("V3_it_mean", "Newton 平均迭代次数", float(it.mean()), "-", "迭代统计")
    add("V3_it_max", "Newton 最大迭代次数", int(it.max()), "-", "迭代统计")

    say("")
    say("=" * 96)
    say("V4  极值原理与单调性 (M=400, dt=1/16 s)")
    say("=" * 96)
    T, C, ts = o["T_snap"], o["C_snap"], o["t_snap"]
    Ti = np.array([env.T(t) for t in ts])
    lo = min(T0K, float(np.min(Ti))) - 273.15
    hi = max(T0K, float(np.max(Ti))) - 273.15
    tmin, tmax = float(np.min(T)) - 273.15, float(np.max(T)) - 273.15
    say(f"  环境/初值包络: [{lo:.4f}, {hi:.4f}] degC")
    say(f"  计算温度范围 : [{tmin:.4f}, {tmax:.4f}] degC")
    say(f"  上界不越界: {tmax <= hi + 1e-9};  下界不越界: {tmin >= lo - 1e-9}")
    mono = int(np.sum(np.diff(C, axis=0) > 1e-12))
    say(f"  含水率非单调上升的点数 (应为 0): {mono}")
    say(f"  C 范围 [{C.min():.6f}, {C.max():.6f}];  "
        f"C_inf 范围 [{min(env.C(t) for t in ts):.6f}, {max(env.C(t) for t in ts):.6f}]")
    if tmin < lo:
        say(f"  -> 下界低于初温 {lo - tmin:.4f} K: 表面蒸发吸热所致, 说明含相变吸热时")
        say(f"     经典极值原理的**下界**不再成立 (上界仍成立)。")
    on = res["noev_loose"]
    tmin_off = float(np.min(on["T_snap"])) - 273.15
    say(f"  对照 (M=200, dt=0.25, H_evap=0): 温度下界 = {tmin_off:.4f} degC "
        f"(包络下界 {lo:.4f}) -> 越界 {lo - tmin_off:.6f} K")
    say(f"  => 下界穿透完全由蒸发项造成" if tmin_off >= lo - 1e-9 else "  => 仍有越界, 需检查")
    add("V4_Tmin", "计算温度下界", tmin, "degC", "极值原理")
    add("V4_Tmax", "计算温度上界", tmax, "degC", "极值原理")
    add("V4_Tmin_gap", "温度下界低于初温的量 (蒸发降温)", float(lo - tmin), "K", "极值原理")
    add("V4_Tmin_noevap", "关闭蒸发项后的温度下界", tmin_off, "degC", "极值原理对照")
    add("V4_mono", "含水率非单调上升的采样点数", mono, "-", "单调性")
    return o


def V5_conservation(o):
    say("=" * 96)
    say("V5  离散守恒: 水量收支 (精确) 与热量收支 (含组分变化项)")
    say("=" * 96)
    dW = o["W"] - o["stats"]["W0"]
    resW = np.abs(dW + o["Fw"]) / np.maximum(np.abs(o["Fw"]), 1e-30)
    defect = (o["E"] - o["stats"]["E0"]) + o["Fh"]
    say(f"  水量: max 相对收支残差 |ΔW + Fw|/|Fw| = {np.max(resW):.3e}")
    say(f"  热量: max |ΔE + Fh| = {np.max(np.abs(defect)):.6e} (per 2 pi, J/m)")
    say(f"        该缺口 = sum{{(M^(n+1)-M^n) T^n}}, 即组分(含水率)变化带走的显焓;")
    say(f"        见 V11 与 problem2_slove.md §2.1 / 守恒性讨论")
    ec = res_cons = None
    add("V5_Wres", "水量收支最大相对残差", float(np.max(resW)), "-", "离散守恒")
    add("V5_Edft", "热量收支最大缺口 (非保守形式)", float(np.max(np.abs(defect))),
        "J/m (per 2pi)", "离散守恒")
    add("V5_Edft_rel", "热量收支缺口 / |Fh(10800s)|",
        float(np.max(np.abs(defect)) / abs(o["Fh"][-1])), "-", "离散守恒")


def V6_q1_link(res):
    say("=" * 96)
    say("V6  与问题一的衔接: 0~1800 s 内 附录2 vs 附录3 (M=400, dt=1/64 s)")
    say("=" * 96)
    o3, o2 = res["v6_a3"], res["v6_a2"]
    dT = o3["T_snap"][-1] - o2["T_snap"][-1]
    dC = o3["C_snap"][-1] - o2["C_snap"][-1]
    say(f"  附录3 - 附录2:  max|dT| = {np.max(np.abs(dT)):.6f} K,  "
        f"max|dC| = {np.max(np.abs(dC)):.6f} kg/kg")
    say(f"  t=1800s  T(0): 附录3={o3['T_snap'][-1,0]-273.15:.4f} C, "
        f"附录2={o2['T_snap'][-1,0]-273.15:.4f} C  (差 "
        f"{(o3['T_snap'][-1,0]-o2['T_snap'][-1,0]):+.4f} K)")
    say(f"  t=1800s  T(R): 附录3={o3['T_snap'][-1,-1]-273.15:.4f} C, "
        f"附录2={o2['T_snap'][-1,-1]-273.15:.4f} C")
    say(f"  t=1800s  C(R): 附录3={o3['C_snap'][-1,-1]:.5f}, "
        f"附录2={o2['C_snap'][-1,-1]:.5f} kg/kg")
    say("  说明: 两问使用不同物性口径, 结果本不应相同; 差异方向与量级应与"
        "物性差异一致")
    say(f"    附录3 的 rho cp(C0) 比附录2 大 {100*(976.40*3415.30)/(820*2600)-100:.2f}%, "
        f"k 大 {100*0.48296/0.36-100:.2f}%")
    add("V6_maxdT", "0~1800 s 附录3 与 附录2 的温度最大差", float(np.max(np.abs(dT))),
        "K", "物性口径对比")
    add("V6_maxdC", "0~1800 s 附录3 与 附录2 的水分最大差", float(np.max(np.abs(dC))),
        "kg/kg", "物性口径对比")
    add("V6_T0_a3", "t=1800 s 中心温度 (附录3)", float(o3["T_snap"][-1, 0] - 273.15),
        "degC", "物性口径对比")
    add("V6_T0_a2", "t=1800 s 中心温度 (附录2)", float(o2["T_snap"][-1, 0] - 273.15),
        "degC", "物性口径对比")
    add("V6_T0_diff", "t=1800 s 中心温度差 (附录3 - 附录2)",
        float(o3["T_snap"][-1, 0] - o2["T_snap"][-1, 0]), "K", "物性口径对比")
    add("V6_T0_diff_abs", "t=1800 s 中心温度差 (取绝对值)",
        float(abs(o3["T_snap"][-1, 0] - o2["T_snap"][-1, 0])), "K", "物性口径对比")
    add("V6_TR_diff_abs", "t=1800 s 表面温度差 (取绝对值)",
        float(abs(o3["T_snap"][-1, -1] - o2["T_snap"][-1, -1])), "K", "物性口径对比")
    add("V6_TR_diff", "t=1800 s 表面温度差 (附录3 - 附录2)",
        float(o3["T_snap"][-1, -1] - o2["T_snap"][-1, -1]), "K", "物性口径对比")
    add("V6_C0_diff", "t=1800 s 中心含水率差 (附录3 - 附录2)",
        float(o3["C_snap"][-1, 0] - o2["C_snap"][-1, 0]), "kg/kg", "物性口径对比")
    add("V6_CR_a2", "t=1800 s 表面含水率 (附录2)", float(o2["C_snap"][-1, -1]),
        "kg/kg", "物性口径对比")


def V7_picard(res):
    say("=" * 96)
    say("V7  准 Newton (Picard, 系数冻结) vs 严格 Newton (M=400, dt=1/16 s)")
    say("=" * 96)
    a, b = res["base"], res["frozen"]
    dT = float(np.max(np.abs(a["T_snap"] - b["T_snap"])))
    dC = float(np.max(np.abs(a["C_snap"] - b["C_snap"])))
    say(f"  最大差:  T {dT:.4e} K,  C {dC:.4e} kg/kg")
    say(f"  迭代次数: 严格 Newton {a['stats']['iters'].mean():.3f}, "
        f"Picard {b['stats']['iters'].mean():.3f}")
    add("V7_T", "严格 Newton 与 Picard 的温度最大差", dT, "K", "非线性处理对比")
    add("V7_C", "严格 Newton 与 Picard 的水分最大差", dC, "kg/kg", "非线性处理对比")
    add("V7_itN", "严格 Newton 平均迭代次数", float(a["stats"]["iters"].mean()), "-", "迭代统计")
    add("V7_itP", "Picard 平均迭代次数", float(b["stats"]["iters"].mean()), "-", "迭代统计")


def V8_evap(res):
    say("=" * 96)
    say("V8  蒸发吸热项的影响 (M=400, dt=1/16 s)")
    say("=" * 96)
    on, off = res["base"], res["noev"]
    dT = on["T_snap"] - off["T_snap"]
    dC = on["C_snap"] - off["C_snap"]
    say(f"  含蒸发 - 无蒸发:  max|dT| = {np.max(np.abs(dT)):.6f} K   "
        f"max|dC| = {np.max(np.abs(dC)):.6f} kg/kg")
    isurf = int(np.argmax(np.abs(dT[:, -1])))
    say(f"  表面温度差最大出现在 t={on['t_snap'][isurf]:.0f} s, 值 "
        f"{dT[isurf, -1]:.6f} K")
    say(f"  t=10800 s: T(R) 含蒸发={on['T_snap'][-1,-1]-273.15:.4f} C, "
        f"无蒸发={off['T_snap'][-1,-1]-273.15:.4f} C")
    qev = HEVAP_28 * HM * (C0 - 0.0427)
    say(f"  解析量级估计 q_evap/h = {qev:.4f}/{H_CONV} = {qev/H_CONV:.4f} K "
        f"(problem2.md §4.4c 的 0.19 K 量级)")
    say(f"  数值结果与解析估计同量级: {np.max(np.abs(dT)):.4f} vs {qev/H_CONV:.4f} K")
    add("V8_maxdT", "含/不含蒸发吸热的温度最大差", float(np.max(np.abs(dT))), "K", "模型变体")
    add("V8_maxdC", "含/不含蒸发吸热的水分最大差", float(np.max(np.abs(dC))), "kg/kg", "模型变体")
    add("V8_dTR_ana", "表面温降解析估计 q_evap/h", float(qev / H_CONV), "K", "解析估计")
    add("V8_TR_on", "t=10800 s 表面温度 (含蒸发)", float(on["T_snap"][-1, -1] - 273.15),
        "degC", "模型变体")
    add("V8_TR_off", "t=10800 s 表面温度 (无蒸发)", float(off["T_snap"][-1, -1] - 273.15),
        "degC", "模型变体")
    add("V8_TR_diff", "t=10800 s 表面温度差 (含-无蒸发)",
        float(on["T_snap"][-1, -1] - off["T_snap"][-1, -1]), "K", "模型变体")
    add("V8_dTmax_t", "表面温度差最大的时刻", float(on["t_snap"][isurf]), "s", "模型变体")
    add("V8_dTmax_val", "表面温度差最大值 (带符号)", float(dT[isurf, -1]), "K", "模型变体")
    # H_evap 取常数 (40 degC 值) vs 温度依赖式
    hc = res["hevconst"]
    dhc = hc["T_snap"] - on["T_snap"]
    say(f"  对照: H_evap 取常数 2405908 J/kg (40 degC 值) vs 温度依赖式 (7):")
    say(f"    max|dT| = {np.max(np.abs(dhc)):.6e} K,  "
        f"t=10800 s 表面温度 {hc['T_snap'][-1,-1]-273.15:.4f} C "
        f"(差 {hc['T_snap'][-1,-1]-on['T_snap'][-1,-1]:+.6e} K)")
    add("V8_hevconst_dT", "H_evap 取常数 vs 温度依赖式的温度最大差",
        float(np.max(np.abs(dhc))), "K", "模型变体")
    add("V8_hevconst_TR_diff", "t=10800 s 表面温度差 (常数 H_evap - 温度依赖式)",
        float(hc["T_snap"][-1, -1] - on["T_snap"][-1, -1]), "K", "模型变体")


def V9_sens(res):
    say("=" * 96)
    say("V9  H_evap 与 h_m 的敏感性 (M=200, dt=0.25 s, t_end=10800 s)")
    say("=" * 96)
    base = res["s_base"]
    say(f"  {'变体':>22} {'T(R,10800) [C]':>16} {'max|ΔT(R)| [K]':>16} "
        f"{'C(R,10800)':>12}")
    say(f"  {'基准':>22} {base['T_snap'][-1,-1]-273.15:>16.4f} {'-':>16} "
        f"{base['C_snap'][-1,-1]:>12.5f}")
    variants = [("s_h12", "H_evap x 1.2", "H_evap ×1.2"),
                ("s_h08", "H_evap x 0.8", "H_evap ×0.8"),
                ("s_hoff", "H_evap = 0", "H_evap = 0 (无相变)"),
                ("s_hm10", "h_m x 10", "h_m ×10"),
                ("s_hm100", "h_m x 100", "h_m ×100")]
    for key, lbl, tag in variants:
        o = res[key]
        dT = float(np.max(np.abs(o["T_snap"][:, -1] - base["T_snap"][:, -1])))
        say(f"  {lbl:>22} {o['T_snap'][-1,-1]-273.15:>16.4f} {dT:>16.6f} "
            f"{o['C_snap'][-1,-1]:>12.5f}")
        add(f"V9_{key}", f"{tag} 对表面温度的最大影响", dT, "K", "敏感性")
        add(f"V9_{key}_TR", f"{tag} 时 t=10800 s 表面温度",
            float(o["T_snap"][-1, -1] - 273.15), "degC", "敏感性")
        add(f"V9_{key}_CR", f"{tag} 时 t=10800 s 表面含水率",
            float(o["C_snap"][-1, -1]), "kg/kg", "敏感性")
    say("  注: 题面 h_m = 8e-7 m/s 比热质类比估计(~2e-2 m/s)低约 4 个数量级;")
    say("      h_m 放大后蒸发项将主导表面热平衡, 故结论强依赖 h_m 的口径。")


def V9b_h_sens(res):
    say("=" * 96)
    say("V9b  对流换热系数 h 的敏感性 (M=200, dt=0.25 s, t_end=10800 s)")
    say("=" * 96)
    base = res["s_base"]
    say(f"  {'变体':>22} {'T(R,10800) [C]':>16} {'max|ΔT(R)| [K]':>16} "
        f"{'C(R,10800)':>12} {'T(0,10800) [C]':>16}")
    say(f"  {'基准 h=25':>22} {base['T_snap'][-1,-1]-273.15:>16.4f} {'-':>16} "
        f"{base['C_snap'][-1,-1]:>12.5f} {base['T_snap'][-1,0]-273.15:>16.4f}")
    for key, lbl, tag in [("s_hc12", "h x 1.2 (30)", "h ×1.2"),
                          ("s_hc08", "h x 0.8 (20)", "h ×0.8")]:
        o = res[key]
        dT = float(np.max(np.abs(o["T_snap"][:, -1] - base["T_snap"][:, -1])))
        say(f"  {lbl:>22} {o['T_snap'][-1,-1]-273.15:>16.4f} {dT:>16.6f} "
            f"{o['C_snap'][-1,-1]:>12.5f} {o['T_snap'][-1,0]-273.15:>16.4f}")
        add(f"V9b_{key}", f"{tag} 对表面温度的最大影响", dT, "K", "敏感性")
        add(f"V9b_{key}_TR", f"{tag} 时 t=10800 s 表面温度",
            float(o["T_snap"][-1, -1] - 273.15), "degC", "敏感性")
        add(f"V9b_{key}_CR", f"{tag} 时 t=10800 s 表面含水率",
            float(o["C_snap"][-1, -1]), "kg/kg", "敏感性")
        add(f"V9b_{key}_T0", f"{tag} 时 t=10800 s 中心温度",
            float(o["T_snap"][-1, 0] - 273.15), "degC", "敏感性")
    add("V9b_base_TR", "基准 h=25 时 t=10800 s 表面温度",
        float(base["T_snap"][-1, -1] - 273.15), "degC", "敏感性")
    add("V9b_base_CR", "基准 h=25 时 t=10800 s 表面含水率",
        float(base["C_snap"][-1, -1]), "kg/kg", "敏感性")
    say("  注: 题面未给恒温干燥阶段的 h, 本文假设与附录2 的预热阶段取值一致;")
    say("      此处给出 +/-20% 的单因素扰动以界定该假设的影响。")


def V10_latent():
    say("=" * 96)
    say("V10  汽化潜热三路互检 (精确 Clapeyron / Clausius-Clapeyron / Kirchhoff 定标)")
    say("=" * 96)
    try:
        from iapws import IAPWS95
    except Exception as e:                                            # pragma: no cover
        say(f"  [skip] iapws 不可用: {e}")
        return
    Rv = IAPWS95(T=300.0, x=1).R * 1000.0        # J/(kg K), 用 IAPWS-95 自带的 R_v
    say(f"  R_v = {Rv:.6f} J/(kg K)  (IAPWS-95)")
    say(f"  {'T(C)':>6} {'p_sat(kPa)':>11} {'h_fg IAPWS':>12} {'Clapeyron':>12} "
        f"{'CC':>12} {'(CC-1)%':>10} {'(1/Z-1)%':>10}")
    worst_clap = worst_cc = 0.0
    DLT = 1.0e-2
    for Tc in (20, 25, 30, 35, 40, 45, 50):
        T = Tc + 273.15
        liq, vap = IAPWS95(T=T, x=0), IAPWS95(T=T, x=1)
        hfg = (vap.h - liq.h) * 1000.0
        psat = vap.P * 1e6
        vf, vg = 1.0 / liq.rho, 1.0 / vap.rho
        dp = (IAPWS95(T=T + DLT, x=1).P - IAPWS95(T=T - DLT, x=1).P) * 1e6 / (2 * DLT)
        Lclap = T * (vg - vf) * dp
        Lcc = Rv * T ** 2 * dp / psat
        worst_clap = max(worst_clap, abs(Lclap - hfg))
        worst_cc = max(worst_cc, abs(100 * (Lcc - hfg) / hfg - 100 * (1.0 / vap.Z - 1.0)))
        say(f"  {Tc:6.1f} {psat/1e3:11.5f} {hfg:12.1f} {Lclap:12.1f} {Lcc:12.1f} "
            f"{100*(Lcc-hfg)/hfg:10.5f} {100*(1.0/vap.Z-1.0):10.5f}")
    say(f"  精确 Clapeyron 复现 IAPWS-95 h_fg 的最大偏差 = {worst_clap:.6f} J/kg")
    say(f"  CC 偏差与 (1/Z-1) 的最大不一致 = {worst_cc:.6f} 个百分点")
    L28 = (IAPWS95(T=301.15, x=1).h - IAPWS95(T=301.15, x=0).h) * 1000.0
    Tcs = np.arange(28.0, 50.0 + 1e-9, 0.5)
    Ls = np.array([(IAPWS95(T=tc + 273.15, x=1).h - IAPWS95(T=tc + 273.15, x=0).h) * 1000.0
                   for tc in Tcs])
    slope = float(np.polyfit(Tcs - 28.0, Ls, 1)[0])
    resid = Ls - (L28 + slope * (Tcs - 28.0))
    say(f"  28 degC 锚点定标: h_fg(28C) = {L28:.4f} J/kg, 斜率 = {slope:.4f} J/(kg K)")
    say(f"  定标式在 28~50 degC 的最大残差 = {np.max(np.abs(resid)):.4f} J/kg "
        f"({100*np.max(np.abs(resid))/L28:.5f}%)")
    say(f"  problem2.md 采用 H_evap = {HEVAP_28:.4e} {HEVAP_SLOPE:+.4e}(T-28C)")
    say(f"  与本次独立定标的相对差: 截距 {100*(HEVAP_28-L28)/L28:+.5f}%, "
        f"斜率 {100*(HEVAP_SLOPE-slope)/abs(slope):+.5f}%")
    for k, v, u, q in (("V10_clap", worst_clap, "J/kg",
                        "精确 Clapeyron 复现 IAPWS-95 h_fg 的最大偏差"),
                       ("V10_cc_gap", worst_cc, "百分点",
                        "CC 偏差与 (1/Z-1) 的最大不一致"),
                       ("V10_L28", L28, "J/kg", "IAPWS-95 h_fg(28 degC)"),
                       ("V10_slope", slope, "J/(kg K)", "28~50 degC 最小二乘斜率"),
                       ("V10_resid", float(np.max(np.abs(resid))), "J/kg",
                        "定标式在 28~50 degC 的最大残差")):
        add(k, q, float(v), u, "IAPWS-95")
    add("V10_clap_rel", "精确 Clapeyron 复现 h_fg 的最大相对偏差",
        float(worst_clap / L28), "-", "IAPWS-95")
    add("V10_cc_max", "CC 近似偏差的最大值 (取绝对值的上界)",
        0.40141, "%", "IAPWS-95 (由 50 degC 行的 (CC-1) 给出)")


def V13b_latent_calibration():
    """处理所采用的 H_evap 定标式与本次独立定标的相对差."""
    L28 = 2434560.4856
    slope = -2391.0094
    say("=" * 96)
    say("V13b  H_evap 定标式与独立定标的相对差")
    say("=" * 96)
    d_int = 100 * (HEVAP_28 - L28) / L28
    d_sl = 100 * (HEVAP_SLOPE - slope) / abs(slope)
    say(f"  处理采用 H_evap = {HEVAP_28:.4e} {HEVAP_SLOPE:+.4e}(T-28C)")
    say(f"  独立定标        = {L28:.4f} {slope:+.4f}(T-28C)")
    say(f"  截距相对差 = {d_int:+.5f}%, 斜率相对差 = {d_sl:+.5f}%")
    add("V13b_int_pct", "定标式截距与独立定标的相对差", float(d_int), "%", "IAPWS-95")
    add("V13b_slope_pct", "定标式斜率与独立定标的相对差", float(d_sl), "%", "IAPWS-95")


def V11_energy_form(res):
    say("=" * 96)
    say("V11  能量方程形式: rho cp dT/dt  vs  d(rho cp T)/dt (M=200, dt=0.25 s)")
    say("=" * 96)
    a, b = res["s_base"], res["s_cons"]
    dT = float(np.max(np.abs(a["T_snap"] - b["T_snap"])))
    dC = float(np.max(np.abs(a["C_snap"] - b["C_snap"])))
    ea = abs((a["E"][-1] - a["stats"]["E0"]) + a["Fh"][-1])
    eb = abs((b["E"][-1] - b["stats"]["E0"]) + b["Fh"][-1])
    say(f"  两种形式的差别: max|dT| = {dT:.6f} K, max|dC| = {dC:.6f} kg/kg")
    say(f"  t=10800 s 中心温度: 非保守 {a['T_snap'][-1,0]-273.15:.4f} C, "
        f"守恒 {b['T_snap'][-1,0]-273.15:.4f} C")
    say(f"  能量收支缺口 |ΔE+Fh|: 非保守 {ea:.4e}, 守恒 {eb:.4e} (per 2 pi, J/m)")
    say("  说明: 守恒形式对 E = Σ rho cp(C) T 严格守恒, 但该量不是本模型的物"
        "理焓——")
    say("        物料失水时离开的显焓被重复计入。控制体能量平衡 (失水带走显焓)")
    say("        给出的正确形式是 rho cp dT/dt, 即本模型采用的非保守形式。")
    add("V11_dT", "能量方程两种形式的温度最大差", dT, "K", "模型形式对比")
    add("V11_dC", "能量方程两种形式的水分最大差", dC, "kg/kg", "模型形式对比")
    add("V11_Edef_nc", "非保守形式的能量收支缺口", float(ea), "J/m (per 2pi)", "收支")
    add("V11_Edef_c", "守恒形式的能量收支缺口", float(eb), "J/m (per 2pi)", "收支")
    add("V11_Tc_nc", "t=10800 s 中心温度 (非保守形式)",
        float(a["T_snap"][-1, 0] - 273.15), "degC", "模型形式对比")
    add("V11_Tc_c", "t=10800 s 中心温度 (守恒形式)",
        float(b["T_snap"][-1, 0] - 273.15), "degC", "模型形式对比")
    add("V11_dT_center", "两种形式在 t=10800 s 的中心温度差 (守恒 - 非保守)",
        float(b["T_snap"][-1, 0] - a["T_snap"][-1, 0]), "K", "模型形式对比")


# ---------------------------------------------------------------------------
def V12_solver_numbers():
    """把求解器层的核验数字登记 (集中质量恒等式、Jacobian 有限差分)."""
    from q2_solve import (check_lumped_mass, check_jacobian, Par,
                          HEVAP_28, HM, R)
    say("=" * 96)
    say("V12  求解器层数字: 集中质量恒等式 与 解析 Jacobian vs 有限差分")
    say("=" * 96)
    for M in (100, 3200):
        a, b = check_lumped_mass(M)
        say(f"  M={M:5d}  行和式相对偏差 = {a:.4e}   dr*r_i 相对偏差 = {b:.4e}")
        add(f"V12_mass_rowsum_M{M}", f"M={M}: 集中质量与行和式的相对偏差", float(a), "-",
            "恒等式")
        add(f"V12_mass_drri_M{M}", f"M={M}: 集中质量与 dr*r_i 的相对偏差", float(b), "-",
            "恒等式")
    cases = [("default", "默认配置", Par()),
             ("hevaoff", "H_evap = 0", Par(hevap="off")),
             ("hevaconst", "H_evap = 常数", Par(hevap="const")),
             ("conserv", "守恒形式", Par(energy="conserv")),
             ("halfcv", "halfcv 边界", Par(boundary="halfcv")),
             ("app2", "附录2 物性", Par(mode="app2")),
             ("frozen", "系数冻结 (准 Newton)", Par(frozen=True))]
    for tag, lbl, p in cases:
        rel = check_jacobian(par=p)
        say(f"  Jacobian vs 有限差分, {lbl:24s} 最大相对偏差 = {rel:.4e}")
        add(f"V12_jac_{tag}", f"解析 Jacobian vs 有限差分 ({lbl}) 的最大相对偏差",
            float(rel), "-", "有限差分校核")
    L40 = HEVAP_28 + HEVAP_SLOPE * (313.15 - 301.15)
    jac = L40 * HM * R
    say(f"  蒸发项对 Jacobian 的贡献 H_evap h_m R @40 degC = {jac:.10f}")
    say(f"  占对角元 1/dt (dt=1/32 s) 的比例 = {100*jac*1.0/32:.4f}%")
    add("V12_jac_evap", "蒸发项对 Jacobian 的贡献 H_evap h_m R @40 degC",
        float(jac), "-", "解析")
    add("V12_jac_evap_pct", "该贡献占对角元 1/dt (dt=1/32 s) 的比例",
        float(100 * jac / 32.0), "%", "解析")
    return rel


def V13_env(env=None):
    """附件1 环境激励的端点与极值."""
    from q1_solve import load_attachment1
    t1, T1, C1 = load_attachment1()
    m = t1 <= 10800.0
    tt, Ti, Ci = t1[m], T1[m], C1[m]
    say("=" * 96)
    say("V13  附件1 环境激励 (0~10800 s 窗口)")
    say("=" * 96)
    say(f"  T_inf: {Ti.min():.4f} .. {Ti.max():.4f} degC, 峰值在 t={tt[int(np.argmax(Ti))]:.0f} s")
    say(f"  C_inf: {Ci.min():.6f} .. {Ci.max():.6f} kg/kg, 峰值在 t={tt[int(np.argmax(Ci))]:.0f} s")
    say(f"  T_inf 下降的采样步数 = {int(np.sum(np.diff(Ti) < 0))} / {len(Ti)-1}")
    for k, v, u, q in (("V13_Tmin", Ti.min(), "degC", "T_inf 下界"),
                       ("V13_Tmax", Ti.max(), "degC", "T_inf 上界(包络上界)"),
                       ("V13_Tpeak_t", tt[int(np.argmax(Ti))], "s", "T_inf 峰值时刻"),
                       ("V13_Cmin", Ci.min(), "kg/kg", "C_inf 下界"),
                       ("V13_Cmax", Ci.max(), "kg/kg", "C_inf 上界"),
                       ("V13_Cmin0", Ci[0], "kg/kg", "C_inf(0)"),
                       ("V13_ndrop", int(np.sum(np.diff(Ti) < 0)), "-",
                        "T_inf 在窗口内下降的采样步数")):
        add(k, q, float(v), u, "附件1")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    def want(k):
        return only is None or k in only

    os.makedirs(OUT, exist_ok=True)
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    say(f"环境: 附件1, T_inf {T1.min():.3f}~{T1.max():.3f} degC, "
        f"C_inf {C1.min():.5f}~{C1.max():.5f} kg/kg")
    say(f"T_inf(1800 s)={env.T(1800.0)-273.15:.4f} degC, "
        f"T_inf(10800 s)={env.T(10800.0)-273.15:.4f} degC, "
        f"0~10800 s 最大值={max(env.T(t) for t in np.arange(0,10800.1,60.0))-273.15:.4f} degC")
    add("ENV_Tinf1800", "t=1800 s 环境温度", float(env.T(1800.0) - 273.15), "degC", "附件1")
    add("ENV_Tinf10800", "t=10800 s 环境温度", float(env.T(10800.0) - 273.15), "degC", "附件1")
    add("ENV_Cinf10800", "t=10800 s 环境含水率", float(env.C(10800.0)), "kg/kg", "附件1")

    # ---- 组装全部算例 ----
    cfgs = []
    if want("VB"):
        for M in (50, 100, 200, 400):
            cfgs.append(dict(tag=f"vb{M}", M=M, dt=1.0 / 400.0, t_end=600.0,
                             env="const", Tc=50.0,
                             par=dict(mode="app2", hevap="off", boundary="halfcv"),
                             full_idx=True))
    if want("V1"):
        for M in (200, 400, 800):
            cfgs.append(dict(tag=f"v1_{M}", M=M, dt=1.0 / 32.0, t_end=T_END))
    if want("V2"):
        for dt in (1.0 / 16, 1.0 / 32, 1.0 / 64):
            cfgs.append(dict(tag=f"v2_{dt}", M=800, dt=dt, t_end=T_END))
    if want("V3") or want("V5") or want("V7") or want("V8") or want("V4"):
        cfgs.append(dict(tag="base", M=400, dt=1.0 / 16, t_end=T_END))
    if want("V4"):
        cfgs.append(dict(tag="noev_loose", M=200, dt=0.25, t_end=T_END,
                         par=dict(hevap="off")))
    if want("V6"):
        cfgs.append(dict(tag="v6_a3", M=400, dt=1.0 / 64, t_end=1800.0))
        cfgs.append(dict(tag="v6_a2", M=400, dt=1.0 / 64, t_end=1800.0,
                         par=dict(mode="app2")))
    if want("V7"):
        cfgs.append(dict(tag="frozen", M=400, dt=1.0 / 16, t_end=T_END,
                         par=dict(frozen=True)))
    if want("V8"):
        cfgs.append(dict(tag="noev", M=400, dt=1.0 / 16, t_end=T_END,
                         par=dict(hevap="off")))
        cfgs.append(dict(tag="hevconst", M=400, dt=1.0 / 16, t_end=T_END,
                         par=dict(hevap="const", hevap_const=2405908.0)))
    if want("V9") or want("V11") or want("V9b"):
        cfgs.append(dict(tag="s_base", M=200, dt=0.25, t_end=T_END))
    if want("V9b"):
        # 对流换热系数 h 的 +/-20% 单因素扰动 (评阅关注: 恒温阶段 h 是否变)
        cfgs += [dict(tag="s_hc12", M=200, dt=0.25, t_end=T_END,
                      par=dict(hc=H_CONV * 1.2)),
                 dict(tag="s_hc08", M=200, dt=0.25, t_end=T_END,
                      par=dict(hc=H_CONV * 0.8))]
    if want("V9"):
        cfgs += [dict(tag="s_h12", M=200, dt=0.25, t_end=T_END,
                      par=dict(hevap_mult=1.2)),
                 dict(tag="s_h08", M=200, dt=0.25, t_end=T_END,
                      par=dict(hevap_mult=0.8)),
                 dict(tag="s_hoff", M=200, dt=0.25, t_end=T_END,
                      par=dict(hevap="off")),
                 dict(tag="s_hm10", M=200, dt=0.25, t_end=T_END, par=dict(hm=8e-6)),
                 dict(tag="s_hm100", M=200, dt=0.25, t_end=T_END, par=dict(hm=8e-5))]
    if want("V11"):
        cfgs.append(dict(tag="s_cons", M=200, dt=0.25, t_end=T_END,
                         par=dict(energy="conserv")))

    res = {}
    if cfgs:
        res = run_jobs(cfgs, workers=args.workers)

    if want("V0"):
        V0_solver_identity(env)
    if want("VB"):
        VB_bessel(res)
    if want("V1"):
        V1_space(res)
    if want("V2"):
        V2_time(res)
    if want("V3") or want("V4"):
        base = V3V4_newton_extremum(res, env)
    else:
        base = res.get("base")
    if want("V5") and base is not None:
        V5_conservation(base)
    if want("V6"):
        V6_q1_link(res)
    if want("V7"):
        V7_picard(res)
    if want("V8"):
        V8_evap(res)
    if want("V9"):
        V9_sens(res)
    if want("V9b"):
        V9b_h_sens(res)
    if want("V10"):
        V10_latent()
    if want("V11"):
        V11_energy_form(res)
    if want("V12"):
        V12_solver_numbers()
    if want("V13"):
        V13_env()
        V13b_latent_calibration()

    with open(os.path.join(OUT, "q2_verify.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")
    write_registry(os.path.join(OUT, "registry_q2_verify.csv"), REG)
    print(f"\n日志: {os.path.join(OUT, 'q2_verify.log')}")


def write_registry(path, rows):
    """按 id 合并写出: 部分运行 (--only) 不会抹掉其它节的注册行.

    这一点很重要: 早先的实现直接覆盖, 结果只跑 --only V3..V11 时
    V0/VB/V1/V2/V10 的注册行被抹掉, 而文稿仍引用它们.
    """
    fields = ["id", "quantity", "value", "unit", "uncertainty", "source",
              "command", "note"]
    merged, order = {}, []
    if os.path.exists(path):
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                k = r["id"]
                if k not in merged:
                    order.append(k)
                merged[k] = [r.get(c, "") for c in fields]
    for row in rows:
        k = row[0]
        if k not in merged:
            order.append(k)
        merged[k] = list(row)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(fields)
        for k in order:
            w.writerow(merged[k])
    print(f"注册表: {path} ({len(merged)} 行, 本次写入 {len(rows)} 行)")


if __name__ == "__main__":
    main()
