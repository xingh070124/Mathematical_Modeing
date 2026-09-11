"""
问题一: 能否"用附件1拟合出一个函数, 再用热传导方程求解析解"?

直接实验回答, 不凭印象. 五个问题:
  Q-a 附件1 的 T_inf(t) 能拟合成什么闭式函数? 拟合残差多大?
  Q-b 拟合函数代进解析解后, 结果与"直接插值"相差多少?
  Q-c 只有 T 能这样做; 水分场能否?
  Q-d 在 0-1800 s 上拟合 vs 在整段 0-14400 s 上拟合, 对问题一的影响?
  Q-e 关键对照: 不拟合, 直接用附件1 原始 31 个点

解析解形式 (线性导热 + Robin 边界 + 变环境温度, Duhamel):
    T(r,t) - T_inf(t) = sum_k b_k(t) J0(lam_k r)
    b_k(t) 满足  db_k/dt = -mu_k b_k - c_k dT_inf/dt,  mu_k = alpha lam_k^2
对分段线性 T_inf 该式有闭式解; 对指数型 T_inf 也有闭式解. 二者即"真解析".

输出: outputs/registry_q1_analytic_fit.csv, outputs/q1_analytic_fit.log
运行: python src/q1_analytic_fit.py
"""

from __future__ import annotations

import csv
import os
import sys

import numpy as np
from scipy.optimize import curve_fit
from scipy.special import j0, j1

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import (  # noqa: E402
    ALPHA, C0, D_of_C, H_CONV, K_COND, R0, T0_K, Env, load_attachment1, solve_q1,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
BI = H_CONV * R0 / K_COND
CMD = "python src/q1_analytic_fit.py"
REG: list = []


def say(s=""):
    print(s)


def add(id_, q, v, u, unc="run", src="run q1_analytic_fit", note=""):
    vs = v if isinstance(v, str) else (f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])
    say(f"    [reg] {id_:16s} {q[:50]:50s} = {vs} {u}")


def write_reg():
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "registry_q1_analytic_fit.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source", "command", "note"])
        w.writerows(REG)
    say(f"\n注册表: {p} ({len(REG)} 行)")


# ---------------------------------------------------------------------------
# 特征值 / 系数 (与 q1_solve 独立实现, 便于交叉验证)
# ---------------------------------------------------------------------------
def eigen(Bi, n_modes):
    from scipy.optimize import brentq
    f = lambda x: x * j1(x) - Bi * j0(x)
    grid = np.linspace(1e-8, 4.0 * n_modes + 40.0, 300 * (n_modes + 20))
    vals = f(grid)
    xs = []
    for k in range(len(grid) - 1):
        if vals[k] * vals[k + 1] < 0:
            xs.append(brentq(f, grid[k], grid[k + 1], xtol=1e-15, rtol=8.9e-16))
        if len(xs) >= n_modes:
            break
    x = np.array(xs)
    lam = x / R0
    c = 2.0 * j1(x) / (x * (j0(x) ** 2 + j1(x) ** 2))
    return x, lam, c


def series_T(times, Tinf, r_eval, x, lam, c, T0=T0_K):
    """Duhamel 半解析解. Tinf 在 times 上被当作分段线性 -> 每段有闭式解."""
    mu = ALPHA * lam ** 2
    b = c * (T0 - Tinf[0])
    snaps = np.empty((len(times), len(x)))
    snaps[0] = b
    for k in range(len(times) - 1):
        d = times[k + 1] - times[k]
        s = (Tinf[k + 1] - Tinf[k]) / d if d > 0 else 0.0
        E = np.exp(-mu * d)
        b = E * b - c * s * (1.0 - E) / mu
        snaps[k + 1] = b
    J = j0(np.outer(lam, np.atleast_1d(r_eval)))
    return Tinf[:, None] + snaps @ J


# ---------------------------------------------------------------------------
# 候选拟合函数
# ---------------------------------------------------------------------------
def f_linear(t, a, b):
    return a + b * t


def f_quad(t, a, b, cc):
    return a + b * t + cc * t ** 2


def f_cubic(t, a, b, cc, d):
    return a + b * t + cc * t ** 2 + d * t ** 3


def f_exp_sat(t, A, B, tau):
    """饱和指数: T_inf = A - B exp(-t/tau). 物理上对应牛顿式升温."""
    return A - B * np.exp(-t / tau)


def f_biexp(t, A, B, t1, C, t2):
    return A - B * np.exp(-t / t1) - C * np.exp(-t / t2)


T_KELVIN = 273.15


