# -*- coding: utf-8 -*-
"""Audit F: remaining spot checks (W, Cbar, Tmin drift, doc's 4.774, S_false ratio, h_m)."""
from __future__ import annotations
import io, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from openpyxl import load_workbook
from q1_solve import Env, load_attachment1
from q2_solve import Par, props, Dfun, hevap_of, H_CONV, HM, R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wb = load_workbook(os.path.join(ROOT, "outputs", "result2.xlsx"), read_only=True, data_only=True)
ws = wb["水分浓度"]
rows = list(ws.iter_rows(min_row=2, values_only=True))
Cc = np.array([[float(x) for x in r[1:]] for r in rows])
rad = np.array([float(x) for x in next(wb["水分浓度"].iter_rows(min_row=1, max_row=1, values_only=True))[1:]])
wb.close()

def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

hr("F1  water inventory from published result2.xlsx (trapezoid on the 0.1 cm grid)")
def mean_C(vec):
    return float(np.trapezoid(vec * rad, rad) / (rad[-1] ** 2 / 2))
for t in (1, 1800, 10800):
    print(f"  t={t:5d}s  Cbar={mean_C(Cc[t-1]):.6f}")
print("  doc: Cbar(10800)=1.383261, W(0)=5.100000e-04, W(10800)=2.766522e-04, "
      "loss=45.7545%")
print(f"  integral C*r dr at t=1: {np.trapezoid(Cc[0]*rad, rad):.6e} m^2 "
      f"(doc W(0)=5.100000e-04)")
loss = 100 * (1 - mean_C(Cc[-1]) / 2.55)
print(f"  loss from the published grid (volume mean) = {loss:.4f}%  (doc 45.7545%)")

hr("F2  T min: registry V4 is from an M=400 run, doc/core numbers from M=1600")
print("  registry V4_Tmin = 27.990477, doc/§7.4 = 27.9905, result2.xlsx min =",
      round(27.9905, 6))
print(f"  difference = {27.9905-27.990477:.6f} K ; V4_Tmin_gap = 0.0095227381847849 K "
      f"but doc states 0.009500 K")

hr("F3  §4.2 table: q_evap numbers vs 1.925*DeltaC with H_evap(40C)=2405908")
h40 = 2405908.0
for tc, Cinf_, qe in ((0.0, 0.0196, 4.774), (1800.0, 0.0331, 4.748), (3600.0, 0.0427, 4.730)):
    T40 = 40 + 273.15
    q = hevap_of(T40, Par())[0] * HM * (2.5 - Cinf_)
    print(f"  t={tc:7.0f}s Cinf={Cinf_} -> 1.925*({2.5-Cinf_:.4f}) = "
          f"{1.925*(2.5-Cinf_):.4f}   recomputed q_evap = {q:.4f}  doc {qe}")
print("  h(Tinf-TR) at t=1800: Tinf=41.5130C ; doc lists 337.5")
print("   H*hm*(2.5-0.0331)   =", 2405908*8e-7*(2.5-0.0331))
print("   25*(41.5130-28)     =", 25*(41.5130-28))
print("  'q_evap ~= 1.925 DC' checks: 2405908*8e-7 =", 2405908*8e-7)

hr("F4  S_false ratio: is 0.252 reproducible from the stated inputs?")
rho_s = 275.04225352113
cl = 4186.0
rcp = 3334694.7943661967
for dTdC in (7.0, 6.85, 6.999):
    S = cl * dTdC * rho_s * 8.3185185185185e-5
    for rate in (2.6031272e3 / rcp, 1e-3):
        print(f"  T-Tref={dTdC:5.2f} K  S_false={S:8.3f} W/m^3  main={rcp*rate:9.2f} "
              f"ratio={S/(rcp*rate):.6f}")
print("  registry: EC_Sfalse=656.0475, EC_main=2603.1272 (implies dT/dt=7.806e-4 K/s), "
      "EC_ratio=0.25202283")
print("  doc line 92 quotes main 'rho cp dT/dt ~ 2.60e3' while line 90 says dTref~7 K; "
      "with 7 K the ratio is 0.2010, not 0.2520")

hr("F5  h_m analogy: is 0.02 m/s right?")
for pair in [(25.0, 1005.0, 1.2), (25.0, 1005.0, 1.18)]:
    h, cp_air, rho_air = pair
    print(f"  h={h} rho_air={rho_air} cp_air={cp_air} -> h_m ~ {h/(rho_air*cp_air):.5f} m/s ; "
          f"ratio to 8e-7 = {h/(rho_air*cp_air)/8e-7:.0f}")
print("  implicit in doc: 0.02 m/s and 25000x are mutually inconsistent (0.02/8e-7 = 25000)")
print("  equivalence check 0.018/8e-7 =", 0.018/8e-7, " 0.016/8e-7 =", 0.016/8e-7)

hr("F6  constants quoted in §3.1")
C0, T0 = 2.55, 301.15
rho, cp, k, _, _, _ = props(C0, "app3")
print(f"  Bi = hR/k = {H_CONV*R/k:.6f} (doc 1.0353)")
D0 = float(Dfun(C0, T0))
print(f"  Bi_m = h_m R/D = {HM*R/D0:.6f} (doc 2.8360)")
alpha = k / (rho * cp)
print(f"  R^2/alpha = {R**2/alpha:.1f} s (doc 2761.9)")
print(f"  R^2/D     = {R**2/D0:.1f} s (doc 7.090e4)")
print(f"  alpha/D   = {alpha/D0:.4f} (doc 25.67)")
print(f"  R^2/D / 10800 = {R**2/D0/10800:.4f} ; in hours = {R**2/D0/3600:.4f}")
print(f"  dlnD/dT at T0 = 3850/T0^2 = {3850/T0**2*100:.4f} %/K (doc 4.2%/K)")
print(f"  D(C0,50C)/D(C0,28C) = {float(Dfun(C0,323.15))/D0:.4f} (doc 2.3878)")
