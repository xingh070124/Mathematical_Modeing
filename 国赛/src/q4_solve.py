# -*- coding: utf-8 -*-
"""
q4_solve.py -- 问题四(收缩体烘干时长)求解器.

模型 (model/problem4.md):
    仿射(均匀)收缩假设下取物质坐标 xi = r/R(t) in [0,1], 求解域固定.
    干基水分守恒在该坐标下给出 (无对流露项):

        rho(C) cp(C) dT/dt = (1/(xi R(t)^2)) d/dxi ( xi k(C) dT/dxi )
        dC/dt              = (1/(xi R(t)^2)) d/dxi ( xi D(C,T) dC/dxi )

    表面 xi=1 (物理半径 R(t)) 第三类边界:
        -k/R dT/dxi = h (T - Tinf) + Lv(T) hm (C - Cinf)
        -D/R dC/dxi = hm (C - Cinf)

    数值方案与问题三同构(线方法 + 自适应 BDF + 终止事件), 差别仅在于:
        (1) 无量纲几何 (dxi = 1/M) 代替物理网格;
        (2) 每个 RHS 分量除以 R(t)^2, 表面通量项带物理半径因子 R(t);
        (3) 物性改用附录 4.
    当 R(t) == R0 且物性取附录 3 时本模块退化为问题三的等价形式,
    --selftest 的 [V0] 用 t_dry 逐位复现问题三作为硬校验.

入口:
    python src/q4_solve.py --selftest  [V0] 复现问题三 / Jacobian FD 校核 / 半径数据检查
    python src/q4_solve.py --solve     生产配置单次求解
"""

from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import load_attachment1                                   # noqa: E402
from q2_solve import (H_CONV, HM, R as R0, T0K, C0,                    # noqa: E402
                      HEVAP_28, HEVAP_SLOPE, HEVAP_TREF)
from q3_solve import Q3Env, CSTAR, TBAR_C, CBAR, TAU, T_MAX            # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")
ATT2 = os.path.join(ROOT, "A题", "附件", "附件2.xlsx")

# ---------------------------------------------------------------------------
# 附录 4 物性经验式 (题面) —— 与附录 3 同构, 仅系数不同
# ---------------------------------------------------------------------------
P4 = dict(rho0=760.0, krho=90.0, cp0=1850.0, kcp=2150.0,
          k0=0.12, kk=0.20, D0=4.2e-4, kD=0.30, EA=3850.0)
P3 = dict(rho0=650.0, krho=128.0, cp0=1450.0, kcp=2736.0,
          k0=0.21, kk=0.38, D0=2.4e-3, kD=0.45, EA=3850.0)
APP = {"app4": P4, "app3": P3}

# 生产配置 (与问题三同量级; 见 problem4.md §6)
PROD_M = 200
PROD_RTOL = 1e-9
PROD_ATOL_T = 1e-6
PROD_ATOL_C = 1e-9
PROD_MAX_STEP = 3600.0


# ---------------------------------------------------------------------------
# 半径 R(t): 附件 2
# ---------------------------------------------------------------------------
def load_attachment2(path=ATT2):
    """读取附件 2: 返回 (t[s], R[cm])."""
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))[1:]
    rows = [r for r in rows if r[0] is not None and r[1] is not None]
    t = np.array([float(r[0]) for r in rows])
    R = np.array([float(r[1]) for r in rows])
    o = np.argsort(t)
    return t[o], R[o]


