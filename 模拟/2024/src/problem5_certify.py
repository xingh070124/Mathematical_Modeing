# -*- coding: utf-8 -*-
"""
问题 5 补充：峰窗子段精确认证 + 弧-线-弧深弯区诊断（读改写 problem5_results.json）

内容：
  A. 峰窗候选区间按事件点切分成光滑子段，逐段黄金分割精确最大化 + 事件端点取值
     —— 把模型 C 的认证从"全域 Lipschitz 网格"（宽 3.3e-4）收紧为
        "结构穷举 + 事件子段精确最大化"（不确定度 < 1e-9）；
  B. 剪枝证书：峰窗外区域以 Δ=0.25 全域粗扫值 + 全局 Lipschitz 常数给出严格上界，
     验证 < R*（结构穷举的域外部分）；
  C. 弧-线-弧扩展诊断：深弯区（弧长 < 弦长的两倍不可容）弦解唯一性扫描 +
     ρ_max_alt 密集扫描，判明 5.17 量级放大的真实性与构型跳变现象，修正 v*_alt。
"""
import os
import sys
import json
import numpy as np
from scipy.optimize import brentq, minimize_scalar

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ---- 复用 problem5_solve 的几何与运动学（import 触发其顶层搜索，太慢）——
# 此处独立实现（与 problem5_solve.py 逐行一致）
PITCH = 1.7
B = PITCH / (2 * np.pi)
R_SPACE = 4.5
HEAD_L, BODY_L = 3.41, 2.20
HOLE_OFF = 0.275
D_HEAD = HEAD_L - 2 * HOLE_OFF
D_BODY = BODY_L - 2 * HOLE_OFF
D_ALL = [D_HEAD] + [D_BODY] * 222
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


def rot(v, ang):
    c, s = np.cos(ang), np.sin(ang)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


E = spiral_point(TH_A)
tE = -spiral_dpoint(TH_A) / np.linalg.norm(spiral_dpoint(TH_A))
nE = rot90(tE)
F = -E
S_STAR = -np.dot(F - E, F - E) / (2.0 * np.dot(F - E, nE))
R1_0, R2_0 = 2.0 / 3.0 * S_STAR, 1.0 / 3.0 * S_STAR
O1_0 = E - R1_0 * nE
O2_0 = F + R2_0 * nE
m0v = (O2_0 - O1_0) / np.linalg.norm(O2_0 - O1_0)
T0 = O1_0 + R1_0 * m0v
phi_E0 = np.arctan2(*(E - O1_0)[::-1])
phi_T20 = np.arctan2(*(T0 - O2_0)[::-1])
phi_F0 = np.arctan2(*(F - O2_0)[::-1])
L1_0 = R1_0 * ((phi_E0 - np.arctan2(*m0v[::-1])) % (2 * np.pi))
L_C = L1_0 + R2_0 * ((phi_F0 - phi_T20) % (2 * np.pi))


def curve_point(u):
    if u < 0:
        return spiral_point(theta_of_arc(S_A - u))
    if u <= L1_0:
        phi = phi_E0 - u / R1_0
        return O1_0 + R1_0 * np.array([np.cos(phi), np.sin(phi)])
    if u <= L_C:
        phi = phi_T20 + (u - L1_0) / R2_0
        return O2_0 + R2_0 * np.array([np.cos(phi), np.sin(phi)])
    return -spiral_point(theta_of_arc(S_A + (u - L_C)))


def curve_tangent(u):
    if u < 0:
        th = theta_of_arc(S_A - u)
        v = spiral_dpoint(th)
        return -v / np.linalg.norm(v)
    if u <= L1_0:
        phi = phi_E0 - u / R1_0
        return np.array([np.sin(phi), -np.cos(phi)])
    if u <= L_C:
        phi = phi_T20 + (u - L1_0) / R2_0
        return np.array([-np.sin(phi), np.cos(phi)])
    th = theta_of_arc(S_A + (u - L_C))
    v = -spiral_dpoint(th)
    return v / np.linalg.norm(v)


def config_at(t):
    us = np.empty(N_H)
    us[0] = t
    for i in range(223):
        di = D_ALL[i]
        P = curve_point(us[i])
        f = lambda dl: np.linalg.norm(curve_point(us[i] - dl) - P) - di
        us[i + 1] = us[i] - brentq(f, 0.4 * di, 2.6 * di, xtol=1e-12)
    return us


