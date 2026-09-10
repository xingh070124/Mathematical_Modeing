"""
AUDIT SCRIPT 1 -- Claims C4 (interior diagonal), C7 (axis node), C8 (surface node),
and the alpha plausibility check.

Everything is re-derived here with sympy from the user's own stated difference
formula; nothing is taken from q1_solve.py.

Run:  python src/audit_coeffs.py
"""

from __future__ import annotations

import os
import sys

import numpy as np
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_common import ALPHA, KCOND, CP, RHO, R0, HCONV  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

hr = lambda s: (print("=" * 94), print(s), print("=" * 94))

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "outputs", "audit")


def c4():
    hr("C4. Interior diagonal b_i from the user's own stated difference formula")
    i, dr, al, dt = sp.symbols("i dr alpha dt", positive=True)
    Tm, T0s, Tp = sp.symbols("T_{i-1} T_i T_{i+1}")

    # user's stated conservative form, verbatim:
    #   (1/r_i) * [ r_{i+1/2}(T_{i+1}-T_i)/dr - r_{i-1/2}(T_i-T_{i-1})/dr ] / dr
    # with r_i = i*dr, r_{i+-1/2} = (i+-1/2)*dr
    expr = sp.expand(
        (1 / (i * dr)) * (
            ((i + sp.Rational(1, 2)) * dr * (Tp - T0s) / dr)
            - ((i - sp.Rational(1, 2)) * dr * (T0s - Tm) / dr)
        ) / dr
    )
    a_i = sp.simplify(expr.coeff(Tm))
    b_i = sp.simplify(expr.coeff(T0s))
    c_i = sp.simplify(expr.coeff(Tp))
    rowsum = sp.simplify(a_i + b_i + c_i)
    print("  --- the operator L(T) = (1/r)(r*alpha*T')' has L-coefficients ---")
    print(f"  L coefficient of T_(i-1) = {a_i}   ; of T_i = {b_i} ; of T_(i+1) = {c_i}")
    print(f"  operator row sum = {rowsum}   (exact zero: {sp.simplify(rowsum)==0})")
    print("  --- the user's tridiagonal system is (1/dt)*(T^{n+1}-T^n) = L(T^{n+1}), i.e.")
    print("      a_i = -L_{i-1},  b_i = 1/dt - L_i,  c_i = -L_{i+1},  d_i = T_i^n/dt ---")
    a_tri = sp.simplify(-a_i * al)
    b_tri_corr = sp.simplify(1 / dt - b_i * al)
    b_tri_user = sp.simplify(1 / dt + (2 * i + 1) / (2 * i * dr ** 2) * al)
    c_tri = sp.simplify(-c_i * al)
    print(f"  a_i = {a_tri}   (user wrote {sp.simplify(-(i - sp.Rational(1,2))/(i*dr**2)*al)})")
    print(f"  c_i = {c_tri}   (user wrote {sp.simplify(-(i + sp.Rational(1,2))/(i*dr**2)*al)})")
    print(f"  b_i correct = {b_tri_corr}   (= 1/dt + 2*alpha/dr^2)")
    print(f"  b_i user    = {b_tri_user}   (= 1/dt + (i+1/2)/(i dr^2) alpha)")
    print(f"  b_user == -c_i (|c_i|) ? {sp.simplify(b_tri_user - 1/dt + c_tri) == 0}")
    diff = sp.simplify(b_tri_user - b_tri_corr)
    print(f"  b_user - b_correct = {diff}   (= -(2i-1)/(2i dr^2) alpha = a_i)")
    print(f"  b_user - b_correct == a_i (i.e. the deficit is exactly a_i, magnitude |a_i|) ? "
          f"{sp.simplify(diff - a_tri) == 0}")
    rsu = sp.simplify((a_tri + b_tri_user + c_tri) - 1 / dt)
    rsc = sp.simplify((a_tri + b_tri_corr + c_tri) - 1 / dt)
    print(f"  operator row sum (dropping 1/dt): correct = {rsc}, user = {rsu}")
    print(f"  user operator row sum == -(2i-1)/(2i dr^2) alpha ? "
          f"{sp.simplify(rsu + (2*i-1)/(2*i*dr**2)*al) == 0}"
          f"   ; == -(1-2i)/(2i dr^2) alpha ? "
          f"{sp.simplify(rsu - (-(1-2*i)/(2*i*dr**2)*al)) == 0}")
    print("  NOTE: in the  dT/dt = A*T  convention used by the repo's E1 check the same row sum")
    print("        appears with the OPPOSITE sign, +alpha*(2i-1)/(2i dr^2) (= A_u.sum(axis=1)).")

    # numeric spot check at M=200
    M = 200
    drv = R0 / M
    print(f"  numeric spot check M=200, dr={drv:g} m:")
    for i_ in (1, 2, 100, 199):
        bn = (2 * i_ + 1) / (2 * i_ * drv ** 2) * ALPHA
        bc = 2 * ALPHA / drv ** 2
        an = -(i_ - 0.5) / (i_ * drv ** 2) * ALPHA
        cn = -(i_ + 0.5) / (i_ * drv ** 2) * ALPHA
        print(f"    i={i_:>4}: a_i={an:+.6e}  b_user={bn:+.6e}  b_corr={bc:+.6e}  c_i={cn:+.6e}  "
              f"|a|={-an:.6e}  b_user-b_corr={bn-bc:+.6e}  rowsum_user={an+bn+cn:+.6e}")
    return