class Q4Radius:
    """收缩半径 R(t) [m].

    mode="data"  : 附件 2 的保形分段三次插值 (PCHIP, 单调不过冲)
    mode="const" : 常数 R0 (隔离"收缩效应", 与问题三对照)
    可选 scale (整体缩放), floor (最小半径).
    t > t_end 时保持末值 (附件 2 末段 R 已近平坦, 见 problem4.md §3.4).
    """

    def __init__(self, t=None, R_cm=None, mode="data", scale=1.0, floor=None,
                 R0_m=R0, kind="pchip"):
        from scipy.interpolate import PchipInterpolator, interp1d
        self.mode = mode
        self.kind = kind
        self.scale = float(scale)
        self.R0 = float(R0_m)
        self.floor = None if floor is None else float(floor)
        if mode == "const":
            self.t_end = float("inf")
            self._p = None
            self._dp = None
            self._Rend = self.R0 * self.scale
        else:
            if t is None:
                t, R_cm = load_attachment2()
            self.t_end = float(t[-1])
            Rm = np.asarray(R_cm, float) * 1e-2
            if kind == "linear":
                f = interp1d(t, Rm, kind="linear")
                self._p = lambda x: np.interp(x, t, Rm)
                self._dp = lambda x: np.gradient(np.interp(x, t, Rm), x) if np.ndim(x) else 0.0
                self._Rend = float(np.interp(self.t_end, t, Rm))
            else:
                self._p = PchipInterpolator(t, Rm)
                self._Rend = float(self._p(self.t_end))
                self._dp = self._p.derivative()

    def R(self, t):
        if self.mode == "const":
            return self._Rend if np.ndim(t) == 0 else np.full(np.shape(t), self._Rend)
        t = np.asarray(t, dtype=float)
        out = np.where(t <= self.t_end, self._p(np.minimum(t, self.t_end)), self._Rend)
        return np.asarray(out, float) * self.scale

    def Rdot(self, t):
        """dR/dt [m/s]; 仅诊断与 euler 对照格式使用, 物质坐标格式不需要."""
        if self.mode == "const":
            return 0.0 if np.ndim(t) == 0 else np.zeros(np.shape(t))
        t = np.asarray(t, dtype=float)
        out = np.where(t <= self.t_end, self._dp(np.minimum(t, self.t_end)), 0.0)
        return np.asarray(out, float) * self.scale

    def stats(self):
        t, Rc = load_attachment2()
        dR = np.diff(Rc)
        return dict(n=int(t.size), dt=float(t[1] - t[0]), t_end=float(t[-1]),
                    R0=float(Rc[0]), Rend=float(Rc[-1]),
                    n_up=int((dR > 0).sum()), dR_max=float(np.abs(dR).max()),
                    t_R15=float(t[int(np.argmax(Rc <= 1.5))]),
                    t_R12=float(t[int(np.argmax(Rc <= 1.2))]))


# ---------------------------------------------------------------------------
# 无量纲几何 (xi in [0,1]) —— 与 q2_solve.geometry 同构, 取半径 1
# ---------------------------------------------------------------------------
def geometry_xi(M):
    dr = 1.0 / M
    r = np.arange(M + 1) * dr
    Gfac = (0.5 * (r[:-1] + r[1:])) / dr
    MLg = np.empty(M + 1)
    MLg[0] = dr * (2.0 * r[0] + r[1]) / 6.0
    MLg[M] = dr * (r[M - 1] + 2.0 * r[M]) / 6.0
    MLg[1:M] = dr * r[1:M]
    return dict(M=M, n=M + 1, dr=dr, xi=r, Gfac=Gfac, MLg=MLg)


# ---------------------------------------------------------------------------
# 附录物性 (参数化, 供灵敏度 / 蒙特卡洛)
# ---------------------------------------------------------------------------
def props_p(C, p):
    """返回 (rho, cp, k, drho/dC, dcp/dC, dk/dC)."""
    C = np.asarray(C, dtype=float)
    Cp1 = C + 1.0
    return (p["rho0"] + p["krho"] * C,
            p["cp0"] + p["kcp"] * C / Cp1,
            p["k0"] + p["kk"] * C / Cp1,
            np.full_like(C, p["krho"]),
            p["kcp"] / Cp1 ** 2,
            p["kk"] / Cp1 ** 2)


def Dfun_p(C, T, p):
    C = np.asarray(C, float)
    T = np.asarray(T, float)
    return p["D0"] * np.exp(-p["kD"] / C) * np.exp(-p["EA"] / T)


def D_derivs_p(C, T, p):
    C, T = np.asarray(C, float), np.asarray(T, float)
    D = Dfun_p(C, T, p)
    return D * p["kD"] / C ** 2, D * p["EA"] / T ** 2


def _fluxes(C, T, p, g):
    """节点物性与单元系数 (RHS 与 Jacobian 共用)."""
    M, n = g["M"], g["n"]
    rho, cp, k, drho, dcp, dk = props_p(C, p)
    rcp = rho * cp
    drcp = drho * cp + rho * dcp
    Dv = Dfun_p(C, T, p)
    dDdC, dDdT = D_derivs_p(C, T, p)
    Ge = 0.5 * (k[:-1] + k[1:]) * g["Gfac"]
    Fe = 0.5 * (Dv[:-1] + Dv[1:]) * g["Gfac"]
    return rho, cp, k, dk, rcp, drcp, Dv, dDdC, dDdT, Ge, Fe


