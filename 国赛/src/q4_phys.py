# -*- coding: utf-8 -*-
"""
q4_phys.py -- 问题四的**物理坐标参考解** (检验物质坐标结论的独立路线).

动机 (直接回应审计意见 F2/F3/F7):
    `q4_verify.py` 的 `make_rhs_fv` 虽然换了离散格式 (单元中心 vs 节点), 但它
    **仍写在物质坐标 xi 里**, 并**直接施加** beta R^2 = beta_0 R_0^2。因此它只
    能验证"同一方程的第二种离散", **不能**验证物质坐标变换本身, 也不能验证
    "水分方程不残留对流露项"这一核心结论。

本模块走**完全不同的路线**: 物理坐标 r、固定的物理网格、显式对流项, 求解域
随 R(t) 缩小, 节点逐个退出。控制方程由坐标恒等式给出 (仿射收缩):

    (dC/dt)|_r + v(r,t) (dC/dr) = (1/r) d/dr ( r D(C,T) dC/dr ),  v = r Rdot/R
    (dT/dt)|_r + v(r,t) (dT/dr) = (1/(rho cp r)) d/dr ( r k dT/dr )

**注意**: 本式**不含** +2(Rdot/R)C 一类的源项。均匀 C 时对流项含 dC/dr=0 而
扩散项亦为零, C 不随时间变化, 与物理一致; 若带 +2(Rdot/R)C 源项则均匀场会
凭空变化。审计意见 F3 指出 `problem4.md` §5.5 原稿的该项有误, 已按此更正。

本模块与主模型共享物性、环境与边界条件, 但**几何、坐标、状态量排布、对流处理
全部不同**, 故其 t_dry 是检验物质坐标结论的独立证据。

入口:
    python src/q4_phys.py            跑 M=100/200/400/800 并给出收敛序列
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

from q4_solve import (APP, Q4Radius, props_p, Dfun_p, CSTAR,   # noqa: E402
                      T_MAX, PROD_ATOL_T, PROD_ATOL_C)
from q3_solve import Q3Env                                     # noqa: E402
from q1_solve import load_attachment1                          # noqa: E402
from q2_solve import (H_CONV, HM, R as R0, T0K, C0,            # noqa: E402
                      HEVAP_28, HEVAP_SLOPE, HEVAP_TREF)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "outputs")

# 主模型 (物质坐标) 生产解, 供对照
MAIN_TDRY = 183906.7128


def make_rhs_phys(M, env, rad, params, hc=H_CONV, hm=HM):
    """物理坐标 + 固定网格 + 显式迎风对流.

    网格 r_i = i*h, h = R0/M, i = 0..M (固定)。
    节点 i 仅当 r_i <= R(t) 时活跃; R(t) 降到 r_i 以下后该节点被冻结 (导数为 0)。
    表面节点取"活跃节点中的最后一个", 其外侧面用 Robin 条件。
    """
    h = R0 / M
    r = np.arange(M + 1) * h
    rh = r + 0.5 * h                     # 外侧半格位置 (r_{i+1/2})
    rl = r - 0.5 * h                     # 内侧半格位置 (r_{i-1/2})
    rl[0] = 0.0
    hc = float(hc)
    hm = float(hm)

    def rhs(t, U):
        T = U[:M + 1]
        C = U[M + 1:]
        Rc = float(rad.R(t))
        Rd = float(rad.Rdot(t))
        Tinf, Cinf = env.T(t), env.C(t)
        rho, cp, k, _, _, _ = props_p(C, params)
        rcp = rho * cp
        Dv = Dfun_p(C, T, params)
        # 活跃节点数: r_i <= R(t), 至少 2 个 (轴心 + 一个内部)
        N = int(np.searchsorted(r, Rc, side="right")) - 1
        N = max(2, min(N, M))
        dT = np.zeros(M + 1)
        dC = np.zeros(M + 1)

        # ---- 轴心 i=0: 轴对称扩散, 对流速度 v(0)=0 ----
        Df = 0.5 * (Dv[0] + Dv[1])
        kf = 0.5 * (k[0] + k[1])
        dC[0] = 4.0 * Df * (C[1] - C[0]) / h ** 2
        dT[0] = 4.0 * kf * (T[1] - T[0]) / (rcp[0] * h ** 2)

        # ---- 内部节点 1..N-1 ----
        for i in range(1, N):
            vi = r[i] * Rd / Rc
            Dm = 0.5 * (Dv[i - 1] + Dv[i])
            Dp_ = 0.5 * (Dv[i] + Dv[i + 1])
            km = 0.5 * (k[i - 1] + k[i])
            kp_ = 0.5 * (k[i] + k[i + 1])
            # (1/r) d/dr ( r D dC/dr ) 的中心差分
            dC[i] = (rh[i] * Dp_ * (C[i + 1] - C[i]) / h
                     - rl[i] * Dm * (C[i] - C[i - 1]) / h) / (r[i] * h)
            dT[i] = (rh[i] * kp_ * (T[i + 1] - T[i]) / h
                     - rl[i] * km * (T[i] - T[i - 1]) / h) / (r[i] * h * rcp[i])
            # 对流: v = r Rd/R <= 0 (收缩), 迎风取上游 i+1
            dC[i] -= vi * (C[i + 1] - C[i]) / h
            dT[i] -= vi * (T[i + 1] - T[i]) / h

        # ---- 表面节点 i=N: 内侧面扩散 + 外侧面 Robin; 对流取零梯度 ----
        i = N
        Dm = 0.5 * (Dv[i - 1] + Dv[i])
        km = 0.5 * (k[i - 1] + k[i])
        Lv = HEVAP_28 + HEVAP_SLOPE * (T[i] - HEVAP_TREF)
        # 水通量与热通量 (每单位面积, 沿 +r 方向)
        Jw_in = -Dm * (C[i] - C[i - 1]) / h
        Jh_in = -km * (T[i] - T[i - 1]) / h
        Jw_out = hm * (C[i] - Cinf)
        Jh_out = hc * (T[i] - Tinf) + Lv * hm * (C[i] - Cinf)
        # 控制体 [r_{i-1/2}, R], 单位轴向长度的体积/2pi = (R^2 - rl_i^2)/2
        V0 = 0.5 * (Rc ** 2 - rl[i] ** 2)
        V0 = max(V0, 1e-12)
        dC[i] = -(rl[i] * Jw_in * 1.0) / (Rc * V0) + (Rc * Jw_out) / (Rc * V0)
        dT[i] = (-(rl[i] * Jh_in) + Rc * Jh_out) / (Rc * V0 * rcp[i])

        # ---- 域外节点冻结 ----
        dC[N + 1:] = 0.0
        dT[N + 1:] = 0.0
        return np.concatenate([dT, dC])

    return rhs, r


def solve_phys(M=200, rtol=1e-8, atol_C=1e-9, atol_T=1e-6, t_max=T_MAX,
               hc=None, hm=None, params=None):
    """物理坐标参考解, 返回 t_dry 与诊断量."""
    t1, T1, C1 = load_attachment1()
    env = Q3Env(t1, T1, C1)
    rad = Q4Radius()
    kw = {}
    if hc is not None:
        kw["hc"] = hc
    if hm is not None:
        kw["hm"] = hm
    rhs, r = make_rhs_phys(M, env, rad, params or APP["app4"], **kw)
    n = M + 1
    U0 = np.concatenate([np.full(n, T0K), np.full(n, C0)])
    at = np.concatenate([np.full(n, atol_T), np.full(n, atol_C)])

    def ev(t, U, _n=n):
        Rc = float(rad.R(t))
        act = r <= Rc * (1.0 + 1e-12)
        return U[_n:][act].max() - CSTAR
    ev.terminal = True
    ev.direction = -1.0
    t0 = time.time()
    sol = solve_ivp(rhs, (0.0, float(t_max)), U0, method="BDF", rtol=rtol,
                    atol=at, max_step=1800.0, events=ev,
                    jac_sparsity=sp.diags([np.ones(2 * n - 1)] * 2, [-1, 1],
                                          format="csr") + sp.eye(2 * n, format="csr"))
    ok = (sol.status == 1 and len(sol.t_events[0]) > 0)
    return dict(t_dry=float(sol.t_events[0][0]) if ok else float("nan"),
                ok=ok, nsteps=len(sol.t) - 1, wall=time.time() - t0, M=M, r=r)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--M", type=int, nargs="*", default=[100, 200, 400, 800])
    a = ap.parse_args()
    print("=" * 78)
    print("问题四: 物理坐标参考解 (固定物理网格 + 显式迎风对流 + 域随 R(t) 缩小)")
    print("=" * 78)
    print(f"对照: 主模型 (物质坐标) M=200 -> {MAIN_TDRY:.4f} s = "
          f"{MAIN_TDRY/3600:.5f} h")
    print()
    prev = None
    for M in a.M:
        res = solve_phys(M=M)
        if not res["ok"]:
            print(f"  M={M:4d}  未触发终止事件")
            continue
        td = res["t_dry"]
        trend = "" if prev is None else \
            f"  相邻差 {abs(td-prev)/3600:.4f} h ({abs(td-prev):.1f} s)"
        print(f"  M={M:4d}  t_dry = {td:14.4f} s = {td/3600:9.5f} h"
              f"   相对主模型 {(td-MAIN_TDRY)/3600:+.4f} h{trend}"
              f"   (nsteps={res['nsteps']}, wall={res['wall']:.1f}s)")
        prev = td


if __name__ == "__main__":
    main()
