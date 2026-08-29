# -*- coding: utf-8 -*-
"""
2024 CUMCM A 题 —— 问题 5 补充：灵敏度测试与鲁棒性测试

灵敏度（单参数扰动对龙头最大容许速度 v* = 2/R_max 的影响）：
  (a) 龙身弦长 D_body ±5%（板凳加工公差）；
  (b) 两弧半径比 k = R1/R2 ∈ {1.5, 2.0, 3.0}（题目基线 k=2，调头曲线几何随 k 变化）；
  (c) 数值参数鲁棒性：弦解 xtol 与差分步长 h 复算 R_max。

鲁棒性（龙头速度随机波动的蒙特卡洛仿真）：
  v_head(t) = v̄·(1+ε(t))，ε 为 OU 过程（τ=0.5 s，σ ∈ {2%, 5%}）；
  在 v̄ = v* 与 v̄ = 0.95·v* 两档下各模拟 N=2000 次，
  统计全链最大把手速度分布与超限概率 P(max_i v_i > 2 m/s)。

输出：src/problem5_sensitivity.json
"""
import os
import json
import numpy as np
from scipy.optimize import brentq, minimize_scalar

# ---------------- 几何与运动学（与 problem5_solve.py 一致） ----------------
PITCH = 1.7
B = PITCH / (2 * np.pi)
R_SPACE = 4.5
HEAD_L, BODY_L = 3.41, 2.20
HOLE_OFF = 0.275
D_HEAD = HEAD_L - 2 * HOLE_OFF
D_BODY = BODY_L - 2 * HOLE_OFF
N_H = 224
TH_A = R_SPACE / B


def arc_len(th):
    return 0.5 * B * (th * np.hypot(th, 1.0) + np.arcsinh(th))


def d_arc_len(th):
    return B * np.hypot(th, 1.0)


S_A = arc_len(TH_A)


def spiral_point(th):
    r = B * th
    return np.array([r * np.cos(th), r * np.sin(th)])


def spiral_dpoint(th):
    return B * np.array([np.cos(th) - th * np.sin(th),
                         np.sin(th) + th * np.cos(th)])


def theta_of_arc(s):
    th = np.sqrt(2.0 * s / B) + 1e-9
    for _ in range(60):
        f = arc_len(th) - s
        if abs(f) < 1e-13:
            break
        th -= f / d_arc_len(th)
        if th <= 0:
            th = 1e-9
    return th


def rot90(v):
    return np.array([-v[1], v[0]])


E = spiral_point(TH_A)
tE = -spiral_dpoint(TH_A) / np.linalg.norm(spiral_dpoint(TH_A))
nE = rot90(tE)
F = -E
DELTA = F - E
S_STAR = -np.dot(DELTA, DELTA) / (2.0 * np.dot(DELTA, nE))


def build_curve(k):
    """R1 = k·R2 的两弧 S 形曲线（含切点/圆心/扫角），返回几何字典."""
    R1, R2 = k / (k + 1.0) * S_STAR, 1.0 / (k + 1.0) * S_STAR
    O1 = E - R1 * nE
    O2 = F + R2 * nE
    m = (O2 - O1) / np.linalg.norm(O2 - O1)
    T = O1 + R1 * m
    phi_E = np.arctan2(*(E - O1)[::-1])
    phi_T1 = np.arctan2(*m[::-1])
    phi_T2 = np.arctan2(*(T - O2)[::-1])
    phi_F = np.arctan2(*(F - O2)[::-1])
    g1 = (phi_E - phi_T1) % (2 * np.pi)
    g2 = (phi_F - phi_T2) % (2 * np.pi)
    L1 = R1 * g1
    L0 = R1 * g1 + R2 * g2
    return dict(k=k, R1=R1, R2=R2, O1=O1, O2=O2, T=T, L1=L1, L0=L0,
                phi_E=phi_E, phi_T2=phi_T2)


G0 = build_curve(2.0)


def curve_point(u, g=G0):
    if u < 0:
        return spiral_point(theta_of_arc(S_A - u))
    if u <= g['L1']:
        phi = g['phi_E'] - u / g['R1']
        return g['O1'] + g['R1'] * np.array([np.cos(phi), np.sin(phi)])
    if u <= g['L0']:
        phi = g['phi_T2'] + (u - g['L1']) / g['R2']
        return g['O2'] + g['R2'] * np.array([np.cos(phi), np.sin(phi)])
    return -spiral_point(theta_of_arc(S_A + (u - g['L0'])))