def c7():
    hr("C7. Axis node i=0")
    print("  Node-centred FV at r=0: V_0 = pi*(dr/2)^2, only outer face A_{1/2} = 2*pi*(dr/2).")
    print("  dT_0/dt = alpha*A_{1/2}*(T_1-T_0)/(dr*V_0) = alpha*pi*dr*(T_1-T_0)/(dr*pi*dr^2/4)")
    print("          = 4*alpha*(T_1-T_0)/dr^2")
    dr_, al = sp.symbols("dr alpha", positive=True)
    T0s, T1s = sp.symbols("T_0 T_1")
    FV = sp.simplify(al * (sp.pi * dr_) * (T1s - T0s) / (dr_ * sp.pi * dr_ ** 2 / 4))
    LH = sp.simplify(2 * al * 2 * (T1s - T0s) / dr_ ** 2)   # L'Hopital: 2*alpha*d2T/dr2, d2T = 2(T1-T0)/dr^2
    print(f"  FV form      = {FV}")
    print(f"  L'Hopital f. = {LH}")
    print(f"  identical: {sp.simplify(FV - LH) == 0}")
    M = 200
    drv = R0 / M
    print(f"  numeric M=200: b_0 = 1/dt + {4*ALPHA/drv**2:.6e},  c_0 = -{4*ALPHA/drv**2:.6e}")
    print("  user wrote  b_0 = 1/dt + 4*alpha/dr^2, c_0 = -4*alpha/dr^2  -> MATCH")
    return


