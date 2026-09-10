"""
AUDIT SUPPORT MODULE (independent re-implementation).

Written from scratch for the adversarial audit of the user-proposed scheme.
Does NOT import anything from q1_solve.py except the attachment path convention;
the tridiagonal solver, the grid geometry and the coefficient assembly are all
re-derived here so that a bug in q1_solve.py cannot propagate into the audit.

Node-centred grid: r_i = i*dr, i=0..M, dr = R0/M.  Both r=0 and r=R are nodes.
Control volumes (per unit axial length, 2*pi factors kept explicitly):
    V_0   = pi*(dr/2)^2                     (half cell at the axis)
    V_i   = pi*((r+dr/2)^2 - (r-dr/2)^2)     (i=1..M-1)
    V_M   = pi*(R^2 - (R-dr/2)^2)            (half cell at the surface)
    A_{i+1/2} = 2*pi*(r_i + dr/2),  A_{i-1/2} = 2*pi*(r_i - dr/2)
"""

from __future__ import annotations

import os

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT1 = os.path.join(ROOT, "A题", "附件", "附件1.xlsx")

R0 = 0.02
RHO = 820.0
CP = 2600.0
KCOND = 0.36
HCONV = 25.0
HM = 8.0e-7
D0 = 7.0e-9
DEXP = 0.89
T0K = 28.0 + 273.15
C0 = 2.55
ALPHA = KCOND / (RHO * CP)


def Dfun(C):
    return D0 * np.exp(-DEXP / np.maximum(np.asarray(C, dtype=float), 1e-12))