def positions(us):
    return np.array([curve_point(u) for u in us])


def velocities(us):
    Ps = positions(us)
    v = np.empty(N_H)
    v[0] = 1.0
    for i in range(223):
        e = Ps[i + 1] - Ps[i]
        e = e / np.linalg.norm(e)
        v[i + 1] = v[i] * np.dot(curve_tangent(us[i]), e) / \
            np.dot(curve_tangent(us[i + 1]), e)
    return v


def rho_max(u1):
    return float(np.max(velocities(config_at(float(u1)))))


def golden_max(lo, hi, fn=None, xatol=1e-11):
    fn = fn or rho_max
    res = minimize_scalar(lambda uu: -fn(uu), bounds=(lo, hi),
                          method="bounded", options={"xatol": xatol})
    return float(res.x)


# ================= A. 峰窗事件子段精确认证 =================
print("=" * 64)
print("A. 峰窗候选区间 [13.0, 16.25] 事件子段精确认证")
print("=" * 64)
# 峰窗内事件点（problem5_solve.py 已算）
evts_win = [13.62124490682112, 13.79492456068406, 14.346040762333253,
            14.975130402453733, 15.576113409739662]
bounds = [13.0] + evts_win + [16.25]
subsegs = list(zip(bounds[:-1], bounds[1:]))
rows = []
gmax, gmax_u = -np.inf, None
for (a, b) in subsegs:
    u_pk = golden_max(a, b)
    r_pk = rho_max(u_pk)
    ends = [rho_max(a + 1e-9), rho_max(b - 1e-9)]
    r_seg = max(r_pk, *ends)
    rows.append({"seg": [a, b], "u_peak": u_pk, "R_peak": r_pk,
                 "R_ends": ends, "R_seg": r_seg})
    if r_seg > gmax:
        gmax, gmax_u = r_seg, (u_pk if r_pk >= max(ends) else
                               (a + 1e-9 if ends[0] >= ends[1] else b - 1e-9))
    print(f"  子段 [{a:.4f}, {b:.4f}]: 峰 R={r_pk:.12f} @ {u_pk:.6f}, "
          f"端点 [{ends[0]:.6f}, {ends[1]:.6f}] → 段max {r_seg:.12f}")
print(f"  峰窗全局 max = {gmax:.12f} @ {gmax_u:.6f}")
R_star = gmax
# 与模型 B/C 一致性
import json as _json
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "problem5_results.json"), encoding="utf-8") as f:
    RES = _json.load(f)
devB = abs(gmax - RES["R_max"]["B"])
print(f"  与模型 B 偏差 {devB:.2e}  {'✓' if devB < 1e-9 else '✗ 异常'}")
# 支配裕度：其余子段 max 与全局峰之差
others = [r["R_seg"] for r in rows if r["R_seg"] < gmax + 1e-12]
margin = gmax - max(o for o in others if o < gmax - 1e-13) if len(others) > 1 else np.inf
print(f"  峰所在子段对其余子段的支配裕度 ≥ {gmax - max(r['R_seg'] for r in rows if r['R_seg'] <= gmax - 1e-12):.4f}" if len(rows) > 1 else "")

# ================= B. 剪枝证书（域外） =================
print("\n" + "=" * 64)
print("B. 剪枝证书：峰窗外区域上界")
print("=" * 64)
d = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "_explore_q5.npz"))
grid, Rg = d["grid"], d["R"]
out_mask = (grid < 13.0 - 1e-9) | (grid > 16.25 + 1e-9)
R_out = float(np.max(Rg[out_mask]))
u_out = float(grid[out_mask][int(np.argmax(Rg[out_mask]))])
LIP = RES["model_C"]["L"]
U_out = R_out + LIP * 0.25 / 2.0
print(f"  峰窗外 Δ=0.25 粗扫 max = {R_out:.6f} @ u1={u_out}")
print(f"  Lipschitz 上界（L={LIP:.4f}, Δ=0.25）: U = {U_out:.6f}")
print(f"  {'✓ 证书成立' if U_out < R_star else '✗ 需加密'}：{U_out:.4f} < R* = {R_star:.6f}，"
      f"裕度 {R_star - U_out:.4f}")