def _tri(lo, diag, up):
    return sp.diags([lo, diag, up], [-1, 0, 1], format="csr")


# ---------------------------------------------------------------------------
# 线方法: RHS
# ---------------------------------------------------------------------------
def make_rhs(g, env, rad, hevap=True, params=None, form="material", eta=0.0,
             hc=None, hm=None, lv_mult=1.0):
    """半离散 ODE 右端 F(t, U).

    form="material" : 物质坐标 (本文模型, 无对流露项)
    form="euler"    : 物理坐标的朴素移动域格式 (对照用): 额外 + (xi Rdot/R) d/dxi U,
                      一阶迎风差分; 该格式不保持干基水量守恒 (problem4.md §3.3)

    eta : 收缩模式参数, 只影响几何增强因子 phi = (R0/R)^(2 eta)
          eta = 0 : 仿射(均匀)收缩, 干物质守恒 (本文模型)
          eta = 1 : 边缘收缩 (收缩全部发生在表面附近)
          eta = -1: 除表面通量外忽略收缩
          仅用于鲁棒性对照, 见 q4_sensitivity.py。
    """
    M, n = g["M"], g["n"]
    Gfac, MLg, xi, dxi = g["Gfac"], g["MLg"], g["xi"], g["dr"]
    p = APP["app4"] if params is None else params
    R0m = float(rad.R(0.0))
    h = H_CONV if hc is None else float(hc)
    hm = HM if hm is None else float(hm)

    def rhs(t, U):
        T, C = U[:n], U[n:]
        Rc = float(rad.R(t))
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, _, _, _ = props_p(C, p)
        rcp = rho * cp
        Dv = Dfun_p(C, T, p)
        if eta == 0.0:
            phi = 1.0
        else:
            phi = (R0m / Rc) ** (2.0 * eta)
        Ge = 0.5 * (k[:-1] + k[1:]) * Gfac
        Fe = 0.5 * (Dv[:-1] + Dv[1:]) * Gfac * phi
        dT = T[:-1] - T[1:]
        dC = C[:-1] - C[1:]
        KT = np.zeros(n)
        KT[:-1] += Ge * dT
        KT[1:] -= Ge * dT
        KC = np.zeros(n)
        KC[:-1] += Fe * dC
        KC[1:] -= Fe * dC
        if hevap:
            Lv = (HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)) * lv_mult
            flux_h = h * Rc * (T[M] - Tinf) + Lv * hm * Rc * (C[M] - Cinf)
        else:
            flux_h = h * Rc * (T[M] - Tinf)
        flux_w = hm * Rc * (C[M] - Cinf)
        s = 1.0 / (Rc * Rc)
        FT = -KT * s / (MLg * rcp)
        FC = -KC * s / MLg
        FT[M] -= flux_h * s / (MLg[M] * rcp[M])
        FC[M] -= flux_w * s / MLg[M]
        if form == "euler":
            Rd = float(rad.Rdot(t))
            a = xi * (Rd / Rc)                     # <= 0, 指向中心 (迎风: 用上游 i-1)
            dTdxi = np.zeros(n)
            dCdxi = np.zeros(n)
            dTdxi[1:] = (T[1:] - T[:-1]) / dxi
            dCdxi[1:] = (C[1:] - C[:-1]) / dxi
            FT = FT + a * dTdxi
            FC = FC + a * dCdxi
        return np.concatenate([FT, FC])

    return rhs


