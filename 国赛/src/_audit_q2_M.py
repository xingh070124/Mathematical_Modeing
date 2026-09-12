# -*- coding: utf-8 -*-
"""Audit M: registry cross-checks for C5 and the §5.5/§6/§7.3 configuration conflict."""
from __future__ import annotations
import csv, io, os, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

print("=" * 70)
print("M1  latent-heat registry rows (LH_*)")
rows = list(csv.DictReader(io.open(os.path.join(OUT, "registry_q2_latent_heat_rows.csv"),
                                   encoding="utf-8-sig")))
want = ("LH_resid28", "LH_resid28_pct", "LH_slope28", "LH_L28", "LH_work_a", "LH_work_b",
        "LH_dcp_ideal_mean", "LH_dLdT_mean", "LH_dLdT_resid", "LH_Rv", "LH_Mw",
        "LH_vf_over_vg", "LH_anchor_b", "LH_L0", "LH_Ltrip")
for r in rows:
    if r["id"] in want:
        print(f"  {r['id']:<20} {r['value']:<24} {r['unit'][:12]:<12} {r['quantity'][:60]}")

print("\n  wide table registry_q2_latent_heat.csv header:")
w = list(csv.reader(io.open(os.path.join(OUT, "registry_q2_latent_heat.csv"),
                            encoding="utf-8-sig")))
print("   ", w[0])
for r in w[1:4]:
    print("   ", r)

print("\n" + "=" * 70)
print("M2  library versions")
import importlib.metadata as md
for p in ("iapws", "numpy", "scipy", "openpyxl", "sympy"):
    try:
        print(f"  {p:<10} {md.version(p)}")
    except Exception as e:
        print(f"  {p:<10} ? {e}")
import sys as _s
print("  python    ", _s.version.split()[0])

print("\n" + "=" * 70)
print("M3  §5.5 boundary diagonal under each candidate configuration")
from q2_solve import geometry, props, H_CONV, HM, R
rho, cp, k, *_ = props(2.55, "app3")
rcp = float(rho * cp)
for M, dt in ((800, 1 / 32), (1600, 1 / 64), (1600, 1 / 32)):
    g = geometry(M, "lumped")
    d = g["MLg"][M] * rcp / dt + H_CONV * R
    print(f"  M={M:5d} dt={dt:.6f}  diag={d:9.5f}  "
          f"H(28C)hmR/diag={2.4346e6*HM*R/d*100:.5f}%  "
          f"H(40C)hmR/diag={2405908*HM*R/d*100:.5f}%")
print("  doc §5.5 claims diag=13.8360 and 0.28154% at 'production (M=1600, dt=1/32)'")
print("  doc §6   claims production M=800,  dt=1/32")
print("  doc §7.3 claims production M=1600, dt=1/64 ; code PROD_M=1600, PROD_DT=1/64")

print("\n" + "=" * 70)
print("M4  §7.4 '66/180' env-noise statement")
from q1_solve import load_attachment1
t1, T1, C1 = load_attachment1()
m = t1 <= 10800.0
d = np.diff(T1[m])
print(f"  n samples in 0..10800 = {int(m.sum())}, steps = {len(d)}, "
      f"descending = {int((d<0).sum())}  -> doc '66/180' : "
      f"{int((d<0).sum())}/{len(d)}")
print(f"  T_inf range over that window: {T1[m].min():.5f} .. {T1[m].max():.5f} degC ; "
      f"peak t={t1[m][np.argmax(T1[m])]:.0f} s")
print(f"  C_inf(0)={C1[0]:.5f}  C_inf(10800)={C1[m][-1]:.5f}")
