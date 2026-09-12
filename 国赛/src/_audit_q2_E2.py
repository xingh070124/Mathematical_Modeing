# -*- coding: utf-8 -*-
"""Audit E2: (a) the (T-Tref) cancellation, re-done cleanly;
(b) upper-bound reinforcement; (c) boundary-layer profile for C4."""
from __future__ import annotations
import os, sys, time
import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from q1_solve import Env, load_attachment1
from q2_solve import Par, march, out_indices, Dfun, H_CONV, HM, R

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")


def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)


hr("E2  the mixture relation and the (T-Tref) cancellation, re-derived")
C = sp.symbols("C", positive=True)
rho = 650 + 128 * C
cp = 1450 + 2736 * C / (C + 1)
rho_s = sp.simplify(rho / (C + 1))
print("  rho_s(C) = rho/(1+C) =", sp.factor(rho_s),
      " -> NOT constant; rho_s(2.55)=%.4f  rho_s(0.15)=%.4f"
      % (float(rho_s.subs(C, 2.55)), float(rho_s.subs(C, 0.15))))
A = sp.expand(sp.simplify(rho * cp))
dA = sp.simplify(sp.diff(A, C))
print("  A(C)=rho*cp = A(C) ; in closed form cp = (1450+4186C)/(1+C) so")
print("     A(C) = rho_s(C) * (1450 + 4186 C)  with rho_s(C)=rho/(1+C).")
cl = sp.Integer(4186)
cs = sp.Integer(1450)
print("  exact check rho_s(C)*(1450 + 4186C) - rho*cp  =",
      sp.simplify(rho_s * (cs + C * cl) - rho * cp))
print("  so the identity rho*cp = rho_s(c_s+C c_l) with c_s=1450,c_l=4186 is EXACT.")
print("  BUT: does a CONSTANT rho_s exist with rho = rho_s(1+C)?")
print("       rho = 650+128C = rho_s + rho_s C  =>  rho_s = 650 AND rho_s = 128.")
print("       Contradiction -> no constant rho_s exists; rho_s(C) is definitional.")
print("  KEY: the doc's expansion needs d(rho c_p)/dC = c_l*rho_s.  Check:")
print("     dA/dC =", sp.factor(dA))
print("     c_l*rho_s = 4186*rho/(1+C) =", sp.factor(4186 * rho_s))
print("     dA/dC - c_l*rho_s =",
      sp.simplify(dA - 4186 * rho_s), " (NOT zero)")
for Cv in (2.55, 1.5, 0.15):
    print(f"     C={Cv}: dA/dC={float(dA.subs(C,Cv)):.1f}  c_l*rho_s="
          f"{float(4186*rho_s.subs(C,Cv)):.1f}  gap={float((dA-4186*rho_s).subs(C,Cv)):.1f}")
print("  => the printed cancellation step (LHS expands to rho_s(c_s+c_lC)dT/dt")
print("     + c_l(T-Tref)rho_s dC/dt) requires d(rho cp)/dC = c_l rho_s, which")
print("     fails.  The exact expansion carries c_s (T-Tref) d(rho_s)/dt instead.")
print("  With a CONSTANT rho_s the two appendix-3 equations have no exact")
print("  (rho_s, c_s, c_l) solution; best LSQ residual:")
from scipy.optimize import least_squares
Cs = np.array([0.05, 0.15, 0.5, 1.0, 2.0, 2.55])
rhov = 650 + 128 * Cs
cpv = 1450 + 2736 * Cs / (Cs + 1)
def res(p):
    a, b, c = p
    return np.concatenate([a * (1 + Cs) - rhov, a * (b + Cs * c) - rhov * cpv])
r = least_squares(res, [300.0, 1450.0, 4186.0])
print(f"    rho_s={r.x[0]:.3f}  c_s={r.x[1]:.1f}  c_l={r.x[2]:.1f}  "
      f"max|resid|={np.max(np.abs(r.fun)):.4e} (rho scale 650-976, A scale ~3.3e6)")
print("  => the 'same mixture relation' reading holds ONLY in the split")
print("     rho_s = rho(C)/(1+C), i.e. it is a definition, not an independent fact.")

# spurious source with the model's own numbers
rho_s0 = float(rho_s.subs(C, 2.55))
rcp0 = float(A.subs(C, 2.55))
dCdt = -8.3185185185185e-5
print(f"\n  spurious source S_false = c_l (T-Tref) rho_s dC/dt")
for dTref in (7.0, 6.85):
    S = float(cl) * dTref * rho_s0 * abs(dCdt)
    print(f"    T-Tref={dTref:5.2f} K -> |S_false| = {S:.4f} W/m^3 "
          f"(registry EC_Sfalse_abs = 656.0475)")
print(f"  registry EC_main = 2603.1272; note rho(1.5)*cp(1.5) = "
      f"{float((650+128*1.5)*(1450+2736*1.5/2.5)):.4f} -> EC_main is just")
print("     rho*cp(C=1.5) x 1e-3 K/s, i.e. two chosen numbers, not a measured")
print("     main term.  rho*cp(C0) = %.1f is 28%% larger." % rcp0)
print(f"  the doc quotes 'rho cp dT/dt ~ 2.60e3' with dTref~7 K. "
      f"With 7 K: S=670.41 -> ratio 0.2575, not 0.2520.")
print(f"  With dTref=6.85 K (as registry implies while text says ~7): ratio 0.25202.")