def curve_tangent(u, g=G0):
    if u < 0:
        th = theta_of_arc(S_A - u)
        v = spiral_dpoint(th)
        return -v / np.linalg.norm(v)
    if u <= g['L1']:
        phi = g['phi_E'] - u / g['R1']
        return np.array([np.sin(phi), -np.cos(phi)])
    if u <= g['L0']:
        phi = g['phi_T2'] + (u - g['L1']) / g['R2']
        return np.array([-np.sin(phi), np.cos(phi)])
    th = theta_of_arc(S_A + (u - g['L0']))
    v = -spiral_dpoint(th)
    return v / np.linalg.norm(v)


def config_at(t, d_body=D_BODY, g=G0, xtol=1e-12):
    us = np.empty(N_H)
    us[0] = t
    for i in range(N_H - 1):
        di = D_HEAD if i == 0 else d_body
        P = curve_point(us[i], g)
        f = lambda dl: np.linalg.norm(curve_point(us[i] - dl, g) - P) - di
        us[i + 1] = us[i] - brentq(f, 0.4 * di, 2.6 * di, xtol=xtol)
    return us


def velocities(us, g=G0):
    Ps = np.array([curve_point(u, g) for u in us])
    v = np.empty(N_H)
    v[0] = 1.0
    for i in range(N_H - 1):
        e = Ps[i + 1] - Ps[i]
        e = e / np.linalg.norm(e)
        v[i + 1] = v[i] * np.dot(curve_tangent(us[i], g), e) / \
            np.dot(curve_tangent(us[i + 1], g), e)
    return v


def rho_max(u1, **kw):
    return float(np.max(velocities(config_at(float(u1), **kw))))


def golden_max(lo, hi, fn=None, xatol=1e-11):
    fn = fn or rho_max
    r = minimize_scalar(lambda u: -fn(u), bounds=(lo, hi), method="bounded",
                        options={"xatol": xatol})
    return float(r.x)


OUT = {}
t0 = __import__('time').time()

# ================ A. 基线 ================
u_pk = golden_max(13.0, 16.25)
R_base = rho_max(u_pk)
v_base = 2.0 / R_base
print(f"基线: R_max = {R_base:.9f} @ u1 = {u_pk:.4f}, v* = {v_base:.9f} m/s")
OUT['baseline'] = {'R_max': R_base, 'u1': u_pk, 'v_star': v_base}

# ================ B. 灵敏度 (a)：龙身弦长 D_body ±5% ================
print("[灵敏度 a] 龙身弦长扰动 ±5% ...")
d_sens = []
for tag, dmod in (('-5%', 0.95), ('基线', 1.0), ('+5%', 1.05)):
    d_b = D_BODY * dmod
    u_p = golden_max(12.0, 17.0, fn=lambda u: rho_max(u, d_body=d_b))
    r_p = rho_max(u_p, d_body=d_b)
    d_sens.append({'case': f'D_body{tag}', 'D_body': d_b, 'R_max': r_p,
                   'v_star': 2.0 / r_p,
                   'dv_pct': (2.0 / r_p - v_base) / v_base * 100})
    print(f"  D_body{tag}: R={r_p:.9f}, v*={2.0/r_p:.6f} "
          f"({(2.0/r_p-v_base)/v_base*100:+.2f}%)")
OUT['sens_D_body'] = d_sens

# ================ C. 灵敏度 (b)：两弧半径比 k = R1/R2 ================
print("[灵敏度 b] 半径比 k 扫描 ...")


def rho_max_safe(u1, g):
    try:
        return rho_max(u1, g=g)
    except (ValueError, RuntimeError):
        return np.nan


k_sens = []
for k in (1.5, 2.0, 3.0):
    gk = build_curve(k)
    # 全域粗扫定位峰窗（不同 k 峰位不同），再黄金分割；深弯区弦解失效点记 NaN
    grid = np.arange(-20.0, 61.0, 0.5)
    rs = np.array([rho_max_safe(u, gk) for u in grid])
    valid = ~np.isnan(rs)
    n_fail = int(np.sum(~valid))
    kb = int(np.nanargmax(np.where(valid, rs, -np.inf)))
    try:
        u_p = golden_max(grid[max(kb - 2, 0)], grid[min(kb + 2, len(grid) - 1)],
                         fn=lambda u: rho_max_safe(u, gk))
        r_p = rho_max_safe(u_p, gk)
    except (ValueError, RuntimeError):
        u_p, r_p = grid[kb], rs[kb]
    k_sens.append({'k': k, 'R1': gk['R1'], 'R2': gk['R2'], 'L0': gk['L0'],
                   'R_max': r_p, 'u1': u_p, 'v_star': 2.0 / r_p,
                   'dv_pct': (2.0 / r_p - v_base) / v_base * 100,
                   'n_fail_points': n_fail})
    print(f"  k={k}: L0={gk['L0']:.4f}, R={r_p:.6f} @ {u_p:.2f}, "
          f"v*={2.0/r_p:.6f} ({(2.0/r_p-v_base)/v_base*100:+.2f}%), "
          f"弦解失效粗扫点 {n_fail}")
