# -*- coding: utf-8 -*-
"""Audit D (C5): independent re-derivation of the latent-heat chain.

Two independent sources:
  (a) iapws.IAPWS95  (IAPWS-95 EOS, as used by the producer)
  (b) closed-form Wagner-Pruss-type saturation curve + IAPWS-95 ideal-gas cp
      derivative, which gives dp_sat/dT analytically (no finite difference).
"""
from __future__ import annotations
import io, os, sys
import numpy as np
from iapws import IAPWS95

sys.stdout.reconfigure(encoding="utf-8")
np.seterr(all="ignore")
TC = 647.096
PC = 22.064e6

def wagner_psat(T):
    """IAPWS-95 release saturation-pressure equation (Wagner & Pruss 2002), Pa.

    Coefficients as in IAPWS R7-97 / Wagner-Pruss 2002 for the IAPWS-95
    formulation.
    """
    t = 1.0 - T / TC
    a = [-7.85951783, 1.84408259, -11.7866497, 22.6807411, -15.9618719, 1.80122502]
    e = [1.0, 1.5, 3.0, 3.5, 4.0, 7.5]
    s = sum(ai * t ** ei for ai, ei in zip(a, e))
    return PC * np.exp(TC / T * s)

def wagner_dpsat(T, h=1e-6):
    return (wagner_psat(T + h) - wagner_psat(T - h)) / (2 * h)

def sat(T):
    liq = IAPWS95(T=T, x=0)
    vap = IAPWS95(T=T, x=1)
    return dict(psat=vap.P * 1e6, vf=1 / liq.rho, vg=1 / vap.rho, Z=vap.Z,
                hf=liq.h * 1000, hg=vap.h * 1000, hfg=(vap.h - liq.h) * 1000,
                cp_l=liq.cp * 1000, cp_v=vap.cp * 1000, Rv=vap.R * 1000)

Rv = sat(300.0)["Rv"]
print("R_v (IAPWS-95) =", Rv)
print("R_v (Wagner/thermo 8.314462618/0.018015268) =",
      8.314462618 / 0.018015268)

rows = []
for tc in (20, 25, 28, 30, 35, 40, 45, 50):
    T = tc + 273.15
    s = sat(T)
    dp = (sat(T + 1e-2)["psat"] - sat(T - 1e-2)["psat"]) / 2e-2
    dpw = wagner_dpsat(T)
    Lclap = T * (s["vg"] - s["vf"]) * dp
    Lclapw = T * (s["vg"] - s["vf"]) * dpw
    Lcc = Rv * T ** 2 * dp / s["psat"]
    Lccw = Rv * T ** 2 * dpw / wagner_psat(T)
    invZ = 1.0 / s["Z"] - 1.0
    rows.append(dict(tc=tc, T=T, hfg=s["hfg"], Lclap=Lclap, Lclapw=Lclapw,
                     Lcc=Lcc, Lccw=Lccw, dclap=Lclap - s["hfg"],
                     dclapw=Lclapw - s["hfg"], dcc=(Lcc - s["hfg"]) / s["hfg"] * 100,
                     dccw=(Lccw - s["hfg"]) / s["hfg"] * 100, invZ=100 * invZ,
                     psat=s["psat"], psatw=wagner_psat(T), Z=s["Z"],
                     dcp=s["cp_v"] - s["cp_l"]))
print(f"\n{'T(C)':>5} {'h_fg IAPWS':>12} {'p_sat W':>12} {'p_sat IA':>12} "
      f"{'Clap-IA':>10} {'Clap-W':>10} {'CC%':>8} {'CCw%':>8} {'1/Z-1%':>8} {'CC-1/Z':>9}")
for r in rows:
    print(f"{r['tc']:5d} {r['hfg']:12.1f} {r['psatw']:12.1f} {r['psat']:12.1f} "
          f"{r['dclap']:10.2f} {r['dclapw']:10.2f} {r['dcc']:8.5f} {r['dccw']:8.5f} "
          f"{r['invZ']:8.5f} {r['dcc']-r['invZ']:9.5f}")

