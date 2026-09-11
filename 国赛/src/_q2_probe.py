# -*- coding: utf-8 -*-
"""临时探针 (v2): 核查 problem2.md 模型与关键数, 并测空间收敛阶."""

import os
import sys

import numpy as np
from scipy.linalg import solve_banded
from scipy.special import j0, j1
from scipy.optimize import brentq

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

R = 0.02
T0 = 301.15
C0 = 2.55
TINF = 323.15

rho = lambda C: 650.0 + 128.0 * C
cp = lambda C: 1450.0 + 2736.0 * C / (C + 1.0)
kcond = lambda C: 0.21 + 0.38 * C / (C + 1.0)
Dfun = lambda C, T: 2.4e-3 * np.exp(-0.45 / C) * np.exp(-3850.0 / T)

print("=" * 96)
print("P4  r=0 节点的等效扩散系数 (集中质量 FEM vs 节点式 FV)")
print("=" * 96)
for M in (100, 200, 400, 800):
    dr = R / M
    k0 = kcond(C0)
    rc = rho(C0) * cp(C0)
    # FEM: 集中质量 ML_00 = dr^2/6 (已约去 rho cp), 刚度 G_1/2 = k*dr/2/dr = k/2
    #      方程 (rho cp dr^2/6) dT0/dt = -(k/2)(T0-T1)  ->  dT0/dt = 3 alpha (T1-T0)/dr^2
    sexp = 3.0 * k0 / (rc * dr * dr)
    # FV : V0 = dr^2/8 (per 2pi), A_1/2 = dr/2 (per 2pi)
    #      (rho cp dr^2/8) dT0/dt = (dr/2) k (T1-T0)/dr = (k/2)(T1-T0)
    sfv = 4.0 * k0 / (rc * dr * dr)
    print(f"  M={M:5d}  dT0/dt = {sexp/(k0/(rc*dr*dr)):.4f} * (k/(rho cp dr^2))(T1-T0)   "
          f"FV = {sfv/(k0/(rc*dr*dr)):.4f}   比值 FEM/FV = {sexp/sfv:.6f}")


_ROOT_CACHE = {}


def bessel_roots(Bi, n_modes=200):
    key = (round(Bi, 12), n_modes)
    if key in _ROOT_CACHE:
        return _ROOT_CACHE[key]
    f = lambda lam: lam * j1(lam) - Bi * j0(lam)
    grid = np.linspace(1e-8, 400.0, 200001)
    v = f(grid)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    roots = [brentq(f, grid[i], grid[i + 1], xtol=1e-15) for i in idx[:n_modes]]
    lam = np.array(roots)
    Cn = 2 * j1(lam) / (lam * (j0(lam) ** 2 + j1(lam) ** 2))
    _ROOT_CACHE[key] = (lam, Cn)
    return lam, Cn


def bessel_T(r, t, alpha, k, h, Tinf, T0, n_modes=200):
    lam, Cn = bessel_roots(h * R / k, n_modes)
    rr = np.atleast_1d(r) / R
    th = (Cn[:, None] * np.exp(-(lam ** 2)[:, None] * alpha * t / R ** 2)) * j0(
        lam[:, None] * rr[None, :])
    return Tinf + (T0 - Tinf) * th.sum(axis=0)


# 检验级数自身: t=0 应为 1
_lam_chk = None
print("\nP0  级数自检: t=0 时 (T-Tinf)/(T0-Tinf) 在 r=0, R/2, R 上应为 1")
th0 = bessel_T(np.array([0.0, R / 2, R]), 0.0, 1e-7, 1.0, 25.0, 0.0, 1.0)
print(f"    {th0}")