# ---- what the conservative form ACTUALLY implemented omits
print(f"\n  the implemented conservative form is  d(rho cp T)/dt = div(k grad T)")
print("  with T ABSOLUTE (q2_solve.py: RT=(MT*T - MLg*rho_o*cp_o*Told)/dt + KT).")
print("  exact identity: d(rho cp T)/dt = div(k grad T) - c_l J_w.gradT")
print("                  - c_l T div(J_w)")
Tmean = 308.0
omit = float(cl) * Tmean * rho_s0 * abs(dCdt)
print(f"  => omitted term c_l T rho_s dC/dt at T=308 K, C=C0: {omit:.4e} W/m^3")
print(f"     vs the doc's S_false = 656.05 W/m^3 -> factor {omit/656.0475:.1f}")

# ---- residual of the exact derivation under rho_s(C)
rhos_p = float(sp.diff(rho_s, C).subs(C, 2.55))
resid = -float(cs) * 7.0 * rhos_p * dCdt
print(f"\n  exact residual term -c_s (T-Tref) d(rho_s)/dt:")
print(f"     drho_s/dC at C0 = {rhos_p:.4f} ; d(rho_s)/dt = {rhos_p*dCdt:.4e}")
print(f"     residual = {resid:.4f} W/m^3 = {abs(resid)/2603.1272*100:.3f}% of EC_main")
print(f"     (the term the doc declares negligible, -c_l J_w.gradT, is 0.864 W/m^3)")


hr("E3  upper bound: over the WHOLE run, is T_R ever above T_inf ?")
o = march(400, 1.0 / 16, 10800.0, env, Par(), out_idx=out_indices(400))
Tr = o["T_snap"][:, -1] - 273.15
Tinf = np.array([env.T(x) - 273.15 for x in o["t_snap"]])
Cr = o["C_snap"][:, -1]
Cinf = np.array([env.C(x) for x in o["t_snap"]])
print(f"  max(T_R - T_inf) over 0..10800 s = {np.max(Tr-Tinf):+.4f} K")
print(f"  q_conv = h(T_R - T_inf): max {H_CONV*np.max(Tr-Tinf):+.4f} W/m^2 "
      f"(never positive => heat always flows IN)")
print(f"  min(C_R - C_inf) = {np.min(Cr-Cinf):+.5f} kg/kg (evaporation always active)")
print(f"  min(T_R - 28C) = {np.min(Tr-28.0):+.6f} K at "
      f"t={o['t_snap'][np.argmin(Tr-28.0)]:.0f} s  <- lower bound violated")
print(f"  max T in whole field = {o['T_snap'].max()-273.15:.4f} C ; "
      f"max T_inf = {Tinf.max():.4f} C ; T_0 = 28 C")
print("  => since dT_R/dt|_t = [h(T_inf-T_R) + H h_m(C_inf-C_R)]/(rho cp M) + conduction,")
print("     the boundary term of the lower side is always +, and the surface flux")
print("     deficit is what keeps T_R below T_inf for the whole run.")
snap = o["T_snap"]
print(f"  is T monotone in t over 0..10800 for r=0? "
      f"{bool(np.all(np.diff(snap[:,0])>=-1e-9))}")
print(f"  number of t with dT(R)/dt<0 after t>60 s: "
      f"{int((np.diff(snap[:, -1])<0).sum())} of {len(snap)-1}")

hr("E4  boundary layer at t<=60 s (M=3200, dt=1/64)")
t0 = time.time()
o2 = march(3200, 1.0 / 64, 60.0, env, Par(), out_idx=out_indices(3200))
g = o2["geom"]
print(f"  wall {time.time()-t0:.1f}s   dr = {g['dr']*100:.6f} cm")
D0 = float(Dfun(2.55, 301.15))
print(f"  D(C0,T0)={D0:.6e} m^2/s -> sqrt(D t): 1 s = {np.sqrt(D0)*100:.6f} cm "
      f"(doc 0.00751 cm); 60 s = {np.sqrt(D0*60)*100:.6f} cm")
for it in (0, 59):
    tt = o2["t_snap"][it]
    Cc = o2["C_snap"][it]
    dev = Cc - Cc[0]
    dlt = np.sqrt(D0 * tt) * 100
    k04 = int(np.max(np.where(dev > 1e-4)[0]))
    k05 = int(np.max(np.where(dev > 5e-5)[0]))
    print(f"\n  t={tt:4.0f}s  C_surface={Cc[0]:.6f}  "
          f"|C-C_s|>1e-4 out to node {k04} (r={g['r'][k04]*100:.5f} cm); "
          f">5e-5 out to node {k05} (r={g['r'][k05]*100:.5f} cm)")
    print(f"          sqrt(Dt)={dlt:.6f} cm = {dlt/(g['dr']*100):.2f} cells; "
          f"node8 r={g['r'][8]*100:.5f} cm")
    print(f"          first 10 nodes: {np.round(Cc[:10], 6)}")
    print(f"          monotone rising over first 12 nodes? "
          f"{bool(np.all(np.diff(Cc[:12]) > 0))}")
    if tt == 1.0:
        print(f"          doc claims: 'surface 2.51983 rising to node 8 = 2.53286, "
              f"still rising at t=1 s on M=3200'")
        print(f"          actual M=3200 t=1 s: node0={Cc[0]:.5f} node8={Cc[8]:.5f} "
              f"node0 vs doc 2.51983, node8 vs doc 2.53286")
        print(f"          cells within 1 sqrt(Dt) of the surface: "
              f"{dlt/(g['dr']*100):.2f}  (doc '>10')")
        print(f"          |C(node k) - C_surface| < 5e-5 for all k > {k05} "
              f"=> perturbation out to {k05} cells")
