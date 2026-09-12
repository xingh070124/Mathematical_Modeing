# -*- coding: utf-8 -*-
"""Audit N: is the Clapeyron-vs-h_fg agreement a differentiation artefact?
Which d p_sat/dT route is right, and how independent is the '0.1016 J/kg' check?"""
from __future__ import annotations
import sys
import numpy as np
from iapws import IAPWS95
sys.stdout.reconfigure(encoding="utf-8")
np.seterr(all="ignore")

def ps(T):
    return IAPWS95(T=T, x=1).P * 1e6

def sat(T):
    liq, vap = IAPWS95(T=T, x=0), IAPWS95(T=T, x=1)
    return dict(vg=1 / vap.rho, vf=1 / liq.rho, hfg=(vap.h - liq.h) * 1000,
                Z=vap.Z, Rv=vap.R * 1000, psat=vap.P * 1e6)

print(f"{'T(C)':>5} {'h_fg':>12} " + "".join(f"{'h=' + h:>14}" for h in
      ("1e-1", "1e-2", "1e-3", "1e-4")) + "   L_clap(h=1e-2)")
for tc in (20, 40, 50):
    T = tc + 273.15
    s = sat(T)
    row = []
    for h in (1e-1, 1e-2, 1e-3, 1e-4):
        dp = (ps(T + h) - ps(T - h)) / (2 * h)
        row.append(T * (s["vg"] - s["vf"]) * dp)
    print(f"{tc:5d} {s['hfg']:12.2f} " + "".join(f"{v:14.2f}" for v in row)
          + f"   dev={row[1]-s['hfg']:+.4f}")
print("\n=> the Clapeyron check is essentially insensitive to the step size for")
print("   h <= 1e-2 K, so 0.1016 J/kg is the EOS's own internal consistency residual")
print("   (Clapeyron is an identity for any consistent EOS), not an independent")
print("   validation of the model's latent-heat use.")

# how far does the CC-vs-1/Z residual equal v_f/v_g ?
print(f"\n{'T(C)':>5} {'err_CC %':>10} {'1/Z-1 %':>10} {'resid pp':>10} "
      f"{'v_f/v_g*100':>12} {'ratio':>7}")
for tc in (20, 25, 30, 35, 40, 45, 50):
    T = tc + 273.15
    s = sat(T)
    dp = (ps(T + 1e-2) - ps(T - 1e-2)) / 2e-2
    Lcc = s["Rv"] * T ** 2 * dp / s["psat"]
    err = (Lcc - s["hfg"]) / s["hfg"] * 100
    inv = (1 / s["Z"] - 1) * 100
    r = s["vf"] / s["vg"] * 100
    print(f"{tc:5d} {err:10.5f} {inv:10.5f} {err-inv:10.6f} {r:12.6f} "
          f"{(err-inv)/r:7.4f}")
print("=> residual pp == (v_f/v_g) in percentage points to ~0.5% -> the 0.008452 pp")
print("   'inconsistency' IS the term from neglecting v_f, not a numerical artefact.")
