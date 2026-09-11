# -*- coding: utf-8 -*-
"""最小复现: 两个应当等价的组装方式为何给出不同结果."""
import sys
import numpy as np
from scipy.linalg import solve_banded
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

R = 0.02; T0 = 301.15; C0 = 2.55; TINF = 323.15; H = 25.0
rho = lambda C: 650.0 + 128.0 * C
cp = lambda C: 1450.0 + 2736.0 * C / (C + 1.0)
kcond = lambda C: 0.21 + 0.38 * C / (C + 1.0)
ALPHA = kcond(C0) / (rho(C0) * cp(C0)); K0 = kcond(C0)
RC = rho(C0) * cp(C0)


def assemble(M, dt, which):
    dr = R / M; r = np.arange(M + 1) * dr; n = M + 1
    if which == "fem":
        G = K0 * (r[:-1] + r[1:]) / (2 * dr)
        ML = np.zeros(n)
        ML[0] = dr * (2 * r[0] + r[1]) / 6.0
        ML[1:M] = dr * (r[:-2] + 2 * r[1:-1] + r[2:]) / 6.0
        ML[M] = dr * (r[M - 1] + 2 * r[M]) / 6.0
        ML *= RC
        d = ML / dt
        a = np.zeros(n); c = np.zeros(n)
        d[:-1] += G
        d[1:] += G
        c[:-1] = -G
        a[1:] = -G
        d[M] += H * R
        Mmat = ML
    else:
        rp = (np.arange(n) + 0.5) * dr; rp[M] = R
        rm = (np.arange(n) - 0.5) * dr; rm[0] = 0.0
        V = (rp ** 2 - rm ** 2) / 2.0
        Gp = K0 * rp / dr
        Gm = K0 * rm / dr
        d = RC * V / dt
        a = np.zeros(n); c = np.zeros(n)
        d[0] += Gp[0]; c[0] = -Gp[0]
        d[1:M] += Gm[1:M] + Gp[1:M]; a[1:M] = -Gm[1:M]; c[1:M] = -Gp[1:M]
        d[M] += Gm[M] + H * R
        a[M] = -Gm[M]
        Mmat = RC * V
    return r, a, c, d, Mmat


M, dt = 100, 0.05
for which in ("fem", "fv"):
    r, a, c, d, Mmat = assemble(M, dt, which)
    print(f"[{which}]  M[0]={Mmat[0]:.6e}  M[M]={Mmat[M]:.6e}  M[1]={Mmat[1]:.6e}  "
          f"M[2]={Mmat[2]:.6e}  d[0]={d[0]:.6e}")
    print(f"       a[1]={a[1]:.6e}  c[0]={c[0]:.6e}  c[1]={c[1]:.6e}  d[M]={d[M]:.6e}")

r1, a1, c1, d1, _ = assemble(M, dt, "fem")
r2, a2, c2, d2, _ = assemble(M, dt, "fv")
print("\n逐项差: max|dM|=", np.max(np.abs(d1 - d2)), " max|da|=", np.max(np.abs(a1 - a2)),
      " max|dc|=", np.max(np.abs(c1 - c2)), " max|dd|=", np.max(np.abs(d1 - d2)))
print("d 差最大的位置:", np.argmax(np.abs(d1 - d2)), "M=", M)
print("d1[0], d2[0] =", d1[0], d2[0])
print("d1[M], d2[M] =", d1[M], d2[M])
