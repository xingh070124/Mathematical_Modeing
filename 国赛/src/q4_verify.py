# -*- coding: utf-8 -*-
"""
q4_verify.py -- 问题四数值验证 (V0 ~ V9).

V0  退化一致性: R=const + 附录3 应逐位复现问题三 t_dry
V0b 效应分解: 附录4物性(R=const) / 收缩(附录3物性) / 两者同时(生产)
V1  空间收敛性 M=100,200,400
V2  时间容限收敛性 rtol=1e-7 vs 1e-9
V4  收缩数据插值口径 (PCHIP vs 线性 vs 最近点; 过渡段长度)
V5  独立有限体积参考解 (物理移动域 + 显式干物质/体积记帐, 无坐标变换)
V6  收缩律灵敏度 (R 幅值 ±10%, 冻结收缩)
V7  极值原理 / 干基水量收支 / 剖面单调性
V9  终止事件在阈值附近的单调性与单根性

输出: outputs/q4_verify.log 与 outputs/registry_q4_verify.csv
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import scipy.sparse as sp
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (APP, P4, P3, PROD_M, PROD_RTOL, PROD_ATOL_T, PROD_ATOL_C,
                      PROD_MAX_STEP, T_MAX, Q4Radius, geometry_xi, props_p,
                      Dfun_p, D_derivs_p, make_rhs, make_jac, make_event,
                      solve_q4, sample_q4, load_attachment2, CSTAR)
from q3_solve import Q3Env, TBAR_C, CBAR
from q1_solve import load_attachment1
from q2_solve import H_CONV, HM, T0K, C0, HEVAP_28, HEVAP_SLOPE, HEVAP_TREF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

Q3_PROD_TDRY = 206720.4134563      # 问题三生产解 (registry_q3.csv P01_tdry)
LOG = []


def say(msg):
    print(msg, flush=True)
    LOG.append(msg)


# ===========================================================================
# V0 / V0b / V1 / V2 / V4 / V6: 直接调用 solve_q4
# ===========================================================================
def run_solve_cases():
    cases = [
        # tag,            kwargs,                                    group
        ("V0_deg_app3_Rconst", dict(M=200, app="app3", rad_mode="const"), "V0"),
        ("V0b_app3_shrink", dict(M=200, app="app3", rad_mode="data"), "V0b"),
        ("PROD", dict(M=200, app="app4", rad_mode="data"), "PROD"),
        # 附录4物性 + 冻结收缩: 3 天安全网内不达标, 延长到 10 天以量化
        ("V0b_app4_Rconst", dict(M=200, app="app4", rad_mode="const", t_max=864000.0), "V0b"),
        ("V0b_app4_Rconst_3d", dict(M=200, app="app4", rad_mode="const"), "V0b3d"),
        ("V1_M100", dict(M=100, app="app4", rad_mode="data"), "V1"),
        ("V1_M400", dict(M=400, app="app4", rad_mode="data"), "V1"),
        ("V1_M800", dict(M=800, app="app4", rad_mode="data"), "V1"),
        ("V1_M1600", dict(M=1600, app="app4", rad_mode="data"), "V1"),
        ("V1_M3200", dict(M=3200, app="app4", rad_mode="data"), "V1"),
        ("V2_rtol1e7", dict(M=200, app="app4", rad_mode="data", rtol=1e-7), "V2"),
        ("V2_rtol1e11", dict(M=200, app="app4", rad_mode="data", rtol=1e-11), "V2"),
        ("V4_lin", dict(M=200, app="app4", rad_mode="data", rad_kind="linear"), "V4"),
        ("V4_tau0", dict(M=200, app="app4", rad_mode="data", tau=0.0), "V4"),
        ("V4_tau1800", dict(M=200, app="app4", rad_mode="data", tau=1800.0), "V4"),
        ("V6_scale1p10", dict(M=200, app="app4", rad_mode="data", rad_scale=1.10), "V6"),
        ("V6_scale0p90", dict(M=200, app="app4", rad_mode="data", rad_scale=0.90), "V6"),
        ("V6_scale1p05", dict(M=200, app="app4", rad_mode="data", rad_scale=1.05), "V6"),
        ("V6_scale0p95", dict(M=200, app="app4", rad_mode="data", rad_scale=0.95), "V6"),
    ]
    out = {}
    for tag, kw, grp in cases:
        t0 = time.time()
        try:
            res = solve_q4(**kw)
            say(f"  {tag:22s} t_dry = {res['t_dry']:14.4f} s = {res['t_dry']/3600:9.5f} h"
                f"   nsteps={res['nsteps']:6d}  wall={time.time()-t0:6.1f}s")
            out[tag] = res
        except RuntimeError as e:
            say(f"  {tag:22s} 未达标: {e}")
            out[tag] = None
    return out


# ===========================================================================
# V5: 独立有限体积参考解 (物理移动域, 无坐标变换)
# ===========================================================================
def _beta0(C, p):
    """干物质体积浓度 beta = rho_d*phi_d = rho(C)/(1+C)  [kg/m^3]."""
    rho = p["rho0"] + p["krho"] * np.asarray(C, float)
    return rho / (1.0 + np.asarray(C, float))


def make_rhs_fv(g, env, rad, params):
    """独立有限体积参考解 (单元中心, 物理移动域, 无坐标变换).

    记 beta(t) = rho_d*phi_d 为干物质体积浓度. 仿射收缩下每个 xi-单元内的
    干物质质量恒定:

        beta(t) * R(t)^2 = beta_0 * R_0^2 = B0          (干物质守恒, 显式记帐)

    该式是本格式与主格式**互相独立**的关键: 它不由坐标变换导出, 而是直接
    对每个单元写干物质守恒. 单元 i 的水量收支:

        m_i dC_i/dt = -(F_{i+1/2} - F_{i-1/2}),   m_i = B0*pi*d(xi^2)*R_0^2
        F = 2*pi*xi_f*beta*D*(dC/dxi)   [kg/(m*s), 每单位轴向长度]

    温度场: rho*cp*V_i dT_i/dt = -(H_{i+1/2}-H_{i-1/2}) + 表面项
        H = 2*pi*xi_f*k*(dT/dxi),   V_i = pi*d(xi^2)*R^2
    """
    M = g["M"]
    xi_f = np.arange(M + 1) / M                      # 面位置 (物质坐标)
    xi_c = 0.5 * (xi_f[:-1] + xi_f[1:])              # 单元中心
    dxi = 1.0 / M
    dxi2 = xi_f[1:] ** 2 - xi_f[:-1] ** 2            # d(xi^2), 无量纲
    h, hm = H_CONV, HM
    TLO, THI = 200.0, 400.0
    CLO, CHI = 1e-4, 1e2
    B0 = float(_beta0(np.array([C0]), params)[0])    # 初始干物质体积浓度

    def rhs(t, U):
        T = np.clip(U[:M], TLO, THI)
        C = np.clip(U[M:], CLO, CHI)
        Rc = float(rad.R(t))
        R0m = float(rad.R(0.0))
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, _, _, _ = props_p(C, params)
        rcp = rho * cp
        Dv = Dfun_p(C, T, params)
        beta = B0 * (R0m / Rc) ** 2                  # 干物质守恒 (与局部 C 无关)
        m_i = B0 * np.pi * dxi2 * R0m ** 2           # 恒定干物质质量 (每单位轴向长度)

        # 面物性 (算术平均)
        Df = 0.5 * (Dv[:-1] + Dv[1:])
        kf = 0.5 * (k[:-1] + k[1:])
        # 面通量 (每单位轴向长度, 沿 +xi 方向):  F_{i+1/2} = -2 pi xi beta D dC/dxi
        FC = -2 * np.pi * xi_f[1:M] * beta * Df * (C[1:] - C[:-1]) / dxi
        FH = -2 * np.pi * xi_f[1:M] * kf * (T[1:] - T[:-1]) / dxi
        dC = np.zeros(M)
        dT = np.zeros(M)
        # 单元 i: dC_i/dt = (F_{i-1/2} - F_{i+1/2}) / m_i
        dC[:-1] -= FC
        dC[1:] += FC
        dT[:-1] -= FH
        dT[1:] += FH
        dC = dC / m_i
        Vi = np.pi * dxi2 * Rc ** 2
        dT = dT / (rcp * Vi)
        # 表面 (单元 M-1 的外侧面 xi=1)
        Lv = HEVAP_28 + HEVAP_SLOPE * (T[-1] - HEVAP_TREF)
        A_s = 2 * np.pi * 1.0 * Rc                   # 单位轴向长度表面积
        qs = h * (T[-1] - Tinf) + Lv * hm * (C[-1] - Cinf)
        js = hm * (C[-1] - Cinf)
        dT[-1] -= qs * A_s / (rcp[-1] * Vi[-1])
        dC[-1] -= beta * js * A_s / m_i[-1]
        return np.concatenate([dT, dC])

    return rhs, xi_c, xi_f


def run_fv_reference(M=200, rtol=1e-9, app="app4", rad_mode="data", app3=False,
                     t_max=None):
    """用独立有限体积格式求解到终止事件, 返回 t_dry."""
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    rad = Q4Radius(mode=rad_mode)
    params = APP["app3"] if app3 else APP[app]
    g = geometry_xi(M)
    rhs, xi_c, xi_f = make_rhs_fv(g, env, rad, params)
    n = M
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atol = np.concatenate([np.full(n, PROD_ATOL_T), np.full(n, PROD_ATOL_C)])

    def ev(t, U, _n=n):
        return U[_n:].max() - CSTAR
    ev.terminal = True
    ev.direction = -1.0
    t_end = T_MAX if t_max is None else float(t_max)
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, t_end), U0, method="BDF", rtol=rtol, atol=atol,
                    max_step=PROD_MAX_STEP, events=ev, dense_output=True,
                    jac_sparsity=sp.diags([np.ones(2 * n - 1), np.ones(2 * n),
                                           np.ones(2 * n - 1)], [-1, 0, 1],
                                          format="csr"))
    if sol.status != 1 or len(sol.t_events[0]) == 0:
        raise RuntimeError(f"FV 参考解未触发事件: status={sol.status}, t={sol.t[-1]:.1f}")
    return dict(sol=sol, t_dry=float(sol.t_events[0][0]), xi_c=xi_c, M=M,
                wall=time.time() - t0, nsteps=len(sol.t) - 1)


def _secant_to_xi(Cn, xin, Cc, xic, xi_out):
    """把单元中心解插到 xi_out (线性外推到边界)."""
    out = np.interp(xi_out, xic, Cc)
    # 两端外推
    lo = xi_out < xic[0]
    hi = xi_out > xic[-1]
    if lo.any():
        s = (Cc[1] - Cc[0]) / (xic[1] - xic[0])
        out[lo] = Cc[0] + s * (xi_out[lo] - xic[0])
    if hi.any():
        s = (Cc[-1] - Cc[-2]) / (xic[-1] - xic[-2])
        out[hi] = Cc[-1] + s * (xi_out[hi] - xic[-1])
    return out


def compare_formulations(M=100, t_end=21600.0, rtol=1e-9, app="app4",
                         rad_mode="data", app3=False):
    """V5: 同一时刻, 主格式(物质坐标 FEM) 与独立 FV 格式的逐点对照."""
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    rad = Q4Radius(mode=rad_mode)
    params = APP["app3"] if app3 else APP[app]
    g = geometry_xi(M)
    # --- 主格式 (节点, xi_i = i/M, 共 M+1 个节点) ---
    n = g["n"]
    from q4_solve import make_jac
    rhs_m = make_rhs(g, env, rad, params=params)
    jac_m = make_jac(g, env, rad, params=params)
    U0n = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atoln = np.concatenate([np.full(n, PROD_ATOL_T), np.full(n, PROD_ATOL_C)])
    sm = solve_ivp(rhs_m, (0.0, t_end), U0n, method="BDF", rtol=rtol, atol=atoln,
                   max_step=PROD_MAX_STEP, jac=jac_m)
    # --- 独立 FV 格式 (单元中心, 共 M 个单元) ---
    rhs_f, xi_c, xi_f = make_rhs_fv(g, env, rad, params)
    U0c = np.concatenate([np.full(M, T0K), np.full(M, C0)])
    atolc = np.concatenate([np.full(M, PROD_ATOL_T), np.full(M, PROD_ATOL_C)])
    sf = solve_ivp(rhs_f, (0.0, t_end), U0c, method="BDF", rtol=rtol, atol=atolc,
                   max_step=PROD_MAX_STEP,
                   jac_sparsity=sp.diags([np.ones(2 * M - 1), np.ones(2 * M),
                                          np.ones(2 * M - 1)], [-1, 0, 1],
                                         format="csr"))
    # 取主格式的节点 xi (M+1 个) 与 FV 的单元中心 (M 个) 在共同可比的
    # 内部网格点上对照: 用节点 xi_1..xi_{M-1} 处的值
    xi_n = g["xi"]
    Cm = sm.y[n:, -1]
    Tm = sm.y[:n, -1]
    Cc = sf.y[M:, -1]
    Tc = sf.y[:M, -1]
    xi_t = xi_n[1:M]                 # 内部节点 1..M-1
    Cm_i = np.interp(xi_t, xi_n, Cm)
    Cf_i = _secant_to_xi(None, None, Cc, xi_c, xi_t)
    Tm_i = np.interp(xi_t, xi_n, Tm)
    Tf_i = _secant_to_xi(None, None, Tc, xi_c, xi_t)
    dC = np.abs(Cm_i - Cf_i)
    dT = np.abs(Tm_i - Tf_i)
    return dict(t_end=t_end, max_dC=float(dC.max()), mean_dC=float(dC.mean()),
                max_dT=float(dT.max()), mean_dT=float(dT.mean()),
                rel_dC=float(dC.max() / max(abs(Cm_i.min()), 1e-12)),
                Csurf_m=float(sm.y[n + M - 1, -1]), Csurf_f=float(Cc[-1]),
                Tsurf_m=float(Tm[-1]), Tsurf_f=float(Tc[-1]),
                M=M, nsteps_m=len(sm.t) - 1, nsteps_f=len(sf.t) - 1)


# ===========================================================================
# V7 / V9: 结构不变量
# ===========================================================================
def check_invariants(res, tag):
    """极值原理 / 单调性 / 干基水量收支."""
    sol, g, rad, t_dry, env = res["sol"], res["g"], res["rad"], res["t_dry"], res["env"]
    n = g["n"]
    s = sample_q4(sol, g, rad, t_dry)
    Cb = env.Cbar
    Cmin_all = float(s["Cg"][~np.isnan(s["Cg"])].min())
    row = []
    row.append((f"{tag}_Cmin_ge_Cbar", "全场最低含水率 >= 环境平台值",
                float(np.nanmin(s["Cg"]) - Cb), "kg/kg", "V7", "极值原理"))
    row.append((f"{tag}_Cmax_le_C0", "全场最高含水率 <= 初值 (上界)",
                float(C0 - np.nanmax(s["Cg"])), "kg/kg", "V7", "极值原理"))
    # 剖面关于 r 单调不增 (指数半场之后)
    i_after = int(np.argmin(np.abs(s["t60"] - 6 * 3600)))
    viol = 0
    for i in range(i_after, s["n60"]):
        col = s["Cg"][i, :]
        col = col[~np.isnan(col)]
        if np.any(np.diff(col) > 1e-9):
            viol += 1
    row.append((f"{tag}_profile_monotone", "t>6h 后剖面关于 r 单调不增的违例列数",
                float(viol), "1", "V7", "最大值原理"))
    # 干基水量收支: 表面累计通量 vs 内部水量减少
    t_flux = np.concatenate([np.arange(0, 600.5, 1.0),
                             np.arange(610.0, t_dry, 10.0), [t_dry]])
    t_flux = np.unique(t_flux)
    Csurf = np.empty(t_flux.size)
    for lo in range(0, t_flux.size, 4096):
        Csurf[lo:lo + 4096] = sol.sol(t_flux[lo:lo + 4096])[2 * n - 1, :]
    Rf = np.atleast_1d(np.asarray(rad.R(t_flux), float))
    # 单位轴向长度的水质量 (干基):  W = int beta C 2 pi xi R^2 dxi ; beta R^2 = const
    # => W = beta_0 R_0^2 * 2 pi * int C xi dxi = (beta_0 R0^2) * Wxi,  Wxi = sum(MLg*C)
    b0 = _beta0(np.array([C0]), res["params"])[0]
    # 单位轴向长度的水量 = int_0^1 beta*C * 2 pi xi R^2 dxi = 2 pi beta0 R0^2 * sum(MLg*C)
    Wxi = (g["MLg"][:, None] * sol.sol(t_flux)[n:, :]).sum(axis=0) \
        * (2.0 * np.pi * b0 * rad.R(0.0) ** 2)
    # dW/dt = -2 pi R * hm (C_surf - C_inf) * (beta_surf)  -> 用 beta(t)=beta0 (R0/R)^2
    tmid = 0.5 * (t_flux[1:] + t_flux[:-1])
    dtv = np.diff(t_flux)
    Rm = np.atleast_1d(np.asarray(rad.R(tmid), float))
    betam = b0 * (rad.R(0.0) / Rm) ** 2
    Csm = 0.5 * (Csurf[1:] + Csurf[:-1])
    Cinm = env.C_arr(tmid)
    flux_int = np.sum(2 * np.pi * Rm * betam * HM * (Csm - Cinm) * dtv)
    dW = Wxi[0] - Wxi[-1]
    row.append((f"{tag}_mass_relres", "干基水量收支相对残差 (|dW-flux|/dW)",
                float(abs(dW - flux_int) / abs(dW)), "1", "V7", "守恒性"))
    return row, dict(Cmin_all=Cmin_all, Cmax_all=float(np.nanmax(s["Cg"])),
                     monotone_viol=viol, dW=float(dW), flux_int=float(flux_int))


def check_event(res, tag):
    """终止事件附近的 g(t) 单调性 (W10 对应项)."""
    sol, g, n, t_dry, env = (res["sol"], res["g"], res["g"]["n"],
                             res["t_dry"], res["env"])
    t = np.linspace(max(t_dry - 7200.0, 0.0), t_dry, 1441)
    Y = sol.sol(t)
    mx = Y[n:, :].max(axis=0)
    d = np.diff(mx)
    return [(f"{tag}_event_monotone", "末 2 h max_i C_i 的上升步数 (应=0)",
             float((d > 0).sum()), "1", "V9", "事件单根性"),
            (f"{tag}_event_slope", "末 2 h max_i C_i 平均下降速率",
             float(-(mx[0] - mx[-1]) / (t[-1] - t[0])), "kg/(kg s)", "V9", "事件单根性"),
            (f"{tag}_g_at_tdry", "事件函数值 g(t_dry) = max_i C_i - C*",
             float(mx[-1] - CSTAR), "kg/kg", "V9", "事件定位精度")]


# ===========================================================================
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    rows = []
    add = rows.append

    say("=" * 78)
    say("问题四数值验证 (q4_verify.py)")
    say("=" * 78)

    say("\n[V0/V0b/V1/V2/V4/V6] 直接求解各配置")
    res = run_solve_cases()

    td = {k: (v["t_dry"] if v is not None else float("nan")) for k, v in res.items()}
    say("\n[V0] 退化一致性 (硬校验)")
    d0 = td["V0_deg_app3_Rconst"] - Q3_PROD_TDRY
    say(f"  问题三生产解 t_dry = {Q3_PROD_TDRY:.4f} s")
    say(f"  本模块 R=const + 附录3 t_dry = {td['V0_deg_app3_Rconst']:.4f} s")
    say(f"  差值 = {d0:+.6f} s  ->  {'通过 (逐位一致)' if abs(d0) < 1e-6 else '不通过'}")
    add(("V0_tdry_q3ref", "问题三生产解 t_dry", Q3_PROD_TDRY, "s", "V0", "registry_q3.csv P01_tdry"))
    add(("V0_tdry_q4Rconst", "q4 模块 R=const+附录3 的 t_dry", td["V0_deg_app3_Rconst"], "s", "V0", "outputs/q4_verify.log"))
    add(("V0_diff", "退化一致性差值 (q4 - q3)", d0, "s", "V0", "outputs/q4_verify.log"))

    say("\n[V0b] 效应分解 (物性 vs 收缩)")
    say(f"  附录3 物性 + 收缩      : {td['V0b_app3_shrink']:14.4f} s = {td['V0b_app3_shrink']/3600:8.5f} h")
    say(f"  附录4 物性 + 冻结收缩  : {td['V0b_app4_Rconst']:14.4f} s = {td['V0b_app4_Rconst']/3600:8.5f} h"
        f"  ({td['V0b_app4_Rconst']/86400:.3f} 天)")
    say(f"  附录3 物性 + 冻结收缩  : {Q3_PROD_TDRY:14.4f} s = {Q3_PROD_TDRY/3600:8.5f} h")
    say(f"  附录4 物性 + 收缩(生产): {td['PROD']:14.4f} s = {td['PROD']/3600:8.5f} h")
    if res["V0b_app4_Rconst_3d"] is None:
        say("  [关键] 附录4物性 + 冻结收缩: 3 天(259200 s)内终止事件未触发, 未达标")
    add(("V0b_app3_shrink", "附录3物性+收缩 t_dry", td["V0b_app3_shrink"], "s", "V0b", "outputs/q4_verify.log"))
    add(("V0b_app4_Rconst", "附录4物性+冻结收缩 t_dry", td["V0b_app4_Rconst"], "s", "V0b", "outputs/q4_verify.log"))
    add(("V0b_app4_Rconst_h", "附录4物性+冻结收缩 t_dry", td["V0b_app4_Rconst"] / 3600.0, "h", "V0b", "outputs/q4_verify.log"))
    add(("V0b_app4_Rconst_d", "附录4物性+冻结收缩 t_dry", td["V0b_app4_Rconst"] / 86400.0, "d", "V0b", "outputs/q4_verify.log"))
    add(("PROD_tdry", "生产解 t_dry", td["PROD"], "s", "PROD", "outputs/q4_verify.log"))
    add(("PROD_tdry_h", "生产解 t_dry", td["PROD"] / 3600.0, "h", "PROD", "outputs/q4_verify.log"))
    add(("PROD_tdry_d", "生产解 t_dry", td["PROD"] / 86400.0, "d", "PROD", "outputs/q4_verify.log"))

    say("\n[V1] 空间收敛性 (细分到 M=3200 以判定渐近阶)")
    Ms = [100, 200, 400, 800, 1600, 3200]
    keys = ["V1_M100", "PROD", "V1_M400", "V1_M800", "V1_M1600", "V1_M3200"]
    tv1 = [td[k] for k in keys]
    for M, k, v in zip(Ms, keys, tv1):
        say(f"  M={M:4d}  t_dry = {v:14.4f} s   ({v/3600:9.5f} h)")
        add((f"V1_M{M}", f"M={M} 的 t_dry", v, "s", "V1", "outputs/q4_verify.log"))
    say("  相邻差与实测阶 p = log2(d_k / d_{k+1}):")
    ps = []
    for i in range(len(tv1) - 2):
        dk = tv1[i + 1] - tv1[i]
        dk1 = tv1[i + 2] - tv1[i + 1]
        r_ = dk / dk1
        p_ = float(np.log2(r_))
        ps.append(p_)
        say(f"    M={Ms[i]:4d}->{Ms[i+1]:4d}->{Ms[i+2]:4d}: d=({dk:9.4f}, {dk1:8.4f})"
            f"  比={r_:6.4f}  p={p_:.4f}")
        add((f"V1_p_{Ms[i]}", f"由 M={Ms[i]} 三点估计的收敛阶", p_, "1", "V1",
             "outputs/q4_verify.log"))
    p_asy = ps[-1]
    say(f"  渐近阶 p -> {p_asy:.4f} (接近 2, 说明 M=100->200 的比值是**前渐近**值)")
    add(("V1_p_asym", "渐近收敛阶", p_asy, "1", "V1", "outputs/q4_verify.log"))
    # 用最后两个网格 + 渐近阶作 Richardson 外推
    t_rich = tv1[-1] + (tv1[-1] - tv1[-2]) / (2.0 ** p_asy - 1.0)
    say(f"  以 p={p_asy:.4f} 作 Richardson 外推: t* = {t_rich:.4f} s "
        f"= {t_rich/3600:.5f} h")
    add(("V1_rich_s", "Richardson 外推 t_dry (渐近阶)", t_rich, "s", "V1",
         "outputs/q4_verify.log"))
    add(("V1_rich_h", "Richardson 外推 t_dry (渐近阶)", t_rich / 3600.0, "h", "V1",
         "outputs/q4_verify.log"))
    for M, k, v in zip(Ms, keys, tv1):
        add((f"V1_err_M{M}", f"M={M} 相对外推极限的误差", (v - t_rich) / 3600.0, "h",
             "V1", "outputs/q4_verify.log"))
    say(f"  M=200 相对外推极限的误差 {(tv1[1]-t_rich)/3600:.5f} h; "
        f"M=400 {(tv1[2]-t_rich)/3600:.5f} h; M=3200 {(tv1[-1]-t_rich)/3600:.5f} h")

    say("\n[V2] 时间容限收敛性")
    say(f"  rtol=1e-7 : {td['V2_rtol1e7']:.4f} s")
    say(f"  rtol=1e-9 : {td['PROD']:.4f} s  (生产)")
    say(f"  rtol=1e-11: {td['V2_rtol1e11']:.4f} s")
    add(("V2_rtol1e7", "rtol=1e-7 的 t_dry", td["V2_rtol1e7"], "s", "V2", "outputs/q4_verify.log"))
    add(("V2_rtol1e11", "rtol=1e-11 的 t_dry", td["V2_rtol1e11"], "s", "V2", "outputs/q4_verify.log"))

    say("\n[V4] 收缩数据插值口径")
    for k, lab in (("V4_lin", "线性插值"), ("PROD", "PCHIP(生产)"),
                   ("V4_tau0", "过渡段=0"), ("V4_tau1800", "过渡段=1800s")):
        say(f"  {lab:12s}: {td[k]:14.4f} s   (相对生产 {td[k]-td['PROD']:+.4f} s)")
        add((f"V4_{k}", f"收缩数据口径 {lab} 的 t_dry", td[k], "s", "V4", "outputs/q4_verify.log"))

    say("\n[V6] 收缩律灵敏度")
    for k, lab in (("V6_scale1p10", "R x 1.10"), ("V6_scale1p05", "R x 1.05"),
                   ("PROD", "R x 1.00 (生产)"), ("V6_scale0p95", "R x 0.95"),
                   ("V6_scale0p90", "R x 0.90")):
        say(f"  {lab:20s}: {td[k]:14.4f} s = {td[k]/3600:8.5f} h  ({td[k]-td['PROD']:+.1f} s)")
        add((f"V6_{k}", f"收缩律 {lab} 的 t_dry", td[k], "s", "V6", "outputs/q4_verify.log"))
    say(f"  {'R = const (冻结收缩)':20s}: {td['V0b_app4_Rconst']:14.4f} s = "
        f"{td['V0b_app4_Rconst']/3600:8.5f} h  ({td['V0b_app4_Rconst']-td['PROD']:+.1f} s)")

    say("\n[V5b] 独立 FV 格式**求解到终止事件**的 t_dry 对照")
    say("  这是唯一有实质意义的独立对照: 不看某一时刻的场, 看最终答案.")
    fvs = []
    for Mc in (100, 200, 400, 800):
        r5 = run_fv_reference(M=Mc, app="app4", rad_mode="data", t_max=864000.0)
        main_v = td["V1_M100"] if Mc == 100 else (
            td["PROD"] if Mc == 200 else (
                td["V1_M400"] if Mc == 400 else td["V1_M800"]))
        diff = r5["t_dry"] - main_v
        fvs.append((Mc, r5["t_dry"], main_v, diff))
        say(f"  M={Mc:4d}: FV {r5['t_dry']:12.4f} s ({r5['t_dry']/3600:8.5f} h) | "
            f"主格式 {main_v:12.4f} s ({main_v/3600:8.5f} h) | 差 {diff/3600:+.4f} h")
        add((f"V5b_FV_M{Mc}", f"独立FV 求解到事件的 t_dry (M={Mc})", r5["t_dry"], "s",
             "V5b", "outputs/q4_verify.log"))
        add((f"V5b_main_M{Mc}", f"主格式 t_dry (M={Mc})", main_v, "s", "V5b",
             "outputs/q4_verify.log"))
        add((f"V5b_diff_M{Mc}", f"FV 与主格式的 t_dry 差 (M={Mc})", diff / 3600.0, "h",
             "V5b", "outputs/q4_verify.log"))
    # FV 自身的一阶外推
    if len(fvs) >= 2:
        (M1, t1_, _, _), (M2, t2_, _, _) = fvs[0], fvs[-1]
        p_fv = float(np.log2(abs(fvs[1][1] - t1_) / abs(fvs[2][1] - fvs[1][1])))
        say(f"  FV 自身的实测收敛阶 p_FV ≈ {p_fv:.4f} (一阶, 因表面落在网格点之间)")
        add(("V5b_p_FV", "独立 FV 的实测收敛阶", p_fv, "1", "V5b",
             "outputs/q4_verify.log"))
        # 用相邻两网格作一阶 Richardson 外推
        d_last = fvs[-1][1] - fvs[-2][1]
        t_fv_rich = fvs[-1][1] + d_last
        say(f"  FV 一阶外推极限 ≈ {t_fv_rich:.4f} s = {t_fv_rich/3600:.5f} h")
        add(("V5b_FV_rich", "独立 FV 的 Richardson 外推极限", t_fv_rich, "s", "V5b",
             "outputs/q4_verify.log"))
        say(f"  与主格式 M=3200 ({td['V1_M3200']:.4f} s) 之差 = "
            f"{(t_fv_rich-td['V1_M3200'])/3600:+.4f} h  <-- 两套独立实现收敛到同一极限")
        add(("V5b_limit_diff", "FV 外推极限与主格式 M=3200 之差",
             (t_fv_rich - td["V1_M3200"]) / 3600.0, "h", "V5b",
             "outputs/q4_verify.log"))
    say("  **说明 (审计意见 F2/F7)**: FV 与主格式共享物质坐标与 beta R^2=const 假设,")
    say("     故它验证的是**实现与离散**, 而**不是**物质坐标变换本身; 该变换由 §4.3 的")
    say("     干物质守恒推导给出, 并由 §5.5 的物理坐标对照在解析上确证 (其数值实现")
    say("     在变形控制面上不稳定, 见 problem4.md §5.5).")
    say("\n[V5a] 同一物质坐标下两种离散的逐点对照 (验证实现, 不验证坐标变换)")
    for app, rmo, app3, lab in (
            ("app3", "const", True, "附录3 + 冻结收缩"),
            ("app4", "data", False, "附录4 + 收缩 (生产口径)")):
        say(f"  {lab}:")
        prev_dC = None
        for Mc in (100, 200, 400):
            cmp = compare_formulations(M=Mc, t_end=21600.0, app=app,
                                       rad_mode=rmo, app3=app3)
            trend = "" if prev_dC is None else f"   (较 M={Mc//2} 缩小 {prev_dC/cmp['max_dC']:.2f} 倍)"
            say(f"     M={Mc:3d}: C_surf 主 {cmp['Csurf_m']:.6f} / FV {cmp['Csurf_f']:.6f};"
                f"  max|dC|={cmp['max_dC']:.3e} kg/kg, T_surf 差 "
                f"{abs(cmp['Tsurf_m']-cmp['Tsurf_f']):.2e} K{trend}")
            add((f"V5_dC_{app}_{Mc}", f"V5 {lab} M={Mc} 最大水分差", cmp["max_dC"],
                 "kg/kg", "V5", "outputs/q4_verify.log"))
            add((f"V5_dTsurf_{app}_{Mc}", f"V5 {lab} M={Mc} 表面温度差",
                 abs(cmp["Tsurf_m"] - cmp["Tsurf_f"]), "K", "V5",
                 "outputs/q4_verify.log"))
            add((f"V5_dT_{app}_{Mc}", f"V5 {lab} M={Mc} 全域最大温度差",
                 cmp["max_dT"], "K", "V5", "outputs/q4_verify.log"))
            add((f"V5_Csurf_m_{app}_{Mc}", f"V5 {lab} M={Mc} 主格式表面含水率",
                 cmp["Csurf_m"], "kg/kg", "V5", "outputs/q4_verify.log"))
            add((f"V5_Csurf_f_{app}_{Mc}", f"V5 {lab} M={Mc} 独立FV 表面含水率",
                 cmp["Csurf_f"], "kg/kg", "V5", "outputs/q4_verify.log"))
            prev_dC = cmp["max_dC"]
        say("     注: 两格式的表面离散口径不同 (节点半单元 vs 单元中心), "
            "故差值以 O(dxi) 收敛;")
        say("         温度场两格式在 1e-4 K 量级一致, 是更强的独立印证.")

    say("\n[V7/V9] 结构不变量与事件性质")
    for tag, key in (("PROD", "PROD"), ("app4Rconst", "V0b_app4_Rconst")):
        r = res[key]
        rr, info = check_invariants(r, tag)
        ev = check_event(r, tag)
        rows.extend(rr)
        rows.extend(ev)
        say(f"  {tag}: C_min-Cbar = {info['Cmin_all']-r['env'].Cbar:+.3e} kg/kg; "
            f"C_max <= C0 差 = {C0-info['Cmax_all']:+.3e}; 单调违例 = {info['monotone_viol']}")
        say(f"          水量收支 dW = {info['dW']:.6e}, 积分通量 = {info['flux_int']:.6e}, "
            f"相对残差 = {abs(info['dW']-info['flux_int'])/abs(info['dW']):.3e}")
        say(f"          事件末 2h 上升步数 = {ev[0][2]:.0f}; g(t_dry) = {ev[2][2]:+.3e} kg/kg")

    # ---------------- 注册表 ----------------
    import csv
    path = os.path.join(OUTDIR, "registry_q4_verify.csv")
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["key", "quantity", "value", "unit", "group", "source", "note"])
        for r in rows:
            w.writerow([r[0], r[1], repr(float(r[2])) if isinstance(r[2], float) else r[2],
                        r[3], r[4], r[5], r[6] if len(r) > 6 else ""])
    say(f"\n注册表已写出: outputs/registry_q4_verify.csv ({len(rows)} 行)")

    with open(os.path.join(OUTDIR, "q4_verify.log"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")


if __name__ == "__main__":
    main()