# 峰窗边界向外一格的加密复核
for x in (12.9, 12.95, 16.3, 16.35):
    print(f"  复核 R({x}) = {rho_max(x):.6f}")

# ================= C. 弧-线-弧深弯区诊断 =================
print("\n" + "=" * 64)
print("C. 弧-线-弧扩展诊断")
print("=" * 64)
alt = RES["alt_curve"]
R1a, R2a, al = alt["R1"], alt["R2"], np.radians(alt["alpha_deg"])
T1 = E + R1a * np.sin(al) * tE - R1a * (1 - np.cos(al)) * nE
md = rot(tE, -al)
nm = rot90(md)
ell = alt["ell"]
T2 = T1 + ell * md
O1a = E - R1a * nE
O2a = T2 + R2a * nm
L1a, Ll_a, L2a = R1a * al, ell, R2a * al
Lc_a = L1a + Ll_a + L2a
phiE_a = np.arctan2(*(E - O1a)[::-1])
phiT2_a = np.arctan2(*(T2 - O2a)[::-1])


def curve_point_alt(u):
    if u < 0:
        return spiral_point(theta_of_arc(S_A - u))
    if u <= L1a:
        phi = phiE_a - u / R1a
        return O1a + R1a * np.array([np.cos(phi), np.sin(phi)])
    if u <= L1a + Ll_a:
        return T1 + (u - L1a) * md
    if u <= Lc_a:
        phi = phiT2_a + (u - L1a - Ll_a) / R2a
        return O2a + R2a * np.array([np.cos(phi), np.sin(phi)])
    return -spiral_point(theta_of_arc(S_A + (u - Lc_a)))


def curve_tangent_alt(u):
    if u < 0:
        th = theta_of_arc(S_A - u)
        v = spiral_dpoint(th)
        return -v / np.linalg.norm(v)
    if u <= L1a:
        phi = phiE_a - u / R1a
        return np.array([np.sin(phi), -np.cos(phi)])
    if u <= L1a + Ll_a:
        return md
    if u <= Lc_a:
        phi = phiT2_a + (u - L1a - Ll_a) / R2a
        return np.array([-np.sin(phi), np.cos(phi)])
    th = theta_of_arc(S_A + (u - Lc_a))
    v = -spiral_dpoint(th)
    return v / np.linalg.norm(v)


print(f"  弧2' 弧长 = {L2a:.4f} m vs 相邻弦长 1.65 m → 相邻两把手"
      f"{'可' if L2a >= 1.65 else '不可'}同时位于弧 2' 上")
print(f"  （弧上容纳一对把手需弧长 ≥ 2R·arcsin(D/2R) = "
      f"{2*R2a*np.arcsin(D_BODY/(2*R2a)):.4f} m）")


def config_at_alt(t):
    """弧-线-弧曲线上逆推构型（常规版，无根数诊断）."""
    us = np.empty(N_H)
    us[0] = t
    for i in range(223):
        di = D_ALL[i]
        P = curve_point_alt(us[i])
        f = lambda dl: np.linalg.norm(curve_point_alt(us[i] - dl) - P) - di
        us[i + 1] = us[i] - brentq(f, 0.4 * di, 2.6 * di, xtol=1e-12)
    return us


def config_at_alt_rootcheck(t, n_sweep=400):
    """弦解 + 对每个把手记录 [0.4D,2.6D] 内 f 的符号变化数（根数诊断，慢）."""
    us = np.empty(N_H)
    nroots = np.zeros(N_H, dtype=int)
    us[0] = t
    for i in range(223):
        di = D_ALL[i]
        P = curve_point_alt(us[i])

        def f(dl):
            return np.linalg.norm(curve_point_alt(us[i] - dl) - P) - di
        dls = np.linspace(0.4 * di, 2.6 * di, n_sweep)
        fs = np.array([f(x) for x in dls])
        nroots[i] = int(np.sum(fs[:-1] * fs[1:] < 0))
        us[i + 1] = us[i] - brentq(f, 0.4 * di, 2.6 * di, xtol=1e-12)
    return us, nroots