def c8():
    hr("C8. Surface node i=M: derive the half-control-volume balance")
    dr_, al, h, k, rho, cp = sp.symbols("dr alpha h k rho cp", positive=True)
    R, M = sp.symbols("R M", positive=True)

    # --- (a) node-centred half CV [R-dr/2, R]
    V_M = sp.simplify(sp.pi * (R ** 2 - (R - dr_ / 2) ** 2))
    A_in = 2 * sp.pi * (R - dr_ / 2)
    A_out = 2 * sp.pi * R
    a_M = sp.simplify(-al * A_in / (dr_ * V_M))
    g_h = sp.simplify(A_out * h / (rho * cp * V_M))
    print("  (a) node-centred HALF CV  [R-dr/2, R]  (the grid the user actually uses:")
    print("      dr = R/M, r_M = R is a node, r_{M-1/2} = R-dr/2 is the inner face)")
    print(f"      V_M      = {V_M}")
    print(f"      A_in     = {A_in}")
    print(f"      a_M      = -alpha*A_in/(dr*V_M) = {sp.simplify(a_M)}")
    print(f"               = -2*alpha/dr^2 * (R-dr/2)/(R-dr/4)")
    a_M_lim = sp.simplify(sp.series(a_M.subs(dr_, R / M), M, sp.oo, 2).removeO())
    g_lim = sp.simplify(sp.series(g_h.subs(dr_, R / M), M, sp.oo, 2).removeO())
    ratio_a = sp.simplify(a_M.subs(dr_, R / M) / (-2 * al / (R / M) ** 2))
    ratio_g = sp.simplify(g_h.subs(dr_, R / M) / (2 * al * h / (k * (R / M))))
    print(f"      M->inf : a_M/(-2*alpha/dr^2) = {sp.simplify(ratio_a)}"
          f"  = 1 - 1/(4M) + O(M^-2)  -> 1")
    print(f"               g_h/[2*alpha*h/(k dr)] = {sp.simplify(ratio_g)} = 1 + 1/(4M) + O(M^-2) -> 1")
    print(f"             user wrote a_M = -2*alpha/dr^2, b_M = 2*alpha/dr^2 + 2*alpha*h/(k*dr) + 1/dt")
    # exact relative correction at M=200
    for Mv in (50, 100, 200, 400):
        f_a = (1 - 1 / (2 * Mv)) / (1 - 1 / (4 * Mv))
        f_g = 1 / (1 - 1 / (4 * Mv))
        print(f"        M={Mv:>4}: a_M/user = {f_a:.8f} (rel {f_a-1:+.3e}) ;  "
              f"g_h/user = {f_g:.8f} (rel {f_g-1:+.3e})")

    # --- (b) cell-centred FULL cell [R-dr, R] (the variant the claim warns about)
    V_F = sp.simplify(sp.pi * (R ** 2 - (R - dr_) ** 2))
    A_in_F = 2 * sp.pi * (R - dr_)
    a_F = sp.simplify(-al * A_in_F / (dr_ * V_F))
    g_F = sp.simplify(A_out * h / (rho * cp * V_F))
    print("  (b) cell-centred FULL CV [R-dr, R]:")
    print(f"      V_M = {V_F}, A_in = {A_in_F}")
    rF = sp.simplify(a_F.subs(dr_, R / M) / (-2 * al / (R / M) ** 2))
    rgF = sp.simplify(g_F.subs(dr_, R / M) / (2 * al * h / (k * (R / M))))
    print(f"      a_M/(-2*alpha/dr^2) = {rF} -> 1/2   (factor 2 OFF)")
    print(f"      g_h/[2*alpha*h/(k dr)] = {rgF} -> 1/2  (factor 2 OFF)")
    print("      -> a full-cell CV reproduces NEITHER of the user's two surface numbers unless a")
    print("         factor 2 is recovered elsewhere; so the user's numbers are the half-CV ones.")

    # --- (c) exact discrete half-CV coefficients with the repo geometry, numeric
    print("  (c) exact discrete half-CV coefficients at M=200 (geometry of audit_common.geom):")
    from audit_common import geom
    for Mv in (200, 400):
        drv, r, V, A_m, A_p = geom(Mv)
        a_num = -ALPHA * A_m[Mv] / (drv * V[Mv])
        b_cond = ALPHA * A_m[Mv] / (drv * V[Mv])
        g_num = 2 * np.pi * R0 * HCONV / (RHO * CP * V[Mv])
        print(f"      M={Mv}: a_M={a_num:.10e} (user-form -2a/dr^2={-2*ALPHA/drv**2:.10e}, "
              f"rel {a_num/(-2*ALPHA/drv**2)-1:+.3e})")
        print(f"            b_cond={b_cond:.10e}, g_h={g_num:.10e} "
              f"(user-form 2ah/(k dr)={2*ALPHA*HCONV/(KCOND*drv):.10e}, rel {g_num/(2*ALPHA*HCONV/(KCOND*drv))-1:+.3e})")
        print(f"            V_M exact = {V[Mv]:.6e}, 2*pi*R*dr/2 = {np.pi*R0*drv:.6e} "
              f"(rel {V[Mv]/(np.pi*R0*drv)-1:+.3e})")
    return


def alpha_check():
    hr("alpha plausibility")
    a = KCOND / (RHO * CP)
    print(f"  alpha = k/(rho cp) = {KCOND}/({RHO}*{CP}) = {a:.10e} m^2/s")
    print(f"  user's stated value 1.679e-7 ;  ratio correct/user = {a/1.679e-7:.8f}")
    print(f"  relative error (correct-user)/user   = {a/1.679e-7-1:+.6%}")
    print(f"  relative error (user-correct)/correct= {1.679e-7/a-1:+.6%}")
    print(f"  1/alpha = {1/a:.4f} s/m^2 ; R^2/alpha = {R0**2/a:.3f} s")
    return a


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    c4()
    c7()
    c8()
    alpha_check()
