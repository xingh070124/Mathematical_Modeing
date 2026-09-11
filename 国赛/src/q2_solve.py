# -*- coding: utf-8 -*-
"""
q2_solve.py -- 问题二 (烘干全过程) 数值求解器与模型核验.

模型 (见 model/problem2.md):
    温度:  rho(C) cp(C) dT/dt = (1/r) d/dr ( k(C) r dT/dr )
    水分:  dC/dt = (1/r) d/dr ( r D(C,T) dC/dr )
    边界:  -k dT/dr|_R = h (T_R - T_inf) + H_evap h_m (C_R - C_inf)
           -D dC/dr|_R = h_m (C_R - C_inf)
    物性:  附录3: rho=650+128C, cp=1450+2736C/(C+1), k=0.21+0.38C/(C+1),
           D  =2.4e-3 exp(-0.45/C) exp(-3850/T)

离散 (problem2.md §9-§11): 线性单元 Galerkin 弱形式 + 行和集中质量矩阵
                          + 后向 Euler + 阻尼 Newton.

入口:
    --selftest   集中质量恒等式 / Jacobian 有限差分校核 / 物性自检
    --converge   空间与时间收敛阶 (与 problem2.md §12/§14 的 V1/V2 对应)
    --variants   蒸发项 / 能量方程形式 / 边界积分方式 / 系数冻结 的对照
    --registry   产出 outputs/registry_q2.csv

运行:  python src/q2_solve.py --selftest
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time

import numpy as np
from scipy.linalg import solve_banded

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import Env, load_attachment1  # noqa: E402  复用同一套环境激励连续化

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

# ---------------------------------------------------------------------------
# 物理常数
# ---------------------------------------------------------------------------
R = 0.02                # m,   药材半径
T0K = 301.15            # K,   初温 28 degC
C0 = 2.55               # kg/kg, 初始干基含水率
H_CONV = 25.0           # W/(m^2 K), 附录2
HM = 8.0e-7             # m/s,       附录2

# 汽化潜热定标式 (problem2.md §4.4c; 由 Clapeyron + Kirchhoff + IAPWS-95 定标)
HEVAP_28 = 2.4346e6     # J/kg @ 28 degC
HEVAP_SLOPE = -2.391e3  # J/(kg K)
HEVAP_TREF = 301.15     # K

_APP2 = dict(rho0=820.0, cp0=2600.0, k0=0.36)


# ---------------------------------------------------------------------------
# 求解参数
# ---------------------------------------------------------------------------
class Par:
    """求解器开关: 把"模型本体"与"模型变体"在代码里显式分开."""

    def __init__(self, mode="app3", hevap="T", hevap_mult=1.0, hevap_const=None,
                 boundary="lumped", energy="T", frozen=False,
                 rtol_R=1e-11, max_newton=25, line_search=True,
                 hc=None, hm=None):
        self.mode = mode              # "app3" | "app2"
        self.hevap = hevap            # "T" | "const" | "off"
        self.hevap_mult = hevap_mult  # 敏感性用倍率
        self.hevap_const = hevap_const
        self.boundary = boundary      # "lumped" (problem2.md §9.3) | "halfcv" (问题一 FV)
        self.energy = energy          # "T" (rho cp dT/dt) | "conserv" (d(rho cp T)/dt)
        self.frozen = frozen          # True: 系数取上一时间步 (Picard / 准 Newton)
        self.rtol_R = rtol_R
        self.max_newton = max_newton
        self.line_search = line_search
        self.hc = H_CONV if hc is None else hc
        self.hm = HM if hm is None else hm


# ---------------------------------------------------------------------------
# 附录3 / 附录2 物性经验式与解析导数
# ---------------------------------------------------------------------------
def props(C, mode="app3"):
    """返回 (rho, cp, k, drho/dC, dcp/dC, dk/dC)."""
    C = np.asarray(C, dtype=float)
    if mode == "app2":
        z = np.zeros_like(C)
        return (np.full_like(C, _APP2["rho0"]), np.full_like(C, _APP2["cp0"]),
                np.full_like(C, _APP2["k0"]), z, z, z)
    Cp1 = C + 1.0
    return (650.0 + 128.0 * C,
            1450.0 + 2736.0 * C / Cp1,
            0.21 + 0.38 * C / Cp1,
            np.full_like(C, 128.0),
            2736.0 / Cp1 ** 2,
            0.38 / Cp1 ** 2)


def Dfun(C, T, mode="app3"):
    C = np.asarray(C, dtype=float)
    if mode == "app2":
        return 7.0e-9 * np.exp(-0.89 / C)
    return 2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / np.asarray(T, dtype=float))


def D_derivs(C, T, mode="app3"):
    """(dD/dC, dD/dT) 的解析式."""
    C = np.asarray(C, dtype=float)
    if mode == "app2":
        D = 7.0e-9 * np.exp(-0.89 / C)
        return D * 0.89 / C ** 2, np.zeros_like(C)
    T = np.asarray(T, dtype=float)
    D = Dfun(C, T, mode)
    return D * 0.45 / C ** 2, D * 3850.0 / T ** 2


def hevap_of(T, par):
    """汽化潜热 H_evap(T) [J/kg] 与其温度导数."""
    if par.hevap == "off":
        return 0.0, 0.0
    if par.hevap == "const":
        v = par.hevap_const if par.hevap_const is not None else HEVAP_28
        return v * par.hevap_mult, 0.0
    v = HEVAP_28 + HEVAP_SLOPE * (float(T) - HEVAP_TREF)
    return v * par.hevap_mult, HEVAP_SLOPE * par.hevap_mult


# ---------------------------------------------------------------------------
# 网格与集中质量矩阵
# ---------------------------------------------------------------------------
def geometry(M, boundary="lumped"):
    """几何量.

    Gfac[i] = r_{i+1/2}/dr  (i=0..M-1);  单元刚度系数 = k_e * Gfac[i]
    MLg[i]  = 集中质量矩阵的几何部分 (已约去 2 pi 与 rho cp):
        lumped : 线性单元行和  ->  M^L_ii = rho cp * MLg[i]
                 MLg[0]=dr^2/6, MLg[i]=dr*r_i (1<=i<=M-1), MLg[M]=dr^2(3M-1)/6
        halfcv : 问题一的精确半控制体体积
                 MLg[0]=dr^2/8, MLg[M]=dr^2(4M-1)/8
    """
    dr = R / M
    r = np.arange(M + 1) * dr
    Gfac = (0.5 * (r[:-1] + r[1:])) / dr
    MLg = np.empty(M + 1)
    if boundary == "halfcv":
        MLg[0] = dr * dr / 8.0
        MLg[M] = dr * dr * (4 * M - 1) / 8.0
    else:
        MLg[0] = dr * (2 * r[0] + r[1]) / 6.0
        MLg[M] = dr * (r[M - 1] + 2 * r[M]) / 6.0
    MLg[1:M] = dr * r[1:M]
    return dict(M=M, n=M + 1, dr=dr, r=r, rf=0.5 * (r[:-1] + r[1:]),
                Gfac=Gfac, MLg=MLg)


# ---------------------------------------------------------------------------
# 残差与 Jacobian
# ---------------------------------------------------------------------------
def assemble(x, xold, dt, g, par, Tinf, Cinf):
    """组装残差 R(x) 与带状 Jacobian (带宽 3,3; 交错排序 [T0,C0,T1,C1,...]).

    R_T,i = M_i (T_i - T_i^n)/dt + [K T]_i + delta_iM [ hR(T_M-Tinf)
                                                       + H_evap h_m R (C_M-Cinf) ]
    R_C,i = Mc_i (C_i - C_i^n)/dt + [Kc C]_i + delta_iM [ h_m R (C_M-Cinf) ]

    返回 (R, ab, aux). 带状存储约定: ab[3 + i - j, j] = A[i, j].
    """
    M, n = g["M"], g["n"]
    Gfac, MLg = g["Gfac"], g["MLg"]

    T, C = x[0::2].copy(), x[1::2].copy()
    Told, Cold = xold[0::2], xold[1::2]

    C_pr, T_pr = (Cold, Told) if par.frozen else (C, T)
    rho, cp, k, drho, dcp, dk = props(C_pr, par.mode)
    rcp = rho * cp
    drcp = drho * cp + rho * dcp
    Dv = Dfun(C_pr, T_pr, par.mode)
    dDdC, dDdT = D_derivs(C_pr, T_pr, par.mode)

    Ge = (0.5 * (k[:-1] + k[1:])) * Gfac          # 单元导热系数
    Fe = (0.5 * (Dv[:-1] + Dv[1:])) * Gfac        # 单元扩散系数
    dT = T[:-1] - T[1:]
    dC = C[:-1] - C[1:]

    KT = np.zeros(n)
    KT[:-1] += Ge * dT
    KT[1:] -= Ge * dT
    KC = np.zeros(n)
    KC[:-1] += Fe * dC
    KC[1:] -= Fe * dC

    rho_o, cp_o, *_ = props(Cold, par.mode)
    MT = MLg * rcp
    MC = MLg
    if par.energy == "conserv":
        RT = (MT * T - MLg * rho_o * cp_o * Told) / dt + KT
    else:
        RT = MT * (T - Told) / dt + KT
    RC = MC * (C - Cold) / dt + KC

    Hev, dHev = hevap_of(T[M], par)
    flux_h = par.hc * R * (T[M] - Tinf) + Hev * par.hm * R * (C[M] - Cinf)
    flux_w = par.hm * R * (C[M] - Cinf)
    RT[M] += flux_h
    RC[M] += flux_w

    Res = np.empty(2 * n)
    Res[0::2] = RT
    Res[1::2] = RC

    # ------------------------- Jacobian -------------------------
    z = np.zeros(n)
    JT = z.copy()
    JT += MT / dt
    JT[:-1] += Ge
    JT[1:] += Ge
    JT[M] += par.hc * R
    JTlo, JTup = -Ge.copy(), -Ge.copy()

    if par.frozen:
        JTC_diag = z.copy()
        JTC_up = np.zeros(M)
        JTC_lo = np.zeros(M)
    else:
        a_i = (0.5 * dk[:-1]) * Gfac * dT
        b_i = (0.5 * dk[1:]) * Gfac * dT
        JTC_diag = z.copy()
        JTC_diag[:-1] += a_i
        JTC_diag[1:] += -b_i
        JTC_up, JTC_lo = b_i, -a_i
    JTC_diag += MLg * drcp * (T if par.energy == "conserv" else (T - Told)) / dt
    JTC_diag[M] += Hev * par.hm * R + dHev * par.hm * R * (C[M] - Cinf)

    if par.frozen:
        JCT_diag = z.copy()
        JCT_up = np.zeros(M)
        JCT_lo = np.zeros(M)
    else:
        c_i = (0.5 * dDdT[:-1]) * Gfac * dC
        e_i = (0.5 * dDdT[1:]) * Gfac * dC
        JCT_diag = z.copy()
        JCT_diag[:-1] += c_i
        JCT_diag[1:] += -e_i
        JCT_up, JCT_lo = e_i, -c_i

    JC = z.copy()
    JC += MC / dt
    JC[:-1] += Fe
    JC[1:] += Fe
    if par.frozen:
        JC_up, JC_lo = -Fe.copy(), -Fe.copy()
    else:
        f_i = (0.5 * dDdC[:-1]) * Gfac * dC
        g_i = (0.5 * dDdC[1:]) * Gfac * dC
        JC[:-1] += f_i
        JC[1:] += -g_i
        JC_up, JC_lo = -Fe + g_i, -Fe - f_i
    JC[M] += par.hm * R

    n2 = 2 * n
    ab = np.zeros((7, n2))
    ab[3, 0::2] = JT
    ab[3, 1::2] = JC
    ab[2, 1::2] = JTC_diag            # A[2i,   2i+1]
    ab[2, 2::2] = JCT_up              # A[2i+1, 2i+2]
    ab[1, 2::2] = JTup               # A[2i,   2i+2]
    ab[1, 3::2] = JC_up              # A[2i+1, 2i+3]
    ab[0, 3::2] = JTC_up             # A[2i,   2i+3]
    ab[4, 0::2] = JCT_diag           # A[2i+1, 2i]
    ab[4, 1:2 * M:2] = JTC_lo        # A[2i+2, 2i+1]
    ab[5, 0:2 * M:2] = JTlo          # A[2i+2, 2i]
    ab[5, 1:2 * M:2] = JC_lo         # A[2i+1, 2i-1]
    ab[6, 0:2 * M:2] = JCT_lo        # A[2i+3, 2i]

    aux = dict(MT=MT, MC=MC, Hev=Hev, flux_h=flux_h, flux_w=flux_w)
    return Res, ab, aux


def residual(x, xold, dt, g, par, Tinf, Cinf):
    return assemble(x, xold, dt, g, par, Tinf, Cinf)[0]


def newton_solve(x, xold, dt, g, par, Tinf, Cinf, ihist=None):
    """阻尼 Newton. 返回 (x, iterations, ||R||_inf).

    每个迭代只组装一次 (一次组装同时给出残差与 Jacobian): 迭代内先判残差再解,
    故 k 次迭代共 k+1 次组装 (此前实现为 2k+1 次)。若某步使残差变大则回溯减半。
    """
    R, ab, _ = assemble(x, xold, dt, g, par, Tinf, Cinf)
    rn = float(np.max(np.abs(R)))
    tol = par.rtol_R * max(rn, 1e-30) + 1e-16
    it = 0
    for it in range(1, par.max_newton + 1):
        if rn <= tol:
            break
        delta = solve_banded((3, 3), ab, -R)
        theta = 1.0
        x = x + delta
        R, ab, _ = assemble(x, xold, dt, g, par, Tinf, Cinf)
        rn_new = float(np.max(np.abs(R)))
        tries = 0
        while ((not np.isfinite(rn_new)) or rn_new > rn) and tries < 12:
            theta *= 0.5
            x = x - delta * (1.0 - theta)
            R, ab, _ = assemble(x, xold, dt, g, par, Tinf, Cinf)
            rn_new = float(np.max(np.abs(R)))
            tries += 1
        rn = rn_new
        if par.frozen:
            break
        if float(np.max(np.abs(theta * delta))) <= 1e-13:
            break
    if ihist is not None:
        ihist.append(it)
    return x, it, rn


# ---------------------------------------------------------------------------
# 时间推进
# ---------------------------------------------------------------------------
def march(M, dt, t_end, env, par=None, out_idx=None, out_every_s=1.0,
          full_at=(), verbose=False):
    """后向 Euler 时间推进, 每 out_every_s 秒记录一次 (dt 必须整除 out_every_s)."""
    if par is None:
        par = Par()
    g = geometry(M, par.boundary)
    n = g["n"]
    per_s = int(round(out_every_s / dt))
    if abs(per_s * dt - out_every_s) > 1e-12:
        raise ValueError("dt 必须整除输出采样间隔")
    nsteps = int(round(t_end / dt))
    n_out = nsteps // per_s
    if out_idx is None:
        out_idx = np.arange(n)
    out_idx = np.asarray(out_idx, dtype=int)

    x = np.empty(2 * n)
    x[0::2] = T0K
    x[1::2] = C0
    xold = x.copy()

    T_snap = np.empty((n_out, len(out_idx)))
    C_snap = np.empty((n_out, len(out_idx)))
    t_snap = np.empty(n_out)
    E_snap = np.empty(n_out)
    W_snap = np.empty(n_out)
    Fh_snap = np.empty(n_out)
    Fw_snap = np.empty(n_out)

    rho0, cp0, *_ = props(C0, par.mode)
    E0 = float(np.sum(g["MLg"] * rho0 * cp0 * T0K))
    W0 = float(np.sum(g["MLg"] * C0))

    full = {}
    full_steps = {int(round(t / dt)): t for t in full_at}
    ihist = []
    cumFh = cumFw = 0.0
    t0 = time.time()
    ptr = 0
    for step in range(1, nsteps + 1):
        tn1 = step * dt
        Tinf, Cinf = env.T(tn1), env.C(tn1)
        x, nit, _ = newton_solve(x, xold, dt, g, par, Tinf, Cinf, ihist)
        if not np.all(np.isfinite(x)):
            raise RuntimeError(f"解发散: t={tn1:.4f} s (step {step})")
        if step in full_steps:
            full[full_steps[step]] = (x[0::2].copy(), x[1::2].copy())
        # 通量用新解的边界值累积 (与后向 Euler 自洽)
        _, _, aux = assemble(x, xold, dt, g, par, Tinf, Cinf)
        cumFh += dt * aux["flux_h"]
        cumFw += dt * aux["flux_w"]
        xold = x.copy()
        if step % per_s == 0:
            T_snap[ptr] = x[0::2][out_idx]
            C_snap[ptr] = x[1::2][out_idx]
            t_snap[ptr] = tn1
            E_snap[ptr] = float(np.sum(aux["MT"] * x[0::2]))
            W_snap[ptr] = float(np.sum(aux["MC"] * x[1::2]))
            Fh_snap[ptr] = cumFh
            Fw_snap[ptr] = cumFw
            ptr += 1
        if verbose and step % max(1, nsteps // 10) == 0:
            print(f"    t={tn1:8.1f}s  T_M={x[2*M]-273.15:8.4f}C  C_M={x[2*M+1]:9.6f}"
                  f"  it={nit}  {time.time()-t0:6.1f}s", flush=True)

    return dict(r=g["r"], T_snap=T_snap, C_snap=C_snap, t_snap=t_snap,
                E=E_snap, W=W_snap, Fh=Fh_snap, Fw=Fw_snap, geom=g,
                stats=dict(iters=np.array(ihist), wall=time.time() - t0,
                           E0=E0, W0=W0, nsteps=nsteps, nmax_iter=int(ihist[0]) if ihist else 0),
                full=full)


# ---------------------------------------------------------------------------
# 核验工具
# ---------------------------------------------------------------------------
def check_lumped_mass(M):
    """集中质量恒等式: MLg[i] == dr(r_{i-1}+4r_i+r_{i+1})/6 == dr r_i (内部)."""
    g = geometry(M, "lumped")
    dr, r, MLg = g["dr"], g["r"], g["MLg"]
    ref = dr * (r[:-2] + 4 * r[1:-1] + r[2:]) / 6.0
    sc = float(np.max(np.abs(MLg)))
    return (float(np.max(np.abs(MLg[1:M] - ref))) / sc,
            float(np.max(np.abs(MLg[1:M] - dr * r[1:M]))) / sc)


def check_jacobian(M=12, dt=0.05, par=None, seed=7, eps=1e-7):
    """解析 Jacobian 与中心差分 Jacobian 的密矩阵逐元比较."""
    if par is None:
        par = Par()
    g = geometry(M, par.boundary)
    n = g["n"]
    rng = np.random.default_rng(seed)
    x = np.empty(2 * n)
    x[0::2] = T0K + rng.uniform(0.0, 3.0, n)
    x[1::2] = C0 - rng.uniform(0.0, 0.4, n)
    xold = x.copy()
    xold[0::2] = x[0::2] - 0.5
    xold[1::2] = x[1::2] + 0.02
    Tinf, Cinf = 320.0, 0.045
    _, ab, _ = assemble(x, xold, dt, g, par, Tinf, Cinf)
    n2 = 2 * n
    dense = np.zeros((n2, n2))
    for j in range(n2):
        for d in range(4):
            if j + d < n2:
                dense[j + d, j] = ab[3 + d, j]
            if d > 0 and j - d >= 0:
                dense[j - d, j] = ab[3 - d, j]
    fd = np.zeros((n2, n2))
    for j in range(n2):
        xp = x.copy(); xp[j] += eps
        xm = x.copy(); xm[j] -= eps
        fd[:, j] = (residual(xp, xold, dt, g, par, Tinf, Cinf)
                    - residual(xm, xold, dt, g, par, Tinf, Cinf)) / (2 * eps)
    return float(np.max(np.abs(dense - fd)) / max(float(np.max(np.abs(fd))), 1e-30))


def out_indices(M, r_cm=None):
    """输出半径 (cm) 在网格 M 上的节点下标; 不在节点上则报错."""
    if r_cm is None:
        r_cm = np.round(np.arange(0.0, 2.0001, 0.1), 10)
    dr = R / M
    idx = np.rint(np.asarray(r_cm) / 100.0 / dr).astype(int)
    err = float(np.max(np.abs(idx * dr - np.asarray(r_cm) / 100.0)))
    if err > 1e-12:
        raise ValueError(f"输出半径不落在网格上: M={M}, max err={err:.2e} m")
    return idx


def boundary_flux(T_M, C_M, Tinf, Cinf, par):
    """边界热流与水流 (per 2 pi, 单位轴长, 向外为正)."""
    Hev, _ = hevap_of(T_M, par)
    qh = par.hc * R * (T_M - Tinf) + Hev * par.hm * R * (C_M - Cinf)
    qw = par.hm * R * (C_M - Cinf)
    return qh, qw


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if not (args.selftest or args.demo):
        args.selftest = True

    if args.selftest:
        print("=" * 96)
        print("S1  集中质量矩阵行和恒等式 (problem2.md §9.3)")
        print("     MLg[i] == dr (r_{i-1} + 4 r_i + r_{i+1})/6 == dr r_i  (1<=i<=M-1)")
        print("=" * 96)
        for M in (10, 100, 800, 3200):
            a, b = check_lumped_mass(M)
            print(f"  M={M:5d}  行和式偏差={a:.3e}   dr*r_i 偏差={b:.3e}   "
                  f"{'OK' if max(a, b) < 1e-14 else '!!'}")

        print()
        print("=" * 96)
        print("S2  解析 Jacobian vs 中心差分 (M=12 密矩阵逐元比较)")
        print("=" * 96)
        cases = [("默认: H_evap(T), rho cp dT/dt", Par()),
                 ("H_evap = 0", Par(hevap="off")),
                 ("H_evap = 常数", Par(hevap="const")),
                 ("守恒形式 d(rho cp T)/dt", Par(energy="conserv")),
                 ("halfcv 边界积分", Par(boundary="halfcv")),
                 ("附录2 物性", Par(mode="app2")),
                 ("系数冻结 (准 Newton, 预期不匹配)", Par(frozen=True))]
        for name, p in cases:
            rel = check_jacobian(par=p)
            exp = "预期: 冻结 Jacobian 故意丢弃 d/dC, d/dT 交叉项" if p.frozen else "OK"
            flag = "OK" if (rel < 1e-6 or p.frozen) else "!! 需检查"
            print(f"  {name:34s} max|J_ana-J_fd|/max|J_fd| = {rel:.3e}   {flag}")
            if p.frozen:
                print(f"      ({exp})")

        print()
        print("=" * 96)
        print("S3  附录3 物性与 D (对照 problem2.md §5)")
        print("=" * 96)
        for C in (2.55, 2.00, 1.00, 0.50, 0.15):
            rho, cp, k, _, _, _ = props(C, "app3")
            print(f"  C={C:5.2f}  rho={float(rho):9.2f}  cp={float(cp):9.2f}  "
                  f"k={float(k):8.5f}  rho*cp={float(rho*cp):12.1f}  "
                  f"alpha={float(k/(rho*cp)):.4e}")
        for C, Tc in ((2.55, 28), (2.55, 50), (1.00, 50), (0.15, 50), (0.05, 50)):
            print(f"  D(C={C:4.2f}, {Tc:2.0f}C) = {float(Dfun(C, Tc + 273.15)):.6e} m2/s")

        print()
        print("=" * 96)
        print("S4  定解条件与边界项系数")
        print("=" * 96)
        print(f"  R={R} m, T0={T0K} K, C0={C0} kg/kg, h={H_CONV}, h_m={HM}")
        print(f"  H_evap(28C)={HEVAP_28:.1f} J/kg, dH/dT={HEVAP_SLOPE:.1f} J/(kg K)")
        print(f"  Jacobian 元 H_evap h_m R = {HEVAP_28*HM*R:.8f}  (对角元 1/dt 的 "
              f"{100*HEVAP_28*HM*R*0.25:.4f}% @dt=0.25 s)")

    if args.demo:
        t1, T1, C1 = load_attachment1()
        env = Env(t1, T1, C1, method="pchip")
        print("[demo] M=200, dt=0.25 s, t_end=1800 s")
        o = march(200, 0.25, 1800.0, env, Par(), out_idx=out_indices(200))
        print(f"  t=1800s  T(0)={o['T_snap'][-1,0]-273.15:.4f} C  "
              f"T(R)={o['T_snap'][-1,-1]-273.15:.4f} C  "
              f"C(R)={o['C_snap'][-1,-1]:.5f}  wall={o['stats']['wall']:.1f}s")


if __name__ == "__main__":
    main()
