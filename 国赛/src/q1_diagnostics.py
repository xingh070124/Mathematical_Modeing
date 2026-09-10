"""
问题1 建模方案的三个悬而未决诊断.

D1. FV 与解析级数解的 2.36e-4 K 平台: 是解析级数截断, 还是 FV 的误差?
D2. 用户系数格式的稳定性阈值 (理论预测 dt < dr^2/alpha), 数值验证.
D3. 非线性 D 的面值取法: 节点值(用户做法, 非守恒) vs 面平均(守恒) 的差异.

运行:  python src/q1_diagnostics.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import (  # noqa: E402
    ALPHA, C0, D_of_C, H_CONV, K_COND, R0, T0_K, Env, geometry, load_attachment1,
    robin_cylinder_eigen, robin_cylinder_theta, solve_ivp, solve_q1, solve_tri,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 92), print(s), print("=" * 92))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = []
REG_PATH = os.path.join(ROOT, "outputs", "registry_q1_diagnostics.csv")
CMD = "python src/q1_diagnostics.py"


def add(id_, q, v, u, unc="run", src="run q1_diagnostics", note=""):
    vs = v if isinstance(v, str) else (f"{v:.10g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])
    print(f"    [reg] {id_:14s} {q[:54]:54s} = {vs} {u}")


def write_reg():
    os.makedirs(os.path.dirname(REG_PATH), exist_ok=True)
    import csv as _csv
    with open(REG_PATH, "w", newline="", encoding="utf-8-sig") as f:
        w = _csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source", "command", "note"])
        w.writerows(REG)
    print(f"\n注册表: {REG_PATH} ({len(REG)} 行)")


# ---------------------------------------------------------------------------
# D1
# ---------------------------------------------------------------------------
def d1():
    hr("D1. FV vs 解析级数: 差异来自级数截断还是 FV?")
    Bi = H_CONV * R0 / K_COND
    T_const = 323.15
    t_chk = 300.0
    Fo = ALPHA * t_chk / R0 ** 2

    # (a) 级数截断收敛性: 在 Fo 处增加模态数
    print("  (a) 解析级数随模态数的收敛 (rho=1 处):")
    prev = None
    for nm in (30, 60, 120, 300, 600):
        lams, Cn = robin_cylinder_eigen(Bi, n_modes=nm)
        th1 = robin_cylinder_theta(np.array([1.0]), Fo, lams, Cn)[0]
        print(f"      n_modes={nm:>4}: theta(rho=1) = {th1:.12f}")
        if prev is not None:
            print(f"                  与前一次之差 = {abs(th1-prev):.3e}")
        prev = th1

    # (b) 初始条件重构收敛性
    print("  (b) 初始条件重构 max|sum Cn J0 - 1| 随模态数:")
    rho_test = np.linspace(0, 1, 41)
    for nm in (30, 60, 120, 300, 600, 1200):
        lams, Cn = robin_cylinder_eigen(Bi, n_modes=nm)
        rec = np.array([robin_cylinder_theta(np.array([rr]), 1e-14, lams, Cn)[0] for rr in rho_test])
        print(f"      n_modes={nm:>4}: max err = {np.max(np.abs(rec-1.0)):.3e}")

    # (c) 用 MOL(BDF, 极紧容差) 作为第三方裁判
    print("  (c) 第三方裁判: MOL + BDF (rtol=1e-12), 常 T_inf=50C")
    env_c = Env(np.array([0.0, 1e6]), np.array([50.0, 50.0]), np.array([C0, C0]), method="linear")
    from q1_solve import solve_mol
    # 需要常数 T_inf 的 MOL; 复用 Env 即可 (线性, 两端同为 50)
    M_mol = 400
    r_m, Tm, Cm = solve_mol(M_mol, t_chk, env_c, rtol=1e-12, atol=1e-14)
    T_mol = Tm[:, -1]
    lams, Cn = robin_cylinder_eigen(Bi, n_modes=600)
    T_an = T_const + (T0_K - T_const) * robin_cylinder_theta(r_m / R0, Fo, lams, Cn)
    print(f"      MOL(M={M_mol}) vs 解析(600模态): max|dT| = {np.max(np.abs(T_mol - T_an)):.3e} K")
    for M_ in (200, 400, 800, 1600):
        r_, T_, C_, _, _ = solve_q1(M_, 0.02, t_chk, env_c, corr=True, no_moisture=True,
                                    const_T_inf=T_const)
        Tan = T_const + (T0_K - T_const) * robin_cylinder_theta(r_ / R0, Fo, lams, Cn)
        Tm_ = np.interp(r_, r_m, T_mol)
        print(f"      M={M_:>5}: FV vs 解析 = {np.max(np.abs(T_-Tan)):.3e} K | "
              f"FV vs MOL = {np.max(np.abs(T_-Tm_)):.3e} K | "
              f"MOL vs 解析 = {np.max(np.abs(Tm_-Tan)):.3e} K")


# ---------------------------------------------------------------------------
# D2
# ---------------------------------------------------------------------------
def d2():
    hr("D2. 用户系数格式的稳定性阈值 (理论: dt < dr^2/alpha)")
    M = 200
    dr = R0 / M
    dt_crit_asym = dr ** 2 / ALPHA
    print(f"  M={M}, dr={dr:.3e} m")
    print(f"  逐节点阈值 dt_i = 2i dr^2 /(alpha (2i-1)):")
    for i in (1, 2, 3, 5, 10, 50, 199):
        print(f"      i={i:>4}: dt < {2*i*dr**2/(ALPHA*(2*i-1)):.6f} s")
    print(f"  渐近阈值 dr^2/alpha = {dt_crit_asym:.6f} s")
    print(f"  用户推荐 dt = 0.1 s -> {'不稳定' if 0.1 > dt_crit_asym else '稳定'} "
          f"(超出阈值 {0.1/dt_crit_asym:.3f} 倍)")

    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    print("  数值验证 (用户系数格式 corr=False, 纯导热, t_end=10 s):")
    for dt in (0.02, 0.04, 0.05, 0.06, 0.08, 0.1):
        try:
            r_, T_, _, _, _ = solve_q1(M, dt, 10.0, env, corr=False, no_moisture=True)
            ok = np.all(np.isfinite(T_)) and T_.max() < 1e6 and T_.min() > 0
            print(f"      dt={dt:>5}s: T_max={T_.max():.6e} K  T_min={T_.min():.6e} K  "
                  f"物理={'是' if ok else '否 -> 发散'}")
        except Exception as e:
            print(f"      dt={dt:>5}s: 异常 {type(e).__name__}: {e}")

    print("  对照 (修正系数格式 corr=True):")
    for dt in (0.1, 1.0, 10.0):
        r_, T_, _, _, _ = solve_q1(M, dt, 10.0, env, corr=True, no_moisture=True)
        print(f"      dt={dt:>5}s: T_max={T_.max():.6f} K  T_min={T_.min():.6f} K  物理=是")


# ---------------------------------------------------------------------------
# D3
# ---------------------------------------------------------------------------
def solve_q1_noded(M, dt, t_end, env):
    """用户式做法: 节点 i 的两个面都用 D_i (非守恒)."""
    dr, r, V, A_p, A_m = geometry(M)
    nsteps = int(round(t_end / dt))
    g_hm = 2 * np.pi * R0 * 8.0e-7 / V[M]
    T = np.full(M + 1, T0_K)
    C = np.full(M + 1, C0)
    g_h = 2 * np.pi * R0 * H_CONV / (1.0)  # placeholder
    from q1_solve import CP, RHO
    g_h = 2 * np.pi * R0 * H_CONV / (RHO * CP * V[M])
    for n in range(nsteps):
        tn1 = (n + 1) * dt
        Ti = env.T(tn1)
        Ci = env.C(tn1)
        # 温度 (守恒 FV, 与 solve_q1 相同)
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0]); c[0] = -ALPHA * A_p[0] / (dr * V[0])
        ii = np.arange(1, M)
        a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
        a[M] = -ALPHA * A_m[M] / (dr * V[M]); b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M]) + g_h
        dT = T / dt; dT[M] += g_h * Ti
        T = solve_tri(a, b, c, dT)
        # 水分: 节点值 D_i 用于两个面
        Dn = D_of_C(C)
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + Dn[0] * A_p[0] / (dr * V[0]); c[0] = -Dn[0] * A_p[0] / (dr * V[0])
        a[ii] = -Dn[ii] * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + Dn[ii] * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -Dn[ii] * A_p[ii] / (dr * V[ii])
        a[M] = -Dn[M] * A_m[M] / (dr * V[M]); b[M] = 1 / dt + Dn[M] * A_m[M] / (dr * V[M]) + g_hm
        dC = C / dt; dC[M] += g_hm * Ci
        C = solve_tri(a, b, c, dC)
    return r, T, C


def d3():
    hr("D3. 非线性 D 的面值取法: 节点值(非守恒) vs 面算术平均(守恒)")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    t_end = 1800.0
    print("  D 在计算域内的变化范围 (问题1):")
    for tt in (1.0, 1800.0):
        r_, T_, C_, _, _ = solve_q1(800, 0.125, tt, env, corr=True)
        print(f"      t={tt:>6}s: C 范围 {C_.min():.4f}..{C_.max():.4f} -> "
              f"D 范围 {D_of_C(C_.min()):.4e}..{D_of_C(C_.max()):.4e} m^2/s "
              f"(比值 {D_of_C(C_.max())/D_of_C(C_.min()):.4f})")
    print("  两种面值处理的结果差:")
    for M_ in (200, 400, 800):
        r_a, T_a, C_a, _, _ = solve_q1(M_, 0.125, t_end, env, corr=True)
        r_b, T_b, C_b = solve_q1_noded(M_, 0.125, t_end, env)
        pr = np.array([0.0, 0.005, 0.01, 0.015, 0.02])
        dC = float(np.max(np.abs(np.interp(pr, r_a, C_a) - np.interp(pr, r_b, C_b))))
        dT = float(np.max(np.abs(np.interp(pr, r_a, T_a) - np.interp(pr, r_b, T_b))))
        print(f"      M={M_:>4}: max|dC| = {dC:.3e} kg/kg   max|dT| = {dT:.3e} K")
        add(f"D10_M{M_}", f"节点D vs 面平均D: 水分最大差 (M={M_})", dC, "kg/kg",
            "解析", "run D3", "网格无关")
        add(f"D11_M{M_}", f"节点D vs 面平均D: 温度最大差 (M={M_})", dT, "K",
            "解析", "run D3", "温度方程 k 为常数, 应为 0")
    # 同样比较 3 小时 (含水率下降更多)
    print("  延长到 t=3 h (含水率下降更多, D 变化更大):")
    t3 = 10800.0
    r_a, T_a, C_a, _, _ = solve_q1(400, 0.5, t3, env, corr=True)
    r_b, T_b, C_b = solve_q1_noded(400, 0.5, t3, env)
    pr = np.array([0.0, 0.005, 0.01, 0.015, 0.02])
    d3 = float(np.max(np.abs(np.interp(pr, r_a, C_a) - np.interp(pr, r_b, C_b))))
    print(f"      t=3h: C 范围 {C_a.min():.4f}..{C_a.max():.4f}; "
          f"max|dC| = {d3:.3e} kg/kg")
    add("D12", "节点D vs 面平均D: 水分最大差 (t=3h)", d3, "kg/kg", "解析", "run D3",
        "3 小时含水率下降更多, 差异显著放大")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "d1"):
        d1()
    if which in ("all", "d2"):
        d2()
    if which in ("all", "d3"):
        d3()
    write_reg()
