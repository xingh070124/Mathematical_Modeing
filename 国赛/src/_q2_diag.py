# -*- coding: utf-8 -*-
"""诊断: FEM(集中质量) 在 r=0 附近为何不收敛."""
import os, sys
import numpy as np
from scipy.linalg import solve_banded
from scipy.special import j0, j1
from scipy.optimize import brentq
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

R = 0.02; T0 = 301.15; C0 = 2.55; TINF = 323.15; H = 25.0
rho = lambda C: 650.0 + 128.0 * C
cp = lambda C: 1450.0 + 2736.0 * C / (C + 1.0)
kcond = lambda C: 0.21 + 0.38 * C / (C + 1.0)
ALPHA = kcond(C0) / (rho(C0) * cp(C0)); K0 = kcond(C0)

_C = {}
def roots(Bi, nm=200):
    if Bi in _C: return _C[Bi]
    f = lambda l: l * j1(l) - Bi * j0(l)
    g = np.linspace(1e-8, 400.0, 200001); v = f(g)
    idx = np.where(np.sign(v[:-1]) != np.sign(v[1:]))[0]
    lam = np.array([brentq(f, g[i], g[i+1], xtol=1e-15) for i in idx[:nm]])
    Cn = 2 * j1(lam) / (lam * (j0(lam) ** 2 + j1(lam) ** 2))
    _C[Bi] = (lam, Cn); return _C[Bi]

def exact(r, t):
    lam, Cn = roots(H * R / K0)
    rr = np.atleast_1d(r) / R
    th = (Cn[:, None] * np.exp(-(lam**2)[:, None] * ALPHA * t / R**2)) * j0(lam[:, None] * rr[None, :])
    return TINF + (T0 - TINF) * th.sum(0)

def solve(M, dt, t_end, node0="fem"):
    dr = R / M; r = np.arange(M + 1) * dr; n = M + 1; rc = K0 / ALPHA
    G = K0 * (r[:-1] + r[1:]) / (2 * dr)
    ML = np.zeros(n)
    ML[0] = dr * (2 * r[0] + r[1]) / 6.0
    ML[1:M] = dr * (r[:-2] + 4 * r[1:-1] + r[2:]) / 6.0
    ML[M] = dr * (r[M-1] + 2 * r[M]) / 6.0
    if node0 == "fv":
        ML[0] = dr * dr / 8.0
    ML *= rc
    d = ML / dt; a = np.zeros(n); c = np.zeros(n)
    d[:-1] += G; d[1:] += G
    c[:-1] = -G; a[1:] = -G
    if node0 == "fv":      # 节点0 刚度: k r_{1/2}/dr = k*(dr/2)/dr = k/2 -> G[0] 已是 k/2
        pass
    d[M] += H * R
    T = np.full(n, T0)
    for _ in range(int(round(t_end / dt))):
        rhs = ML / dt * T; rhs[M] += H * R * TINF
        ab = np.zeros((3, n)); ab[0, 1:] = c[:-1]; ab[1, :] = d; ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, rhs)
    return r, T

print("=" * 100)
print("D1  轮廓对比 t=600 s, M=400, dt=0.002 s")
M, tE = 400, 600.0
r, Tf = solve(M, 2e-3, tE)
Te = exact(r, tE)
print(f"  {'i':>4} {'r/cm':>8} {'FEM':>12} {'exact':>12} {'diff':>12}")
for i in list(range(0, 12)) + [50, 100, 200, 300, 400]:
    print(f"  {i:4d} {r[i]*100:8.4f} {Tf[i]:12.6f} {Te[i]:12.6f} {Tf[i]-Te[i]:12.3e}")

print("\n" + "=" * 100)
print("D2  空间收敛 (dt=0.02 s, t=600 s), 两种节点0处理")
prev = {}
for M in (50, 100, 200, 400, 800, 1600):
    for tag in ("fem", "fv"):
        r, T = solve(M, 2e-2, tE, node0=tag)
        e = np.abs(T - exact(r, tE))
        key = tag
        rat = "" if key not in prev else f" ratio={prev[key]/e.max():.4f}"
        prev[key] = e.max()
        print(f"  M={M:5d} node0={tag:>3}  max|dT|={e.max():.4e}  中心={e[0]:.4e}  "
              f"r=0.5cm 处={e[np.argmin(abs(r-0.005))]:.4e}{rat}")

print("\n" + "=" * 100)
print("D3  时间收敛 (M=400, t=600 s)")
for dt in (0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002):
    r, T = solve(M, dt, tE)
    e = np.abs(T - exact(r, tE))
    print(f"  dt={dt:6.4f}  max|dT|={e.max():.4e}  中心={e[0]:.4e}")
