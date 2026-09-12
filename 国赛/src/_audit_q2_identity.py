# -*- coding: utf-8 -*-
"""Falsification test for the paper's reading of the energy-balance defect.

The paper (tex lines 857-860, 1260-1266) claims that the non-conservative
form's defect |dE + Fh| is NOT a conservation error but is exactly the sensible
enthalpy carried away by the water leaving the control volume, i.e.
    sum_n sum_i MLg_i [ (rho cp)^{n+1} - (rho cp)^n ]_i T^{n+1}_i .

Derivation from src/q2_solve.py (lumped mass): summing the converged residual
R_T = MLg rcp (T-Told)/dt + KT + e_M*flux_h over all nodes gives, because
sum_i (KT)_i = 0 identically for the element-stiffness assembly,
    sum_i MLg rcp^n (T^{n+1}-T^n) = -dt*flux_h .
And  dE = sum MLg[rcp^{n+1}T^{n+1} - rcp^n T^n]
        = sum MLg rcp^n (T^{n+1}-T^n) + sum MLg (rcp^{n+1}-rcp^n) T^{n+1} .
Hence  dE + Fh = sum_n sum_i MLg_i d(rcp)_i T^{n+1}_i   exactly.

This script accumulates both sides on a real run and reports the residuals.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q1_solve import Env, load_attachment1  # noqa: E402
from q2_solve import (Par, assemble, geometry, props, newton_solve,  # noqa: E402
                      T0K, C0)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")


def run(M, dt, t_end, par):
    g = geometry(M, par.boundary)
    n = g["n"]
    MLg = g["MLg"]
    t1, T1, C1 = load_attachment1()
    env = Env(t1, T1, C1, method="pchip")

    x = np.empty(2 * n)
    x[0::2] = T0K
    x[1::2] = C0
    xold = x.copy()

    rho0, cp0, *_ = props(C0, par.mode)
    E0 = float(np.sum(MLg * rho0 * cp0 * T0K))
    W0 = float(np.sum(MLg * C0))

    nsteps = int(round(t_end / dt))
    cumFh = cumFw = 0.0
    E = E0
    acc_dM_T = 0.0          # sum MLg d(rcp) T^{n+1}
    acc_dM_Tn = 0.0         # sum MLg d(rcp) T^n     (paper's index convention)
    rcp_old, _, _, _, _, _ = props(xold[1::2], par.mode)
    rcp_old = rcp_old * props(xold[1::2], par.mode)[1]
    for step in range(1, nsteps + 1):
        tn1 = step * dt
        Tinf, Cinf = env.T(tn1), env.C(tn1)
        x, nit, _ = newton_solve(x, xold, dt, g, par, Tinf, Cinf)
        _, _, aux = assemble(x, xold, dt, g, par, Tinf, Cinf)
        cumFh += dt * aux["flux_h"]
        cumFw += dt * aux["flux_w"]
        Tn1 = x[0::2]
        rho1, cp1, *_ = props(x[1::2], par.mode)
        rcp1 = rho1 * cp1
        E = float(np.sum(MLg * rcp1 * Tn1))
        acc_dM_T += float(np.sum(MLg * (rcp1 - rcp_old) * Tn1))
        acc_dM_Tn += float(np.sum(MLg * (rcp1 - rcp_old) * xold[0::2]))
        rcp_old = rcp1
        xold = x.copy()
    return dict(E0=E0, E=E, Fh=cumFh, Fw=cumFw, W0=W0,
                W=float(np.sum(MLg * x[1::2])),
                acc_dM_T=acc_dM_T, acc_dM_Tn=acc_dM_Tn)


def main():
    print("=" * 100)
    print("恒等式检验: |ΔE + Fh|  ==  Σ_n Σ_i MLg_i Δ(ρcₚ)_i T^{n+1}_i")
    print("=" * 100)
    for M, dt in ((200, 0.25), (400, 1.0 / 16)):
        for lbl, par in (("非保守 T", Par()), ("守恒 conserv", Par(energy="conserv"))):
            r = run(M, dt, 10800.0, par)
            gap = r["E"] - r["E0"] + r["Fh"]
            rel = abs(gap) / max(abs(r["Fh"]), 1e-300)
            print(f"  M={M:4d} dt={dt:.5f} {lbl:16s}")
            print(f"     E0 = {r['E0']:.6e}  E(10800) = {r['E']:.6e}  "
                  f"Fh = {r['Fh']:.6e}  (per 2π, J/m)")
            print(f"     |ΔE + Fh|                        = {abs(gap):.6e}")
            print(f"     |Σ MLg Δ(ρcₚ) T^(n+1)|           = {abs(r['acc_dM_T']):.6e}")
            print(f"     |Σ MLg Δ(ρcₚ) T^n| (论文写法)     = {abs(r['acc_dM_Tn']):.6e}")
            print(f"     相对差 (对 Fh)                   = "
                  f"{abs(abs(gap)-abs(r['acc_dM_T']))/abs(r['Fh']):.3e}")
            print(f"     水量: W0={r['W0']:.8e} W={r['W']:.8e} "
                  f"水量收支残差 = {abs(r['W']-r['W0']+r['Fw'])/abs(r['Fw']):.3e}")


if __name__ == "__main__":
    main()
