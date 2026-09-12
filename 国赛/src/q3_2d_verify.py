# -*- coding: utf-8 -*-
"""
q3_2d_verify.py -- 问题三 W11: 降维合理性验证 (二维 r-z 轴对称对照模型).

问题二/三的生产模型是径向一维 (假设 B2: 忽略轴向与周向传递, 端面面积仅占
侧面的 4%). 本脚本构造二维轴对称 (r, z) 对照模型, 定量检验"忽略轴向"对
问题三 (t_dry ~ 57.4 h, 时间跨度远大于问题一/二) 是否仍然成立:

    * 求解域: 半圆柱 z in [0, L/2], 中截面 z = L/2 为对称面 (dz = 0 精确),
      端面 z = 0 为第三类边界, 与侧面处于同一环境 (h, h_m, T_inf(t), C_inf(t));
    * 半离散: 守恒型有限体积, 径向半控制体体积与问题一 halfcv 离散逐项一致
      (vol_r[0] = dr^2/8, vol_r[i] = r_i dr, vol_r[Nr] = dr^2(4Nr-1)/8),
      集中质量 -> 标准 ODE -> scipy BDF + 终止事件 (与生产求解器同配置);
    * 对角化验证: Nz = 0 (无轴向通量) 必须复现 q3_solve.make_rhs + halfcv 的
      一维半离散 —— 同一离散、同一求解器, t_dry 差应在机器精度量级;
    * 轴向收敛性: Nz = 25 与 Nz = 50 两套轴向网格;
    * 最不利算例: 端面传质系数放大 1e4 倍 (等效第一类边界 C = C_inf,
      表面平衡偏移 ~ J/h_m ~ 2e-4 kg/kg), 传热不变 —— 端面效应的上界;
    * 比较原理: 一维解沿 z 常数延拓是二维问题的上解 (端面外通量 0 <= 边界
      定律要求的 h_m (u - C_inf) >= 0, 全程 C >= C_inf 成立),
      故 t_dry^2D <= t_dry^1D, 一维模型给出的烘干时间是保守上界.

运行:
    python src/q3_2d_verify.py --pilot   小网格冒烟 (Nr=40, Nz=10, rtol=1e-7)
    python src/q3_2d_verify.py --full    完整验证, 写 outputs/registry_q3_2d.csv
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
from q2_solve import (props, Dfun, geometry, H_CONV, HM, R, T0K, C0,    # noqa: E402
                      HEVAP_28, HEVAP_SLOPE, HEVAP_TREF, out_indices)
from q3_solve import (Q3Env, make_rhs, make_event, sparsity_pattern,    # noqa: E402
                      solve_q3, write_registry, CSTAR, T_MAX,
                      PROD_ATOL_T, PROD_ATOL_C, PROD_MAX_STEP, PROD_M)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

L_HALF = 0.125          # m, 半长 L/2 (L = 25 cm)
END_HM_MULT = 1.0e4     # 最不利算例: 端面传质系数放大倍数 (等效第一类边界)


# ---------------------------------------------------------------------------
# 二维轴对称几何与半离散
# ---------------------------------------------------------------------------
def geometry2d(Nr, Nz):
    """二维 (r, z) 半域几何 (per 2 pi, 即按 1 弧度切片计).

    节点 (i, j): r_i = i dr (i = 0..Nr), z_j = j dz (j = 0..Nz, z_0 = 端面,
    z_Nz = 中截面对称面). 未知量平坦索引 (行主序, 与 rhs 的 reshape 一致):
    k = i*(Nz+1) + j (j 最快, 径向步长 Nz+1).

    vol_r[i]  径向积分 (半控制体): vol_r[0]=dr^2/8, vol_r[i]=r_i dr,
              vol_r[Nr]=dr^2(4Nr-1)/8 -- 与问题一 halfcv 逐项一致;
    zext[j]   z 向控制体厚度: 内部 dz, 端面/对称面 dz/2 (Nz=0 时取 1, 无量纲);
    v[i,j]    = vol_r[i] * zext[j]                控制体体积 (per 2 pi);
    Ar[i,j]   = rf[i] * zext[j] / dr              径向面几何 (i=0..Nr-1);
    Az[i,j]   = vol_r[i] / dz                     轴向面几何 (j=0..Nz-1);
    侧面面积  = R * zext[j] (仅 i=Nr);  端面面积 = vol_r[i] (仅 j=0).
    """
    dr = R / Nr
    r = np.arange(Nr + 1) * dr
    rf = 0.5 * (r[:-1] + r[1:])
    vol_r = np.empty(Nr + 1)
    vol_r[0] = 0.5 * rf[0] ** 2
    vol_r[1:Nr] = 0.5 * (rf[1:] ** 2 - rf[:-1] ** 2)
    vol_r[Nr] = 0.5 * (R ** 2 - rf[-1] ** 2)
    if Nz == 0:                     # 无限长圆柱参照 (无端面, 无轴向通量)
        z = np.array([0.0])
        dz = 0.0
        zext = np.array([1.0])
    else:
        dz = L_HALF / Nz
        z = np.arange(Nz + 1) * dz
        zext = np.full(Nz + 1, dz)
        zext[0] = zext[-1] = 0.5 * dz
    Ar = rf[:, None] * zext[None, :] / dr
    Az = (vol_r / dz)[:, None] * np.ones((1, Nz)) if Nz else np.zeros((Nr + 1, 0))
    return dict(Nr=Nr, Nz=Nz, n2=(Nr + 1) * (Nz + 1), dr=dr, r=r, rf=rf,
                vol_r=vol_r, z=z, dz=dz, zext=zext, Ar=Ar, Az=Az,
                v=vol_r[:, None] * zext[None, :])


def make_rhs2d(g2, env, hevap=True, end_hm_mult=1.0):
    """二维半离散 ODE 右端. 方程与物性与 q3_solve 完全一致 (附录 3 + H_evap(T))."""
    Nr, Nz = g2["Nr"], g2["Nz"]
    Ar, Az, v = g2["Ar"], g2["Az"], g2["v"]
    lat = R * g2["zext"]                       # 侧面面积 (per 2 pi)
    endA = g2["vol_r"]                         # 端面面积 (per 2 pi)

    def rhs(t, U):
        n2 = U.size // 2
        T = U[:n2].reshape(Nr + 1, Nz + 1)
        C = U[n2:].reshape(Nr + 1, Nz + 1)
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, _, _, _ = props(C, "app3")
        Dv = Dfun(C, T, "app3")
        rcp = rho * cp
        KT = np.zeros_like(T)
        KC = np.zeros_like(C)
        # 径向面 (正 = 由 i 流向 i+1)
        Fr = 0.5 * (k[:-1, :] + k[1:, :]) * Ar * (T[:-1, :] - T[1:, :])
        KT[:-1, :] += Fr
        KT[1:, :] -= Fr
        Fq = 0.5 * (Dv[:-1, :] + Dv[1:, :]) * Ar * (C[:-1, :] - C[1:, :])
        KC[:-1, :] += Fq
        KC[1:, :] -= Fq
        # 轴向面
        if Nz:
            Fz = 0.5 * (k[:, :-1] + k[:, 1:]) * Az * (T[:, :-1] - T[:, 1:])
            KT[:, :-1] += Fz
            KT[:, 1:] -= Fz
            Fw = 0.5 * (Dv[:, :-1] + Dv[:, 1:]) * Az * (C[:, :-1] - C[:, 1:])
            KC[:, :-1] += Fw
            KC[:, 1:] -= Fw
        # 侧面 (i = Nr): 对流 + 蒸发吸热 (与一维表面定律相同)
        Hev_l = HEVAP_28 + HEVAP_SLOPE * (T[Nr, :] - HEVAP_TREF)
        if hevap:
            KT[Nr, :] += H_CONV * lat * (T[Nr, :] - Tinf) \
                + Hev_l * HM * lat * (C[Nr, :] - Cinf)
        else:
            KT[Nr, :] += H_CONV * lat * (T[Nr, :] - Tinf)
        KC[Nr, :] += HM * lat * (C[Nr, :] - Cinf)
        # 端面 (j = 0): 传热用正常 h_m; 传质可放大 (最不利算例)
        if Nz and end_hm_mult > 0.0:
            Hev_0 = HEVAP_28 + HEVAP_SLOPE * (T[:, 0] - HEVAP_TREF)
            KT[:, 0] += H_CONV * endA * (T[:, 0] - Tinf) \
                + Hev_0 * HM * endA * (C[:, 0] - Cinf)
            KC[:, 0] += HM * end_hm_mult * endA * (C[:, 0] - Cinf)
        return np.concatenate([-(KT / (rcp * v)).ravel(), -(KC / v).ravel()])

    return rhs


def sparsity2d(Nr, Nz):
    """Jacobian 稀疏结构: 每场 5 点模板 + 自身; 四个场块同构.

    平坦索引与 rhs 的 reshape(Nr+1, Nz+1) 行主序一致:
    k = i*(Nz+1) + j (j 最快), 径向邻居步长 nx = Nz+1, 轴向邻居步长 1.
    (若模式与 rhs 顺序错位, 分组差分 Jacobian 会算错, Newton 收敛失败,
    BDF 步长崩塌 -- pilot 阶段曾因此卡死, 已由稠密 FD Jacobian 支撑集核验.)
    """
    nx = Nz + 1
    ny = Nr + 1
    rows, cols = [], []
    for i in range(ny):
        for j in range(nx):
            k = i * nx + j
            nb = [k]
            if i > 0:
                nb.append(k - nx)           # 径向 i-1
            if i < Nr:
                nb.append(k + nx)           # 径向 i+1
            if j > 0:
                nb.append(k - 1)            # 轴向 j-1
            if j < Nz:
                nb.append(k + 1)            # 轴向 j+1
            rows.extend([k] * len(nb))
            cols.extend(nb)
    rows = np.asarray(rows, dtype=int)
    cols = np.asarray(cols, dtype=int)
    n2 = ny * nx
    rr = np.concatenate([rows, rows + n2, rows, rows + n2])
    cc = np.concatenate([cols, cols, cols + n2, cols + n2])
    return sp.coo_matrix((np.ones(rr.size), (rr, cc)),
                         shape=(2 * n2, 2 * n2)).tocsr()


def check_sparsity(Nr=20, Nz=6, t=1.0e4, seed=3, eps=1e-7):
    """自检: 稠密 FD Jacobian 的显著非零元必须全部落在 sparsity2d 模式内.

    返回模式外最大相对泄漏. 非零 -- 说明模式与 rhs 的平坦化顺序错位
    (分组差分 Jacobian 将给出错误矩阵, BDF 步长崩塌).
    """
    g2 = geometry2d(Nr, Nz)
    n2 = g2["n2"]
    rhs = make_rhs2d(g2, Q3Env(*load_attachment1()))
    rng = np.random.default_rng(seed)
    U = np.empty(2 * n2)
    U[:n2] = 310.0 + 8.0 * rng.random(n2)
    U[n2:] = np.maximum(2.55 - 1.5 * rng.random(n2), 0.3)
    J = np.zeros((2 * n2, 2 * n2))
    for j in range(2 * n2):
        Up, Um = U.copy(), U.copy()
        h = eps * max(abs(U[j]), 1.0)
        Up[j] += h
        Um[j] -= h
        J[:, j] = (rhs(t, Up) - rhs(t, Um)) / (2 * h)
    scale = max(float(np.abs(J).max()), 1e-30)
    outside = float(np.abs(J[~(sparsity2d(Nr, Nz).toarray() > 0)]).max())
    return outside / scale


# ---------------------------------------------------------------------------
# 求解
# ---------------------------------------------------------------------------
def solve_2d(Nr, Nz, rtol=1e-8, atol_T=PROD_ATOL_T, atol_C=PROD_ATOL_C,
             max_step=PROD_MAX_STEP, t_max=T_MAX, end_hm_mult=1.0,
             t_eval=None, env=None, cstar=CSTAR):
    """二维 MOL + BDF + 终止事件 (配置与生产一致; 不用 dense_output 以省内存)."""
    g2 = geometry2d(Nr, Nz)
    n2 = g2["n2"]
    if env is None:
        t1, T1, C1 = load_attachment1()
        env = Q3Env(t1, T1, C1)
    rhs = make_rhs2d(g2, env, end_hm_mult=end_hm_mult)
    sps = sparsity2d(Nr, Nz)
    U0 = np.concatenate([np.full(n2, T0K), np.full(n2, C0)])
    atol = np.concatenate([np.full(n2, atol_T), np.full(n2, atol_C)])
    ev = make_event(n2, cstar)
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, float(t_max)), U0, method="BDF", rtol=rtol,
                    atol=atol, max_step=float(max_step), events=ev,
                    t_eval=t_eval, jac_sparsity=sps)
    wall = time.time() - t0
    if sol.status != 1 or len(sol.t_events[0]) == 0:
        Cend = sol.y[n2:, -1]
        raise RuntimeError(
            f"2D 终止事件未触发: status={sol.status}, t={sol.t[-1]:.1f} s, "
            f"max C = {Cend.max():.6f} (end_hm_mult={end_hm_mult})")
    return dict(sol=sol, g2=g2, env=env, rhs=rhs, sps=sps,
                t_dry=float(sol.t_events[0][0]), nsteps=len(sol.t) - 1,
                nfev=int(sol.nfev), njev=int(sol.njev), nlu=int(sol.nlu),
                wall=wall, rtol=rtol, end_hm_mult=end_hm_mult,
                atol_T=atol_T, atol_C=atol_C, max_step=max_step)


def state_at(res, t_target):
    """取 t_target 时刻的状态.

    终止事件触发时 scipy 已把 sol.t[-1]/sol.y[:, -1] 精确替换为事件时刻
    (无 t_eval 的情形, 直接返回); 有 t_eval 时末点是 t_target 之前最近的
    采样点, 从那里向前重启一小段积分 (无事件).
    """
    sol = res["sol"]
    if abs(float(sol.t[-1]) - t_target) < 1e-9 * max(1.0, abs(t_target)):
        return sol.y[:, -1].copy()
    k = max(int(np.searchsorted(sol.t, t_target, side="right")) - 1, 0)
    n2 = res["g2"]["n2"]
    y0 = sol.y[:, k]
    t0 = float(sol.t[k])
    atol = np.concatenate([np.full(n2, res["atol_T"]), np.full(n2, res["atol_C"])])
    s2 = solve_ivp(res["rhs"], (t0, float(t_target)), y0, method="BDF",
                   rtol=res["rtol"], atol=atol, max_step=res["max_step"],
                   jac_sparsity=res["sps"], t_eval=[float(t_target)])
    # 无事件积分成功到达区间终点的 status 是 0 (1 是事件终止), 勿混用
    if s2.status not in (0, 1) or s2.y.shape[1] == 0:
        raise RuntimeError(f"state_at 重启积分失败: status={s2.status}")
    return s2.y[:, -1]


def solve_1d_q3(boundary="halfcv", M=200, rtol=1e-8, atol_T=PROD_ATOL_T,
                atol_C=PROD_ATOL_C, max_step=PROD_MAX_STEP, env=None):
    """一维参照: q3_solve 的半离散 + halfcv (有限体积) 质量矩阵, BDF + 事件."""
    g = geometry(M, boundary)
    n = g["n"]
    if env is None:
        t1, T1, C1 = load_attachment1()
        env = Q3Env(t1, T1, C1)
    rhs = make_rhs(g, env)
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    atol = np.concatenate([np.full(n, atol_T), np.full(n, atol_C)])
    ev = make_event(n, CSTAR)
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, T_MAX), U0, method="BDF", rtol=rtol, atol=atol,
                    max_step=max_step, events=ev, dense_output=True,
                    jac_sparsity=sparsity_pattern(g))
    wall = time.time() - t0
    if sol.status != 1 or len(sol.t_events[0]) == 0:
        raise RuntimeError("1D 参照解终止事件未触发")
    return dict(sol=sol, g=g, env=env, t_dry=float(sol.t_events[0][0]),
                nsteps=len(sol.t) - 1, wall=wall, M=M, boundary=boundary,
                rtol=rtol)


# ---------------------------------------------------------------------------
# 采样
# ---------------------------------------------------------------------------
def sample_2d(res, idx21):
    """二维解的诊断量 (在已存采样点上 + t_dry 重启终态)."""
    g2 = res["g2"]
    Nr, Nz, n2 = g2["Nr"], g2["Nz"], g2["n2"]
    ny = Nr + 1
    nx = Nz + 1
    kmid = idx21 * nx + Nz                    # 中截面 21 个输出半径的行号
    te = res["sol"].t
    Y = res["sol"].y
    C2, T2 = Y[n2:], Y[:n2]
    out = dict(t=te, C_mid=C2[kmid, :], T_mid=T2[kmid, :])
    # argmax 诊断: 期望恒为 (r=0, 中截面) => 平坦号 0*nx + Nz
    # (t≈0 各内部节点并列取最大, argmax 在并列节点间抖动属数值噪声;
    #  报告偏离点数与最后一次偏离时刻, 以区分并列与真实异常)
    off = C2.argmax(axis=0) != Nz
    out["argmax_off"] = int(off.sum())
    out["argmax_last_t"] = float(te[off][-1]) if off.any() else 0.0
    # 水量收支 (半圆柱, per 2 pi): W(t) 与表面水通量 Q(t)
    Cgrid = C2.reshape(ny, Nz + 1, -1)
    out["W"] = (g2["v"].ravel()[:, None] * C2).sum(axis=0)
    Cinf = res["env"].C_arr(te)
    Q = (HM * R * g2["zext"][:, None]
         * (Cgrid[Nr, :, :] - Cinf[None, :])).sum(axis=0)
    if Nz and res["end_hm_mult"] > 0.0:
        Q = Q + (HM * res["end_hm_mult"] * g2["vol_r"][:, None]
                 * (Cgrid[:, 0, :] - Cinf[None, :])).sum(axis=0)
    out["Q"] = Q
    # t_dry 终态 (重启积分): 中截面剖面 + 轴线轴向剖面
    Yd = state_at(res, res["t_dry"])
    Cd = Yd[n2:].reshape(ny, Nz + 1)
    Td = Yd[:n2].reshape(ny, Nz + 1)
    out["C_mid_dry"] = Cd[idx21, Nz]
    out["T_mid_dry"] = Td[idx21, Nz]
    out["C_axis_z_dry"] = Cd[0, :]            # C(r=0, z, t_dry), z 从端面起
    out["T_axis_z_dry"] = Td[0, :]
    out["C_dry_max"] = float(Cd.max())
    out["W_dry"] = float((g2["v"].ravel() * Yd[n2:]).sum())
    return out


# ---------------------------------------------------------------------------
# 多进程 worker (Windows spawn: 顶层函数)
# ---------------------------------------------------------------------------
def run_2d_case(cfg):
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    res = solve_2d(env=env, **{k: v for k, v in cfg.items() if k != "tag"})
    smp = sample_2d(res, out_indices(PROD_M))
    keep = dict(tag=cfg.get("tag", ""), t_dry=res["t_dry"],
                nsteps=res["nsteps"], nfev=res["nfev"], njev=res["njev"],
                nlu=res["nlu"], wall=res["wall"], rtol=res["rtol"],
                end_hm_mult=res["end_hm_mult"],
                t=smp["t"], C_mid=smp["C_mid"], T_mid=smp["T_mid"],
                argmax_off=smp["argmax_off"],
                argmax_last_t=smp["argmax_last_t"], W=smp["W"], Q=smp["Q"],
                C_mid_dry=smp["C_mid_dry"], T_mid_dry=smp["T_mid_dry"],
                C_axis_z_dry=smp["C_axis_z_dry"],
                T_axis_z_dry=smp["T_axis_z_dry"],
                C_dry_max=smp["C_dry_max"], W_dry=smp["W_dry"],
                z_cm=res["g2"]["z"] * 100.0, Nz=res["g2"]["Nz"],
                Nr=res["g2"]["Nr"])
    return keep


def run_parallel(cfgs, workers=3):
    from concurrent.futures import ProcessPoolExecutor
    out = {}
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for res in ex.map(run_2d_case, cfgs):
            out[res["tag"]] = res
            print(f"  [{res['tag']}] Nr={res['Nr']} Nz={res['Nz']} "
                  f"rtol={res['rtol']:g} end_mult={res['end_hm_mult']:g}: "
                  f"t_dry={res['t_dry']:.3f} s ({res['t_dry'] / 3600.0:.4f} h), "
                  f"{res['nsteps']} 步, nlu={res['nlu']}, 用时 {res['wall']:.1f} s",
                  flush=True)
    print(f"  [{len(cfgs)} 组二维算例并行, 共用时 {time.time() - t0:.1f} s]",
          flush=True)
    return out


# ---------------------------------------------------------------------------
# 解析尺度估计
# ---------------------------------------------------------------------------
def analytic_estimates(t_prod):
    """端面面积占比 / 轴向时间尺度 / 穿透深度 (全部由常数与 Dfun 现算)."""
    T50 = 50.0 + 273.15
    L = 2.0 * L_HALF
    D0 = float(Dfun(np.array([C0]), np.array([T50]), "app3")[0])      # C=2.55
    Ds = float(Dfun(np.array([CSTAR]), np.array([T50]), "app3")[0])   # C=0.15
    rho, cp, k, _, _, _ = props(np.array([C0]), "app3")
    alpha0 = float(k[0] / (rho[0] * cp[0]))
    est = dict(
        area_end=R / (2 * L),                    # 单端面/侧面 = R/(2L) = 4%
        area_both=R / L,                         # 双端面/侧面 = R/L = 8%
        tscale_ax=L_HALF ** 2 / Ds,              # (L/2)^2 / D(C*, 50 degC)
        tscale_ratio=(L_HALF / R) ** 2,          # 轴向/径向湿分时间尺度比
        pen_dmax_cm=np.sqrt(D0 * t_prod) * 100.0,      # 恒取湿态 D 的保守穿透
        pen_dstar_cm=np.sqrt(Ds * t_prod) * 100.0,     # 阈值态 D 的穿透
        pen_alpha_cm=np.sqrt(alpha0 * t_prod) * 100.0, # 热穿透 (讨论用)
        D_over_alpha=Ds / alpha0,
    )
    est["tscale_ax_h"] = est["tscale_ax"] / 3600.0
    est["tscale_over_tdry"] = est["tscale_ax"] / t_prod
    return est


# ---------------------------------------------------------------------------
# pilot / full
# ---------------------------------------------------------------------------
def pilot():
    print("=" * 96)
    print("P0  稀疏模式自检: FD Jacobian 支撑集 vs sparsity2d (Nr=20, Nz=6)")
    print("=" * 96)
    leak = check_sparsity()
    print(f"  模式外最大相对泄漏 = {leak:.3e} "
          f"{'OK' if leak < 1e-6 else '!! 模式与 rhs 顺序错位'}")

    print()
    print("=" * 96)
    print("P1  对角化验证: 二维代码 Nz=0 vs q3_solve.make_rhs + halfcv (M=40)")
    print("=" * 96)
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    tt = np.array([1800.0, 7200.0, 14400.0])
    r1 = solve_1d_q3(boundary="halfcv", M=40, rtol=1e-7, env=env)
    print(f"  1D halfcv  : t_dry = {r1['t_dry']:.6f} s ({r1['nsteps']} 步, "
          f"{r1['wall']:.1f} s)")
    r2 = solve_2d(Nr=40, Nz=0, rtol=1e-7, env=env, t_eval=tt)
    print(f"  2D Nz=0    : t_dry = {r2['t_dry']:.6f} s ({r2['nsteps']} 步, "
          f"{r2['wall']:.1f} s)")
    print(f"  差 |t_2d0 - t_1d| = {abs(r2['t_dry'] - r1['t_dry']):.3e} s "
          f"(应为机器精度量级)")
    idx = out_indices(40)
    n1, n2 = r1["g"]["n"], r2["g2"]["n2"]
    C1v = r1["sol"].sol(tt)[n1 + idx, :]
    C2v = r2["sol"].y[n2 + idx, :]
    print(f"  共同时刻中截面 max|dC| = {np.max(np.abs(C2v - C1v)):.3e} kg/kg")

    print()
    print("=" * 96)
    print("P2  小网格二维算例 (Nr=40, Nz=10, rtol=1e-7) -- 计时与轴向效应量级")
    print("=" * 96)
    r3 = solve_2d(Nr=40, Nz=10, rtol=1e-7, env=env)
    smp = sample_2d(r3, idx)
    print(f"  2D Nr=40 Nz=10: t_dry = {r3['t_dry']:.6f} s "
          f"({r3['nsteps']} 步, nlu={r3['nlu']}, {r3['wall']:.1f} s)")
    print(f"  轴向效应 dt = t_2D - t_1D = {r3['t_dry'] - r1['t_dry']:+.3f} s")
    print(f"  argmax 偏离 (0,中截面) 的采样点数 = {smp['argmax_off']}")
    Cz = smp["C_axis_z_dry"]
    print("  t_dry 轴线轴向剖面 C(0, z): " +
          "  ".join(f"z={z * 100:.2f}cm:{c:.4f}"
                    for z, c in zip(r3["g2"]["z"][:6], Cz[:6])))


def full():
    t_all = time.time()
    print("=" * 96)
    print("W11  二维轴对称 (r, z) 对照: 完整验证 (Nr=200)")
    print("=" * 96)
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    te = build_t_eval()
    idx21 = out_indices(PROD_M)

    # ---- 一维参照 ----
    print("\n[1/4] 一维参照 (q3 半离散 + halfcv + 生产 BDF 配置)")
    r_fv = solve_1d_q3(boundary="halfcv", M=200, rtol=1e-8, env=env)
    print(f"  1D FV halfcv, rtol=1e-8: t_dry = {r_fv['t_dry']:.6f} s "
          f"({r_fv['nsteps']} 步, {r_fv['wall']:.1f} s)")
    r_fv9 = solve_1d_q3(boundary="halfcv", M=200, rtol=1e-9, env=env)
    print(f"  1D FV halfcv, rtol=1e-9: t_dry = {r_fv9['t_dry']:.6f} s "
          f"(容限差 {abs(r_fv9['t_dry'] - r_fv['t_dry']):.3f} s)")
    print("[2/4] 生产基准复算 (FEM lumped, rtol=1e-9)")
    r_prod = solve_q3(M=PROD_M, rtol=1e-9, env=env)
    print(f"  生产 (lumped, rtol=1e-9): t_dry = {r_prod['t_dry']:.6f} s "
          f"(注册表 V1_M200 = 206720.4134563)")
    assert abs(r_prod["t_dry"] - 206720.4134563) < 0.01, "生产基准复算不一致!"

    # ---- 二维算例 (并行) ----
    print("[3/4] 二维算例 (并行 4 进程)")
    cfgs = [
        dict(tag="2d_Nz0", Nr=200, Nz=0, rtol=1e-8, t_eval=te),
        dict(tag="2d_Nz25", Nr=200, Nz=25, rtol=1e-8, t_eval=te),
        dict(tag="2d_Nz50", Nr=200, Nz=50, rtol=1e-8, t_eval=te),
        dict(tag="2d_enddir", Nr=200, Nz=50, rtol=1e-8, t_eval=te,
             end_hm_mult=END_HM_MULT),
    ]
    res = run_parallel(cfgs, workers=4)

    # ---- 对角化 + 诊断 ----
    print("[4/4] 对角化与诊断")
    n1 = r_fv["g"]["n"]
    idxm = n1 + idx21
    # 共同比较窗: 各解 (含最不利算例) 终止事件时刻的最小值.
    # 终止事件之后 1D 稠密输出是外插、2D 列已被截断, 必须裁掉.
    tmin = min([r_fv["t_dry"], r_prod["t_dry"]]
               + [res[k]["t_dry"] for k in res])
    keep1 = te <= tmin
    S_fv = r_fv["sol"].sol(te[keep1])
    C1fv, T1fv = S_fv[idxm, :], S_fv[:n1][idx21, :]
    S_p = r_prod["sol"].sol(te[keep1])
    C1p, T1p = S_p[idxm, :], S_p[:n1][idx21, :]
    print(f"  共同比较窗: t <= {tmin:.1f} s ({int(keep1.sum())} 个采样点)")

    d0 = res["2d_Nz0"]
    val_1d = abs(d0["t_dry"] - r_fv["t_dry"])
    print(f"  对角化 |t_2d(Nz=0) - t_1d(halfcv)| = {val_1d:.3e} s")

    dC_sch = float(np.max(np.abs(C1fv - C1p)))
    dT_sch = float(np.max(np.abs(T1fv - T1p)))
    print(f"  离散格式差 (FV-halfcv vs FEM-lumped, 同 M=200): "
          f"max|dC| = {dC_sch:.3e}, max|dT| = {dT_sch:.3e}")

    def mid_diffs(tag):
        d = res[tag]
        m = d["t"] <= tmin          # d["t"] 是 te 的子序列, 掩码逐点对应
        dC_ax = float(np.max(np.abs(d["C_mid"][:, m] - C1fv[:, m])))
        dT_ax = float(np.max(np.abs(d["T_mid"][:, m] - T1fv[:, m])))
        dC_pr = float(np.max(np.abs(d["C_mid"][:, m] - C1p[:, m])))
        dT_pr = float(np.max(np.abs(d["T_mid"][:, m] - T1p[:, m])))
        return dC_ax, dT_ax, dC_pr, dT_pr

    for tag in ("2d_Nz25", "2d_Nz50", "2d_enddir"):
        dC_ax, dT_ax, dC_pr, dT_pr = mid_diffs(tag)
        dt = res[tag]["t_dry"] - r_fv["t_dry"]
        print(f"  [{tag}] dt = t2D - t1D = {dt:+.3f} s; "
              f"中截面 max|dC|_axial = {dC_ax:.3e}, max|dT|_axial = {dT_ax:.3e}; "
              f"argmax 偏离 = {res[tag]['argmax_off']} 点, "
              f"最后偏离 t = {res[tag]['argmax_last_t']:.1f} s")

    # 水量收支 (2d_Nz50)
    d50 = res["2d_Nz50"]
    tf, Q, W = d50["t"], d50["Q"], d50["W"]
    integ = float(np.trapezoid(Q, tf))
    resid = abs(d50["W_dry"] - W[0] + integ) / abs(integ)
    wloss_2d = 1.0 - d50["W_dry"] / float(W[0])
    print(f"  2D 水量收支相对残差 = {resid:.3e}; 全程失水率 = {100 * wloss_2d:.2f}%")

    # 轴向 dip (t_dry, r=0)
    Cz = d50["C_axis_z_dry"]
    zcm = d50["z_cm"]
    below = zcm[Cz < CSTAR - 0.005]
    z_dip = float(below.max()) if below.size else 0.0
    print(f"  t_dry 轴线轴向剖面: z=0: {Cz[0]:.4f}, "
          f"z=1cm: {np.interp(1.0, zcm, Cz):.4f}, "
          f"z=2cm: {np.interp(2.0, zcm, Cz):.4f}, "
          f"z=5cm: {np.interp(5.0, zcm, Cz):.6f}, "
          f"z=12.5cm(中截面): {Cz[-1]:.4f}")
    print(f"  dip 范围 (C < 0.145 的轴向范围) = {z_dip:.2f} cm << 半长 12.5 cm")

    # 失水率对照 (1D)
    g1 = r_fv["g"]
    W0_1d = float(g1["MLg"].sum() * C0)
    Yd1 = r_fv["sol"].sol(r_fv["t_dry"])
    Wd_1d = float((g1["MLg"] * Yd1[n1:]).sum())
    wloss_1d = 1.0 - Wd_1d / W0_1d
    print(f"  失水率: 2D = {100 * wloss_2d:.2f}%, 1D = {100 * wloss_1d:.2f}%")

    # ---- 注册表 ----
    est = analytic_estimates(r_prod["t_dry"])
    rows = []

    def add(rid, q, v, unit="", note=""):
        rows.append([rid, q, v, unit, "", "outputs/q3_2d_verify.log",
                     "python src/q3_2d_verify.py --full", note])

    add("W11_area_end", "单端面换热面积/侧面积 R/(2L)", est["area_end"], "-")
    add("W11_area_both", "双端面换热面积/侧面积 R/L", est["area_both"], "-")
    add("W11_tscale_ax", "轴向湿分特征时间 (L/2)^2/D(C*,50C)", est["tscale_ax"], "s")
    add("W11_tscale_ax_h", "轴向湿分特征时间", est["tscale_ax_h"], "h")
    add("W11_tscale_ratio", "轴向/径向湿分时间尺度比 ((L/2)/R)^2",
        est["tscale_ratio"], "-")
    add("W11_tscale_over_tdry", "轴向特征时间/t_dry", est["tscale_over_tdry"], "-")
    add("W11_pen_dmax_cm", "恒取 D(C0,50C) 的轴向穿透深度", est["pen_dmax_cm"], "cm")
    add("W11_pen_dstar_cm", "取 D(C*,50C) 的轴向穿透深度", est["pen_dstar_cm"], "cm")
    add("W11_pen_alpha_cm", "热扩散轴向穿透深度 (alpha(C0))", est["pen_alpha_cm"], "cm")
    add("W11_D_over_alpha", "D(C*,50C)/alpha(C0)", est["D_over_alpha"], "-")

    add("W11_t_prod", "生产基准复算 t_dry (FEM lumped, rtol=1e-9)",
        r_prod["t_dry"], "s")
    add("W11_t_1dfv", "一维 FV halfcv 参照 t_dry (rtol=1e-8)", r_fv["t_dry"], "s")
    add("W11_t_1dfv_h", "一维 FV halfcv 参照 t_dry", r_fv["t_dry"] / 3600.0, "h")
    add("W11_t_1dfv_r9", "一维 FV halfcv 参照 t_dry (rtol=1e-9)",
        r_fv9["t_dry"], "s")
    add("W11_t_1dfv_tol", "一维参照容限敏感性 |r9-r8|",
        abs(r_fv9["t_dry"] - r_fv["t_dry"]), "s")
    add("W11_t_2d_nz0", "二维代码 Nz=0 对角化算例 t_dry", d0["t_dry"], "s")
    add("W11_val_1d", "对角化偏差 |t_2d(Nz=0)-t_1d(halfcv)|", val_1d, "s")

    for tag, rid in (("2d_Nz25", "n25"), ("2d_Nz50", "n50"),
                     ("2d_enddir", "enddir")):
        d = res[tag]
        add(f"W11_t_2d_{rid}", f"二维 {tag} t_dry", d["t_dry"], "s")
        add(f"W11_t_2d_{rid}_h", f"二维 {tag} t_dry", d["t_dry"] / 3600.0, "h")
        add(f"W11_dt_axial_{rid}", f"二维 {tag} 轴向效应 t2D-t1D",
            d["t_dry"] - r_fv["t_dry"], "s")
        dC_ax, dT_ax, dC_pr, dT_pr = mid_diffs(tag)
        add(f"W11_dC_mid_{rid}", f"二维 {tag} 中截面 max|dC| (vs 1D FV)",
            dC_ax, "kg/kg")
        add(f"W11_dT_mid_{rid}", f"二维 {tag} 中截面 max|dT| (vs 1D FV)",
            dT_ax, "K")
        add(f"W11_dC_prod_{rid}", f"二维 {tag} 中截面 max|dC| (vs 生产 FEM)",
            dC_pr, "kg/kg")
        add(f"W11_dT_prod_{rid}", f"二维 {tag} 中截面 max|dT| (vs 生产 FEM)",
            dT_pr, "K")
        add(f"W11_argmax_off_{rid}", f"二维 {tag} argmax 偏离中截面轴心采样数",
            d["argmax_off"], "-")
        add(f"W11_argmax_last_t_{rid}",
            f"二维 {tag} argmax 最后一次偏离时刻 (t≈0 并列噪声)",
            d["argmax_last_t"], "s")
    add("W11_dt_axial_consist", "轴向收敛 |dt(n50)-dt(n25)|",
        abs((res["2d_Nz50"]["t_dry"] - r_fv["t_dry"])
            - (res["2d_Nz25"]["t_dry"] - r_fv["t_dry"])), "s")
    add("W11_dt_scheme", "离散格式差 t_1dFV - t_prod",
        r_fv["t_dry"] - r_prod["t_dry"], "s")
    add("W11_dC_scheme", "离散格式差 max|dC| (FV vs FEM, 同 M)", dC_sch, "kg/kg")
    add("W11_dT_scheme", "离散格式差 max|dT| (FV vs FEM, 同 M)", dT_sch, "K")
    add("W11_dt_prod", "二维主算例 vs 生产基准 t2D(n50)-t_prod",
        d50["t_dry"] - r_prod["t_dry"], "s")

    add("W11_z_dip_cm", "t_dry 轴线轴向 dip 范围 (C<0.145)", z_dip, "cm")
    add("W11_C_end_axis", "t_dry 端面轴线角点 C(0,0)", float(Cz[0]), "kg/kg")
    add("W11_C_ax_1cm", "t_dry C(0, z=1cm)", float(np.interp(1.0, zcm, Cz)), "kg/kg")
    add("W11_C_ax_2cm", "t_dry C(0, z=2cm)", float(np.interp(2.0, zcm, Cz)), "kg/kg")
    add("W11_C_ax_5cm", "t_dry C(0, z=5cm)", float(np.interp(5.0, zcm, Cz)), "kg/kg")
    add("W11_C_mid_axis", "t_dry C(0, 中截面)", float(Cz[-1]), "kg/kg")
    add("W11_water_resid", "二维水量收支相对残差", resid, "-")
    add("W11_wloss_2d", "二维全程失水率", wloss_2d, "-")
    add("W11_wloss_1d", "一维全程失水率", wloss_1d, "-")
    add("W11_2d_steps", "二维主算例 (n50) 步数", d50["nsteps"], "-")
    add("W11_2d_nlu", "二维主算例 (n50) LU 分解次数", d50["nlu"], "-")

    dts = [abs(res[t]["t_dry"] - r_fv["t_dry"])
           for t in ("2d_Nz25", "2d_Nz50", "2d_enddir")]
    dcs = [mid_diffs(t)[0] for t in ("2d_Nz25", "2d_Nz50", "2d_enddir")]
    add("W11_max_dt_axial", "全部二维变体最大 |t2D-t1D|", max(dts), "s")
    add("W11_max_dt_axial_h", "全部二维变体最大 |t2D-t1D|", max(dts) / 3600.0, "h")
    add("W11_max_dC_mid", "全部二维变体中截面最大 |dC|", max(dcs), "kg/kg")

    path = os.path.join(OUTDIR, "registry_q3_2d.csv")
    write_registry(path, rows)
    print(f"\n注册表已写: {path} ({len(rows)} 行)")
    print(f"总用时 {time.time() - t_all:.1f} s")


def build_t_eval():
    """诊断时刻: 6 h 网格 + 快照 + argmax 诊断 + 水量收支复合网格."""
    snap = np.array([1800.0, 3600.0, 7200.0, 14400.0, 28800.0, 57600.0,
                     86400.0, 115200.0, 144000.0, 172800.0, 200000.0])
    t6 = 21600.0 * np.arange(1, 12)
    diag = np.union1d(snap, t6)
    argm = np.geomspace(600.0, T_MAX - 3600.0, 60)
    t_flux = np.concatenate([np.arange(60.0, 14400.0 + 1e-9, 60.0),
                             np.arange(15000.0, T_MAX, 600.0)])
    return np.unique(np.concatenate([diag, argm, t_flux]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if not (args.pilot or args.full):
        args.pilot = True
    if args.pilot:
        pilot()
    if args.full:
        full()


if __name__ == "__main__":
    main()