OUT['sens_k'] = k_sens

# ================ D. 数值参数鲁棒性 ================
print("[数值鲁棒性] xtol / 差分步长 ...")
num_rob = []
for xt in (1e-10, 1e-12, 1e-14):
    r_p = rho_max(u_pk, xtol=xt)
    num_rob.append({'param': f'xtol={xt:.0e}', 'R_max_at_peak': r_p,
                    'dev': abs(r_p - R_base)})
for h in (1e-5, 1e-6, 1e-7):
    r_p = (rho_max(u_pk + h) + rho_max(u_pk - h)) / 2
    num_rob.append({'param': f'h={h:.0e}', 'R_max_at_peak': r_p,
                    'dev': abs(r_p - R_base)})
for it in num_rob:
    print(f"  {it['param']}: R = {it['R_max_at_peak']:.12f} (偏差 {it['dev']:.1e})")
OUT['numerical_robustness'] = num_rob

# ================ E. 鲁棒性：龙头速度随机波动蒙特卡洛 ================
print("[鲁棒性] OU 速度扰动蒙特卡洛（N=2000）...")
# 预计算峰区 R(u1) 细网格（插值用）
uu = np.arange(-10.0, 40.001, 0.02)
RR = np.array([rho_max(u) for u in uu])
np.save('_mc_R_grid.npy', np.stack([uu, RR]))
R_interp = lambda x: np.interp(x, uu, RR)

rng = np.random.default_rng(2024)
N_SIM, DT, T_END, TAU = 2000, 0.02, 30.0, 0.5
NSTEP = int(T_END / DT)
mc = []
for v_scale, sig in ((1.00, 0.02), (1.00, 0.05), (0.95, 0.02), (0.95, 0.05)):
    vbar = v_base * v_scale
    # OU 过程向量化模拟：d eps = -eps/tau dt + sigma*sqrt(2/tau) dW
    eps = np.zeros(N_SIM)
    u1 = np.full(N_SIM, -5.0)
    mx = np.zeros(N_SIM)
    coefs = np.exp(-DT / TAU)
    vol = sig * np.sqrt(2.0 * DT / TAU)
    for _ in range(NSTEP):
        eps = eps * coefs + vol * rng.standard_normal(N_SIM)
        vh = vbar * (1.0 + eps)
        # 把手瞬时最大速度 = 龙头瞬时速度 × 当前构型最大速度比
        mx = np.maximum(mx, vh * R_interp(u1))
        u1 += vh * DT
    p_over = float(np.mean(mx > 2.0))
    mc.append({'v_bar_pct': v_scale, 'sigma': sig,
               'v_bar': vbar, 'max_v_mean': float(np.mean(mx)),
               'max_v_p95': float(np.percentile(mx, 95)),
               'max_v_max': float(np.max(mx)),
               'p_over_2': p_over})
    print(f"  v̄={v_scale:.2f}v*, σ={sig:.0%}: max_v 均值 {np.mean(mx):.4f}, "
          f"P95 {np.percentile(mx,95):.4f}, P(>2) = {p_over:.1%}")
OUT['monte_carlo'] = mc
OUT['mc_R_grid'] = {'u_range': [-10.0, 40.0], 'step': 0.02}

# ================ 灵敏度系数汇总 ================
# dv*/v* 对 dD/D 的归一化灵敏度 S = (Δv*/v*)/(ΔD/D)
dpm = {s['case']: s for s in d_sens}
S_D = ((dpm['D_body+5%']['v_star'] - dpm['D_body-5%']['v_star']) / v_base) / 0.10
k_s = {s['k']: s for s in k_sens}
OUT['summary'] = {
    'S_D_body': S_D,
    'k_slope_15_2': (k_s[1.5]['v_star'] - k_s[2.0]['v_star']) / v_base / (-0.5),
    'k_slope_3_2': (k_s[3.0]['v_star'] - k_s[2.0]['v_star']) / v_base / (1.0),
}
print(f"\n归一化灵敏度 S_D = Δ(v*/v*)/Δ(D/D) = {S_D:.3f}")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       'problem5_sensitivity.json'), 'w', encoding='utf-8') as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print(f"[输出] problem5_sensitivity.json（耗时 {__import__('time').time()-t0:.0f} s）")