doc = {20: (2453519.3, 2453519.4, 2456879.9, 0.13697, 0.13523),
       25: (2441676.2, 2441676.3, 2445738.8, 0.16639, 0.16407),
       30: (2429811.2, 2429811.3, 2434689.9, 0.20078, 0.19772),
       35: (2417914.6, 2417914.7, 2423736.5, 0.24078, 0.23678),
       40: (2405977.3, 2405977.4, 2412884.1, 0.28707, 0.28189),
       45: (2393990.9, 2393990.9, 2402138.9, 0.34035, 0.33371),
       50: (2381947.1, 2381947.2, 2391508.4, 0.40141, 0.39295)}
print("\nDoc table 7.8 vs independent recomputation (max abs diff per column):")
cols = ["hfg", "Lclap", "Lcc", "dcc", "invZ"]
arr = {c: [] for c in cols}
for tc, vals in doc.items():
    r = [x for x in rows if x["tc"] == tc][0]
    for c, v in zip(cols, vals):
        arr[c].append(abs(r[c] - v))
for c in cols:
    print(f"  {c:6s} max|doc - recomputed| = {max(arr[c]):.6g}")

print("\nClapeyron reproduction of IAPWS-95 h_fg (max |dev|):")
print("  central diff dp/dT, h=1e-2 K :", max(abs(r["dclap"]) for r in rows), "J/kg")
print("  analytic Wagner dp/dT        :", max(abs(r["dclapw"]) for r in rows), "J/kg")
print("  CC deviation vs (1/Z-1) max inconsistency [pct points]:",
      max(abs(r["dcc"] - r["invZ"]) for r in rows),
      " (over 20-50C; doc quotes 0.008452)")

# --- the actual calibration used by the model (28..50 C, step 0.5)
tf = np.arange(28.0, 50.0 + 1e-9, 0.5)
L = np.array([sat(t + 273.15)["hfg"] for t in tf])
b, a = np.polyfit(tf, L, 1)
print(f"\nleast squares over 28..50C:  a={a:.4f}  b={b:.6f}")
print("  doc/registry: a=2434560.4856 (as anchor L28), b=-2391.0094")
L28 = sat(28 + 273.15)["hfg"]
b28 = float(np.polyfit(tf - 28.0, L, 1)[0])
print(f"  L28 = {L28:.6f} ; slope about 28C = {b28:.6f}")
res = L - (L28 + b28 * (tf - 28.0))
print(f"  max|resid| on 28..50C = {np.max(np.abs(res)):.4f} J/kg "
      f"(doc 109.2122) ; endpoint resid @50C = {res[-1]:.4f}")
res2 = L - (a + b * tf)
print(f"  max|resid| using the 2-parameter LSQ (a,b) = {np.max(np.abs(res2)):.4f} J/kg")
tc20 = np.arange(20.0, 50.0 + 1e-9, 0.5)
L20 = np.array([sat(t + 273.15)["hfg"] for t in tc20])
res20 = L20 - (L28 + b28 * (tc20 - 28.0))
print(f"  max|resid| on 20..50C = {np.max(np.abs(res20)):.4f} J/kg "
      f"(registry LH_resid28 claims this quantity) ; % = "
      f"{100*np.max(np.abs(res20))/L28:.5f}")
print("\nmodel applies  2.4346e6 - 2.391e3*(T-28C):")
print(f"  intercept rel diff = {abs(2.4346e6-L28)/L28*100:.5f}% (doc 0.00162%)")
print(f"  slope     rel diff = {abs(-2.391e3-b28)/abs(b28)*100:.5f}% (doc 0.00039%)")
print(f"  H(50C) model={2.4346e6-2.391e3*22:.1f}  IAPWS={sat(323.15)['hfg']:.1f} "
      f"err={2.4346e6-2.391e3*22-sat(323.15)['hfg']:.1f} J/kg -> "
      f"dT = {abs(2.4346e6-2.391e3*22-sat(323.15)['hfg'])/(25/8e-7):.5f} K")
print("\nKirchhoff check dH/dT = cp_v - cp_l:")
for tc in (28, 40, 50):
    r = [x for x in rows if x["tc"] == tc]
    if r:
        print(f"  {tc}C: c_p,v - c_p,l = {r[0]['dcp']:.1f} J/(kg K)")
    else:
        s = sat(tc + 273.15)
        dnum = (sat(tc + 274.15)["hfg"] - sat(tc + 272.15)["hfg"]) / 2.0
        print(f"  {tc}C: cp_v-cp_l={s['cp_v']-s['cp_l']:.1f}  numerical dH/dT={dnum:.1f}")
