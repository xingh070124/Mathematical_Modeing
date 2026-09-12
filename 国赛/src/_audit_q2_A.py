# -*- coding: utf-8 -*-
"""Independent adversarial audit of Q2 claims C1..C7. Reads only primary artefacts."""
from __future__ import annotations
import io, os, sys, csv, math
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")

def hr(t):
    print("\n" + "=" * 78 + "\n" + t + "\n" + "=" * 78)

# ---------------------------------------------------------------- C1 algebra
hr("C1  mixture relation  rho(C)=650+128C , cp(C)=1450+2736C/(C+1)")
# Try to solve rho_s(1+C) = 650+128C and rho_s(cs + C cl) = rho(C)*cp(C)
Cs = np.array([0.05, 0.15, 0.5, 1.0, 2.0, 2.55])
rho = 650 + 128 * Cs
cp = 1450 + 2736 * Cs / (Cs + 1)
A = rho * cp
rs = rho / (1 + Cs)
print("rho_s implied = ", rs)
print("rho_s is constant?  spread =", rs.max() - rs.min())
# Solve the two equations exactly with rational arithmetic.
import sympy as sp
C, cs, cl, rs_ = sp.symbols("C cs cl rs_", positive=True)
rho_sym = 650 + 128 * C
cp_sym = 1450 + 2736 * C / (C + 1)
eq1 = sp.Eq(rs_ * (1 + C), rho_sym)
eq2 = sp.Eq(rs_ * (cs + C * cl), rho_sym * cp_sym)
sol = sp.solve([eq1, eq2], [cs, cl, rs_], dict=True)
print("sympy exact solution:", sol)
cs_v, cl_v = sp.Rational(1450), sp.Rational(4186)
diff = sp.simplify((650 + 128 * C) * cp_sym - (650 + 128 * C) / (1 + C) * (cs_v + C * cl_v))
print("residual of the claimed (cs,cl) with rho_s=rho/(1+C):", sp.simplify(diff))

# is the pair unique? parametrise: rho_s = (650+128C)/(1+C) is NOT constant ->
# the 'mixture' reading cannot hold for all C with constant rho_s.
print("rho_s(C) from rho/(1+C):", [sp.nsimplify(v) for v in sp.simplify(rho_sym/(1+C)).as_numer_denom()])
# ---- alternative (rho_s, cs, cl) fit over a C-range: least squares
from scipy.optimize import least_squares
def res(p):
    rs_, cs_, cl_ = p
    return np.concatenate([rs_ * (1 + Cs) - rho, rs_ * (cs_ + Cs * cl_) - A])
for guess in ([275.0, 1450, 4186], [300, 1400, 4000], [581, 1450, 4186]):
    r = least_squares(res, guess)
    print(f"  LSQ from {guess}: rho_s={r.x[0]:.6f} cs={r.x[1]:.6f} cl={r.x[2]:.6f} "
          f"max|res|={np.max(np.abs(r.fun)):.4e}")

# spurious source magnitude
Tref = 28.0
rho_s = float(rho_sym.subs(C, 2.55) / (1 + 2.55))
dCdt = -8.3185185185185e-05
dTdt = 1e-3
rcp = float((rho_sym * cp_sym).subs(C, 2.55))
Sf = 4186 * 7.0 * rho_s * abs(dCdt)
main = rcp * dTdt
print(f"\nrho_s(C0)={rho_s:.6f}  rho*cp(C0)={rcp:.1f}")
print(f"S_false(c_l=4186,T-Tref=7)={Sf:.4f}  main(rho cp dT/dt, dT/dt=1e-3)={main:.4f}  ratio={Sf/main:.6f}")
# what (T-Tref) and cs/cl would make ratio 0.2520228 exactly?
print("registry EC_Sfalse = 656.0475, EC_main = 2603.1272 -> ratio",
      f"{656.04748410407/2603.1272:.8f}")
print("=> implied (T-Tref) =", 656.04748410407 / (4186 * rho_s * abs(dCdt)))
print("=> implied dT/dt =", 2603.1272 / rcp)

# ---------------------------------------------------------------- C2 mass matrix
hr("C2  lumped mass: r=0 coefficient and interior identity (from problem2.md element matrix)")
def elem_mass(a, b, dr):
    return dr / 12.0 * np.array([[3 * a + b, a + b], [a + b, a + 3 * b]])
for M in (10, 100, 800, 1600, 3200):
    dr = 0.02 / M
    r = np.arange(M + 1) * dr
    # assemble row-sum lumped mass by summation over element rows
    ML = np.zeros(M + 1)
    for e in range(M):
        Me = elem_mass(r[e], r[e + 1], dr)
        ML[e] += Me[0, 0] + Me[0, 1]
        ML[e + 1] += Me[1, 0] + Me[1, 1]
    # stiffness diagonal (geometry only, no k)
    Gd = np.zeros(M + 1)
    for e in range(M):
        Gd[e] += 0.5 * (r[e] + r[e + 1]) / dr
        Gd[e + 1] += 0.5 * (r[e] + r[e + 1]) / dr
    ratio = (Gd[0] / ML[0]) / (4.0 / dr ** 2)
    print(f"  M={M:5d} ML[0]={ML[0]:.6e} dr^2/6={dr**2/6:.6e} "
          f"ML[M]={ML[M]:.6e} dr^2(3M-1)/6={dr**2*(3*M-1)/6:.6e} "
          f"K00/M00 = {Gd[0]/ML[0]*dr**2:.6f} alpha/dr^2 (exact 4) ratio={ratio:.6f}")
    print(f"        interior max rel dev from dr*r_i: "
          f"{np.max(np.abs(ML[1:M]-dr*r[1:M]))/np.max(np.abs(ML)):.3e}")