def fit_all(t, y, tmax=None):
    """返回 {名字: (y_fit, 参数字典)}.

    注意: 附件1 的 T 为摄氏度, 而 series_T 要求热力学温度.
    拟合在摄氏温标下做 (截距平移, 参数等价), 使用时必须 +273.15.
    """
    m = (t <= tmax) if tmax is not None else np.ones_like(t, bool)
    tt, yy = t[m], y[m]
    out = {}
    for name, fn, p0 in (
        ("线性", f_linear, [yy[0], (yy[-1] - yy[0]) / (tt[-1] - tt[0])]),
        ("二次", f_quad, [yy[0], (yy[-1] - yy[0]) / (tt[-1] - tt[0]), 0.0]),
        ("三次", f_cubic, [yy[0], (yy[-1] - yy[0]) / (tt[-1] - tt[0]), 0.0, 0.0]),
        ("饱和指数", f_exp_sat, [yy[-1] + 5.0, yy[-1] + 5.0 - yy[0], (tt[-1] - tt[0]) / 3.0]),
        ("双指数", f_biexp, [yy[-1] + 5.0, 2.0, 500.0, max(yy[-1] + 3.0 - yy[0], 1.0), 3000.0]),
    ):
        try:
            p, _ = curve_fit(fn, tt, yy, p0=p0, maxfev=200000)
            out[name] = (fn(t, *p), p)
        except Exception as e:
            out[name] = (np.full_like(t, np.nan), str(e))
    return out