# ---------------------------------------------------------------------------
# 线方法: 解析稀疏 Jacobian (物质坐标格式, 每行 <= 3 非零元/块)
# ---------------------------------------------------------------------------
def make_jac(g, env, rad, hevap=True, params=None, form="material",
             hc=None, hm=None, lv_mult=1.0):
    M, n = g["M"], g["n"]
    Gfac, MLg, xi, dxi = g["Gfac"], g["MLg"], g["xi"], g["dr"]
    p = APP["app4"] if params is None else params
    h = H_CONV if hc is None else float(hc)
    hm = HM if hm is None else float(hm)

    def jac(t, U):
        T, C = U[:n], U[n:]
        Rc = float(rad.R(t))
        Cinf = env.C(t)
        (rho, cp, k, dk, rcp, drcp, Dv, dDdC, dDdT, Ge, Fe) = _fluxes(C, T, p, g)
        dT = T[:-1] - T[1:]
        dC = C[:-1] - C[1:]
        s = 1.0 / (Rc * Rc)
        if hevap:
            Lv = (HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)) * lv_mult
            Lvp = HEVAP_SLOPE * lv_mult
            flux_h = h * Rc * (T[M] - env.T(t)) + Lv * hm * Rc * (C[M] - Cinf)
        else:
            Lv, Lvp = 0.0, 0.0
            flux_h = h * Rc * (T[M] - env.T(t))
        KT = np.zeros(n)
        KT[:-1] += Ge * dT
        KT[1:] -= Ge * dT
        KC = np.zeros(n)
        KC[:-1] += Fe * dC
        KC[1:] -= Fe * dC
        NT = -KT.copy()
        NT[M] -= flux_h
        NC = -KC.copy()
        NC[M] -= hm * Rc * (C[M] - Cinf)

        # ---- 温度块 dN_i/dT_j : -K_ij (k 不依赖 T) ----
        sumGe = np.concatenate([Ge, [0.0]]) + np.concatenate([[0.0], Ge])
        diagT = -sumGe.copy()
        diagT[M] += -h * Rc
        if hevap:
            diagT[M] += -Lvp * hm * Rc * (C[M] - Cinf)
        # -K 的非对角元为 +Ge: K_ij = -Ge (|i-j|=1), 故 dFT/dT 的非对角元 = +Ge/(MLg rcp R^2)
        JTT = _tri(Ge, diagT, Ge)

        # ---- dN_i/dC_j = -d(KT)_i/dC_j ; 单元 e 的系数 p_e (=d/dC_e), q_e (=d/dC_{e+1}) ----
        pe = 0.5 * dk[:-1] * Gfac * dT
        qe = 0.5 * dk[1:] * Gfac * dT
        dKT_diag = np.zeros(n)
        dKT_diag[:n - 1] += pe
        dKT_diag[1:] += -qe
        dKT_up = qe.copy()              # (i, i+1)
        dKT_lo = -pe.copy()             # (i+1, i)
        dNTC = _tri(-dKT_lo, -dKT_diag, -dKT_up)
        # 质量矩阵对 C 的依赖: -N_i (d(rcp)/dC)_i / rcp_i (仅对角)
        dNTC = dNTC - sp.diags(NT * drcp / rcp)
        if hevap:
            dNTC = dNTC - sp.diags(np.where(np.arange(n) == M, Lv * hm * Rc, 0.0))

        # ---- dN_C/dC_j = -d(KC)_i/dC_j - delta_iM hm R ----
        dKC_diag = np.zeros(n)
        dKC_diag[:n - 1] += Fe + 0.5 * dDdC[:-1] * Gfac * dC
        dKC_diag[1:] += Fe - 0.5 * dDdC[1:] * Gfac * dC
        dKC_up = 0.5 * dDdC[1:] * Gfac * dC - Fe          # (i, i+1)
        dKC_lo = -0.5 * dDdC[:-1] * Gfac * dC - Fe        # (i+1, i)
        JCC = _tri(-dKC_lo, -dKC_diag, -dKC_up)
        JCC = JCC - sp.diags(np.where(np.arange(n) == M, hm * Rc, 0.0))

        # ---- dN_C/dT_j : 仅经由 De 的 T 依赖 ----
        dKC_diag_T = np.zeros(n)
        dKC_diag_T[:n - 1] += 0.5 * dDdT[:-1] * Gfac * dC
        dKC_diag_T[1:] += -0.5 * dDdT[1:] * Gfac * dC
        dKC_up_T = 0.5 * dDdT[1:] * Gfac * dC
        dKC_lo_T = -0.5 * dDdT[:-1] * Gfac * dC
        JCT = _tri(-dKC_lo_T, -dKC_diag_T, -dKC_up_T)

        # ---- 行缩放: FT = N_i/(MLg_i rcp_i R^2),  FC = N_i/(MLg_i R^2) ----
        wT = s / (MLg * rcp)
        wC = s / MLg
        JTT = sp.diags(wT) @ JTT
        JTC = sp.diags(wT) @ dNTC
        JCT = sp.diags(wC) @ JCT
        JCC = sp.diags(wC) @ JCC
        if form == "euler":
            Rd = float(rad.Rdot(t))
            a = xi * (Rd / Rc)
            # 迎风差分算子 D_up: (D_up U)_i = (U_i - U_{i-1})/dxi, i>=1; i=0 -> 0
            lo = -a[1:] / dxi
            diag = np.zeros(n)
            diag[1:] = a[1:] / dxi
            Dup = _tri(lo, diag, np.zeros(n - 1))
            I0 = sp.identity(n, format="csr")
            J = sp.bmat([[JTT + Dup, JTC], [JCT, JCC + Dup]], format="csr")
            return J
        return sp.bmat([[JTT, JTC], [JCT, JCC]], format="csr")

    return jac


