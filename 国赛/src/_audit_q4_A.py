# -*- coding: utf-8 -*-
"""AUDIT q4 - probe 1: sign/magnitude of the semi-discrete RHS at t=0 uniform C.

Checks (a) whether the surface term implemented in make_rhs has the sign the
stated PDE requires, (b) the total water budget of the semi-discrete RHS, and
(c) the R^2 normalisation question.
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from q4_solve import (geometry_xi, make_rhs, Q4Radius, props_p, APP,
                      Dfun_p, T0K, C0, HM, H_CONV, CSTAR)
from q3_solve import Q3Env
from q1_solve import load_attachment1

M = 8
g = geometry_xi(M)
n = g["n"]
t1, T1, C1 = load_attachment1()
env = Q3Env(t1, T1, C1)
rad = Q4Radius()
rhs4 = make_rhs(g, env, rad, params=APP["app4"])

tprobe = 3600.0
Rc = float(rad.R(tprobe))
U = np.concatenate([np.full(n, T0K + 20.0), np.full(n, C0)])
F = rhs4(tprobe, U)
FC = F[n:]
FT = F[:n]

print("=" * 74)
print("PROBE 1: make_rhs surface-term sign, t = %.0f s, R = %.6f m" % (tprobe, Rc))
print("=" * 74)
Cinf = env.C(tprobe)
Tinf = env.T(tprobe)
rho, cp, k, _, _, _ = props_p(np.full(n, C0), APP["app4"])
Dv = Dfun_p(np.full(n, C0), np.full(n, T0K + 20.0), APP["app4"])
print("C inf =", Cinf, " T inf (K) =", Tinf)
print("uniform C0 =", C0, "-> (C[0]-Cinf) =", C0 - Cinf, " (positive: interior wetter)")
print("D(C0,T) =", Dv[0], " k(C0) =", k[0], " hm =", HM)
print()
print("rhs dC/dt per node (should ALL be NEGATIVE for drying):")
for i in range(n):
    print("   i=%d xi=%.3f  dC/dt=%+.6e" % (i, g["xi"][i], FC[i]))
print()
print("surface node dC/dt = %+.6e   (negative = losing water = OK)" % FC[-1])
print("interior node  dC/dt = %+.6e" % FC[1])

# --- analytic check of the stated PDE's water budget -----------------------
# Stated PDE:  dC/dt = (1/(xi R^2)) d/dxi( xi D dC/dxi )
# Interior: uniform C -> 0 exactly.
# Discrete surface (node M, half control volume Delta xi^2(3M-1)/6):
#   the discrete source must equal -(hm R (C-Cinf))/... i.e. NEGATIVE.
print()
print("--- discrete surface source as implemented ---")
s = 1.0 / (Rc * Rc)
flux_w = HM * Rc * (C0 - Cinf)
term = -flux_w * s / g["MLg"][M]
print(" -flux_w * s / MLg[M] = %+.6e   (negative -> drying)" % term)
print(" note: hm*R^2*(C-Cinf)/2 = %+.6e" % (HM * Rc * Rc * (C0 - Cinf) / 2.0))
print(" ratio (implied coeff)/(R^2/2) =", abs(term) / (HM * Rc * Rc * (C0 - Cinf) / 2.0) * g["MLg"][M])

# --- reconstruct the implied radius entering the surface flux --------------
# dC_M/dt = -hm (C_M - Cinf) * X / (R^2 * MLg[M])  -> X = ?
X = abs(FC[-1]) * (Rc ** 2) * g["MLg"][M] / (HM * (C0 - Cinf))
print()
print("implied geometric factor X in surface term = %.6f" % X)
print("  X should be R(t) if the stated PDE/BC pair is faithful; R = %.6f m" % Rc)
print("  X / R(t) = %.4f   (= 1/R(t) = %.4f per m? see note)" % (X / Rc, 1.0 / Rc))
print("  X/(R^2/2) = %.4f" % (X / (Rc ** 2 / 2)))

# --- what the analytic PDE says the surface coefficient should be ----------
# For dC/dt = (1/(xi R^2)) d/dxi(xi D dC/dxi) on [0,1] nodes, node M has
# half-cell volume MLg[M] = dxi*(r_{M-1}+2 r_M)/6.  Discretising the flux
# divergence: the surface boundary flux enters as -A_s*J / V where
# A_s = 2 pi R (per unit length), V_cell = pi dxi2 R^2 ... derive below.
print()
print("--- what a faithful discretisation of the STATED equation gives ---")
# The stated equation in physical terms is
#   d/dt( int beta C 2 pi r dr ) = [2 pi r beta D dC/dxi / R]
# so the surface term is  -2 pi R beta_phys J / (cell mass).
# With beta_phys = rho/(1+C) evaluated at the surface:
beta_s = (APP["app4"]["rho0"] + APP["app4"]["krho"] * C0) / (1.0 + C0)
print(" surface beta = rho/(1+C) =", beta_s)
J = HM * (C0 - Cinf)                      # kg/(m^2 s) physical surface flux
print(" physical surface mass flux J =", J, "kg/(m2 s)")
# cell dry mass per unit length in material coordinate xi_M cell:
dxi = g["dr"]
dxi2 = 1.0 ** 2 - (1.0 - dxi) ** 2
m_cell = beta_s * np.pi * dxi2 * float(rad.R(0.0)) ** 2
print(" cell dry mass/len m_M = %.6e" % m_cell)
dCdt_faithful = -2 * np.pi * Rc * beta_s * J / m_cell
print(" faithful dC_M/dt = %+.6e" % dCdt_faithful)
print(" implemented      = %+.6e" % FC[-1])
print(" ratio implemented/faithful = %.6f" % (FC[-1] / dCdt_faithful))
