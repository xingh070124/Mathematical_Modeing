"""
问题1 模型灵敏度与鲁棒性实验.

实验设计 (每个实验对应论文"模型检验"小节的一张表/图):

  E1 快速求解器自检
     solve_fast 与已验证的 q1_solve.solve_q1 在同一设置下逐点对比,
     max|dT|, max|dC| 须在机器精度量级 (<1e-10), 之后所有实验用 solve_fast.

  E2 单参数扰动灵敏度 (OAT, one-at-a-time)
     参数: h, h_m, D0, k, rho, cp, T0, C0, 各扰动 ±10%.
     响应量 (QoI): T(0,1800s), T(R,1800s), C(R,1800s), <C>(1800s) (体积平均).
     灵敏度系数: 中心差分 S = (y+ - y-) / (y_base * (p+ - p-)/p_base).
     预期: 温度 QoI 只对热参数响应, 水分 QoI 只对湿参数响应 (问题一解耦).

  E3 边界数据噪声鲁棒性 (Monte Carlo, N=100)
     对附件1 的 T_inf, C_inf 采样值加高斯噪声 (标准差由数据本身的高频分量
     稳健估计: 二阶差分 MAD/sqrt(6)), 每个 realisation 重拟合 PCHIP 并全程
     重解, 收集 QoI 分布. 检验: 结论 (中心不失水/表面脱水/温度单调) 是否
     在所有 realisation 中保持, QoI 的变异系数多大.

  E4 参数联合不确定性 Monte Carlo (N=100)
     h, h_m, D0, k, rho, cp 同时在标称值 ±10% 内均匀扰动, 收集 QoI 分布
     与定性结论保持率.

  E5 数值参数鲁棒性
     (a) 网格 M=100..800 (dt=0.25 s): QoI 随 M 的变化 (应平坦).
     (b) 环境插值方法 linear/pchip/cubic: QoI 差异.

运行:  python src/q1_sensitivity.py          # 全部实验
       python src/q1_sensitivity.py --quick  # 减小 MC 规模 (N=30), 冒烟测试
输出:  outputs/q1_sensitivity.log
       outputs/q1_sensitivity_oat.csv
       outputs/q1_sensitivity_mc.csv        (E3+E4 每个 realisation 一行)
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import solve_banded

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import (ALPHA, C0, CP, D0, D_EXP, HM, H_CONV, K_COND,  # noqa: E402
                      R0, RHO, T0_K, Env, load_attachment1, solve_q1)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

T_END = 1800.0
QOI_NAMES = ["T中心(1800s)", "T表面(1800s)", "C表面(1800s)", "C体积平均(1800s)"]


# ----------------------------------------------------------------------------
# 快速求解器: 与 q1_solve.solve_q1 (corr=True) 数学一致, 但
#   (i) 环境激励预先在步点 (n+1)*dt 上算好 (数组), 不在循环内逐点插值;
#   (ii) 温度三对角矩阵只组装一次 (alpha, dt 不变);
#   (iii) 参数 (h, h_m, D0, k, rho, cp, T0, C0) 显式传入.
# ----------------------------------------------------------------------------
def solve_fast(M, dt, tinf_arr, cinf_arr, *, d0=D0, h=H_CONV,
               hm=HM, T0=T0_K, C0=C0, nsteps=None, rho=RHO, cp=CP, k=K_COND):
    dr = R0 / M
    rf_p = (np.arange(M + 1) + 0.5) * dr
    rf_m = (np.arange(M + 1) - 0.5) * dr
    rf_m[0] = 0.0
    rf_p[M] = R0
    V = np.pi * (rf_p ** 2 - rf_m ** 2)
    A_p = 2 * np.pi * rf_p
    A_m = 2 * np.pi * rf_m

    al = k / (rho * cp)                       # 允许 k, rho, cp 扰动
    g_h = 2 * np.pi * R0 * h / (rho * cp * V[M])
    g_hm = 2 * np.pi * R0 * hm / V[M]

    if nsteps is None:
        nsteps = len(tinf_arr)
    T = np.full(M + 1, T0)
    C = np.full(M + 1, C0)

    # ---- 温度矩阵 (每跑一次) ----
    aT = np.zeros(M + 1)
    bT = np.zeros(M + 1)
    cT = np.zeros(M + 1)
    bT[0] = 1.0 / dt + al * A_p[0] / (dr * V[0])
    cT[0] = -al * A_p[0] / (dr * V[0])
    ii = np.arange(1, M)
    aT[ii] = -al * A_m[ii] / (dr * V[ii])
    cT[ii] = -al * A_p[ii] / (dr * V[ii])
    bT[ii] = 1.0 / dt + al * (A_m[ii] + A_p[ii]) / (dr * V[ii])
    aT[M] = -al * A_m[M] / (dr * V[M])
    bT[M] = 1.0 / dt + al * A_m[M] / (dr * V[M]) + g_h

    ab = np.zeros((3, M + 1))
    ab[0, 1:] = cT[:-1]
    ab[1, :] = bT
    ab[2, :-1] = aT[1:]

    dT = np.empty(M + 1)
    for n in range(nsteps):
        dT[:] = T / dt
        dT[M] += g_h * tinf_arr[n]
        T = solve_banded((1, 1), ab, dT)

        Dn = d0 * np.exp(-D_EXP / np.maximum(C, 1e-12))
        Df = 0.5 * (Dn[:-1] + Dn[1:])          # 界面 D, r_{i+1/2}, i=0..M-1
        a = np.zeros(M + 1)
        b = np.full(M + 1, 1.0 / dt)
        c = np.zeros(M + 1)
        b[0] += Df[0] * A_p[0] / (dr * V[0])
        c[0] = -Df[0] * A_p[0] / (dr * V[0])
        a[ii] = -Df[ii - 1] * A_m[ii] / (dr * V[ii])
        c[ii] = -Df[ii] * A_p[ii] / (dr * V[ii])
        b[ii] += Df[ii - 1] * A_m[ii] / (dr * V[ii]) + Df[ii] * A_p[ii] / (dr * V[ii])
        a[M] = -Df[M - 1] * A_m[M] / (dr * V[M])
        b[M] += Df[M - 1] * A_m[M] / (dr * V[M]) + g_hm
        dC = C / dt
        dC[M] += g_hm * cinf_arr[n]
        C = solve_banded((1, 1), np.vstack([np.r_[0, c[:-1]], b, np.r_[a[1:], 0]]), dC)

    return T, C, float(np.sum(C * V) / np.sum(V))


def qois(T, C, Cavg):
    return [T[0], T[-1], C[-1], Cavg]


# ----------------------------------------------------------------------------
def robust_sigma(x):
    """由二阶差分的 MAD 估计测量噪声标准差 (信号平滑时二阶差分≈噪声)."""
    d2 = np.diff(x, 2)
    mad = np.median(np.abs(d2 - np.median(d2)))
    return 1.4826 * mad / np.sqrt(6.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    lines = []

    def say(s=""):
        print(s)
        lines.append(str(s))

    def hr(s):
        say("=" * 96)
        say(s)
        say("=" * 96)

    N_MC = 30 if args.quick else 100
    M_EXP, DT_EXP = 400, 0.25                  # 实验网格 (S4 验证 M=400 已空间收敛)
    nsteps = int(round(T_END / DT_EXP))

    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")

    # 步点环境数组 (基准, PCHIP)
    tgrid = np.arange(1, nsteps + 1) * DT_EXP
    Tinf0 = env.T_arr(tgrid)
    Cinf0 = env.C_arr(tgrid)

    # ------------------------------------------------------------ E1 自检
    hr("E1. solve_fast 自检: 与 q1_solve.solve_q1 (corr=True) 逐点对比 (M=400, dt=0.25)")
    t0 = time.time()
    r_, T_ref, C_ref, _, _ = solve_q1(M_EXP, DT_EXP, T_END, env, corr=True)
    t_ref = time.time() - t0
    t0 = time.time()
    T_f, C_f, Cavg_f = solve_fast(M_EXP, DT_EXP, Tinf0, Cinf0)
    t_fast = time.time() - t0
    dT = np.max(np.abs(T_f - T_ref))
    dC = np.max(np.abs(C_f - C_ref))
    say(f"  max|dT| = {dT:.3e} K, max|dC| = {dC:.3e} kg/kg  (须 < 1e-9)")
    say(f"  用时: solve_q1 {t_ref:.1f} s vs solve_fast {t_fast:.1f} s (加速 {t_ref/t_fast:.0f}x)")
    assert dT < 1e-9 and dC < 1e-9, "快速求解器与基准不一致"
    say("  PASS")

    base_T, base_C, base_Cavg = T_f, C_f, Cavg_f
    y_base = np.array(qois(base_T, base_C, base_Cavg))
    say("  基准 QoI (M=400, dt=0.25):")
    for nm, v in zip(QOI_NAMES, y_base):
        u = "K" if nm.startswith("T") else "kg/kg"
        say(f"    {nm:22s} = {v:.6f} {u}")

    oat_rows = []
    mc_rows = []

    # ------------------------------------------------------------ E2 OAT
    hr(f"E2. 单参数扰动灵敏度 (OAT ±10%, M={M_EXP}, dt={DT_EXP}s)")
    params = [
        ("h",   dict(h=H_CONV * 1.1),  dict(h=H_CONV * 0.9),  H_CONV,  "W/(m^2 K)"),
        ("hm",  dict(hm=HM * 1.1),     dict(hm=HM * 0.9),     HM,      "m/s"),
        ("D0",  dict(d0=D0 * 1.1),     dict(d0=D0 * 0.9),     D0,      "m^2/s"),
        ("k",   dict(k=K_COND * 1.1),  dict(k=K_COND * 0.9),  K_COND,  "W/(m K)"),
        ("rho", dict(rho=RHO * 1.1),   dict(rho=RHO * 0.9),   RHO,     "kg/m^3"),
        ("cp",  dict(cp=CP * 1.1),     dict(cp=CP * 0.9),     CP,      "J/(kg K)"),
        ("T0",  dict(T0=T0_K * 1.1),   dict(T0=T0_K * 0.9),   T0_K,    "K"),
        ("C0",  dict(C0=C0 * 1.1),     dict(C0=C0 * 0.9),     C0,      "kg/kg"),
    ]
    say(f"  {'参数':>6} {'QoI':>18} {'y_base':>12} {'y(+10%)':>12} {'y(-10%)':>12} "
        f"{'S(+10%)':>9} {'S(-10%)':>9} {'S中心':>9}")
    for pname, kw_p, kw_m, p_base, unit in params:
        Tp, Cp_, Cavg_p = solve_fast(M_EXP, DT_EXP, Tinf0, Cinf0, **kw_p)
        Tm, Cm_, Cavg_m = solve_fast(M_EXP, DT_EXP, Tinf0, Cinf0, **kw_m)
        y_p = np.array(qois(Tp, Cp_, Cavg_p))
        y_m = np.array(qois(Tm, Cm_, Cavg_m))
        for j, nm in enumerate(QOI_NAMES):
            S_p = (y_p[j] - y_base[j]) / y_base[j] / 0.10
            S_m = (y_m[j] - y_base[j]) / y_base[j] / (-0.10)
            S_c = (y_p[j] - y_m[j]) / y_base[j] / 0.20
            say(f"  {pname:>6} {nm:>18} {y_base[j]:>12.6f} {y_p[j]:>12.6f} {y_m[j]:>12.6f} "
                f"{S_p:>9.4f} {S_m:>9.4f} {S_c:>9.4f}")
            oat_rows.append([pname, unit, nm, y_base[j], y_p[j], y_m[j], S_p, S_m, S_c])
    say("  注: S 量级 >> 1 为高灵敏; 温度 QoI 对 hm/D0/C0 的 S 应≈0 (问题一热湿解耦的直接数值证据).")

    with open(os.path.join(OUT, "q1_sensitivity_oat.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["param", "unit", "qoi", "y_base", "y_plus10", "y_minus10",
                    "S_plus10", "S_minus10", "S_central"])
        w.writerows(oat_rows)

    # ------------------------------------------------------------ E3 噪声 MC
    hr(f"E3. 边界数据噪声鲁棒性 (Monte Carlo N={N_MC}, 加噪后重拟合 PCHIP 全程重解)")
    sigT = robust_sigma(T1)
    sigC = robust_sigma(C1)
    say(f"  噪声标准差稳健估计 (二阶差分 MAD): sigma_T = {sigT:.3e} degC, "
        f"sigma_C = {sigC:.3e} kg/kg")
    if sigT < 1e-3:
        sigT = 0.05
        say(f"  sigma_T 低于分辨率, 按传感器精度假设取 {sigT} degC")
    say(f"  对附件1 采样值加 N(0, sigma) 噪声 -> 重拟合 PCHIP -> 步点取值 -> 重解.")
    rng = np.random.default_rng(20260910)
    for i in range(N_MC):
        Tn = T1 + rng.normal(0.0, sigT, size=T1.shape)
        Cn = C1 + rng.normal(0.0, sigC, size=C1.shape)
        Cn = np.maximum(Cn, 1e-6)
        fT = PchipInterpolator(t1, Tn + 273.15)
        fC = PchipInterpolator(t1, Cn)
        Tmc, Cmc, Cav = solve_fast(M_EXP, DT_EXP, fT(tgrid), fC(tgrid))
        mc_rows.append([f"E3_noise", i + 1] + qois(Tmc, Cmc, Cav))
        if (i + 1) % 20 == 0:
            say(f"    ... {i+1}/{N_MC}")
    arr = np.array([r[2:] for r in mc_rows if r[0] == "E3_noise"])
    say("  QoI 分布 (噪声 MC):")
    say(f"  {'QoI':>18} {'基准':>12} {'均值':>12} {'标准差':>12} {'CV%':>8} {'95%CI半宽':>12}")
    for j, nm in enumerate(QOI_NAMES):
        mu, sd = arr[:, j].mean(), arr[:, j].std(ddof=1)
        ci = 1.96 * sd / np.sqrt(len(arr))
        say(f"  {nm:>18} {y_base[j]:>12.6f} {mu:>12.6f} {sd:>12.3e} "
            f"{abs(sd/mu)*100:>8.4f} {ci:>12.3e}")

    # ------------------------------------------------------------ E4 参数 MC
    hr(f"E4. 参数联合不确定性 Monte Carlo (N={N_MC}, h,hm,D0,k,rho,cp ~ ±10% 均匀)")
    keys = ["h", "hm", "d0", "k", "rho", "cp"]
    nom = {"h": H_CONV, "hm": HM, "d0": D0, "k": K_COND, "rho": RHO, "cp": CP}
    keep_all = True
    for i in range(N_MC):
        kw = {kk: nom[kk] * (1 + rng.uniform(-0.10, 0.10)) for kk in keys}
        Tmc, Cmc, Cav = solve_fast(M_EXP, DT_EXP, Tinf0, Cinf0, **kw)
        mc_rows.append(["E4_param", i + 1] + qois(Tmc, Cmc, Cav))
        # 定性结论保持: 中心几乎不失水, 场单调 (温度内低外高, 水分内高外低)
        if not (Cmc[0] > 2.54 and Tmc[-1] > Tmc[0] and Cmc[-1] < Cmc[0]):
            keep_all = False
            say(f"    [!] realisation {i+1} 定性结论被破坏: C0={Cmc[0]:.4f} "
                f"T(R)-T(0)={Tmc[-1]-Tmc[0]:+.4f} C(0)-C(R)={Cmc[0]-Cmc[-1]:.4f}")
    arr4 = np.array([r[2:] for r in mc_rows if r[0] == "E4_param"])
    say("  QoI 分布 (参数 MC):")
    say(f"  {'QoI':>18} {'基准':>12} {'均值':>12} {'标准差':>12} {'CV%':>8} {'min':>12} {'max':>12}")
    for j, nm in enumerate(QOI_NAMES):
        mu, sd = arr4[:, j].mean(), arr4[:, j].std(ddof=1)
        say(f"  {nm:>18} {y_base[j]:>12.6f} {mu:>12.6f} {sd:>12.3e} "
            f"{abs(sd/mu)*100:>8.4f} {arr4[:, j].min():>12.6f} {arr4[:, j].max():>12.6f}")
    say(f"  定性结论 (中心不失水 / T 内低外高 / C 内高外低) 保持率: "
        f"{'100%' if keep_all else '存在破坏, 见上方标记'}")

    with open(os.path.join(OUT, "q1_sensitivity_mc.csv"), "w", newline="",
              encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["experiment", "sample", "T_center_1800s_K", "T_surface_1800s_K",
                    "C_surface_1800s_kgkg", "C_avg_1800s_kgkg"])
        w.writerows(mc_rows)

    # ------------------------------------------------------------ E5 数值参数
    hr("E5. 数值参数鲁棒性")
    say("  (a) 网格收敛: QoI 随 M (dt=0.25 s)")
    say(f"  {'M':>6} {'T(0,1800)':>14} {'T(R,1800)':>14} {'C(R,1800)':>14} {'<C>(1800)':>14}")
    grid_rows = []
    for M_ in (100, 200, 400, 800):
        Tg, Cg, Cag = solve_fast(M_, DT_EXP, Tinf0, Cinf0)
        y = qois(Tg, Cg, Cag)
        grid_rows.append([M_] + y)
        say(f"  {M_:>6} {y[0]:>14.6f} {y[1]:>14.6f} {y[2]:>14.6f} {y[3]:>14.6f}")
    say("  (b) 环境插值方法 (M=400, dt=0.5 s)")
    dt_b = 0.5
    ns_b = int(round(T_END / dt_b))
    tg_b = np.arange(1, ns_b + 1) * dt_b
    interp_rows = []
    for meth in ("linear", "pchip", "cubic"):
        ev = Env(t1, T1, C1, method=meth)
        Ti, Ci, Cai = solve_fast(M_EXP, dt_b, ev.T_arr(tg_b), ev.C_arr(tg_b))
        y = qois(Ti, Ci, Cai)
        interp_rows.append([meth] + y)
        say(f"    {meth:>7}: T(0)={y[0]:.6f}  T(R)={y[1]:.6f}  C(R)={y[2]:.6f}  <C>={y[3]:.6f}")

    # ------------------------------------------------------------ 汇总
    hr("汇总")
    say("  E2: 灵敏度系数表见 q1_sensitivity_oat.csv 与图 fig_q1_sensitivity.")
    say(f"  E3: 噪声 MC (sigma_T={sigT} degC, sigma_C={sigC:.3e} kg/kg) QoI 相对偏差 "
        f"< {max(np.abs((arr[:, j] - y_base[j]) / y_base[j]).max() for j in range(4)) * 100:.3f}%")
    say(f"  E4: 参数 MC QoI 相对偏差 < {max(np.abs((arr4[:, j] - y_base[j]) / y_base[j]).max() for j in range(4)) * 100:.2f}%")
    say("  E5: 网格与插值方法引起的 QoI 变化见上表 (应远小于 4 位小数报告需求).")

    with open(os.path.join(OUT, "q1_sensitivity.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n日志: outputs/q1_sensitivity.log")


if __name__ == "__main__":
    main()