def sparsity_pattern(g):
    M, n = g["M"], g["n"]

    def blk(roff, coff):
        rr = np.concatenate([np.arange(n), np.arange(M), np.arange(1, n)]) + roff
        cc = np.concatenate([np.arange(n), np.arange(1, n), np.arange(M)]) + coff
        return rr, cc

    rr = np.concatenate([blk(0, 0)[0], blk(0, n)[0], blk(n, 0)[0], blk(n, n)[0]])
    cc = np.concatenate([blk(0, 0)[1], blk(0, n)[1], blk(n, 0)[1], blk(n, n)[1]])
    return sp.coo_matrix((np.ones(rr.size), (rr, cc)),
                         shape=(2 * n, 2 * n)).tocsr()


# ---------------------------------------------------------------------------
# 求解
# ---------------------------------------------------------------------------
def make_event(n, cstar=CSTAR):
    def event(t, U, _n=n, _c=cstar):
        return U[_n:].max() - _c
    event.terminal = True
    event.direction = -1.0
    return event


def solve_q4(M=PROD_M, rtol=PROD_RTOL, atol_T=PROD_ATOL_T, atol_C=PROD_ATOL_C,
             max_step=PROD_MAX_STEP, t_max=T_MAX, cstar=CSTAR, method="BDF",
             jac_mode="analytic", hevap=True, env=None, tau=TAU,
             Tbar_C=TBAR_C, Cbar=CBAR, params=None, app="app4",
             form="material", rad=None, rad_mode="data", rad_scale=1.0,
             t_span=None, rad_kind="pchip", eta=0.0, hc=None, hm=None,
             lv_mult=1.0):
    """MOL + 自适应 BDF + 终止事件. 返回 dict(sol, t_dry, 统计)."""
    g = geometry_xi(M)
    n = g["n"]
    if env is None:
        t1, T1, C1 = load_attachment1()
        env = Q3Env(t1, T1, C1, tau=tau, Tbar_C=Tbar_C, Cbar=Cbar)
    if rad is None:
        rad = Q4Radius(mode=rad_mode, scale=rad_scale, kind=rad_kind)
    if params is None:
        params = APP[app]
    skw = dict(hc=hc, hm=hm, lv_mult=lv_mult)
    rhs = make_rhs(g, env, rad, hevap=hevap, params=params, form=form,
                   eta=eta, **skw)
    kw = {}
    if jac_mode == "analytic":
        kw["jac"] = make_jac(g, env, rad, hevap=hevap, params=params,
                            form=form, **skw)
    elif jac_mode == "sparsity":
        kw["jac_sparsity"] = sparsity_pattern(g)
    elif jac_mode not in ("dense", "none"):
        raise ValueError(f"jac_mode={jac_mode} 不合法")

    event = make_event(n, cstar)
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atol = np.concatenate([np.full(n, atol_T), np.full(n, atol_C)])
    span = (0.0, float(t_max)) if t_span is None else t_span
    t0 = time.time()
    sol = solve_ivp(rhs, span, U0, method=method, rtol=rtol,
                    atol=atol, max_step=float(max_step), events=event,
                    dense_output=True, **kw)
    wall = time.time() - t0
    if sol.status != 1 or len(sol.t_events[0]) == 0:
        Ce = sol.y[n:, -1]
        i = int(Ce.argmax())
        raise RuntimeError(
            f"终止事件未触发: status={sol.status}, t={sol.t[-1]:.1f} s, "
            f"max_i C_i = {Ce.max():.6f} @ xi={g['xi'][i]:.3f} "
            f"(物理 r = {g['xi'][i] * float(rad.R(sol.t[-1])) * 100:.3f} cm)")
    return dict(sol=sol, g=g, env=env, rad=rad, t_dry=float(sol.t_events[0][0]),
                nsteps=len(sol.t) - 1, nfev=int(sol.nfev), njev=int(sol.njev),
                nlu=int(sol.nlu), wall=wall, M=M, n=n, rtol=rtol, app=app,
                atol_T=atol_T, atol_C=atol_C, max_step=max_step, form=form,
                method=method, jac_mode=jac_mode, status=int(sol.status),
                tau=env.tau, Tbar=env.Tbar, Cbar=env.Cbar, params=params,
                rad_mode=rad.mode, rad_scale=rad.scale, hevap=hevap)