def fem_lumped(M, dt, t_end, alpha, k, h, Tinf, T0):
    """线性单元 + 集中质量(行和) + 后向 Euler, 常数系数. 单位轴长, 已约 2pi."""
    dr = R / M
    r = np.arange(M + 1) * dr
    n = M + 1
    rc = k / alpha
    G = k * (r[:-1] + r[1:]) / (2 * dr)          # G[i] = k r_{i+1/2}/dr, i=0..M-1
    ML = np.zeros(n)
    ML[0] = dr * (2 * r[0] + r[1]) / 6.0
    ML[1:M] = dr * (r[:-2] + 4 * r[1:-1] + r[2:]) / 6.0
    ML[M] = dr * (r[M - 1] + 2 * r[M]) / 6.0
    ML *= rc

    d = ML / dt
    a = np.zeros(n); c = np.zeros(n)
    d[:-1] += G
    d[1:] += G
    c[:-1] = -G
    a[1:] = -G
    d[M] += h * R

    T = np.full(n, T0)
    for _ in range(int(round(t_end / dt))):
        rhs = ML / dt * T
        rhs[M] += h * R * Tinf
        ab = np.zeros((3, n))
        ab[0, 1:] = c[:-1]
        ab[1, :] = d
        ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, rhs)
    return r, T


def fv_halfcv(M, dt, t_end, alpha, k, h, Tinf, T0):
    """节点式 FV + 精确半控制体 + 后向 Euler (问题一的方案), 常数系数."""
    dr = R / M
    r = np.arange(M + 1) * dr
    n = M + 1
    rc = k / alpha
    rp = (np.arange(n) + 0.5) * dr; rp[M] = R
    rm = (np.arange(n) - 0.5) * dr; rm[0] = 0.0
    V = (rp ** 2 - rm ** 2) / 2.0        # per 2pi
    Ap = rp; Am = rm
    Gp = k * Ap / dr                     # 面系数 k r_{i+1/2}/dr
    Gm = k * Am / dr
    d = rc * V / dt
    a = np.zeros(n); c = np.zeros(n)
    d[0] += Gp[0]; c[0] = -Gp[0]
    d[1:M] += Gm[1:M] + Gp[1:M]; a[1:M] = -Gm[1:M]; c[1:M] = -Gp[1:M]
    d[M] += Gm[M] + h * R
    a[M] = -Gm[M]
    T = np.full(n, T0)
    for _ in range(int(round(t_end / dt))):
        rhs = rc * V / dt * T
        rhs[M] += h * R * Tinf
        ab = np.zeros((3, n))
        ab[0, 1:] = c[:-1]
        ab[1, :] = d
        ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, rhs)
    return r, T


alpha0 = kcond(C0) / (rho(C0) * cp(C0))
k0 = kcond(C0)
print("\n" + "=" * 96)
print("P5  常数系数 Robin 圆柱 (T0=28C -> Tinf=50C, t=600 s): 与 Bessel 解析解对比")
print("=" * 96)
H_CONV = 25.0
h = H_CONV
print(f"  alpha={alpha0:.6e} m2/s, k={k0:.6f}, h={h}, Fo(600s) = {alpha0*600/R**2:.4f}")
print(f"  {'M':>6} {'FEM max|dT|':>14} {'FEM@r=0':>12} {'FV max|dT|':>14} {'FV@r=0':>12}")
prev_f = prev_v = None
for M in (50, 100, 200, 400, 800, 1600, 3200):
    r, Tf = fem_lumped(M, 5e-2, 600.0, alpha0, k0, h, TINF, T0)
    _, Tv = fv_halfcv(M, 5e-2, 600.0, alpha0, k0, h, TINF, T0)
    Te = bessel_T(r, 600.0, alpha0, k0, h, TINF, T0)
    ef = np.abs(Tf - Te); ev = np.abs(Tv - Te)
    ratio_f = "" if prev_f is None else f"  FEM ratio={prev_f/ef.max():.3f}"
    ratio_v = "" if prev_v is None else f"  FV ratio={prev_v/ev.max():.3f}"
    irf = r[ef.argmax()] * 100
    print(f"  {M:6d} {ef.max():14.4e} {ef[0]:12.4e} {ev.max():14.4e} {ev[0]:12.4e}"
          f"   | 最坏点 r={irf:.4f} cm{ratio_f}{ratio_v}")
    prev_f, prev_v = ef.max(), ev.max()
