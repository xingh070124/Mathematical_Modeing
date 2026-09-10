"""
问题1 建模方案的后续诊断 (第二轮).

E1. 用户系数格式的失稳机理: 算子特征值 + 实际失稳 dt 阈值扫描.
E2. 非线性 D 面值的离散质量守恒残差 (守恒 vs 非守恒).
E3. FV 与解析级数解在 dt -> 0 时的吻合 (确认 2.36e-4 K 平台是时间步误差).

运行:  python src/q1_energy_check.py
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import (  # noqa: E402
    ALPHA, C0, CP, H_CONV, HM, K_COND, R0, RHO, T0_K, Env, geometry,
    load_attachment1, robin_cylinder_eigen, robin_cylinder_theta, solve_q1,
    solve_tri,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 92), print(s), print("=" * 92))

# ---------------------------------------------------------------------------
# 数字注册表 (每个打印出来的数值都要有登记)
# ---------------------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = []
REG_PATH = os.path.join(ROOT, "outputs", "registry_q1_energy.csv")
CMD = "python src/q1_energy_check.py"


def add(id_, q, v, u, unc="run", src="run q1_energy_check", note=""):
    vs = v if isinstance(v, str) else (f"{v:.10g}" if isinstance(v, (int, float, np.floating)) else str(v))
    REG.append([id_, q, vs, u, unc, src, CMD, note])
    print(f"    [reg] {id_:12s} {q[:56]:56s} = {vs} {u}")


def write_reg():
    os.makedirs(os.path.dirname(REG_PATH), exist_ok=True)
    import csv as _csv
    with open(REG_PATH, "w", newline="", encoding="utf-8-sig") as f:
        w = _csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty", "source", "command", "note"])
        w.writerows(REG)
    print(f"\n注册表: {REG_PATH} ({len(REG)} 行)")


def operator_matrices(M):
    """返回 (正确算子 A_corr, 用户算子 A_user) 在 dT/dt = A T 的约定下."""
    dr, r, V, A_p, A_m = geometry(M)
    n = M + 1
    A_c = np.zeros((n, n))
    A_u = np.zeros((n, n))
    # node 0
    A_c[0, 0] = -ALPHA * A_p[0] / (dr * V[0])
    A_c[0, 1] = ALPHA * A_p[0] / (dr * V[0])
    A_u[0] = A_c[0]
    ii = np.arange(1, M)
    for i in ii:
        A_c[i, i - 1] = ALPHA * A_m[i] / (dr * V[i])
        A_c[i, i] = -ALPHA * (A_m[i] + A_p[i]) / (dr * V[i])
        A_c[i, i + 1] = ALPHA * A_p[i] / (dr * V[i])
        A_u[i, i - 1] = ALPHA * A_m[i] / (dr * V[i])
        A_u[i, i] = -ALPHA * A_p[i] / (dr * V[i])       # 缺 |a_i| 项
        A_u[i, i + 1] = ALPHA * A_p[i] / (dr * V[i])
    A_c[M, M - 1] = ALPHA * A_m[M] / (dr * V[M])
    A_c[M, M] = -ALPHA * A_m[M] / (dr * V[M])
    A_u[M] = A_c[M]
    return A_c, A_u


def e1():
    hr("E1. 用户系数格式的失稳机理与阈值")
    M = 200
    A_c, A_u = operator_matrices(M)
    ev_c = np.linalg.eigvals(A_c)
    ev_u = np.linalg.eigvals(A_u)
    print(f"  M={M}")
    print(f"  正确算子 A_corr:  max Re(lambda) = {ev_c.real.max():.6e} 1/s   (应 <= 0, 耗散)")
    print(f"  用户算子 A_user:  max Re(lambda) = {ev_u.real.max():.6e} 1/s   (应 <= 0!)")
    print(f"  用户算子行和 (应恒为 0): min={np.min(A_u.sum(1)):.6e}, max={np.max(A_u.sum(1)):.6e}")
    print(f"  正确算子行和:            min={np.min(A_c.sum(1)):.6e}, max={np.max(A_c.sum(1)):.6e}")
    lam_max = ev_u.real.max()
    lam_min_corr = ev_c.real.max()
    add("E01", "正确算子 max Re(lambda)", float(lam_min_corr), "1/s", "解析", "run E1",
        "应 <= 0 (耗散)")
    add("E02", "用户算子 max Re(lambda)", float(lam_max), "1/s", "解析", "run E1",
        ">0 => 反耗散")
    add("E03", "用户算子行和 max (应恒为 0)", float(np.max(A_u.sum(1))), "1/s", "解析", "run E1", "")
    add("E04", "正确算子行和 max |.|", float(np.max(np.abs(A_c.sum(1)))), "1/s", "解析", "run E1",
        "机器精度零")
    add("E05", "理论放大型失稳阈值 2/lambda_max", float(2 / lam_max), "s", "解析", "run E1",
        "dt < 该值时扰动被放大")
    print(f"  隐式 Euler 放大因子 = 1/|1 - dt*lambda|; 发散当 dt*lambda > 2")
    print(f"  dt*lambda_max > 2  <=>  dt > {2/lam_max if lam_max>0 else float('inf'):.6f} s")

    # 数值扫描: 找到真正失稳的 dt
    print("  实际数值扫描 (t_end=5 s, 纯导热, 用户格式):")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    stable_hi = None
    for dt in (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1):
        r_, T_, _, _, _ = solve_q1(M, dt, 5.0, env, corr=False, no_moisture=True)
        growth = T_.max() / T0_K
        ok = growth < 1.05
        print(f"      dt={dt:>7}s: T_max={T_.max():.6e} K  放大={growth:.4e}  "
              f"{'稳定' if ok else '发散'}")
        add(f"E06_dt{dt}", f"用户格式 dt={dt}s 在 t=5s 的放大倍数", float(growth), "-",
            "解析", "run E1", ">1 即发散")
        add(f"E07_dt{dt}", f"用户格式 dt={dt}s 在 t=5s 的温度最大值", float(T_.max()), "K",
            "解析", "run E1", "物理上界约 301 K")
        add(f"E08_dt{dt}", f"用户格式 dt={dt}s 在 t=5s 的温度最小值", float(T_.min()), "K",
            "解析", "run E1", "")
    # 精确二分阈值
    lo, hi = 0.0001, 0.1
    def stable(dt):
        try:
            r_, T_, _, _, _ = solve_q1(M, dt, 2.0, env, corr=False, no_moisture=True)
            return np.all(np.isfinite(T_)) and T_.max() < 1.05 * T0_K
        except Exception:
            return False
    if not stable(lo):
        print(f"      dt={lo} 即已发散 -> 不存在可用的稳定时间步")
    else:
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            if stable(mid):
                lo = mid
            else:
                hi = mid
        print(f"      数值二分失稳阈值约 dt* = {lo:.6f} s (理论 2/Re(lambda_max) = {2/lam_max:.6f} s)")

    # 正特征值谱与真正的溢出阈值
    evp = ev_u.real[ev_u.real > 1e-9]
    add("E09", "用户算子正特征值个数 (M=200)", len(evp), "个", "解析", "run E1", "")
    add("E10", "用户算子最小正特征值", float(evp.min()), "1/s", "解析", "run E1",
        "控制幅值增长")
    add("E11", "溢出停止阈值 2/lambda_min^+", float(2 / evp.min()), "s", "解析", "run E1",
        "dt >= 此值才不再溢出(但仍为符号振荡)")
    print(f"  正特征值 {len(evp)} 个, 范围 [{evp.min():.6f}, {evp.max():.6f}] 1/s")
    print(f"  => 溢出停止阈值 2/lambda_min^+ = {2/evp.min():.6f} s "
          f"(而非 2/lambda_max = {2/evp.max():.6f} s)")
    # 放大规律: 隐式 Euler 为 (1-lambda*dt)^(-n), 不是 (1+lambda*dt)^n
    print("  放大规律校验 (lambda_max, t=5 s):")
    for dt in (0.0005, 0.005, 0.05):
        n = int(round(5.0 / dt))
        ldt = lam_max * dt
        if ldt < 1:
            correct = (1 - ldt) ** (-n)
            wrong = (1 + ldt) ** n
            print(f"      dt={dt:>7}: (1-l*dt)^-n = {correct:.4e} (正确); "
                  f"(1+l*dt)^n = {wrong:.4e} (错误)")
            add(f"E15_dt{dt}_correct", f"放大规律 (1-l*dt)^-n (dt={dt},t=5s)",
                float(correct), "-", "解析", "run E1", "隐式 Euler 正确形式")
            add(f"E16_dt{dt}_wrong", f"放大规律 (1+l*dt)^n (dt={dt},t=5s)",
                float(wrong), "-", "解析", "run E1", "错误形式, 仅作对照")
    print("  dt 扫描 (t_end=1800 s, 用户格式):")
    for dt in (0.5, 1, 2, 3, 5, 6, 7, 7.4, 7.4683, 7.5, 10, 20):
        try:
            r_, T_, _, _, _ = solve_q1(M, dt, 1800.0, env, corr=False, no_moisture=True)
            fin = bool(np.all(np.isfinite(T_)))
            print(f"      dt={dt:>7}: 有限={fin}  T in [{T_.min():.4g}, {T_.max():.4g}] K")
            add(f"E12_dt{dt}_fin", f"用户格式 dt={dt}s 在 1800 s 是否有限", str(fin), "-",
                "解析", "run E1", "")
            if fin:
                add(f"E13_dt{dt}_min", f"用户格式 dt={dt}s 的 T 最小值", float(T_.min()), "K",
                    "解析", "run E1", f"物理值应为 {T0_K:.2f} K 附近")
                add(f"E14_dt{dt}_max", f"用户格式 dt={dt}s 的 T 最大值", float(T_.max()), "K",
                    "解析", "run E1", "")
        except Exception as ex:
            print(f"      dt={dt:>7}: 异常 {type(ex).__name__} (溢出)")
            add(f"E12_dt{dt}_fin", f"用户格式 dt={dt}s 在 1800 s 是否有限", "False", "-",
                "解析", "run E1", "抛出 " + type(ex).__name__)


def mass_balance(M, dt, t_end, env, scheme):
    """离散水量守恒残差: d(sum V_i C_i)/dt 应等于 -2*pi*R*hm*(C_M - C_inf)."""
    dr, r, V, A_p, A_m = geometry(M)
    nsteps = int(round(t_end / dt))
    g_hm = 2 * np.pi * R0 * HM / V[M]
    g_h = 2 * np.pi * R0 * H_CONV / (RHO * CP * V[M])
    T = np.full(M + 1, T0_K)
    C = np.full(M + 1, C0)
    ii = np.arange(1, M)

    W0 = float(np.sum(V * C))
    acc_surf = 0.0
    for n in range(nsteps):
        tn1 = (n + 1) * dt
        Ti, Ci = env.T(tn1), env.C(tn1)
        # 温度 (始终用守恒格式, 与水分无关)
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0]); c[0] = -ALPHA * A_p[0] / (dr * V[0])
        a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
        a[M] = -ALPHA * A_m[M] / (dr * V[M]); b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M]) + g_h
        dT = T / dt; dT[M] += g_h * Ti
        T = solve_tri(a, b, c, dT)
        # 水分
        Dn = D_of_C_local = 7e-9 * np.exp(-0.89 / np.maximum(C, 1e-12))
        if scheme == "face":
            Df = 0.5 * (Dn[:-1] + Dn[1:])
            Dm_f = np.concatenate([[Df[0]], Df])      # 内侧面 (node 0 用第一个面)
            Dp_f = np.concatenate([Df, [Df[-1]]])     # 外侧面
        else:
            Dm_f = Dn.copy()
            Dp_f = Dn.copy()
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + Dp_f[0] * A_p[0] / (dr * V[0]); c[0] = -Dp_f[0] * A_p[0] / (dr * V[0])
        a[ii] = -Dm_f[ii] * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + Dm_f[ii] * A_m[ii] / (dr * V[ii]) + Dp_f[ii] * A_p[ii] / (dr * V[ii])
        c[ii] = -Dp_f[ii] * A_p[ii] / (dr * V[ii])
        a[M] = -Dm_f[M] * A_m[M] / (dr * V[M])
        b[M] = 1 / dt + Dm_f[M] * A_m[M] / (dr * V[M]) + g_hm
        dC = C / dt; dC[M] += g_hm * Ci
        C = solve_tri(a, b, c, dC)
        acc_surf += 2 * np.pi * R0 * HM * (Ci - C[M]) * dt
    W1 = float(np.sum(V * C))
    return W1 - W0, acc_surf


def e2():
    hr("E2. 离散水量守恒残差 (节点值 D vs 面平均 D)")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    t_end = 1800.0
    print(f"  {'M':>5} {'scheme':>6} {'dW(内部)':>18} {'表面累计通量':>18} {'残差':>16} {'相对':>12}")
    for M in (100, 200, 400):
        for sch in ("face", "node"):
            dW, acc = mass_balance(M, 0.25, t_end, env, sch)
            res = dW - acc
            rel = abs(res) / max(abs(acc), 1e-30)
            print(f"  {M:>5} {sch:>6} {dW:>18.10e} {acc:>18.10e} {res:>16.6e} {rel:>12.3e}")
            add(f"E10_{sch}_M{M}", f"水量收支残差 ({sch}, M={M})", float(res),
                "kg/kg*m^2", "解析", "run E2", "")
            add(f"E11_{sch}_M{M}", f"水量收支相对残差 ({sch}, M={M})", float(rel), "-",
                "解析", "run E2", "节点值取法应不随网格收敛到 0")
            add(f"E12_{sch}_M{M}", f"内部水量变化 ({sch}, M={M})", float(dW),
                "kg/kg*m^2", "解析", "run E2", "")


def e3():
    hr("E3. FV vs 解析级数解: dt -> 0 极限")
    Bi = H_CONV * R0 / K_COND
    lams, Cn = robin_cylinder_eigen(Bi, n_modes=200)
    T_const = 323.15
    t_chk = 300.0
    Fo = ALPHA * t_chk / R0 ** 2
    env_c = Env(np.array([0.0, 1e6]), np.array([50.0, 50.0]), np.array([C0, C0]), method="linear")
    print(f"  Bi={Bi:.6f}, Fo={Fo:.6f}, 解析(theta(rho=1)={robin_cylinder_theta(np.array([1.0]),Fo,lams,Cn)[0]:.10f})")
    print(f"  {'M':>6} {'dt[s]':>9} {'max|T_FV - T_analytic| [K]':>30}")
    for M in (200, 400, 800):
        for dt in (0.05, 0.01, 0.002, 0.0005):
            r_, T_, _, _, _ = solve_q1(M, dt, t_chk, env_c, corr=True, no_moisture=True,
                                       const_T_inf=T_const)
            Tan = T_const + (T0_K - T_const) * robin_cylinder_theta(r_ / R0, Fo, lams, Cn)
            e = float(np.max(np.abs(T_ - Tan)))
            print(f"  {M:>6} {dt:>9.4f} {e:>30.6e}")
            add(f"E20_M{M}_dt{dt}", f"FV vs 解析级数 max|dT| (M={M}, dt={dt}s)", e, "K",
                "解析级数 200 项", "run E3", f"Fo={Fo:.6f}")


def solve_surface_variant(M, dt, t_end, T_const, variant="flux"):
    """纯导热 + 常 T_inf, 只改表面节点系数, 隔离表面处理的影响.

    variant="flux" : 本文做法 —— 外侧界面直接代入第三类边界的实际热流
                     a_M = -alpha*f_M^-/dr, b_M = 1/dt + alpha*f_M^-/dr + g_h
    variant="cell" : 原方案写法 —— 整格控制体近似
                     a_M = -2*alpha/dr^2, b_M = 1/dt + 2*alpha/dr^2 + 2*alpha*h/(k*dr)
    """
    dr, r, V, A_p, A_m = geometry(M)
    nsteps = int(round(t_end / dt))
    g_h = 2 * np.pi * R0 * H_CONV / (RHO * CP * V[M])
    fM = A_m[M] / V[M]
    T = np.full(M + 1, T0_K)
    n = M + 1
    ii = np.arange(1, M)
    for _ in range(nsteps):
        a = np.zeros(n); b = np.zeros(n); c = np.zeros(n)
        b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0]); c[0] = -ALPHA * A_p[0] / (dr * V[0])
        a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
        if variant == "flux":
            a[M] = -ALPHA * fM / dr
            b[M] = 1 / dt + ALPHA * fM / dr + g_h
        else:
            a[M] = -2 * ALPHA / dr ** 2
            b[M] = 1 / dt + 2 * ALPHA / dr ** 2 + 2 * ALPHA * H_CONV / (K_COND * dr)
        d = T / dt
        d[M] += g_h * T_const
        T = solve_tri(a, b, c, d)
        if not np.all(np.isfinite(T)):
            raise RuntimeError("diverged")
    return r, T


def e4():
    hr("E4. 表面节点系数的两种取法 vs 解析级数解 (纯导热, 常 T_inf=50C)")
    Bi = H_CONV * R0 / K_COND
    lams, Cn = robin_cylinder_eigen(Bi, n_modes=400)
    T_const = 323.15
    t_chk = 300.0
    Fo = ALPHA * t_chk / R0 ** 2
    print(f"  Bi={Bi:.6f}, Fo={Fo:.6f}, t={t_chk}s")
    print(f"  {'M':>6} {'dt[s]':>10} {'flux(本文) [K]':>18} {'cell(原方案) [K]':>20} {'比值':>10}")
    for M in (400, 800, 1600):
        for dt in (0.02, 0.002, 0.0005):
            e = {}
            for var in ("flux", "cell"):
                r_, T_ = solve_surface_variant(M, dt, t_chk, T_const, var)
                Tan = T_const + (T0_K - T_const) * robin_cylinder_theta(r_ / R0, Fo, lams, Cn)
                e[var] = float(np.max(np.abs(T_ - Tan)))
            print(f"  {M:>6} {dt:>10.4f} {e['flux']:>18.6e} {e['cell']:>20.6e} "
                  f"{e['cell']/e['flux']:>10.3f}")
            add(f"E30_M{M}_dt{dt}_flux", f"表面取法=通量(本文) vs 解析 (M={M},dt={dt})",
                e["flux"], "K", "解析级数 400 项", "run E4", "")
            add(f"E31_M{M}_dt{dt}_cell", f"表面取法=整格(原方案) vs 解析 (M={M},dt={dt})",
                e["cell"], "K", "解析级数 400 项", "run E4", "")
            add(f"E32_M{M}_dt{dt}_ratio", f"表面取法误差比 cell/flux (M={M},dt={dt})",
                e["cell"] / e["flux"], "-", "解析比值", "run E4", "")


def solve_q1_user_diag_moist(M, dt, t_end, env):
    """温度用修正格式, 水分用原方案的对角元 (b_i = 1/dt + c_i), 检验水分是否失稳.

    返回 (t_blow, C_min, C_max).  t_blow = 首次出现非有限值的时刻 (s), 未失稳则为 None.
    """
    dr, r, V, A_p, A_m = geometry(M)
    nsteps = int(round(t_end / dt))
    g_h = 2 * np.pi * R0 * H_CONV / (RHO * CP * V[M])
    g_hm = 2 * np.pi * R0 * HM / V[M]
    T = np.full(M + 1, T0_K)
    C = np.full(M + 1, C0)
    ii = np.arange(1, M)
    t_blow = None
    for n in range(nsteps):
        tn1 = (n + 1) * dt
        Ti, Ci = env.T(tn1), env.C(tn1)
        # 温度: 修正格式
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0]); c[0] = -ALPHA * A_p[0] / (dr * V[0])
        a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
        a[M] = -ALPHA * A_m[M] / (dr * V[M]); b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M]) + g_h
        d = T / dt; d[M] += g_h * Ti
        T = solve_tri(a, b, c, d)
        # 水分: 原方案对角元 (缺 |a_i| 项), 面值用界面平均以隔离对角元错误的影响
        Dn = 7e-9 * np.exp(-0.89 / np.maximum(C, 1e-12))
        Df = 0.5 * (Dn[:-1] + Dn[1:])
        g_ip = A_p / (dr * V); g_im = A_m / (dr * V)
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        b[0] = 1 / dt + Df[0] * g_ip[0]; c[0] = -Df[0] * g_ip[0]
        a[ii] = -Df[ii - 1] * g_im[ii]
        b[ii] = 1 / dt + Df[ii] * g_ip[ii]          # <-- 原方案: 缺 Df[ii-1]*g_im[ii]
        c[ii] = -Df[ii] * g_ip[ii]
        a[M] = -Df[M - 1] * g_im[M]
        b[M] = 1 / dt + g_hm                        # <-- 原方案: 缺 Df[M-1]*g_im[M]
        dC = C / dt; dC[M] += g_hm * Ci
        C = solve_tri(a, b, c, dC)
        if t_blow is None and not np.all(np.isfinite(C)):
            t_blow = float(tn1)
            break
    return t_blow, float(np.nanmin(C)), float(np.nanmax(C))


def e5():
    hr("E5. 原方案对角元对水分场的影响 (温度场始终用修正格式)")
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")
    M = 200
    print(f"  M={M}, t_end=1800 s")
    print(f"  {'dt[s]':>7} {'水分对角元':>10} {'失稳时刻[s]':>13} {'C_min':>16} {'C_max':>16}")
    for dt in (0.1, 0.05, 0.01):
        tb, cmin, cmax = solve_q1_user_diag_moist(M, dt, 1800.0, env)
        tbs = "未失稳" if tb is None else f"{tb:.1f}"
        print(f"  {dt:>7} {'原方案':>10} {tbs:>13} {cmin:>16.6e} {cmax:>16.6e}")
        if tb is not None:
            add(f"E40_dt{dt}", f"水分方程采用原方案对角元时的失稳时刻 (dt={dt}s)", tb, "s",
                "解析", "run E5", "随网格/时间步均不改善")
            add(f"E41_dt{dt}", f"失稳时 C_min (dt={dt}s)", cmin, "kg/kg", "解析", "run E5", "")
            add(f"E42_dt{dt}", f"失稳时 C_max (dt={dt}s)", cmax, "kg/kg", "解析", "run E5", "")
        r_, T_, C_, _, _ = solve_q1(M, dt, 1800.0, env, corr=True)
        print(f"  {dt:>7} {'修正':>10} {'未失稳':>13} {C_.min():>16.6e} {C_.max():>16.6e}")
        add(f"E43_dt{dt}", f"修正格式的水分最小值 (dt={dt}s)", float(C_.min()), "kg/kg",
            "解析", "run E5", "")
        add(f"E44_dt{dt}", f"修正格式的水分最大值 (dt={dt}s)", float(C_.max()), "kg/kg",
            "解析", "run E5", "")


def e6():
    """精确半控制体系数与用户写法的逐项比较 (证明首项一致, 偏差 O(1/M))."""
    hr("E6. 精确半控制体表面系数 vs 用户写法")
    print(f"  {'M':>6} {'a_M_exact':>18} {'-2a/dr^2':>18} {'比值':>12} "
          f"{'g_h_exact':>16} {'2ah/(k dr)':>16} {'比值':>12}")
    for M in (200, 800, 3200):
        dr = R0 / M
        V_M = np.pi * (R0 ** 2 - (R0 - dr / 2) ** 2)
        A_in = 2 * np.pi * (R0 - dr / 2)
        A_s = 2 * np.pi * R0
        a_ex = -ALPHA * A_in / (dr * V_M)
        a_us = -2 * ALPHA / dr ** 2
        g_ex = A_s * H_CONV / (RHO * CP * V_M)
        g_us = 2 * ALPHA * H_CONV / (K_COND * dr)
        print(f"  {M:>6} {a_ex:>18.8e} {a_us:>18.8e} {a_ex/a_us:>12.6f} "
              f"{g_ex:>16.8e} {g_us:>16.8e} {g_ex/g_us:>12.6f}")
        add(f"E50_M{M}_a_ex", f"精确半控制体 a_M (M={M})", a_ex, "1/s", "解析精确",
            "run E6", "V_M = pi*dr*(R-dr/4) 半环")
        add(f"E51_M{M}_a_us", f"用户写法 a_M=-2a/dr^2 (M={M})", a_us, "1/s", "解析精确",
            "run E6", "")
        add(f"E52_M{M}_a_ratio", f"a_M 比值 exact/user (M={M})", a_ex / a_us, "-",
            "解析比值", "run E6", "= 1-1/(4M)")
        add(f"E53_M{M}_g_ex", f"精确半控制体 g_h (M={M})", g_ex, "1/s", "解析精确",
            "run E6", "")
        add(f"E54_M{M}_g_us", f"用户写法 g_h=2ah/(k dr) (M={M})", g_us, "1/s", "解析精确",
            "run E6", "")
        add(f"E55_M{M}_g_ratio", f"g_h 比值 exact/user (M={M})", g_ex / g_us, "-",
            "解析比值", "run E6", "= 1/(1-1/(4M))")
        add(f"E56_M{M}_rel", f"用户写法相对精确系数的偏差 (M={M})", (a_us - a_ex) / a_ex,
            "-", "解析", "run E6", "= 1/(4M)")
    add("E57", "用户表面系数偏差公式", "1/(4M)", "-", "解析", "run E6", "")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "e1"):
        e1()
    if which in ("all", "e2"):
        e2()
    if which in ("all", "e3"):
        e3()
    if which in ("all", "e4"):
        e4()
    if which in ("all", "e5"):
        e5()
    if which in ("all", "e6"):
        e6()
    write_reg()