# ---------------------------------------------------------------------------
# 输出采样: 物理半径口径与材料坐标口径
# ---------------------------------------------------------------------------
def sample_q4(sol, g, rad, t_dry, r_out_cm=(0.0, 0.5, 1.0, 1.5, 2.0),
              grid_cm=None):
    """物理半径口径采样 (超出当前表面的位置记 NaN).

    返回:
      t60 : 60 s 网格 (不含 t=0)
      Cg  : (n60, len(grid_cm)) 物理半径处的水分浓度
      Cs  : (n60,) 表面 r=R(t) 处
      Rs  : (n60,) R(t) [cm]
      Ts  : 表面温度 [degC];  Tmax: 全场最高温度 [degC]
      W60 : 总水量 (干基质量加权, 去掉 2 pi L 因子)
      matC: (n60, len(r_out_cm)) 材料坐标口径 (初始半径 r0 处)
    """
    if grid_cm is None:
        grid_cm = np.arange(0.0, 2.0 + 1e-9, 0.1)
    grid_cm = np.asarray(grid_cm, float)
    n = g["n"]
    xi = g["xi"]
    n60 = int(np.floor(t_dry / 60.0))
    t60 = 60.0 * np.arange(1, n60 + 1)
    Y = sol.sol(t60)
    C = Y[n:, :]
    T = Y[:n, :]
    Rt = np.atleast_1d(np.asarray(rad.R(t60), float))
    R0m = float(rad.R(0.0))
    Cs = C[-1, :]
    Cg = np.full((n60, grid_cm.size), np.nan)
    for j, rcm in enumerate(grid_cm):
        xit = (rcm * 1e-2) / Rt
        ok = np.where(xit <= 1.0 + 1e-12)[0]
        if ok.size == 0:
            continue
        # 各处 R(t) 不同 -> 目标 xi 随列变化, 逐列线性插值 (M=200 时误差 O(dxi^2))
        cols = C[:, ok]
        Cg[ok, j] = [np.interp(xit[i], xi, cols[:, k]) for k, i in enumerate(ok)]
    idx = [int(round((r0 * 1e-2) / R0m * g["M"])) for r0 in r_out_cm]
    matC = C[idx, :].T
    W = (g["MLg"][:, None] * C).sum(axis=0)
    return dict(t60=t60, n60=n60, grid_cm=grid_cm, Cg=Cg, Cs=Cs, Rs=Rt * 100.0,
                Ts=T[-1, :] - 273.15, Tmax=T.max(axis=0) - 273.15,
                W60=W, W0=float(g["MLg"].sum() * C0),
                matC=matC, r_out_cm=np.asarray(r_out_cm, float),
                maxC=C.max(axis=0))


