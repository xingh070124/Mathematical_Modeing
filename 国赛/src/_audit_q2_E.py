# -*- coding: utf-8 -*-
"""Audit E: (1) replay the central energy-form comparison C1 (V11);
(2) short boundary-layer profile check for C4 (t<=60 s);
(3) upper-bound reinforcement: sign of q_evap and of (T_inf - T_R) over the whole run."""
from __future__ import annotations
import io, os, sys, time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from q1_solve import Env, load_attachment1
from q2_solve import Par, march, out_indices, props, Dfun, hevap_of, H_CONV, HM, R

t1, T1, C1 = load_attachment1()
env = Env(t1, T1, C1, method="pchip")

def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

hr("E1  replay V11: rho cp dT/dt  vs  d(rho cp T)/dt   (M=200, dt=0.25 s, 0..10800 s)")
t0 = time.time()
oo = {}
for tag, eps in (("T", "T"), ("conserv", "conserv")):
    o = march(200, 0.25, 10800.0, env, Par(energy=eps), out_idx=out_indices(200))
    oo[tag] = o
    print(f"  [{tag}] wall {time.time()-t0:.1f}s  T(0,10800)={o['T_snap'][-1,0]-273.15:.4f} C "
          f"T(R,10800)={o['T_snap'][-1,-1]-273.15:.4f} C  C(R,10800)={o['C_snap'][-1,-1]:.6f}")
dT = np.max(np.abs(oo["T"]["T_snap"] - oo["conserv"]["T_snap"]))
dC = np.max(np.abs(oo["T"]["C_snap"] - oo["conserv"]["C_snap"]))
print(f"  max|dT| = {dT:.6f} K   (registry V11_dT = 17.274457167999)")
print(f"  max|dC| = {dC:.6f} kg/kg (registry V11_dC = 0.23457361579963)")
print(f"  centre T at 10800 s: non-conservative {oo['T']['T_snap'][-1,0]-273.15:.4f}, "
      f"conservative {oo['conserv']['T_snap'][-1,0]-273.15:.4f}")
print(f"  energy gaps: nc {abs((oo['T']['E'][-1]-oo['T']['stats']['E0'])+oo['T']['Fh'][-1]):.4e}"
      f"   c {abs((oo['conserv']['E'][-1]-oo['conserv']['stats']['E0'])+oo['conserv']['Fh'][-1]):.4e}")

hr("E2  the (T-Tref) partial-tC cancellation: reproduce it symbolically and numerically")
import sympy as sp
C = sp.symbols("C", positive=True)
rho = 650 + 128 * C
cp = 1450 + 2736 * C / (C + 1)
rho_s = sp.simplify(rho / (1 + C))
print("  rho_s(C) = rho/(1+C) =", rho_s)
print("  is rho_s constant? rho_s(2.55)=%.6f, rho_s(0.15)=%.6f"
      % (float(rho_s.subs(C, 2.55)), float(rho_s.subs(C, 0.15))))
lhs = sp.expand(rho * cp)                      # d(rho cp T)/dt with T=0 reference
rhs_num = sp.expand(sp.diff(rho * cp, C))      # = c_l rho_s
print("  d(rho cp)/dC =", rhs_num)
cl = sp.simplify(rhs_num / rho_s)
print("  => implied c_l = d(rho cp)/dC / rho_s =", cl, "=", float(cl))
# the exact statement: rho*cp == rho_s*(cs + C*cl) with cs = cp(0)
cs = cp.subs(C, 0)
print("  cp(0) =", cs, " ; rho_s*(cs + C*cl) - rho*cp simplifies to",
      sp.simplify(rho_s * (cs + C * cl) - rho * cp))
# Tref independence: if the control volume keeps (T-Tref) instead of T, the
# residual difference is -Tref * d(rho cp)/dt = -Tref * cl * rho_s * dC/dt,
# i.e. exactly what the "conservative" form omits; check with Tref=273.15
S = cl * (T0ref := 273.15) * rho_s * sp.symbols("dCdt")
print("  spurious source with T_ref=273.15 K instead of 0 K:",
      float(cl) * 273.15 * 275.04225352113, "W/m^3 per unit dC/dt")

hr("E3  upper bound: does the model ever have T_inf < T_R (which would allow T>T_inf)?")
Tr = oo["T"]["T_snap"][:, -1] - 273.15
Tinf = np.array([env.T(x) - 273.15 for x in oo["T"]["t_snap"]])
Cr = oo["T"]["C_snap"][:, -1]
Cinf = np.array([env.C(x) for x in oo["T"]["t_snap"]])
print(f"  max over t of (T_R - T_inf) = {np.max(Tr - Tinf):+.4f} K  "
      f"(positive would be needed for T_R > T_inf at any time)")
print(f"  q_conv = h(T_R - T_inf): max {H_CONV*np.max(Tr-Tinf):+.4f} W/m^2 "
      f"(negative = heat INTO the body through the whole run)")
print(f"  C_R - C_inf: min {np.min(Cr-Cinf):+.5f} kg/kg (always >0 => evaporation always on)")
print(f"  T_R - T_0 (28C): min {np.min(Tr-28.0):+.6f} K at t={oo['T']['t_snap'][np.argmin(Tr-28.0)]:.0f}s")
print(f"  overall max T in run = {oo['T']['T_snap'].max()-273.15:.4f} C ; "
      f"env max = {Tinf.max():.4f} C ; T_0 = 28 K above ambient? {28.0 <= Tinf.max()}")

hr("E4  boundary layer at t<=60 s: profile on a fine grid (M=3200, dt=1/64)")
t0 = time.time()
o = march(3200, 1.0 / 64, 60.0, env, Par(), out_idx=out_indices(3200))
g = o["geom"]
print(f"  wall {time.time()-t0:.1f}s  dr = {g['dr']*100:.6f} cm")
D0 = float(Dfun(2.55, 301.15))
print(f"  D(C0,T0) = {D0:.6e} m^2/s -> sqrt(D t) at t=1 s = {np.sqrt(D0)*100:.6f} cm "
      f"(doc 0.00751 cm)")
for it in (0, 59):
    tt = o["t_snap"][it]
    Cc = o["C_snap"][it]
    dev = np.abs(Cc - Cc[0])
    # deepest interior node whose |C - C_surface| still exceeds 1e-4 (doc's own 4-dec scale)
    k5 = np.max(np.where(dev > 5e-5)[0])
    k4 = np.max(np.where(dev > 1e-5)[0])
    dlt = np.sqrt(D0 * tt) * 100  # cm
    print(f"  t={tt:5.0f}s  C_surface={Cc[0]:.5f}  node8={Cc[8]:.5f}  "
          f"|C-C_s|>1e-5 out to node {k4} (r={g['r'][k4]*100:.4f} cm), "
          f">5e-5 out to node {k5} (r={g['r'][k5]*100:.4f} cm)")
    print(f"          sqrt(Dt)={dlt:.6f} cm = {dlt/(g['dr']*100):.2f} cells ; "
          f"node8 r={g['r'][8]*100:.4f} cm = {g['r'][8]*100/dlt:.3f}*sqrt(Dt)")
    print(f"          monotonically rising from surface? "
          f"{bool(np.all(np.diff(Cc[:12]) > 0))}  first 10 nodes: {np.round(Cc[:10],5)}")
