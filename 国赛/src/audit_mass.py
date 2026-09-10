"""
AUDIT SCRIPT 4 -- Claims C10 (discrete mass balance, nodal D) and C11 (practical
impact of nodal D on the Q1 output).

Self-contained: own grid, own assembly, own mass-balance accounting.

The discrete identity used is exact, not approximate.  Summing
    V_i (C_i^{n+1}-C_i^n)/dt = D_i A_p[i](C_{i+1}-C_i)/dr - D_i A_m[i](C_i-C_{i-1})/dr
over i (nodal-D scheme) telescopes into
    (W^{n+1}-W^n)/dt = -2*pi*R*h_m*(C_M - C_inf)  +  MISMATCH
    MISMATCH = sum_{j=0}^{M-1} (D_j - D_{j+1}) A_{j+1/2} (C_{j+1}-C_j)/dr
so MISMATCH is computed twice: (i) as W_change - surface flux (the audit
quantity), and (ii) face by face (the mechanism).

Run:  python src/audit_mass.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
from scipy.linalg import solve_banded

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import (ALPHA, C0, CP, Dfun, HCONV, HM, RHO, R0, T0K, geom,  # noqa: E402
                          make_env, thomas)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))


def banded(a, b, c, d):
    n = len(d)
    ab = np.zeros((3, n))
    ab[0, 1:] = c[:-1]
    ab[1, :] = b
    ab[2, :-1] = a[1:]
    return solve_banded((1, 1), ab, d)


def mass_run(M, dt, t_end, fT, fC, Dface="node", Cdiag="fixed", use_banded=True,
             probes_t=None, r_probe=None):
    dr, r, V, A_m, A_p = geom(M)
    n = M + 1
    nsteps = int(round(t_end / dt))
    g_h = 2 * np.pi * R0 * HCONV / (RHO * CP * V[M])
    g_hm = 2 * np.pi * R0 * HM / V[M]
    sol = banded if use_banded else (lambda a, b, c, d: thomas(a, b, c, d))

    T = np.full(n, T0K)
    C = np.full(n, C0)
    ii = np.arange(1, M)
    W0 = float(np.sum(V * C))
    Ws = [W0]
    acc_surf = 0.0
    acc_mismatch = 0.0
    per_face = np.zeros(M)          # time-integrated mismatch per face
    snaps = None
    if probes_t is not None:
        snaps = (np.full((len(probes_t), n), np.nan), np.full((len(probes_t), n), np.nan))
        ptr = 0

    for k in range(nsteps):
        tn1 = (k + 1) * dt
        Tinf = float(np.atleast_1d(fT(tn1))[0])
        Cinf = float(np.atleast_1d(fC(tn1))[0])
        # ---- temperature (conservative, fixed diagonal) ----
        a, b, c = np.zeros(n), np.zeros(n), np.zeros(n)
        b[0] = 1 / dt + ALPHA * A_p[0] / (dr * V[0])
        c[0] = -ALPHA * A_p[0] / (dr * V[0])
        a[ii] = -ALPHA * A_m[ii] / (dr * V[ii])
        b[ii] = 1 / dt + ALPHA * (A_m[ii] + A_p[ii]) / (dr * V[ii])
        c[ii] = -ALPHA * A_p[ii] / (dr * V[ii])
        a[M] = -ALPHA * A_m[M] / (dr * V[M])
        b[M] = 1 / dt + ALPHA * A_m[M] / (dr * V[M]) + g_h
        d = T / dt
        d[M] += g_h * Tinf
        T = sol(a, b, c, d)
        # ---- moisture ----
        Dn = Dfun(C)
        if Dface == "face":
            Df = 0.5 * (Dn[:-1] + Dn[1:])
            Dm_f = np.concatenate([[Df[0]], Df])
            Dp_f = np.concatenate([Df, [Df[-1]]])
        else:
            Dm_f = Dn.copy()
            Dp_f = Dn.copy()
        a, b, c = np.zeros(n), np.zeros(n), np.zeros(n)
        b[0] = 1 / dt + Dp_f[0] * A_p[0] / (dr * V[0])
        c[0] = -Dp_f[0] * A_p[0] / (dr * V[0])
        a[ii] = -Dm_f[ii] * A_m[ii] / (dr * V[ii])
        c[ii] = -Dp_f[ii] * A_p[ii] / (dr * V[ii])
        if Cdiag == "fixed":
            b[ii] = 1 / dt + Dm_f[ii] * A_m[ii] / (dr * V[ii]) + Dp_f[ii] * A_p[ii] / (dr * V[ii])
        else:
            b[ii] = 1 / dt + Dp_f[ii] * A_p[ii] / (dr * V[ii])
        a[M] = -Dm_f[M] * A_m[M] / (dr * V[M])
        b[M] = 1 / dt + Dm_f[M] * A_m[M] / (dr * V[M]) + g_hm
        d = C / dt
        d[M] += g_hm * Cinf
        C = sol(a, b, c, d)

        # ---- exact accounting at the new time level ----
        Csurf = C[M]
        acc_surf += 2 * np.pi * R0 * HM * (Cinf - Csurf) * dt
        mism = (Dn[:-1] - Dn[1:]) * A_p[:-1] * (C[1:] - C[:-1]) / dr
        acc_mismatch += float(np.sum(mism)) * dt
        per_face += mism * dt
        Ws.append(float(np.sum(V * C)))
        if probes_t is not None:
            while ptr < len(probes_t) and tn1 >= probes_t[ptr] - 1e-9:
                snaps[0][ptr] = T
                snaps[1][ptr] = C
                ptr += 1

    res = (Ws[-1] - W0) - acc_surf
    out = dict(r=r, V=V, dr=dr, T=T, C=C, W0=W0, W1=Ws[-1], acc_surf=acc_surf,
               res=res, acc_mismatch=acc_mismatch, per_face=per_face,
               ident_gap=(Ws[-1] - W0) - (acc_surf + acc_mismatch), Ws=np.array(Ws))
    if snaps is not None:
        out["snaps_T"], out["snaps_C"] = snaps
    return out


def c10(fT, fC):
    hr("C10. Discrete water balance: nodal D vs face-averaged D")
    t_end = 1800.0
    print("  identity check (own implementation, M=200, dt=0.25):")
    for sch in ("face", "node"):
        o = mass_run(200, 0.25, t_end, fT, fC, Dface=sch)
        print(f"    [{sch}] dW = {o['W1']-o['W0']:.10e} ; surface flux integral = {o['acc_surf']:.10e}")
        print(f"           residual (dW - flux) = {o['res']:.6e}   "
              f"face-by-face mismatch = {o['acc_mismatch']:.6e}   "
              f"identity gap = {o['ident_gap']:.3e}")
    print()
    print(f"  {'M':>6} {'dr[mm]':>8} {'scheme':>6} {'dW':>17} {'surf flux':>17} "
          f"{'residual':>14} {'|res|/|flux|':>13}")
    for M in (50, 100, 200, 400, 800, 1600):
        for sch in ("face", "node"):
            o = mass_run(M, 0.25, t_end, fT, fC, Dface=sch)
            print(f"  {M:>6} {R0/M*1000:>8.4f} {sch:>6} {o['W1']-o['W0']:>17.10e} "
                  f"{o['acc_surf']:>17.10e} {o['res']:>14.6e} "
                  f"{abs(o['res'])/abs(o['acc_surf']):>13.5e}")
    print("\n  dt dependence of the nodal-D residual (M=200):")
    for dt in (1.0, 0.5, 0.25, 0.125, 0.05, 0.01):
        o = mass_run(200, dt, t_end, fT, fC, Dface="node")
        print(f"    dt={dt:>6}: dW={o['W1']-o['W0']:.8e} flux={o['acc_surf']:.8e} "
              f"res={o['res']:.5e} rel={abs(o['res'])/abs(o['acc_surf']):.5e}")
    print("\n  mechanism: time-integrated mismatch per face, M=200, dt=0.25, nodal D")
    o = mass_run(200, 0.25, t_end, fT, fC, Dface="node")
    pf = o["per_face"]
    print(f"    sum(per-face) = {pf.sum():.6e} ; residual = {o['res']:.6e} ; "
          f"ratio = {pf.sum()/o['res']:.6f}")
    idx = np.argsort(-np.abs(pf))[:8]
    print(f"    largest faces (index j -> between r_j and r_{{j+1}}):")
    for j in idx:
        print(f"      j={j:>4} r_j={j*o['dr']*1000:>6.3f} mm  per-face={pf[j]:+.6e}  "
              f"share={pf[j]/pf.sum():+.3f}")
    print(f"    sum over first half (axis region) = {pf[:100].sum():.6e} ; "
          f"second half = {pf[100:].sum():.6e}")
    print(f"    C profile at t=1800 s: min={o['C'].min():.6f} max={o['C'].max():.6f} "
          f"C_M={o['C'][-1]:.6f} C_0={o['C'][0]:.6f}")
    print(f"    D profile: D_0={Dfun(o['C'][0]):.4e} D_M={Dfun(o['C'][-1]):.4e} "
          f"(ratio {Dfun(o['C'][0])/Dfun(o['C'][-1]):.3f})")
    return


def c11(fT, fC):
    hr("C11. Practical impact: nodal D vs face-averaged D on the Q1 output")
    t_end = 1800.0
    pr = np.array([0.0, 0.005, 0.01, 0.015, 0.02])
    for dt in (0.125, 0.02):
        print(f"  dt = {dt} s")
        prev = None
        for M in (100, 200, 400, 800, 1600):
            of = mass_run(M, dt, t_end, fT, fC, Dface="face")
            on = mass_run(M, dt, t_end, fT, fC, Dface="node")
            Cf = np.interp(pr, of["r"], of["C"])
            Cn = np.interp(pr, on["r"], on["C"])
            dC = np.max(np.abs(Cn - Cf))
            dT = np.max(np.abs(np.interp(pr, on["r"], on["T"])
                               - np.interp(pr, of["r"], of["T"])))
            sf = sn = float("nan")
            if prev is not None:
                sf = np.max(np.abs(np.interp(pr, of["r"], of["C"])
                                   - np.interp(pr, prev[0], prev[1])))
                sn = np.max(np.abs(np.interp(pr, on["r"], on["C"])
                                   - np.interp(pr, prev[0], prev[2])))
            prev = (of["r"].copy(), of["C"].copy(), on["C"].copy())
            print(f"    M={M:>5}: max|dC|(node-face)={dC:.6e}  max|dT|={dT:.3e} K  "
                  f"| face vs M/2 = {sf:.3e}  node vs M/2 = {sn:.3e}")
        print()

    hr("C11b. EXTRA: convergence of the output radii themselves (face-averaged D = the repaired scheme)")
    print(f"  {'M':>5} {'dr[mm]':>8} " + " ".join(f"{q:>12.6f}" for q in pr) + f" {'C at r=R':>14}")
    ref = mass_run(1600, 0.02, t_end, fT, fC, Dface="face")
    Cref = np.interp(pr, ref["r"], ref["C"])
    Tref = np.interp(pr, ref["r"], ref["T"])
    print(f"  {'1600(ref)':>5} {R0/1600*1000:>8.4f} " + " ".join(f"{v:>12.6f}" for v in Cref))
    for M, dt in ((100, 0.0625), (200, 0.0625), (400, 0.0625), (800, 0.0625)):
        o = mass_run(M, dt, t_end, fT, fC, Dface="face")
        Cm = np.interp(pr, o["r"], o["C"])
        Tm = np.interp(pr, o["r"], o["T"])
        eC = np.max(np.abs(Cm - Cref))
        eT = np.max(np.abs(Tm - Tref))
        print(f"  {M:>5} {R0/M*1000:>8.4f} " + " ".join(f"{v:>12.6f}" for v in Cm)
              + f"   max|dC|={eC:.3e}  max|dT|={eT:.3e} K")
    print("  (production grid in the repo is M=800, dt=0.125; reference here is M=1600, dt=0.02)")


if __name__ == "__main__":
    fT, fC = make_env("pchip")
    # cross-check own Thomas vs LAPACK banded
    o1 = mass_run(200, 0.25, 300.0, fT, fC, Dface="node", use_banded=False)
    o2 = mass_run(200, 0.25, 300.0, fT, fC, Dface="node", use_banded=True)
    print(f"[solver cross-check] own Thomas vs LAPACK banded: max|dC| = "
          f"{np.max(np.abs(o1['C']-o2['C'])):.3e}, max|dT| = {np.max(np.abs(o1['T']-o2['T'])):.3e}")
    c10(fT, fC)
    c11(fT, fC)
