# -*- coding: utf-8 -*-
"""Audit O: close C3 (no-evaporation control) and C7/§7.7 (附录2 vs 附录3)."""
from __future__ import annotations
import os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from q1_solve import Env, load_attachment1
from q2_solve import Par, march, out_indices, props, Dfun, hevap_of, H_CONV, HM, R

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")

print("=" * 78)
print("O1  C3 control: does switching evaporation OFF restore the lower bound?")
print("=" * 78)
for tag, par in (("with evaporation", Par()), ("no evaporation", Par(hevap="off"))):
    t0 = time.time()
    o = march(400, 1.0 / 16, 10800.0, env, par, out_idx=out_indices(400))
    T = o["T_snap"] - 273.15
    imin = np.unravel_index(np.argmin(T), T.shape)
    print(f"  {tag:>16}: min T = {T.min():.6f} C at t={o['t_snap'][imin[0]]:.0f} s "
          f"r={o['r'][imin[1]]*100:.1f} cm ; violation = {max(0.0, 28.0-T.min()):.9f} K "
          f"[{time.time()-t0:.0f} s]")
    print(f"        max T = {T.max():.6f} C  (env max 50.2460)")

print("\n" + "=" * 78)
print("O2  §7.7 附录2 vs 附录3 property comparison")
print("=" * 78)
rho3, cp3, k3, *_ = props(2.55, "app3")
rho2, cp2, k2, *_ = props(2.55, "app2")
for nm, a, b in (("rho", rho3, rho2), ("cp", cp3, cp2), ("k", k3, k2),
                 ("rho*cp", rho3 * cp3, rho2 * cp2)):
    print(f"  {nm:>7}: app3={float(a):12.4f}  app2={float(b):12.4f}  "
          f"rel={100*(float(a)-float(b))/float(b):+7.2f}%")
al3 = float(k3) / float(rho3 * cp3)
al2 = float(k2) / float(rho2 * cp2)
print(f"  alpha  : app3={al3:.5e}  app2={al2:.5e}  rel="
      f"{100*(al3-al2)/al2:+.2f}%")
print(f"  D(C0,28C): app3={float(Dfun(2.55,301.15,'app3')):.6e}  "
      f"app2={float(Dfun(2.55,301.15,'app2')):.6e}  "
      f"ratio={float(Dfun(2.55,301.15,'app3'))/float(Dfun(2.55,301.15,'app2')):.4f}")
print(f"  D(C0,50C): app3={float(Dfun(2.55,323.15,'app3')):.6e}")
print("  doc §7.7 says '附录3 的 D 处处比附录2 大 1.14~2.52 倍'")

print("\n" + "=" * 78)
print("O3  §4.2  'q_evap ≈ 1.925 ΔC' and the h(Tinf-TR) column")
print("=" * 78)
L40 = float(hevap_of(313.15, Par())[0])
print(f"  H_evap(40C) from the model line = {L40:.1f} J/kg (code comment says 2405908)")
print(f"  L40*h_m = {L40*HM:.6f} (doc 1.925)")
print(f"  t=0     q_evap with C_R=2.5, C_inf=0.0196: {L40*HM*(2.5-0.0196):.4f} (doc 4.774)")
print(f"  t=1800  C_inf=0.0331: {L40*HM*(2.5-0.0331):.4f} (doc 4.748); "
      f"t=3600 C_inf=0.0427: {L40*HM*(2.5-0.0427):.4f} (doc 4.730)")
print(f"  h(T_inf-T_R) with T_R=28: t=1800 {25*(41.5130-28):.2f} (doc 337.5) ; "
      f"t=3600 {25*(47.5000-28):.2f} (doc 487.5, implies T_inf=47.5C)")
