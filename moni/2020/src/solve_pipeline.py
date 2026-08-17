"""2020A 炉温曲线 全流程求解管线。

完成问题一至四的全部数值计算，输出 JSON 供论文填入，
并生成论文插图。时间原点取"电路板进入回焊炉"（x=0, t=0, T(0)=25），
与 paper/example.tex 的关键位置时刻表（t=x/v）保持一致。
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar, differential_evolution, minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)            # moni/2020
FIGDIR = os.path.join(ROOT, "paper", "figures")

# ---------------- 几何参数 ----------------
L, G, P, N = 30.5, 5.0, 25.0, 11
X_TOTAL = P + N * L + (N - 1) * G + P   # 435.5 cm


# ---------------- 环境温度场 ----------------
def ambient(x: float, zt: tuple) -> float:
    """zt = (T1~5, T6, T7, T8~9, T10~11)。"""
    T1_5, T6, T7, T8_9, T10_11 = zt
    Tset = [T1_5] * 5 + [T6, T7, T8_9, T8_9, T10_11, T10_11]
    if 0 <= x < P:
        return 25.0 + x / P * (Tset[0] - 25.0)
    for i in range(N):
        xs = P + i * (L + G)
        xe = xs + L
        if xs <= x <= xe:
            return Tset[i]
        if i < N - 1:
            nxs = P + (i + 1) * (L + G)
            if xe < x < nxs:
                return Tset[i] + (x - xe) / (nxs - xe) * (Tset[i + 1] - Tset[i])
    x11e = P + (N - 1) * (L + G) + L
    if x11e < x <= x11e + P:
        return Tset[-1] + (x - x11e) / P * (25.0 - Tset[-1])
    return 25.0


# ---------------- ODE 求解（RK4，分段换热系数） ----------------
def solve_curve(v_cm_s: float, alpha, zt: tuple,
                t_end: float = 430.0, dt: float = 0.25):
    """alpha: 常数 或 (a1, a2)。分段时按 Ta 与 T 相对大小切换：
    环境高于工件（Ta>T，升温）用 a1，否则（冷却）用 a2。"""
    if isinstance(alpha, (tuple, list)):
        a1, a2 = float(alpha[0]), float(alpha[1])

        def alpha_at(x, T):
            return a1 if ambient(x, zt) > T else a2
    else:
        a0 = float(alpha)

        def alpha_at(x, T):
            return a0

    n = int(np.ceil(t_end / dt)) + 1
    ts = np.linspace(0.0, (n - 1) * dt, n)
    Ts = np.empty(n)
    Ts[0] = 25.0
    for k in range(n - 1):
        t = ts[k]
        T = Ts[k]
        x0 = v_cm_s * t
        xh = v_cm_s * (t + dt / 2)
        xq = v_cm_s * (t + dt)
        k1 = alpha_at(x0, T) * (ambient(x0, zt) - T)
        k2 = alpha_at(xh, T + dt * k1 / 2) * (ambient(xh, zt) - (T + dt * k1 / 2))
        k3 = alpha_at(xh, T + dt * k2 / 2) * (ambient(xh, zt) - (T + dt * k2 / 2))
        k4 = alpha_at(xq, T + dt * k3) * (ambient(xq, zt) - (T + dt * k3))
        Ts[k + 1] = T + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return ts, Ts


# ---------------- 制程指标 ----------------
def crossing(t, T, level, direction):
    """返回 T 穿越 level 的时刻。direction='up'|'down'。"""
    idx = np.where(np.diff(np.sign(T - level)) != 0)[0]
    for i in idx:
        if direction == 'up' and T[i + 1] > T[i]:
            return np.interp(level, [T[i], T[i + 1]], [t[i], t[i + 1]])
        if direction == 'down' and T[i + 1] < T[i]:
            return np.interp(level, [T[i], T[i + 1]], [t[i], t[i + 1]])
    return None


def process_metrics(t, T):
    dT = np.gradient(T, t)
    T_pk = float(T.max())
    i_pk = int(np.argmax(T))
    S_r = float(dT[dT > 1e-9].max())
    S_d = float(dT[dT < -1e-9].min())
    # 150~190 ℃ 升温时间（仅升温段）
    rise = np.where(dT > 1e-9)[0]
    t_150 = crossing(t, T, 150.0, 'up')
    t_190 = crossing(t, T, 190.0, 'up')
    dt_150_190 = (t_190 - t_150) if (t_150 and t_190) else np.nan
    # >217 ℃ 时间
    t_in = crossing(t, T, 217.0, 'up')
    t_out = crossing(t, T, 217.0, 'down')
    dt_gt217 = (t_out - t_in) if (t_in and t_out) else np.nan
    return dict(T_pk=T_pk, i_pk=i_pk, S_r=S_r, S_d=S_d,
                dt_150_190=dt_150_190, dt_gt217=dt_gt217,
                t_in=t_in, t_out=t_out,
                t_peak=float(t[i_pk]))


def excess_area_up(t, T):
    """问题三面积：∫_{t217_up}^{t_pk}(T-217)dt（仅升温侧）。"""
    m = process_metrics(t, T)
    if m['t_in'] is None:
        return 1e9
    t_in, t_pk = m['t_in'], m['t_peak']
    mask = (t >= t_in) & (t <= t_pk)
    tt = np.concatenate([[t_in], t[mask], [t_pk]])
    TT = np.interp(tt, t, T)
    return float(np.trapezoid(TT - 217.0, tt))


def symmetry_index(t, T, n_grid=500):
    """问题四对称性：∫_0^1 |T_pre(θ)-T_post(θ)| dθ。"""
    m = process_metrics(t, T)
    if m['t_in'] is None or m['t_out'] is None:
        return np.inf
    t_in, t_out, t_pk = m['t_in'], m['t_out'], m['t_peak']
    theta = np.linspace(0.0, 1.0, n_grid)
    t_pre = t_pk - theta * (t_pk - t_in)
    t_post = t_pk + theta * (t_out - t_pk)
    T_pre = np.interp(t_pre, t, T)
    T_post = np.interp(t_post, t, T)
    return float(np.trapezoid(np.abs(T_pre - T_post), theta))


def feasible(m):
    return (240.0 <= m['T_pk'] <= 250.0 and
            0.0 <= m['S_r'] <= 3.0 and
            -3.0 <= m['S_d'] <= 0.0 and
            60.0 <= m['dt_150_190'] <= 120.0 and
            40.0 <= m['dt_gt217'] <= 90.0)


def constraint_violation(m):
    v = 0.0
    for lo, hi, key in [(240, 250, 'T_pk'), (0, 3, 'S_r'), (-3, 0, 'S_d'),
                        (60, 120, 'dt_150_190'), (40, 90, 'dt_gt217')]:
        val = m[key]
        if not np.isfinite(val):
            return 1e3
        v += max(0.0, lo - val) ** 2 + max(0.0, val - hi) ** 2
    return v


# ---------------- 数据读取与参数标定 ----------------
def load_obs():
    df = pd.read_excel(os.path.join(ROOT, "附件.xlsx"), header=0)
    arr = df.to_numpy(dtype=float)
    t = arr[:, 0]
    T = arr[:, 1]
    # 剔除占位行（T 为噪声的 t=0 行已由 header=0 跳过，再剔除 T<10 的行）
    ok = T >= 10
    return t[ok], T[ok]


def calibrate(zt_cal, v_cal, t_obs, T_obs, dt=0.25,
              piecewise=True):
    """标定综合换热系数。

    piecewise=True: 标定 (a1, a2)——升温段（环境高于工件）a1、冷却段 a2，
      经 2 参数最小二乘（least_squares）求解；
    piecewise=False: 标定单一常数 alpha。
    """
    from scipy.optimize import least_squares

    # 时间对齐：模型为"进入回焊炉"原点（T(0)=25），实测为"传感器 30℃ 零点"。
    # 传感器零点 τ=0 对应模型时刻 t*（T=30.03 的穿越时刻），即 model_time = t* + τ，
    # 其中 τ = raw - 19。标定时对每个候选 α 先求 t* 再对齐比较。
    def aligned_fit(p):
        ts, Ts = solve_curve(v_cal, (float(p[0]), float(p[1])),
                             zt_cal, t_end=430.0, dt=dt)
        i = int(np.argmin(np.abs(Ts - 30.03)))
        if Ts[:i + 1].min() < 30.03:
            t_star = float(np.interp(30.03, Ts[:i + 1], ts[:i + 1]))
        else:
            t_star = float(ts[i])
        tau = t_obs - 19.0                    # 传感器零点
        return np.interp(t_star + tau, ts, Ts), t_star

    if not piecewise:
        def J(alpha):
            T_fit, _ = aligned_fit((alpha, alpha))
            return float(np.sum((T_fit - T_obs) ** 2))

        res = minimize_scalar(J, bounds=(0.001, 1.0), method='bounded',
                              options=dict(xatol=1e-8))
        alpha_star = float(res.x)
    else:
        def rmse_of(p):
            T_fit, _ = aligned_fit(p)
            return float(np.sqrt(np.mean((T_fit - T_obs) ** 2)))

        # 粗网格定位全局最优，再 least_squares 精化
        best = (1e9, None)
        for a1 in np.arange(0.008, 0.10, 0.004):
            for a2 in np.arange(0.004, 0.05, 0.003):
                r = rmse_of((a1, a2))
                if r < best[0]:
                    best = (r, (a1, a2))
        x0 = best[1]

        def resid(p):
            T_fit, _ = aligned_fit(p)
            return T_fit - T_obs

        sol = least_squares(resid, list(x0),
                            bounds=([0.001, 0.001], [0.3, 0.3]),
                            xtol=1e-12, ftol=1e-12, gtol=1e-12)
        alpha_star = (float(sol.x[0]), float(sol.x[1]))

    # 拟合指标（使用相同的时间对齐）
    ts, Ts = solve_curve(v_cal, alpha_star, zt_cal, t_end=430.0, dt=dt)
    i0 = int(np.argmin(np.abs(Ts - 30.03)))
    t_star = float(np.interp(30.03, Ts[:i0 + 1], ts[:i0 + 1]))
    T_fit = np.interp(t_star + (t_obs - 19.0), ts, Ts)
    resid_v = T_fit - T_obs
    ss_res = float(np.sum(resid_v ** 2))
    ss_tot = float(np.sum((T_obs - T_obs.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot
    rmse = float(np.sqrt(ss_res / len(T_obs)))
    max_err = float(np.max(np.abs(resid_v)))
    return alpha_star, r2, rmse, max_err


# ---------------- 问题一 ----------------
def solve_q1(alpha, zt, v_cm_min):
    v = v_cm_min / 60.0
    ts, Ts = solve_curve(v, alpha, zt)
    keys = [(111.25, '温区3中点'), (217.75, '温区6中点'),
            (253.25, '温区7中点'), (304.00, '温区8结束处')]
    temps = {}
    for xk, name in keys:
        tk = xk / v
        temps[name] = dict(x=xk, t=tk, T=float(np.interp(tk, ts, Ts)))
    # result.csv（每 0.5 s，从进入回焊炉 t=0 起）
    t_out = np.arange(0.0, 430.0, 0.5)
    T_out = np.interp(t_out, ts, Ts)
    return dict(ts=ts, Ts=Ts, temps=temps, t_out=t_out, T_out=T_out)


# ---------------- 问题二 ----------------
def solve_q2(alpha, zt2, v_lo=65.0, v_hi=100.0):
    grid = []
    for v in np.arange(v_lo, v_hi + 1.0, 1.0):
        ts, Ts = solve_curve(v / 60.0, alpha, zt2)
        m = process_metrics(ts, Ts)
        grid.append((v, m, feasible(m)))
    feas_v = [v for v, m, ok in grid if ok]
    if not feas_v:
        return None
    vL = float(max(feas_v))
    vR = min(vL + 1.0, v_hi)
    while vR - vL > 1e-3:
        vM = (vL + vR) / 2.0
        ts, Ts = solve_curve(vM / 60.0, alpha, zt2)
        ok = feasible(process_metrics(ts, Ts))
        if ok:
            vL = vM
        else:
            vR = vM
    v_max = vL
    ts, Ts = solve_curve(v_max / 60.0, alpha, zt2)
    m = process_metrics(ts, Ts)
    # 活跃约束：裕量最小的下限约束
    margins = {
        'T_pk>=240': 240.0 - m['T_pk'],
        'dt_150_190>=60': 60.0 - m['dt_150_190'],
        'dt_gt217>=40': 40.0 - m['dt_gt217'],
    }
    active = max(margins, key=lambda k: margins[k]) if max(margins.values()) > -1e-6 else None
    # 边界复核
    ts_p, Ts_p = solve_curve((v_max + 0.5) / 60.0, alpha, zt2)
    m_p = process_metrics(ts_p, Ts_p)
    feas_plus = feasible(m_p)
    return dict(v_max=v_max, metrics=m, active=active, margins=margins,
                feas_plus=feas_plus, ts=ts, Ts=Ts)


# ---------------- 问题三 ----------------
def objective_q3(x, alpha):
    zt = (x[0], x[1], x[2], x[3], 25.0)
    v = x[4] / 60.0
    ts, Ts = solve_curve(v, alpha, zt)
    m = process_metrics(ts, Ts)
    viol = constraint_violation(m)
    A = excess_area_up(ts, Ts)
    if viol <= 1e-9:
        return A
    return A + 1e6 * viol


def _obj_q3(x, alpha):
    return objective_q3(x, alpha)


def solve_q3(alpha, seed=2026):
    bounds = [(165, 185), (185, 205), (225, 245), (245, 265), (65, 100)]
    lo = np.array([b[0] for b in bounds])
    hi = np.array([b[1] for b in bounds])
    res = differential_evolution(
        _obj_q3, bounds, args=(alpha,),
        strategy='best1bin', maxiter=50, popsize=8, tol=1e-6,
        polish=True, seed=seed, workers=1,
        mutation=(0.5, 1.0), recombination=0.8)
    # L-BFGS-B 多起点精化（罚函数，避免 SLSQP 约束雅可比开销）
    best = dict(x=res.x, A=res.fun, viol=0)
    rng = np.random.default_rng(seed + 7)
    starts = [res.x] + [res.x + rng.normal(0, 2.0, 5) for _ in range(4)]
    for s0 in starts:
        s = np.clip(s0, lo, hi)
        try:
            r = minimize(lambda x: objective_q3(x, alpha), s,
                         method='L-BFGS-B', bounds=bounds,
                         options=dict(ftol=1e-8, maxiter=80))
            zt = (r.x[0], r.x[1], r.x[2], r.x[3], 25.0)
            ts, Ts = solve_curve(r.x[4] / 60.0, alpha, zt)
            viol = constraint_violation(process_metrics(ts, Ts))
            A = excess_area_up(ts, Ts)
            if viol <= best['viol'] + 1e-9 and A < best['A']:
                best = dict(x=r.x.copy(), A=A, viol=viol)
        except Exception:
            continue
    return best


def metric_ineq(x, alpha, lo, hi, key):
    zt = (x[0], x[1], x[2], x[3], 25.0)
    ts, Ts = solve_curve(x[4] / 60.0, alpha, zt)
    m = process_metrics(ts, Ts)
    return min(m[key] - lo, hi - m[key])


# ---------------- 问题四 ----------------
def objective_q4(x, alpha, A_ref, D_ref, lam):
    zt = (x[0], x[1], x[2], x[3], 25.0)
    v = x[4] / 60.0
    ts, Ts = solve_curve(v, alpha, zt)
    m = process_metrics(ts, Ts)
    viol = constraint_violation(m)
    A = excess_area_up(ts, Ts)
    D = symmetry_index(ts, Ts)
    if viol > 1e-9:
        return 1e6 * viol + A / A_ref + D / D_ref
    return (1.0 - lam) * A / A_ref + lam * D / D_ref


def _obj_q4(x, alpha, A_ref, D_ref, lam):
    return objective_q4(x, alpha, A_ref, D_ref, lam)


def solve_q4(alpha, A_ref, D_ref, lam=0.4, seed=2026):
    bounds = [(165, 185), (185, 205), (225, 245), (245, 265), (65, 100)]
    lo = np.array([b[0] for b in bounds])
    hi = np.array([b[1] for b in bounds])
    res = differential_evolution(
        _obj_q4, bounds, args=(alpha, A_ref, D_ref, lam),
        strategy='best1bin', maxiter=50, popsize=8, tol=1e-6,
        polish=True, seed=seed, workers=1,
        mutation=(0.5, 1.0), recombination=0.8)
    best = dict(x=res.x, F=res.fun, viol=0)
    rng = np.random.default_rng(seed + 11)
    starts = [res.x] + [res.x + rng.normal(0, 2.0, 5) for _ in range(4)]
    for s0 in starts:
        s = np.clip(s0, lo, hi)
        try:
            r = minimize(lambda x: objective_q4(x, alpha, A_ref, D_ref, lam),
                         s, method='L-BFGS-B', bounds=bounds,
                         options=dict(ftol=1e-8, maxiter=80))
            zt = (r.x[0], r.x[1], r.x[2], r.x[3], 25.0)
            ts, Ts = solve_curve(r.x[4] / 60.0, alpha, zt)
            viol = constraint_violation(process_metrics(ts, Ts))
            if viol <= 1e-9 and r.fun < best['F']:
                best = dict(x=r.x.copy(), F=r.fun, viol=viol)
        except Exception:
            continue
    return best


# ---------------- 绘图 ----------------
def make_figures(alpha, v_cal, zt_cal, t_obs, T_obs,
                 q1, q2, q3, q4, q4_A, q4_D):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    # 配置中文字体，避免图内中文乱码
    for name in ["Microsoft YaHei", "SimHei", "DengXian", "SimSun"]:
        try:
            font_manager.findfont(name, fallback_to_default=False)
            plt.rcParams["font.sans-serif"] = [name]
            plt.rcParams["font.family"] = "sans-serif"
            plt.rcParams["axes.unicode_minus"] = False
            break
        except Exception:
            continue

    os.makedirs(FIGDIR, exist_ok=True)
    alpha_star = alpha

    # 校准对比（对齐后的模型曲线）
    ts, Ts = solve_curve(v_cal, alpha_star, zt_cal)
    i0 = int(np.argmin(np.abs(Ts - 30.03)))
    t_star = float(np.interp(30.03, Ts[:i0 + 1], ts[:i0 + 1]))
    tau = t_obs - 19.0
    T_fit = np.interp(t_star + tau, ts, Ts)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(tau, T_fit, 'b-', lw=1.2, label='模型曲线（对齐）')
    ax.plot(tau, T_obs, 'r.', ms=2, label='实测数据')
    ax.set_xlabel('时间（传感器零点）τ / s'); ax.set_ylabel('温度 / ℃')
    ax.set_title('参数标定：模型 vs 实测')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q1_calibration.png'), dpi=150)
    plt.close(fig)

    # 问题一曲线
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(q1['ts'], q1['Ts'], 'b-', lw=1.2)
    for name, d in q1['temps'].items():
        ax.plot(d['t'], d['T'], 'ro', ms=5)
        ax.annotate(f"{d['T']:.1f}", (d['t'], d['T']),
                    textcoords='offset points', xytext=(6, 6), fontsize=8)
    ax.set_xlabel('时间 t / s'); ax.set_ylabel('温度 / ℃')
    ax.set_title('问题一 炉温曲线（v=78 cm/min）')
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q1_curve.png'), dpi=150)
    plt.close(fig)

    # 问题二曲线
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(q2['ts'], q2['Ts'], 'b-', lw=1.2)
    ax.axhline(217, color='r', ls='--', lw=0.9)
    ax.axhline(240, color='g', ls=':', lw=0.9)
    ax.axhline(250, color='g', ls=':', lw=0.9)
    ax.axhline(150, color='gray', ls='--', lw=0.7)
    ax.axhline(190, color='gray', ls='--', lw=0.7)
    ax.annotate(f"v_max={q2['v_max']:.2f} cm/min", xy=(0.6, 0.95),
                xycoords='axes fraction', fontsize=11)
    ax.set_xlabel('时间 t / s'); ax.set_ylabel('温度 / ℃')
    ax.set_title('问题二 最大允许速度下炉温曲线')
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q2_curve.png'), dpi=150)
    plt.close(fig)

    # 问题三曲线（面积阴影）
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ts3, Ts3 = solve_curve(q3['x'][4] / 60.0, alpha_star,
                           (q3['x'][0], q3['x'][1], q3['x'][2], q3['x'][3], 25.0))
    m3 = process_metrics(ts3, Ts3)
    ax.plot(ts3, Ts3, 'b-', lw=1.2)
    if m3['t_in'] is not None:
        mask = (ts3 >= m3['t_in']) & (ts3 <= m3['t_peak'])
        ax.fill_between(ts3[mask], 217, Ts3[mask], color='r', alpha=0.25,
                        label=f"面积 A={q3['A']:.1f} ℃·s")
    ax.axhline(217, color='r', ls='--', lw=0.9)
    ax.legend()
    ax.set_xlabel('时间 t / s'); ax.set_ylabel('温度 / ℃')
    ax.set_title('问题三 最优炉温曲线（超温面积最小）')
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q3_curve.png'), dpi=150)
    plt.close(fig)

    # 问题四曲线 + 对称性
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ts4, Ts4 = solve_curve(q4['x'][4] / 60.0, alpha_star,
                           (q4['x'][0], q4['x'][1], q4['x'][2], q4['x'][3], 25.0))
    m4 = process_metrics(ts4, Ts4)
    ax.plot(ts4, Ts4, 'b-', lw=1.2, label='最优曲线')
    if m4['t_in'] is not None:
        mask = (ts4 >= m4['t_in']) & (ts4 <= m4['t_out'])
        ax.fill_between(ts4[mask], 217, Ts4[mask], color='orange', alpha=0.15,
                        label=f"A={q4_A:.1f}, D={q4_D:.1f}")
    ax.axhline(217, color='r', ls='--', lw=0.9)
    ax.legend()
    ax.set_xlabel('时间 t / s'); ax.set_ylabel('温度 / ℃')
    ax.set_title('问题四 兼顾面积与对称性的最优炉温曲线')
    ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q4_curve.png'), dpi=150)
    plt.close(fig)

    # 对称性示意图：归一化峰前/峰后
    theta = np.linspace(0, 1, 200)
    t_pre = m4['t_peak'] - theta * (m4['t_peak'] - m4['t_in'])
    t_post = m4['t_peak'] + theta * (m4['t_out'] - m4['t_peak'])
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(theta, np.interp(t_pre, ts4, Ts4), 'b-', lw=1.4, label='峰前 T_pre')
    ax.plot(theta, np.interp(t_post, ts4, Ts4), 'r--', lw=1.4, label='峰后 T_post')
    ax.set_xlabel('归一化时间 θ'); ax.set_ylabel('温度 / ℃')
    ax.set_title('问题四 峰值两侧归一化曲线对比')
    ax.legend(); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(FIGDIR, 'q4_symmetry.png'), dpi=150)
    plt.close(fig)


# ---------------- 主流程 ----------------
if __name__ == '__main__':
    t0 = time.time()

    # ---- 标定 ----
    zt_cal = (175.0, 195.0, 235.0, 255.0, 25.0)
    v_cal = 70.0 / 60.0
    t_obs, T_obs = load_obs()
    alpha_star, r2, rmse, max_err = calibrate(zt_cal, v_cal, t_obs, T_obs)
    a_str = (f"alpha*=(a1,a2)=({alpha_star[0]:.4f},{alpha_star[1]:.4f})"
             if isinstance(alpha_star, tuple) else f"alpha*={alpha_star:.6f}")
    print(f"[标定] {a_str} s^-1, R^2={r2:.5f}, "
          f"RMSE={rmse:.3f} ℃, max|err|={max_err:.3f} ℃")

    # ---- 问题一 ----
    zt1 = (173.0, 198.0, 230.0, 257.0, 25.0)
    q1 = solve_q1(alpha_star, zt1, 78.0)
    print("\n[问题一] 指定位置温度：")
    for name, d in q1['temps'].items():
        print(f"  {name}: x={d['x']} cm, t={d['t']:.2f} s, T={d['T']:.2f} ℃")
    pd.DataFrame({'时间(s)': q1['t_out'], '温度(℃)': q1['T_out']}
                 ).to_csv(os.path.join(ROOT, 'result.csv'), index=False,
                          encoding='utf-8-sig')

    # ---- 问题二 ----
    zt2 = (182.0, 203.0, 237.0, 254.0, 25.0)
    q2 = solve_q2(alpha_star, zt2)
    print(f"\n[问题二] v_max={q2['v_max']:.4f} cm/min")
    for k in ['T_pk', 'S_r', 'S_d', 'dt_150_190', 'dt_gt217']:
        print(f"  {k} = {q2['metrics'][k]:.3f}")
    print(f"  活跃约束: {q2['active']}")
    print(f"  v_max+0.5 可行? {q2['feas_plus']}")

    # ---- 问题三 ----
    q3 = solve_q3(alpha_star)
    zt3 = (q3['x'][0], q3['x'][1], q3['x'][2], q3['x'][3], 25.0)
    ts3, Ts3 = solve_curve(q3['x'][4] / 60.0, alpha_star, zt3)
    m3 = process_metrics(ts3, Ts3)
    q3_D = symmetry_index(ts3, Ts3)
    print(f"\n[问题三] u*={np.round(q3['x'],2).tolist()}, A*={q3['A']:.2f} ℃·s")
    print(f"  指标: Tpk={m3['T_pk']:.2f}, dt>217={m3['dt_gt217']:.2f}, "
          f"dt150-190={m3['dt_150_190']:.2f}, Sr={m3['S_r']:.3f}, Sd={m3['S_d']:.3f}")
    print(f"  问题三解的对称性 D={q3_D:.3f}")

    # ---- 问题四 ----
    q4 = solve_q4(alpha_star, q3['A'], q3_D, lam=0.4)
    zt4 = (q4['x'][0], q4['x'][1], q4['x'][2], q4['x'][3], 25.0)
    ts4, Ts4 = solve_curve(q4['x'][4] / 60.0, alpha_star, zt4)
    m4 = process_metrics(ts4, Ts4)
    q4_A = excess_area_up(ts4, Ts4)
    q4_D = symmetry_index(ts4, Ts4)
    print(f"\n[问题四] u4={np.round(q4['x'],2).tolist()}")
    print(f"  A4={q4_A:.2f}, D4={q4_D:.3f}")
    print(f"  dA/A3={(q4_A-q3['A'])/q3['A']*100:.2f}%, "
          f"dD/D3={(q4_D-q3_D)/q3_D*100:.2f}%")
    print(f"  指标: Tpk={m4['T_pk']:.2f}, dt>217={m4['dt_gt217']:.2f}, "
          f"dt150-190={m4['dt_150_190']:.2f}, Sr={m4['S_r']:.3f}, Sd={m4['S_d']:.3f}")

    # ---- 敏感性 ----
    sens_alpha = {}
    for eta in [-0.10, -0.05, 0.05, 0.10]:
        a = tuple((1 + eta) * val for val in alpha_star)
        q2s = solve_q2(a, zt2)
        q1m = process_metrics(*solve_curve(78 / 60.0, a, zt1)[:2])
        sens_alpha[f"{eta:+.0%}"] = dict(
            v_max=(q2s['v_max'] if q2s else None),
            T_pk_q1=q1m['T_pk'],
            dt_gt217_q2=(q2s['metrics']['dt_gt217'] if q2s else None))
    print("\n[敏感性] alpha 扰动:")
    for k, v in sens_alpha.items():
        print(f"  {k}: {v}")

    sens_dt = {}
    for dt in [1.0, 0.5, 0.25, 0.125]:
        a, r, rm, me = calibrate(zt_cal, v_cal, t_obs, T_obs, dt=dt)
        m1 = process_metrics(*solve_curve(78 / 60.0, a, zt1, dt=dt)[:2])
        sens_dt[f"{dt}"] = dict(alpha=a, T_pk=m1['T_pk'], dt_gt217=m1['dt_gt217'])
    print("\n[敏感性] RK4 步长:")
    for k, v in sens_dt.items():
        print(f"  dt={k}: {v}")

    # ---- 汇总 JSON ----
    out = dict(
        alpha_star=alpha_star, r2=r2, rmse=rmse, max_err=max_err,
        q1_temps={k: v['T'] for k, v in q1['temps'].items()},
        q2=dict(v_max=q2['v_max'],
                **{k: q2['metrics'][k] for k in
                   ['T_pk', 'S_r', 'S_d', 'dt_150_190', 'dt_gt217']},
                active=q2['active'], feas_plus=q2['feas_plus']),
        q3=dict(T1_5=q3['x'][0], T6=q3['x'][1], T7=q3['x'][2],
                T8_9=q3['x'][3], v=q3['x'][4], A=q3['A'], D=q3_D,
                T_pk=m3['T_pk'], S_r=m3['S_r'], S_d=m3['S_d'],
                dt_150_190=m3['dt_150_190'], dt_gt217=m3['dt_gt217']),
        q4=dict(T1_5=q4['x'][0], T6=q4['x'][1], T7=q4['x'][2],
                T8_9=q4['x'][3], v=q4['x'][4], A=q4_A, D=q4_D,
                T_pk=m4['T_pk'], S_r=m4['S_r'], S_d=m4['S_d'],
                dt_150_190=m4['dt_150_190'], dt_gt217=m4['dt_gt217']),
        sens_alpha=sens_alpha, sens_dt=sens_dt,
        runtime=time.time() - t0,
    )
    with open(os.path.join(ROOT, 'results.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    # ---- 绘图 ----
    make_figures(alpha_star, v_cal, zt_cal, t_obs, T_obs,
                 q1, q2, q3, q4, q4_A, q4_D)

    print(f"\n总耗时 {time.time()-t0:.1f}s，结果已写入 results.json 与 result.csv")