def velocities_alt(us):
    Ps = np.array([curve_point_alt(u) for u in us])
    v = np.empty(N_H)
    v[0] = 1.0
    for i in range(223):
        e = Ps[i + 1] - Ps[i]
        e = e / np.linalg.norm(e)
        v[i + 1] = v[i] * np.dot(curve_tangent_alt(us[i]), e) / \
            np.dot(curve_tangent_alt(us[i + 1]), e)
    return v


def rho_max_alt(u1):
    return float(np.max(velocities_alt(config_at_alt(float(u1)))))


# C1: u1=12.0 根数诊断
us_d, nroots = config_at_alt_rootcheck(12.0)
print(f"\n  [根数诊断] u1=12.0：多根把手数 = {int(np.sum(nroots > 1))}，"
      f"把手编号 {np.where(nroots > 1)[0][:10] + 1}（0 表示无多根）")
vs_d = velocities_alt(us_d)
print(f"  [构型] u1=12.0: max ρ = {np.max(vs_d):.4f}（把手 {int(np.argmax(vs_d))+1}），"
      f"前 8 把手 ρ = {np.round(vs_d[:8], 3).tolist()}")

# C2: ρ_max_alt 密集扫描（u1 ∈ [0, 30] step 0.05）
print("  [密扫] ρ_max_alt(u1), u1∈[0,30], Δ=0.05 ...")
uu_a = np.arange(0.0, 30.001, 0.05)
RR_a = np.array([rho_max_alt(u) for u in uu_a])
kmax = int(np.argmax(RR_a))
print(f"  密扫最大 = {RR_a[kmax]:.6f} @ u1 = {uu_a[kmax]:.2f}")
# 跳变检测
jumps = np.where(np.abs(np.diff(RR_a)) > 0.3)[0]
print(f"  跳变（|Δρ|>0.3/0.05m）位置: {np.round(uu_a[jumps], 2).tolist()[:12]}")
# 精确峰：峰顶邻域 golden
u_alt_pk = golden_max(uu_a[max(kmax - 3, 0)], uu_a[min(kmax + 3, len(uu_a) - 1)],
                      fn=rho_max_alt)
R_alt = rho_max_alt(u_alt_pk)
v_alt = velocities_alt(config_at_alt(u_alt_pk))
h_alt = int(np.argmax(v_alt)) + 1
us_alt_pk = config_at_alt(u_alt_pk)
h_alt_pos = [float(x) for x in us_alt_pk[:8]]
v_star_alt = 2.0 / R_alt
print(f"  弧-线-弧精确峰: R = {R_alt:.9f} @ u1 = {u_alt_pk:.6f}（把手 {h_alt}）")
print(f"  峰值构型前 8 把手 ρ = {np.round(v_alt[:8], 4).tolist()}")
print(f"  ⇒ v*_opt = {v_star_alt:.6f} m/s（基线 v* = {RES['v_star']:.6f}）")
print(f"  权衡: 调头曲线缩短 {(1 - Lc_a / L_C) * 100:.2f}% ⇒ "
      f"龙头最大速度下降 {(1 - v_star_alt / RES['v_star']) * 100:.2f}%")

# ================= 更新 JSON =================
RES["certify"] = {
    "peak_window_subsegs": rows,
    "R_star_certified": R_star,
    "u_star_certified": gmax_u,
    "dev_vs_model_B": devB,
    "prune_certificate": {"R_out_coarse": R_out, "u_out": u_out,
                          "L": LIP, "delta": 0.25, "U_out": U_out,
                          "margin": R_star - U_out,
                          "check_points": {str(x): rho_max(x) for x in
                                           (12.9, 12.95, 16.3, 16.35)}},
}
RES["alt_curve"].update({
    "R_max": R_alt, "u1": u_alt_pk, "handle": h_alt,
    "v_star": v_star_alt,
    "diag_multiroot_handles_at_12": int(np.sum(nroots > 1)),
    "diag_jump_locations": [float(x) for x in uu_a[jumps][:12]],
    "diag_arc2_len": float(L2a),
    "diag_pair_need": float(2 * R2a * np.arcsin(D_BODY / (2 * R2a))),
    "v_drop_pct": float((1 - v_star_alt / RES["v_star"]) * 100),
})
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "problem5_results.json"), "w", encoding="utf-8") as f:
    _json.dump(RES, f, ensure_ascii=False, indent=1)
print("\n[输出] problem5_results.json 已更新（certify + alt 诊断）")