def crossing_times_q4(sol, g, rad, t_dry, cstar=CSTAR, r_out_cm=(0.0, 0.5, 1.0),
                      t_grid=None):
    """物理半径 r 处 C 首次降到阈值的时刻.

    返回 {r_cm: t_s 或 None}; None 表示该位置在过程中收缩出域 (r > R(t)),
    或在整个 [0, t_dry] 内未达到阈值. 为区分两种情形, 另返回 {r_cm: 'str'} 标记:
        'out'    : r > R(t_dry) 或中途出域
        'inside' : 全程在域内但未达标 (应只出现在 t 网格未覆盖 t_dry 时)
    """
    from scipy.optimize import brentq
    n = g["n"]
    xi = g["xi"]
    tg = np.arange(1, int(np.floor(t_dry / 60.0)) + 1) * 60.0 if t_grid is None else t_grid
    Y = sol.sol(tg)
    C = Y[n:, :]
    Rt = np.atleast_1d(np.asarray(rad.R(tg), float))
    out, flag = {}, {}
    for rcm in r_out_cm:
        xit = (rcm * 1e-2) / Rt
        if (xit > 1.0 + 1e-12).any():
            out[rcm] = None
            flag[rcm] = "out"
            continue
        vals = np.array([np.interp(xit[i], xi, C[:, i]) for i in range(tg.size)])
        idx = np.where(vals < cstar)[0]
        if idx.size == 0:
            out[rcm] = None
            flag[rcm] = "inside"
            continue
        i0 = idx[0]
        t_lo = tg[i0 - 1] if i0 > 0 else 0.0
        t_hi = tg[i0]

        def f(t, _r=rcm):
            x_ = (_r * 1e-2) / float(rad.R(t))
            if x_ > 1.0:
                return 1.0
            return float(np.interp(x_, xi, sol.sol(t)[n:])) - cstar
        try:
            out[rcm] = float(brentq(f, t_lo, t_hi, xtol=1e-6))
        except ValueError:
            out[rcm] = float(t_hi)
        flag[rcm] = "ok"
    return out, flag
    """物理半径 r 处 C 首次降到阈值的时刻; r 越界后返回 None."""


# ---------------------------------------------------------------------------
# 自检
# ---------------------------------------------------------------------------
def check_jacobian_fd(M=12, t=1.0e4, seed=7, eps=1e-7, app="app4", form="material"):
    """中心差分逐元核验解析 Jacobian."""
    rng = np.random.default_rng(seed)
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    g = geometry_xi(M)
    rad = Q4Radius()
    n = g["n"]
    U = np.concatenate([np.full(n, T0K) + 3.0 * rng.standard_normal(n),
                        C0 * (0.6 + 0.4 * rng.random(n))])
    rhs = make_rhs(g, env, rad, params=APP[app], form=form)
    J = np.asarray(make_jac(g, env, rad, params=APP[app], form=form)(t, U).todense())
    Jfd = np.zeros_like(J)
    for j in range(2 * n):
        d = np.zeros(2 * n)
        d[j] = eps * max(abs(U[j]), 1.0)
        Jfd[:, j] = (rhs(t, U + d) - rhs(t, U - d)) / (2 * d[j])
    big = np.abs(Jfd) > 1e-9 * np.max(np.abs(Jfd))
    rel = np.abs(J - Jfd)[big] / np.maximum(np.abs(Jfd)[big], 1e-12)
    extra = np.abs(J)[~big].max() if (~big).any() else 0.0
    return dict(max_rel=float(rel.max()), n_checked=int(big.sum()),
                max_extra=float(extra))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--solve", action="store_true")
    ap.add_argument("--M", type=int, default=PROD_M)
    a = ap.parse_args()
    if a.selftest:
        print("[A2] 附件2:", Q4Radius().stats())
        for app in ("app4", "app3"):
            forms = ("material", "euler") if app == "app4" else ("material",)
            for form in forms:
                r = check_jacobian_fd(app=app, form=form)
                print(f"[JAC] app={app} form={form}: n={r['n_checked']} "
                      f"max_rel={r['max_rel']:.3e} max_extra={r['max_extra']:.3e}")
        print("[V0] R=const(2cm) + 附录3 应复现问题三 t_dry = 206726.278 s")
        res = solve_q4(M=200, app="app3", rad_mode="const")
        print(f"     t_dry = {res['t_dry']:.3f} s = {res['t_dry']/3600:.4f} h "
              f"(nsteps={res['nsteps']}, wall={res['wall']:.1f} s)")
    if a.solve:
        res = solve_q4(M=a.M)
        print(f"t_dry = {res['t_dry']:.3f} s = {res['t_dry']/3600:.4f} h "
              f"(nsteps={res['nsteps']}, wall={res['wall']:.1f} s)")
        s = sample_q4(res["sol"], res["g"], res["rad"], res["t_dry"])
        print("R(t_dry) =", s["Rs"][-1], "cm ; C_surface(t_dry) =", s["Cs"][-1])


if __name__ == "__main__":
    main()
