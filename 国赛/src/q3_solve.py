# -*- coding: utf-8 -*-
"""
q3_solve.py -- 问题三(确定烘干时间) 求解器: 线方法(MOL) + scipy 自适应 BDF + 终止事件.

控制方程 / 物性 / 空间离散与问题二完全一致 (problem2.md, q2_solve.py);
问题三的差异只在时间积分方案与求解目标 (problem3.md):
    * 终止时刻 t_dry 是未知量, 由事件 g(t,U) = max_i C_i - C* = 0 隐式定义;
    * 时间跨度 ~2.07e5 s (问题二的 19 倍), 必须自适应变阶(1~5)变步长;
    * t > 14400 s 的环境条件需外推: 恒温平台 (附件1 末段均值) + 线性过渡 (§6.4).

半离散 ODE 系统 (problem3.md §8.3, 集中质量矩阵为对角 => 标准 ODE):
    U = (T_0..T_M, C_0..C_M) in R^{2(M+1)}
    dT_i/dt = -(K(C) T)_i / (MLg_i rho cp_i)                          (i < M)
    dT_M/dt = -[(K T)_M + hR(T_M-T_inf) + H_evap h_m R (C_M-C_inf)]
              / (MLg_M rho cp_M)
    dC_i/dt = -(K^C(C,T) C)_i / MLg_i                                 (i < M)
    dC_M/dt = -[(K^C C)_M + h_m R (C_M-C_inf)] / MLg_M

解析稀疏 Jacobian (problem3.md §8.4 + H_evap(T_M) 的温度导数修正):
每行 <= 6 个非零元; 由 --selftest 的中心差分逐元核验.

入口:
    python src/q3_solve.py --selftest   质量恒等式 / Jacobian FD 校核 / 环境连续性 / 冒烟求解
    python src/q3_solve.py --solve      生产配置单次求解 (打印 t_dry 与表5)
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

from q1_solve import load_attachment1                                  # noqa: E402
from q2_solve import (props, Dfun, D_derivs, geometry, out_indices,    # noqa: E402
                      H_CONV, HM, R, T0K, C0, HEVAP_28, HEVAP_SLOPE, HEVAP_TREF)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

# ---------------------------------------------------------------------------
# 问题三常数 (problem3.md §5.1, §6.4, §10, §11)
# ---------------------------------------------------------------------------
CSTAR = 0.15        # kg/kg, 烘干达标阈值 (题面)
TBAR_C = 50.00      # degC, 恒温干燥阶段环境温度 (附件1 末段均值, 4 位有效数字)
CBAR = 0.0500       # kg/kg, 恒温干燥阶段环境水分浓度 (同上)
T_CEND = 14400.0    # s,     附件1 覆盖上界 t_c
TAU = 600.0         # s,     PCHIP -> 平台的线性过渡段长度 (10 min)
T_MAX = 259200.0    # s,     积分上界 (3 天, 安全网, §10.5)

# 生产配置 (problem3.md §11.1)
PROD_M = 200
PROD_RTOL = 1e-9
PROD_ATOL_T = 1e-6    # K
PROD_ATOL_C = 1e-9    # kg/kg
PROD_MAX_STEP = 3600.0  # s


# ---------------------------------------------------------------------------
# 环境激励 (problem3.md §6.4)
# ---------------------------------------------------------------------------
class Q3Env:
    """问题三环境激励: 附件1 PCHIP + 恒温平台 + 线性过渡.

        t <= t_c - tau : 附件1 保形分段三次插值 (PCHIP)
        t in [t_c-tau, t_c]: PCHIP 与平台值的线性过渡 (连续衔接)
        t >  t_c       : 常数 (Tbar, Cbar) = 附件1 末段均值 (取 4 位有效数字)
    """

    def __init__(self, t1, T1_C, C1, t_c=14400.0, tau=600.0,
                 Tbar_C=TBAR_C, Cbar=CBAR):
        from scipy.interpolate import PchipInterpolator
        self.t_c = float(t_c)
        self.tau = float(tau)
        self.Tbar = float(Tbar_C) + 273.15
        self.Cbar = float(Cbar)
        self._pT = PchipInterpolator(t1, np.asarray(T1_C, dtype=float) + 273.15)
        self._pC = PchipInterpolator(t1, np.asarray(C1, dtype=float))
        m = np.asarray(t1, dtype=float) >= 10800.0      # 末段 10800~14400 s, 61 点
        Tseg, Cseg = np.asarray(T1_C)[m], np.asarray(C1)[m]
        self.stats = dict(n=int(m.sum()),
                          T_mean=float(Tseg.mean()), T_std=float(Tseg.std()),
                          T_min=float(Tseg.min()), T_max=float(Tseg.max()),
                          C_mean=float(Cseg.mean()), C_std=float(Cseg.std()),
                          C_min=float(Cseg.min()), C_max=float(Cseg.max()))

    def _val(self, t, interp, bar):
        t = float(t)
        if t >= self.t_c:
            return bar
        if t <= self.t_c - self.tau:
            return float(interp(t))
        w = (t - (self.t_c - self.tau)) / self.tau
        return (1.0 - w) * float(interp(t)) + w * bar

    def _val_arr(self, t, interp, bar):
        t = np.asarray(t, dtype=float)
        out = np.full(t.shape, bar)
        lo = t < self.t_c
        if self.tau <= 0.0:
            out[lo] = interp(t[lo])
            return out
        mid = lo & (t > self.t_c - self.tau)
        w = np.zeros_like(t)
        w[mid] = (t[mid] - (self.t_c - self.tau)) / self.tau
        out[lo] = (1.0 - w[lo]) * interp(t[lo]) + w[lo] * bar
        return out

    def T(self, t):
        return self._val(t, self._pT, self.Tbar)

    def C(self, t):
        return self._val(t, self._pC, self.Cbar)

    def T_arr(self, t):
        return self._val_arr(t, self._pT, self.Tbar)

    def C_arr(self, t):
        return self._val_arr(t, self._pC, self.Cbar)


# ---------------------------------------------------------------------------
# 线方法: RHS 与解析稀疏 Jacobian
# ---------------------------------------------------------------------------
# 附录 3 物性参数 (蒙特卡洛/单因素扰动用; params=None 时直接用 q2_solve 的实现)
P3 = dict(rho0=650.0, krho=128.0, cp0=1450.0, kcp=2736.0,
          k0=0.21, kk=0.38, D0=2.4e-3, kD=0.45, EA=3850.0)


def props_p(C, p):
    """参数化附录 3 物性: 返回 (rho, cp, k, drho/dC, dcp/dC, dk/dC)."""
    C = np.asarray(C, dtype=float)
    Cp1 = C + 1.0
    z = np.zeros_like(C)
    return (p["rho0"] + p["krho"] * C,
            p["cp0"] + p["kcp"] * C / Cp1,
            p["k0"] + p["kk"] * C / Cp1,
            z + p["krho"], p["kcp"] / Cp1 ** 2, p["kk"] / Cp1 ** 2)


def Dfun_p(C, T, p):
    return p["D0"] * np.exp(-p["kD"] / np.asarray(C, float)) \
        * np.exp(-p["EA"] / np.asarray(T, float))


def D_derivs_p(C, T, p):
    C, T = np.asarray(C, float), np.asarray(T, float)
    D = Dfun_p(C, T, p)
    return D * p["kD"] / C ** 2, D * p["EA"] / T ** 2


def make_rhs(g, env, hevap=True, params=None):
    """半离散 ODE 右端 F(t, U) (problem3.md §8.3). params 给出时用扰动物性."""
    M, n = g["M"], g["n"]
    Gfac, MLg = g["Gfac"], g["MLg"]
    if params is None:
        _props, _D = (lambda C: props(C, "app3")), (lambda C, T: Dfun(C, T, "app3"))
    else:
        _props = lambda C: props_p(C, params)    # noqa: E731
        _D = lambda C, T: Dfun_p(C, T, params)   # noqa: E731

    def rhs(t, U):
        T, C = U[:n], U[n:]
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, _, _, _ = _props(C)
        rcp = rho * cp
        Dv = _D(C, T)
        Ge = 0.5 * (k[:-1] + k[1:]) * Gfac
        Fe = 0.5 * (Dv[:-1] + Dv[1:]) * Gfac
        dT = T[:-1] - T[1:]
        dC = C[:-1] - C[1:]
        KT = np.zeros(n)
        KT[:-1] += Ge * dT
        KT[1:] -= Ge * dT
        KC = np.zeros(n)
        KC[:-1] += Fe * dC
        KC[1:] -= Fe * dC
        if hevap:
            Hev = HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)
            flux_h = H_CONV * R * (T[M] - Tinf) + Hev * HM * R * (C[M] - Cinf)
        else:
            flux_h = H_CONV * R * (T[M] - Tinf)
        flux_w = HM * R * (C[M] - Cinf)
        FT = -(KT) / (MLg * rcp)
        FC = -(KC) / MLg
        FT[M] -= flux_h / (MLg[M] * rcp[M])
        FC[M] -= flux_w / MLg[M]
        return np.concatenate([FT, FC])

    return rhs


def make_jac(g, env, hevap=True, params=None):
    """解析稀疏 Jacobian dF/dU (problem3.md §8.4), 返回 CSR 矩阵.

    分块 J = [[JTT, JTC], [JCT, JCC]], 每块三对角; 额外项:
      * JTT[M,M] 含 -dHev/dT * h_m R (C_M - C_inf)  (H_evap(T_M) 的温度导数,
        problem3.md §8.4 式中未写出, 量级 ~1e-7 相对, 此处按精确式保留);
      * JTC 对角含质量矩阵对 C 的依赖: -FT_i (d(ricp)/dC)_i / (rho cp)_i;
      * 边界行含 hR / H_evap h_m R / h_m R.
    """
    M, n = g["M"], g["n"]
    Gfac, MLg = g["Gfac"], g["MLg"]
    if params is None:
        _props = lambda C: props(C, "app3")                       # noqa: E731
        _D = lambda C, T: Dfun(C, T, "app3")                      # noqa: E731
        _Dd = lambda C, T: D_derivs(C, T, "app3")                 # noqa: E731
    else:
        _props = lambda C: props_p(C, params)                     # noqa: E731
        _D = lambda C, T: Dfun_p(C, T, params)                    # noqa: E731
        _Dd = lambda C, T: D_derivs_p(C, T, params)               # noqa: E731

    def jac(t, U):
        T, C = U[:n], U[n:]
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, drho, dcp, dk = _props(C)
        rcp = rho * cp
        drcp = drho * cp + rho * dcp
        Dv = _D(C, T)
        dDdC, dDdT = _Dd(C, T)
        Ge = 0.5 * (k[:-1] + k[1:]) * Gfac
        Fe = 0.5 * (Dv[:-1] + Dv[1:]) * Gfac
        dT = T[:-1] - T[1:]
        dC = C[:-1] - C[1:]
        MT = MLg * rcp

        # ---- 复算 FT (JTC 的质量导数项需要) ----
        KT = np.zeros(n)
        KT[:-1] += Ge * dT
        KT[1:] -= Ge * dT
        if hevap:
            Hev = HEVAP_28 + HEVAP_SLOPE * (T[M] - HEVAP_TREF)
            dHev = HEVAP_SLOPE
            flux_h = H_CONV * R * (T[M] - Tinf) + Hev * HM * R * (C[M] - Cinf)
        else:
            Hev = dHev = 0.0
            flux_h = H_CONV * R * (T[M] - Tinf)
        FT = -(KT) / MT
        FT[M] -= flux_h / MT[M]

        # ---- JTT = dF_T/dT ----
        diagT = np.zeros(n)
        diagT[:M] -= Ge
        diagT[1:] -= Ge
        diagT[M] -= H_CONV * R + dHev * HM * R * (C[M] - Cinf)
        diagT /= MT
        upT = Ge / MT[:M]
        loT = Ge / MT[1:]

        # ---- JTC = dF_T/dC ----
        #   dF_T,i/dC_j = -(dKT_i/dC_j + delta_Hev)/MT_i - FT_i (d(ricp)/dC)_i/(ricp)_i
        #   (注意: 与问题二残差形式的 dKT/dC 相差一个负号, 因 MOL 已除以质量矩阵)
        a = 0.5 * dk[:M] * Gfac * dT          # dGe_k/dC_k   * dT_k
        b = 0.5 * dk[1:] * Gfac * dT          # dGe_k/dC_{k+1} * dT_k
        diagTC = np.zeros(n)
        diagTC[:M] -= a
        diagTC[1:] += b
        diagTC[M] -= Hev * HM * R
        diagTC /= MT
        diagTC -= FT * drcp / rcp             # 质量矩阵的 C 依赖
        upTC = -b / MT[:M]
        loTC = a / MT[1:]

        # ---- JCT = dF_C/dT ----
        c = 0.5 * dDdT[:M] * Gfac * dC
        e = 0.5 * dDdT[1:] * Gfac * dC
        diagCT = np.zeros(n)
        diagCT[:M] += c
        diagCT[1:] -= e
        diagCT /= -MLg
        upCT = -e / MLg[:M]
        loCT = c / MLg[1:]

        # ---- JCC = dF_C/dC ----
        f = 0.5 * dDdC[:M] * Gfac * dC
        h = 0.5 * dDdC[1:] * Gfac * dC
        diagCC = np.zeros(n)
        diagCC[:M] += Fe
        diagCC[1:] += Fe
        diagCC[:M] += f
        diagCC[1:] -= h
        diagCC[M] += HM * R
        diagCC /= -MLg
        upCC = (Fe - h) / MLg[:M]
        loCC = (Fe + f) / MLg[1:]

        def blk(diag, up, lo, roff, coff):
            rr = np.concatenate([np.arange(n), np.arange(M), np.arange(1, n)]) + roff
            cc = np.concatenate([np.arange(n), np.arange(1, n), np.arange(M)]) + coff
            return rr, cc, np.concatenate([diag, up, lo])

        parts = [blk(diagT, upT, loT, 0, 0),
                 blk(diagTC, upTC, loTC, 0, n),
                 blk(diagCT, upCT, loCT, n, 0),
                 blk(diagCC, upCC, loCC, n, n)]
        rr = np.concatenate([p[0] for p in parts])
        cc = np.concatenate([p[1] for p in parts])
        vv = np.concatenate([p[2] for p in parts])
        return sp.coo_matrix((vv, (rr, cc)), shape=(2 * n, 2 * n)).tocsr()

    return jac


def sparsity_pattern(g):
    """Jacobian 稀疏结构 (与 make_jac 完全同构), 供 jac_sparsity 分组差分."""
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
    """终止事件 g(t,U) = max_i C_i - C* (problem3.md §10.1)."""

    def event(t, U, _n=n, _c=cstar):
        return U[_n:].max() - _c

    event.terminal = True
    event.direction = -1.0
    return event


def solve_q3(M=PROD_M, rtol=PROD_RTOL, atol_T=PROD_ATOL_T, atol_C=PROD_ATOL_C,
             max_step=PROD_MAX_STEP, t_max=T_MAX, CSTAR=CSTAR, method="BDF",
             jac_mode="analytic", hevap=True, env=None, tau=TAU,
             Tbar_C=TBAR_C, Cbar=CBAR, params=None):
    """MOL + 自适应 BDF + 终止事件. 返回 dict(sol, t_dry, 统计)."""
    if M % 20:
        raise ValueError("M 必须是 20 的倍数 (输出半径 0.1 cm 间隔落在节点上)")
    g = geometry(M, "lumped")
    n = g["n"]
    if env is None:
        t1, T1, C1 = load_attachment1()
        env = Q3Env(t1, T1, C1, tau=tau, Tbar_C=Tbar_C, Cbar=Cbar)
    rhs = make_rhs(g, env, hevap=hevap, params=params)
    kw = {}
    if jac_mode == "analytic":
        kw["jac"] = make_jac(g, env, hevap=hevap, params=params)
    elif jac_mode == "sparsity":
        kw["jac_sparsity"] = sparsity_pattern(g)
    elif jac_mode not in ("dense", "none"):
        raise ValueError(f"jac_mode={jac_mode} 不合法")

    event = make_event(n, CSTAR)
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atol = np.concatenate([np.full(n, atol_T), np.full(n, atol_C)])
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, float(t_max)), U0, method=method, rtol=rtol,
                    atol=atol, max_step=float(max_step), events=event,
                    dense_output=True, **kw)
    wall = time.time() - t0
    if sol.status != 1 or len(sol.t_events[0]) == 0:
        # §10.5: 3 天内未达标 -> 诊断后报错, 不静默返回
        Cend = sol.y[n:, -1]
        raise RuntimeError(
            f"终止事件未触发: status={sol.status}, t={sol.t[-1]:.1f} s, "
            f"max_i C_i = {Cend.max():.6f} @ r={g['r'][int(Cend.argmax())] * 100:.2f} cm")
    return dict(sol=sol, g=g, env=env, t_dry=float(sol.t_events[0][0]),
                nsteps=len(sol.t) - 1, nfev=int(sol.nfev), njev=int(sol.njev),
                nlu=int(sol.nlu), wall=wall, M=M, n=n, rtol=rtol,
                atol_T=atol_T, atol_C=atol_C, max_step=max_step,
                method=method, jac_mode=jac_mode, status=int(sol.status),
                tau=env.tau, Tbar=env.Tbar, Cbar=env.Cbar, params=params)


# ---------------------------------------------------------------------------
# 采样 (生产与诊断共用)
# ---------------------------------------------------------------------------
def sample_all(sol, g, env, t_dry, final_window=7200.0):
    """60 s 网格 + t_dry 终态 + 诊断序列.

    返回:
        t60, C60 (n60 x 21 输出半径), C_dry/T_dry (21,), 终态 max/argmax,
        W0/W60/W_dry (总水量, per 2 pi), maxC60/argmax60 (W9/W10),
        t_flux/flux_w (水量收支用复合网格), t_fin/maxC_fin (末 2 h, 1 s, W10)
    """
    M, n = g["M"], g["n"]
    idx = out_indices(M)
    n60 = int(np.floor(t_dry / 60.0))
    t60 = 60.0 * np.arange(1, n60 + 1)
    Y = sol.sol(np.append(t60, t_dry))
    Cfull = Y[n:, :-1]
    out = dict(t60=t60, n60=n60, idx=idx,
               C60=Cfull[idx, :].T,                    # (n60, 21)
               C_dry=Y[n:, -1][idx], T_dry=Y[:n, -1][idx],
               C60_min=float(Cfull.min()), C60_max=float(Cfull.max()),
               maxC60=Cfull.max(axis=0), argmax60=Cfull.argmax(axis=0),
               maxC_dry=float(Y[n:, -1].max()),
               argmax_dry=int(Y[n:, -1].argmax()),
               W0=float(g["MLg"].sum() * C0),
               W60=(g["MLg"][:, None] * Cfull).sum(axis=0),
               W_dry=float((g["MLg"] * Y[n:, -1]).sum()))
    # 水量收支: 表面水通量 (per 2 pi) 在复合网格上 (1 s 到 600 s, 之后 10 s)
    t_a = np.arange(0.0, 600.0 + 0.5, 1.0)
    t_b = np.arange(610.0, t_dry, 10.0)
    tf = np.concatenate([t_a, t_b, [t_dry]])
    Csurf = np.empty(tf.size)
    for lo in range(0, tf.size, 4096):
        Csurf[lo:lo + 4096] = sol.sol(tf[lo:lo + 4096])[-1]   # 行 2n-1 = 表面节点 C_M
    out["t_flux"] = tf
    out["flux_w"] = HM * R * (Csurf - env.C_arr(tf))
    # 末 2 h 的 max_i C_i 序列 (1 s, W10)
    tfin = np.linspace(max(t_dry - final_window, 0.0), t_dry, 7201)
    Yf = sol.sol(tfin)
    out["t_fin"], out["maxC_fin"] = tfin, Yf[n:, :].max(axis=0)
    return out


def crossing_times(sol, g, n, t_dry, cstar=CSTAR,
                   radii_cm=(0.0, 0.5, 1.0, 1.5, 2.0)):
    """各输出半径 C 首次降到 cstar 的时刻 (60 s 网格定位 + brentq 精化).

    返回 {r_cm: t_s 或 None}. 依赖 C(r,t) 关于 t 单调不增 (最大值原理).
    """
    from scipy.optimize import brentq
    dr = g["dr"]
    t60 = 60.0 * np.arange(1, int(np.floor(t_dry / 60.0)) + 1)
    Y = sol.sol(t60)
    res = {}
    for rc in radii_cm:
        i = int(round(rc / 100.0 / dr))
        below = np.nonzero(Y[n + i] < cstar)[0]
        if below.size == 0:
            # 轴心等事件半径: C(r, t_dry) = c* 精确成立 (事件定义), 达标时刻 = t_dry
            if abs(float(sol.sol(t_dry)[n + i]) - cstar) < 1e-9:
                res[rc] = float(t_dry)
            else:
                res[rc] = None
            continue
        k = int(below[0])
        t_hi = t60[k]
        t_lo = t60[k - 1] if k > 0 else 0.0
        f = lambda tt: float(sol.sol(tt)[n + i]) - cstar
        res[rc] = float(brentq(f, t_lo, t_hi, xtol=1e-6))
    return res


_CASE_KEYS = ("M", "rtol", "atol_T", "atol_C", "max_step", "t_max", "CSTAR",
              "method", "jac_mode", "hevap", "tau", "Tbar_C", "Cbar", "params")


def run_case(cfg):
    """多进程 worker: 子进程内独立建 env 与求解器, 返回采样结果 (不回传 sol)."""
    kw = {k: cfg[k] for k in _CASE_KEYS if k in cfg}
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1, tau=kw.pop("tau", TAU),
                Tbar_C=kw.pop("Tbar_C", TBAR_C), Cbar=kw.pop("Cbar", CBAR))
    o = solve_q3(env=env, **kw)
    res = dict(tag=cfg.get("tag", ""), M=o["M"], t_dry=o["t_dry"],
               nsteps=o["nsteps"], nfev=o["nfev"], njev=o["njev"], nlu=o["nlu"],
               wall=o["wall"], method=o["method"], jac_mode=o["jac_mode"],
               rtol=o["rtol"], max_step=o["max_step"], status=o["status"])
    if cfg.get("sample", False):
        res.update(sample_all(o["sol"], o["g"], env, o["t_dry"]))
    if cfg.get("crossings", False):
        res["crossings"] = crossing_times(o["sol"], o["g"], o["n"], o["t_dry"])
    st = cfg.get("sample_times")
    if st is not None:
        from q2_solve import out_indices as _oi
        idx = _oi(o["M"])
        Y = o["sol"].sol(np.asarray(st, dtype=float))
        res["C_ts"] = Y[o["n"]:][idx, :].T          # (n_times, 21)
        res["T_ts"] = Y[:o["n"]][idx, :].T
    return res


def run_parallel(cfgs, workers=3):
    """并行跑一组算例 (Windows 下函数与 cfg 均可 pickle)."""
    from concurrent.futures import ProcessPoolExecutor
    out = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(run_case, cfgs):
            out[res["tag"]] = res
            print(f"  [{res['tag']}] M={res['M']} rtol={res['rtol']:g} "
                  f"method={res['method']}/{res['jac_mode']}: "
                  f"t_dry={res['t_dry']:.3f} s ({res['t_dry'] / 3600.0:.4f} h), "
                  f"{res['nsteps']} 步, nfev={res['nfev']}, "
                  f"用时 {res['wall']:.1f} s", flush=True)
    print(f"  [{len(cfgs)} 组算例并行, 共用时 {time.time() - t0:.1f} s]", flush=True)
    return out


# ---------------------------------------------------------------------------
# 核验工具
# ---------------------------------------------------------------------------
def check_jacobian_fd(M=12, t=1.0e4, seed=7, eps=1e-7, hevap=True, tau=TAU,
                      wet=True):
    """解析稀疏 Jacobian 与中心差分的密矩阵逐元比较.

    返回 (相对偏差, 稀疏结构外的最大相对泄漏).
    """
    g = geometry(M, "lumped")
    n = g["n"]
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1, tau=tau)
    rng = np.random.default_rng(seed)
    U = np.empty(2 * n)
    U[:n] = T0K + rng.uniform(0.0, 3.0, n)
    if wet:
        U[n:] = np.maximum(C0 - rng.uniform(0.0, 0.4, n), 0.3)
    else:                                   # 干燥后期状态 (C ~ 0.05~0.15)
        U[n:] = 0.05 + rng.uniform(0.0, 0.12, n)
    rhs = make_rhs(g, env, hevap=hevap)
    J = make_jac(g, env, hevap=hevap)(t, U).toarray()
    fd = np.zeros((2 * n, 2 * n))
    for j in range(2 * n):
        Up, Um = U.copy(), U.copy()
        Up[j] += eps
        Um[j] -= eps
        fd[:, j] = (rhs(t, Up) - rhs(t, Um)) / (2 * eps)
    rel = float(np.max(np.abs(J - fd)) / max(float(np.max(np.abs(fd))), 1e-30))
    pat = sparsity_pattern(g).toarray() > 0
    leak = float(np.max(np.abs(fd[~pat])) / max(float(np.max(np.abs(fd))), 1e-30))
    return rel, leak


def fmt(v):
    return f"{v:.14g}" if isinstance(v, (int, float, np.floating)) else str(v)


def write_registry(path, rows):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "quantity", "value", "unit", "uncertainty",
                    "source", "command", "note"])
        for row in rows:
            w.writerow([row[0], row[1], fmt(row[2])] + list(row[3:]))


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--solve", action="store_true")
    args = ap.parse_args()
    if not (args.selftest or args.solve):
        args.selftest = True

    if args.selftest:
        print("=" * 96)
        print("S1  环境激励 (problem3.md §5.1 / §6.4)")
        print("=" * 96)
        t1, T1, C1 = load_attachment1()
        env = Q3Env(t1, T1, C1)
        s = env.stats
        print(f"  附件1 末段 [{10800}-{14400:.0f} s] {s['n']} 点:")
        print(f"    T_inf: 均值 {s['T_mean']:.4f} degC, 标准差 {s['T_std']:.4f}, "
              f"极差 {s['T_max'] - s['T_min']:.3f}")
        print(f"    C_inf: 均值 {s['C_mean']:.6f} kg/kg, 标准差 {s['C_std']:.6f}, "
              f"极差 {s['C_max'] - s['C_min']:.6f}")
        print(f"  平台值: Tbar={env.Tbar - 273.15:.2f} degC, Cbar={env.Cbar:.4f}")
        t_c, tau = env.t_c, env.tau
        print(f"  连续性: T(t_c-tau)={env.T(t_c - tau) - 273.15:.4f} (PCHIP 值 "
              f"{float(env._pT(t_c - tau)) - 273.15:.4f}), "
              f"T(t_c-)={env.T(t_c - 1e-9) - 273.15:.4f}, "
              f"T(t_c+)={env.T(t_c + 1.0) - 273.15:.4f}")
        print(f"          C(t_c-)={env.C(t_c - 1e-9):.6f}, "
              f"C(t_c+)={env.C(t_c + 1.0):.6f}")
        print(f"  平台:   T(2 t_c)={env.T(2 * t_c) - 273.15:.4f}, "
              f"C(2 t_c)={env.C(2 * t_c):.6f}")
        print(f"  初值:   T(0)={env.T(0) - 273.15:.4f} degC, C(0)={env.C(0):.5f}")

        print()
        print("=" * 96)
        print("S2  解析稀疏 Jacobian vs 中心差分 (M=12 密矩阵逐元比较)")
        print("=" * 96)
        cases = [("湿态/含蒸发/PCHIP 段", dict(hevap=True, wet=True)),
                 ("湿态/关闭蒸发", dict(hevap=False, wet=True)),
                 ("干态(后期)/含蒸发/平台段", dict(hevap=True, wet=False,
                                                   t=2.0e5)),
                 ("湿态/零过渡 tau=0", dict(hevap=True, wet=True, tau=0.0)),
                 ("湿态/长过渡 tau=1800", dict(hevap=True, wet=True, tau=1800.0))]
        for name, kw in cases:
            t = kw.pop("t", 1.0e4)
            rel, leak = check_jacobian_fd(t=t, **kw)
            ok = "OK" if rel < 1e-5 and leak < 1e-6 else "!! 需检查"
            print(f"  {name:28s} max|J_ana-J_fd|/max|J_fd| = {rel:.3e}   "
                  f"结构外泄漏 = {leak:.3e}   {ok}")

        print()
        print("=" * 96)
        print("S3  冒烟求解 (M=50, rtol=1e-7, 解析 Jacobian)")
        print("=" * 96)
        o = solve_q3(M=40, rtol=1e-7)
        smp = sample_all(o["sol"], o["g"], o["env"], o["t_dry"])
        dm = np.diff(smp["maxC60"])
        print(f"  t_dry = {o['t_dry']:.3f} s = {o['t_dry'] / 3600.0:.4f} h, "
              f"{o['nsteps']} 步, nfev={o['nfev']}, njev={o['njev']}, "
              f"nlu={o['nlu']}, 用时 {o['wall']:.2f} s")
        print(f"  终态 max_i C_i = {smp['maxC_dry']:.12f} (应=C*={CSTAR}), "
              f"argmax @ 节点 {smp['argmax_dry']} (r="
              f"{o['g']['r'][smp['argmax_dry']] * 100:.2f} cm)")
        print(f"  maxC 单调不增: 最大正增量 = {dm.max():.3e} kg/kg "
              f"{'OK' if dm.max() < 1e-10 else '!!'}")
        print(f"  argmax 非 0 的采样点数 = {int((smp['argmax60'] != 0).sum())} "
              f"/ {smp['n60']}")
        fr = abs(smp["W_dry"] - smp["W0"] + float(np.trapezoid(
            smp["flux_w"], smp["t_flux"]))) / abs(float(np.trapezoid(
                smp["flux_w"], smp["t_flux"])))
        print(f"  水量收支相对残差 = {fr:.3e}")

    if args.solve:
        print("=" * 96)
        print("问题三生产配置单次求解: M=%d, rtol=%g, atol=(%g K, %g), "
              "max_step=%.0f s, tau=%.0f s" % (PROD_M, PROD_RTOL, PROD_ATOL_T,
                                               PROD_ATOL_C, PROD_MAX_STEP, TAU))
        print("=" * 96)
        o = solve_q3()
        smp = sample_all(o["sol"], o["g"], o["env"], o["t_dry"])
        print(f"  t_dry = {o['t_dry']:.3f} s = {o['t_dry'] / 3600.0:.4f} h, "
              f"{o['nsteps']} 步, nfev={o['nfev']}, njev={o['njev']}, "
              f"nlu={o['nlu']}, 用时 {o['wall']:.2f} s")
        print(f"  表5 (kg/kg), t_dry 行 = t={o['t_dry'] / 3600.0:.2f} h:")
        print("  t/h      " + "".join(f"r={d:>4.1f}  " for d in (0, 0.5, 1, 1.5, 2)))
        t6 = 21600.0 * np.arange(1, int(np.floor(o["t_dry"] / 21600.0)) + 1)
        for tt in t6:
            i = int(round(tt / 60.0)) - 1
            print(f"  {tt / 3600.0:5.1f}   "
                  + "".join(f"{smp['C60'][i, j]:8.4f}  " for j in (0, 5, 10, 15, 20)))
        print(f"  {o['t_dry'] / 3600.0:5.2f}   "
              + "".join(f"{smp['C_dry'][j]:8.4f}  " for j in (0, 5, 10, 15, 20)))


if __name__ == "__main__":
    main()