def load_att1():
    """附件1: t[s], T_inf[degC], C_inf[kg/kg]. Read directly with openpyxl."""
    from openpyxl import load_workbook

    wb = load_workbook(ATT1, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
    wb.close()
    a = np.array([[float(v) for v in r[:3]] for r in rows])
    return a[:, 0], a[:, 1], a[:, 2]


def make_env(method="pchip"):
    t, TC, C = load_att1()
    from scipy.interpolate import CubicSpline, PchipInterpolator, interp1d

    if method == "pchip":
        fT = PchipInterpolator(t, TC + 273.15)
        fC = PchipInterpolator(t, C)
    elif method == "linear":
        fT = interp1d(t, TC + 273.15)
        fC = interp1d(t, C)
    elif method == "cubic":
        fT = CubicSpline(t, TC + 273.15)
        fC = CubicSpline(t, C)
    else:
        raise ValueError(method)
    return fT, fC


def const_env(T_C=50.0, C_inf=2.55):
    return (lambda tt: np.full_like(np.atleast_1d(float(tt)), T_C + 273.15),
            lambda tt: np.full_like(np.atleast_1d(float(tt)), C_inf))


def geom(M):
    dr = R0 / M
    r = np.arange(M + 1) * dr
    rf_p = np.minimum((np.arange(M + 1) + 0.5) * dr, R0)
    rf_m = np.maximum((np.arange(M + 1) - 0.5) * dr, 0.0)
    V = np.pi * (rf_p ** 2 - rf_m ** 2)
    A_m = 2 * np.pi * rf_m
    A_p = 2 * np.pi * rf_p
    return dr, r, V, A_m, A_p


def thomas(a, b, c, d):
    """Own tridiagonal solver (a[0], c[-1] ignored)."""
    n = len(d)
    cp = np.empty(n)
    dp = np.empty(n)
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = np.empty(n)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def temp_matrices(M):
    """(a,b,c) for the heat equation, both diagonal variants, no convection term.

    Tdiag='fixed' -> b_i = 1/dt + alpha*(A_m+A_p)/(dr V)   (conservative)
    Tdiag='user'  -> b_i = 1/dt + alpha*A_p/(dr V)         (user's written value)
    """
    dr, r, V, A_m, A_p = geom(M)
    return dr, r, V, A_m, A_p


def assemble(dr, V, A_m, A_p, M, dt, coef, diag, g=None):
    """Generic tridiagonal assembly for (1/r) d/dr( r * coef * d/dr ) + 1/dt."""
    a = np.zeros(M + 1)
    b = np.zeros(M + 1)
    c = np.zeros(M + 1)
    ii = np.arange(1, M)
    b[0] = 1.0 / dt + coef[0] * A_p[0] / (dr * V[0])
    c[0] = -coef[0] * A_p[0] / (dr * V[0])
    a[ii] = -coef[ii] * A_m[ii] / (dr * V[ii])
    if diag == "fixed":
        b[ii] = 1.0 / dt + coef[ii] * (A_m[ii] + A_p[ii]) / (dr * V[ii])
    elif diag == "user":
        b[ii] = 1.0 / dt + coef[ii] * A_p[ii] / (dr * V[ii])
    else:
        raise ValueError(diag)
    c[ii] = -coef[ii] * A_p[ii] / (dr * V[ii])
    a[M] = -coef[M] * A_m[M] / (dr * V[M])
    b[M] = 1.0 / dt + coef[M] * A_m[M] / (dr * V[M])
    if g is not None:
        b[M] += g
    return a, b, c


def run(M, dt, t_end, fT, fC, Tdiag="fixed", Cdiag="fixed", Dface="fixed",
        moisture=True, probes_t=None, probe_step=1, hard_stop=None,
        blow_tol=1e120, const_T=None):
    """Implicit-Euler solve.

    Dface='fixed' -> arithmetic mean of neighbouring nodal D (conservative)
    Dface='node'  -> D_i used on both faces of node i (user's structure)
    Returns dict with T, C, r, plus blow-up diagnostics.
    """
    dr, r, V, A_m, A_p = geom(M)
    n = M + 1
    nsteps = int(round(t_end / dt))

    g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * V[M])
    g_hm = 2 * np.pi * R0 * HM / V[M]

    T = np.full(n, T0K)
    C = np.full(n, C0)

    snaps_T = np.full((len(probes_t), n), np.nan) if probes_t else None
    snaps_C = np.full((len(probes_t), n), np.nan) if probes_t else None
    ptr = 0
    t_blow = None
    W_log = []

    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        for k in range(nsteps):
            tn1 = (k + 1) * dt
            Tinf = const_T if const_T is not None else float(np.atleast_1d(fT(tn1))[0])
            Cinf = float(np.atleast_1d(fC(tn1))[0])

            # ---------------- temperature ----------------
            a, b, c = assemble(dr, V, A_m, A_p, M, dt, np.full(n, ALPHA), Tdiag, g=g_h)
            d = T / dt
            d[M] += g_h * Tinf
            T = thomas(a, b, c, d)
            if not np.all(np.isfinite(T)):
                t_blow = tn1
                break
            if T.max() > blow_tol or np.abs(T).max() > blow_tol:
                t_blow = tn1
                break

            # ---------------- moisture ----------------
            if moisture:
                Dn = Dfun(C)
                if Dface == "fixed":
                    Df = 0.5 * (Dn[:-1] + Dn[1:])          # faces 1/2 ... M-1/2
                    Dm_f = np.concatenate([[Df[0]], Df])
                    Dp_f = np.concatenate([Df, [Df[-1]]])
                    coefC = Dm_f          # used for the inner face
                    coefC_p = Dp_f        # used for the outer face
                elif Dface == "node":
                    coefC = Dn
                    coefC_p = Dn
                else:
                    raise ValueError(Dface)
                a = np.zeros(n)
                b = np.zeros(n)
                c = np.zeros(n)
                ii = np.arange(1, M)
                b[0] = 1.0 / dt + coefC_p[0] * A_p[0] / (dr * V[0])
                c[0] = -coefC_p[0] * A_p[0] / (dr * V[0])
                a[ii] = -coefC[ii] * A_m[ii] / (dr * V[ii])
                c[ii] = -coefC_p[ii] * A_p[ii] / (dr * V[ii])
                if Cdiag == "fixed":
                    b[ii] = (1.0 / dt + coefC[ii] * A_m[ii] / (dr * V[ii])
                             + coefC_p[ii] * A_p[ii] / (dr * V[ii]))
                else:
                    b[ii] = 1.0 / dt + coefC_p[ii] * A_p[ii] / (dr * V[ii])
                a[M] = -coefC[M] * A_m[M] / (dr * V[M])
                b[M] = 1.0 / dt + coefC[M] * A_m[M] / (dr * V[M]) + g_hm
                d = C / dt
                d[M] += g_hm * Cinf
                C = thomas(a, b, c, d)
                W_log.append(float(np.sum(V * C)))
                if not np.all(np.isfinite(C)):
                    t_blow = tn1
                    break
                if np.abs(C).max() > blow_tol:
                    t_blow = tn1
                    break

            if probes_t is not None:
                while ptr < len(probes_t) and tn1 >= probes_t[ptr] - 1e-9:
                    snaps_T[ptr] = T
                    snaps_C[ptr] = C
                    ptr += 1

    return dict(r=r, T=T, C=C, ok=(t_blow is None), t_blow=t_blow,
                snaps_T=snaps_T, snaps_C=snaps_C, V=V, W_log=np.array(W_log),
                dr=dr, A_m=A_m, A_p=A_p)
