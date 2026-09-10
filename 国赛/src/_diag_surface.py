"""Diagnostic: why does lead_cn differ from exact_cn by 6 orders of magnitude?
Compares the Python variants against the Wolfram-validated CN configuration
(W2: Dd=2*alpha*dt/dr^2, G=2*alpha*h*dt/(k*dr), a=-theta*Dd, b=1+theta*(Dd+G))."""
import numpy as np
from scipy.linalg import solve_banded, eig_banded
from scipy.special import j0, j1
from scipy.optimize import brentq

RHO, CP, K = 820.0, 2600.0, 0.36
H, T0K = 25.0, 301.15
R0, ALPHA = 0.02, K / (RHO * CP)
BI = H * R0 / K
TINF = 323.15


def eigen(Bi, n):
    f = lambda x: x * j1(x) - Bi * j0(x)
    g = np.linspace(1e-8, 4.0 * n + 40.0, 300 * (n + 20))
    v = f(g)
    xs = []
    for k in range(len(g) - 1):
        if v[k] * v[k + 1] < 0:
            xs.append(brentq(f, g[k], g[k + 1], xtol=1e-15, rtol=8.9e-16))
        if len(xs) >= n:
            break
    x = np.array(xs)
    return x, 2 * j1(x) / (x * (j0(x) ** 2 + j1(x) ** 2))


def analytic(M, t):
    r = np.arange(M + 1) * (R0 / M)
    x, c = eigen(BI, 400)
    Fo = ALPHA * t / R0 ** 2
    return r, TINF + (T0K - TINF) * np.sum(
        c[None, :] * j0(np.outer(r / R0, x)) * np.exp(-x ** 2 * Fo), axis=1)


def mat(M, dt, theta, variant):
    dr = R0 / M
    af = 2 * np.pi * (np.arange(M) + 0.5) * dr
    V = np.empty(M + 1)
    V[0] = np.pi * (dr / 2) ** 2
    V[1:M] = 2 * np.pi * np.arange(1, M) * dr ** 2
    V[M] = np.pi * (R0 * dr - dr ** 2 / 4.0)
    ii = np.arange(1, M)
    f_int = af[1:M] / (dr * V[1:M])
    f_lo = af[0:M - 1] / (dr * V[1:M])
    fM_ex = af[M - 1] / (dr * V[M])
    fM_ld = 2.0 / dr ** 2
    A_s = 2 * np.pi * R0
    g_ex = ALPHA * H * A_s / (K * V[M])
    g_ld = ALPHA * 2 * H / (K * dr)
    Kd = 4 * ALPHA * dt / dr ** 2
    a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
    b[0] = 1 + theta * Kd; c[0] = -theta * Kd
    b[1:M] = 1 + theta * ALPHA * dt * (f_int + f_lo)
    a[1:M] = -theta * ALPHA * dt * f_lo
    c[1:M] = -theta * ALPHA * dt * f_int
    if variant == "lead_cn":
        afM, Gdt = fM_ld, g_ex * dt
    elif variant == "exact_cn":
        afM, Gdt = fM_ex, g_ex * dt
    elif variant == "wolfram_v2":
        afM, Gdt = fM_ld, g_ld * dt
    a[M] = -theta * ALPHA * dt * afM
    b[M] = 1 + theta * (ALPHA * dt * afM + Gdt)
    return dr, a, b, c, (f_int, f_lo, Kd, afM, Gdt, dt, theta, variant)


def run(M, dt, theta, variant, tend):
    dr, a, b, c, geo = mat(M, dt, theta, variant)
    f_int, f_lo, Kd, afM, Gdt, ddt, th, var = geo
    T = np.full(M + 1, T0K)
    for s in range(1, int(round(tend / dt)) + 1):
        d = np.empty(M + 1)
        d[0] = (1 - (1 - th) * Kd) * T[0] + (1 - th) * Kd * T[1]
        d[1:M] = ((1 - (1 - th) * ALPHA * ddt * (f_int + f_lo)) * T[1:M]
                  + (1 - th) * ALPHA * ddt * f_lo * T[0:M - 1]
                  + (1 - th) * ALPHA * ddt * f_int * T[2:M + 1])
        d[M] = ((1 - (1 - th) * (ALPHA * ddt * afM + Gdt)) * T[M]
                + (1 - th) * ALPHA * ddt * afM * T[M - 1] + Gdt * TINF)
        ab = np.zeros((3, M + 1)); ab[0, 1:] = c[:-1]; ab[1, :] = b; ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, d)
    return dr, T


print("dt=0.5, t=300, Tinf=50C")
print("variant      M     maxerr[K]      T(0)        T(R)")
for var in ("lead_cn", "exact_cn", "wolfram_v2"):
    for M in (50, 100, 200):
        r, T = run(M, 0.5, 0.5, var, 300.0)
        _, Ta = analytic(M, 300.0)
        print("%-12s %4d   %12.6e  %10.6f  %10.6f" % (var, M, np.max(np.abs(T - Ta)), T[0], T[-1]))
    print()

print("kappa_M = A_{M-1/2}/(dr*V_M):  exact vs 2/dr^2")
for M in (50, 100, 200, 400):
    dr = R0 / M
    af = 2 * np.pi * (M - 0.5) * dr
    V = np.pi * (R0 * dr - dr ** 2 / 4.0)
    fM_ex = af / (dr * V)
    print("  M=%4d  exact=%.10e  2/dr^2=%.10e  ratio=%.10f"
          % (M, fM_ex, 2 / dr ** 2, (2 / dr ** 2) / fM_ex))

print()
print("Gdt: exact(=A_s*h/(rho*cp*V_M)) vs leading(2*alpha*h*dt/(k*dr))")
for M in (50, 100, 200):
    dr = R0 / M
    V = np.pi * (R0 * dr - dr ** 2 / 4.0)
    gex = ALPHA * H * 2 * np.pi * R0 / (K * V) * 0.5
    gld = ALPHA * 2 * H / (K * dr) * 0.5
    print("  M=%4d  exact=%.8f  leading=%.8f  ratio=%.8f" % (M, gex, gld, gld / gex))