# ---------------------------------------------------------------------------
def main():
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    x, lam, c = eigen(BI, 400)
    say("=" * 96)
    say("问题一: 拟合环境函数 + 热传导解析解 的可行性实验")
    say("=" * 96)
    say(f"  Bi = hR/k = {BI:.6f}; 前 4 个特征根 x_k = "
        + ", ".join(f"{v:.10f}" for v in x[:4]))

    tg = np.arange(0.0, 1800.0 + 1.0, 1.0)
    r_out = np.array([0.0, 0.005, 0.010, 0.015, 0.020])
    t_tab = np.array([100, 300, 600, 900, 1200, 1500, 1800], dtype=float)
    ri = np.array([int(np.where(np.isclose(tg, v))[0][0]) for v in t_tab])

    # ---- 参考: 直接对附件1 做 PCHIP 插值 ----
    Tinf_pchip = np.array([env.T(v) for v in tg])
    T_ref = series_T(tg, Tinf_pchip, r_out, x, lam, c)
    say(f"\n  参考(半解析 + PCHIP 环境): T(r=R,t=1800s) = "
        f"{T_ref[-1, -1] - 273.15:.4f} degC")

    r_fv, T_fv, _, _, _ = solve_q1(1600, 0.0125, 1800.0, env, corr=True)
    Tfv_out = np.interp(r_out, r_fv, T_fv)
    d_chain = float(np.max(np.abs(T_ref[-1] - Tfv_out)))
    say(f"  半解析 vs 有限体积生产解 (t=1800s, 5 个输出半径): max|dT| = {d_chain:.3e} K")
    add("G01", "半解析 vs 有限体积 max|dT| (t=1800s)", d_chain, "K", "两条独立实现",
        "run q1_analytic_fit", "确认解析链路可信")

    # ---- Q-a / Q-b: 在 0-1800 s 上拟合 ----
    say("\n" + "=" * 96)
    say("Q-a/Q-b. 在 0-1800 s 上拟合 T_inf(t), 再代进解析解")
    say("=" * 96)
    say(f"  {'拟合形式':<10} {'参数个数':>8} {'max|拟合-数据|[K]':>20} "
        f"{'max|dT| vs 参考 [K]':>22}")
    fits_1800 = fit_all(t1, T1, tmax=1800.0)
    for name, (yfit, p) in fits_1800.items():
        npar = len(p) if not isinstance(p, str) else 0
        mask = t1 <= 1800.0
        rf = float(np.max(np.abs(yfit[mask] - T1[mask])))
        if isinstance(p, str):
            say(f"  {name:<10} {npar:>8} {'拟合失败':>20} {p:>22}")
            continue
        Tinf_f = np.interp(tg, t1, yfit) + T_KELVIN
        Tsol = series_T(tg, Tinf_f, r_out, x, lam, c)
        dT_tab = float(np.max(np.abs(Tsol[ri] - T_ref[ri])))
        dT_all = float(np.max(np.abs(Tsol - T_ref)))
        say(f"  {name:<10} {npar:>8} {rf:>20.3e} {dT_all:>22.3e}   "
            f"(7 时刻 5 半径: {dT_tab:.3e})")
        add(f"G02_{name}_fitres", f"拟合残差 max|fit-data| ({name}, 0-1800s)", rf, "K",
            "最小二乘", "run q1_analytic_fit", f"参数个数 {npar}")
        add(f"G03_{name}_dT", f"解析解偏差 max|dT| ({name}, 0-1800s)", dT_all, "K",
            "vs PCHIP 半解析", "run q1_analytic_fit", "全时段全半径")
        add(f"G04_{name}_dTtab", f"解析解偏差 7时刻x5半径 ({name})", dT_tab, "K",
            "vs PCHIP 半解析", "run q1_analytic_fit", "题面要求的输出点")

    for nm in ("二次", "饱和指数", "双指数"):
        if nm in fits_1800 and not isinstance(fits_1800[nm][1], str):
            p = fits_1800[nm][1]
            say(f"\n  {nm} 参数: " + ", ".join(f"{v:.6g}" for v in p))
            for j, pv in enumerate(p):
                add(f"G07_{nm}_p{j}", f"{nm}拟合参数 p{j}", float(pv), "-",
                    "最小二乘", "run q1_analytic_fit", "")

    # ---- Q-d: 在整段 0-14400 s 上拟合 ----
    say("\n" + "=" * 96)
    say("Q-d. 若在整段 0-14400 s 上拟合, 对问题一(0-1800 s)的影响")
    say("=" * 96)
    say(f"  {'拟合形式':<10} {'0-1800残差[K]':>16} {'0-14400残差[K]':>17} "
        f"{'问题一 max|dT| [K]':>20}")
    fits_full = fit_all(t1, T1, tmax=None)
    for name, (yfit, p) in fits_full.items():
        if isinstance(p, str):
            continue
        mask = t1 <= 1800.0
        r_win = float(np.max(np.abs(yfit[mask] - T1[mask])))
        r_all = float(np.max(np.abs(yfit - T1)))
        Tinf_f = np.interp(tg, t1, yfit) + T_KELVIN
        Tsol = series_T(tg, Tinf_f, r_out, x, lam, c)
        dT = float(np.max(np.abs(Tsol - T_ref)))
        say(f"  {name:<10} {r_win:>16.3e} {r_all:>17.3e} {dT:>20.3e}")
        add(f"G05_{name}_win", f"整段拟合的 0-1800s 残差 ({name})", r_win, "K",
            "最小二乘", "run q1_analytic_fit", "拟合被后段数据主导")
        add(f"G06_{name}_dT", f"整段拟合导致的问题一偏差 ({name})", dT, "K",
            "vs PCHIP 半解析", "run q1_analytic_fit", "")

    # ---- Q-e: 不拟合, 直接用原始点 ----
    say("\n" + "=" * 96)
    say("Q-e. 关键对照: 不拟合, 直接用附件1 原始 31 个点")
    say("=" * 96)
    say("  解析解对分段线性环境温度有逐段闭式解, 所以原始点可直接代入, 不需要拟合.")
    Tinf_pl_raw = np.interp(tg, t1[t1 <= 1800.0], T1[t1 <= 1800.0]) + T_KELVIN
    T_pl_raw = series_T(tg, Tinf_pl_raw, r_out, x, lam, c)
    d_pl = float(np.max(np.abs(T_pl_raw - T_ref)))
    d_pl_tab = float(np.max(np.abs(T_pl_raw[ri] - T_ref[ri])))
    say(f"  原始31点·分段线性(60s) vs PCHIP: 全时段 max|dT| = {d_pl:.3e} K; "
        f"7时刻x5半径 = {d_pl_tab:.3e} K")
    add("G20", "原始31点分段线性 vs PCHIP: 全时段 max|dT|", d_pl, "K",
        "vs PCHIP 半解析", "run q1_analytic_fit", "不拟合的基线")
    add("G21", "原始31点分段线性 vs PCHIP: 7时刻x5半径", d_pl_tab, "K",
        "vs PCHIP 半解析", "run q1_analytic_fit", "题面输出点")
    add("G22", "附件1 温度的记录精度", 1e-3, "degC", "附件1", "run q1_analytic_fit",
        "数据只到 3 位小数")
    say(f"  附件1 温度只记录到 1e-3 degC; 而题面要求输出 4 位小数 (需要 5e-5 degC 分辨率).")
    say(f"  -> 输出位数高于输入数据精度, 四位小数是报告约定而非可达精度指标.")

    say("\n  环境函数处理方式 -> 问题一温度解偏差 (全时段 max|dT|, 单位 K):")
    say(f"    {'原始31点·分段线性':<22} {d_pl:.3e}")
    say(f"    {'原始31点·PCHIP (本文)':<22} {0.0:.3e}   (基准)")
    for name, (yfit, p) in fits_1800.items():
        if isinstance(p, str):
            continue
        Tinf_f = np.interp(tg, t1, yfit) + T_KELVIN
        Tsol = series_T(tg, Tinf_f, r_out, x, lam, c)
        dT = float(np.max(np.abs(Tsol - T_ref)))
        say(f"    {'光滑拟合·' + name:<22} {dT:.3e}")
        add(f"G30_{name}_ratio", f"光滑拟合·{name} 偏差相对不拟合基线的倍数",
            dT / d_pl, "倍", "解析比值", "run q1_analytic_fit",
            f"基线 = 原始31点分段线性 {d_pl:.4e} K")

    # ---- Q-c: 水分场能否解析 ----
    say("\n" + "=" * 96)
    say("Q-c. 水分场能否用同一套解析方法? (D(C) 非线性)")
    say("=" * 96)
    D0v = float(D_of_C(C0))
    say(f"  D(C0=2.55) = {D0v:.6e} m^2/s")
    say("  做法: 把 D 冻结在 D(C0) 当作常数, 用同一条 Bessel+Duhamel 公式解线性扩散方程,")
    say("        再与真正的非线性数值解对照 —— 这给出线性化的上限误差.")
    Bim = 8.0e-7 * R0 / D0v
    xm, lamm, cm = eigen(Bim, 400)
    say(f"  传质 Biot 数 Bi_m = hm R / D(C0) = {Bim:.6f}")
    add("G08", "传质 Biot 数 Bi_m = hm R/D(C0)", float(Bim), "-", "解析精确",
        "run q1_analytic_fit", "")
    add("G09", "D(C0=2.55)", D0v, "m^2/s", "解析精确", "附录2", "线性化取此常数")

    Cinf_lin = np.array([env.C(v) for v in tg])
    mu_c = D0v * lamm ** 2
    b = cm * (C0 - Cinf_lin[0])
    snaps = np.empty((len(tg), len(xm)))
    snaps[0] = b
    for k in range(len(tg) - 1):
        d = tg[k + 1] - tg[k]
        s = (Cinf_lin[k + 1] - Cinf_lin[k]) / d if d > 0 else 0.0
        E = np.exp(-mu_c * d)
        b = E * b - cm * s * (1.0 - E) / mu_c
        snaps[k + 1] = b
    C_lin = Cinf_lin[:, None] + snaps @ j0(np.outer(lamm, r_out))

    r_nl, T_nl, C_nl, _, _ = solve_q1(1600, 0.05, 1800.0, env, corr=True)
    Cnl_out = np.interp(r_out, r_nl, C_nl)
    dC_lin = float(np.max(np.abs(C_lin[-1] - Cnl_out)))
    say(f"  线性化解析 vs 真非线性数值:")
    say(f"     t=1800s 5 个输出半径: max|dC| = {dC_lin:.4e} kg/kg")
    say(f"     (四位小数阈值 5e-5 -> 超出 {dC_lin/5e-5:.0f} 倍)")
    say("  各半径对照 (t=1800s):")
    for j, rr in enumerate(r_out):
        say(f"     r={rr*100:.1f} cm: 线性化 {C_lin[-1, j]:.6f} | 非线性 {Cnl_out[j]:.6f} "
            f"| 差 {C_lin[-1, j]-Cnl_out[j]:+.4e}")
    add("G10", "线性化 D 解析解 vs 非线性数值 max|dC| (t=1800s)", dC_lin, "kg/kg",
        "vs 有限体积", "run q1_analytic_fit", "结论: 水分不能用解析解")
    add("G11", "该偏差相对四位小数阈值的倍数", dC_lin / 5e-5, "倍", "解析比值",
        "run q1_analytic_fit", "阈值 = 5e-5 kg/kg")
    for j, rr in enumerate(r_out):
        add(f"G12_r{int(rr*1000)}", f"线性化含水率 C(r={rr*100}cm,t=1800s)",
            float(C_lin[-1, j]), "kg/kg", "线性化解析", "run q1_analytic_fit", "")
        add(f"G13_r{int(rr*1000)}", f"非线性含水率 C(r={rr*100}cm,t=1800s)",
            float(Cnl_out[j]), "kg/kg", "有限体积", "run q1_analytic_fit", "")
        add(f"G15_r{int(rr*1000)}",
            f"线性化误差 C_lin-C_nonlin (r={rr*100}cm,t=1800s)",
            float(C_lin[-1, j] - Cnl_out[j]), "kg/kg", "解析差值",
            "run q1_analytic_fit", "定义: 线性化减非线性")

    Ddom = float(D_of_C(1.510265658) / D_of_C(2.549992318))
    add("G14", "D 在 t=1800s 计算域内的最大/最小之比", Ddom, "-", "解析比值",
        "run q1_analytic_fit", ">1 即 D 不是常数")
    add("G16", "D(C0)/D(0.15)", float(D_of_C(C0) / D_of_C(0.15)), "倍", "解析比值",
        "run q1_analytic_fit", "干壳效应量级")
    say(f"\n  注: 问题一末端 D 在计算域内变化 {Ddom:.4f} 倍;")
    say("      随干燥推进该倍数迅速增大 -> 线性化在问题 2-4 完全不可用.")

    write_reg()


if __name__ == "__main__":
    main()
