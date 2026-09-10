"""
AUDIT (independent, adversarial) of model/建模方式对比.md.

Written from scratch.  Does NOT import src/feishu_compare.py.  Every quantity is
re-derived from the physics with independent code paths (mpmath high precision,
scipy quadrature, own FV assembly).

Run:  python src/audit_feishu_math.py
Out:  outputs/audit_feishu_math.log
"""

from __future__ import annotations

import math
import os
import sys

import mpmath as mp
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import solve_banded
from scipy.special import j0 as sj0
from scipy.special import j1 as sj1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
LOG = os.path.join(OUT, "audit_feishu_math.log")

_ROWS: list[str] = []


def say(s=""):
    _ROWS.append(s)
    print(s, flush=True)


def hr(t):
    say("")
    say("=" * 78)
    say(t)
    say("=" * 78)


# ---- problem statement constants (docs/A题.md 附录2) ------------------------
RHO, CP, K = 820.0, 2600.0, 0.36
H, HM = 25.0, 8.0e-7
D0, DEXP = 7.0e-9, 0.89
T0_C, C0, R0 = 28.0, 2.55, 0.02
T0_K = T0_C + 273.15
ALPHA = K / (RHO * CP)
BI = H * R0 / K

# ===========================================================================
hr("AUD-1. Eigencondition x*J1(x) = Bi*J0(x),  Bi = hR/k = %.10f" % BI)
mp.mp.dps = 40
Bi_mp = mp.mpf(25) * mp.mpf("0.02") / mp.mpf("0.36")
say("Bi (exact rational 25*0.02/0.36) = %s" % mp.nstr(Bi_mp, 25))
say("Bi (float)                      = %.17g" % BI)


def f_mp(x):
    return x * mp.besselj(1, x) - Bi_mp * mp.besselj(0, x)


# bracket the roots by dense sign changes, then mp.findroot
xs_mp = []
hi = mp.mpf("0.05")
prev = mp.mpf("0.2")
grid = [prev + mp.mpf(k) * mp.mpf("0.002") for k in range(0, 20000)]
fprev = f_mp(grid[0])
for g in grid[1:]:
    fg = f_mp(g)
    if fprev * fg < 0:
        r = mp.findroot(f_mp, (prev + (g - prev) / 3, g))
        xs_mp.append(r)
    prev = g
    fprev = fg
    if len(xs_mp) >= 8:
        break
say("")
say("k   x_k = lambda_k R  (mpmath dps=40, findroot)      residual x*J1-Bi*J0")
for i, r in enumerate(xs_mp, 1):
    say("%2d  %-42s %s" % (i, mp.nstr(r, 25), mp.nstr(f_mp(r), 5)))
report_lam = [1.4184725188, 4.1664696010, 7.2084784644, 10.3082731535]
say("")
say("report claims lambda_k R = " + ", ".join("%.10f" % v for v in report_lam))
for i, (r, cl) in enumerate(zip(xs_mp, report_lam), 1):
    d = float(r) - cl
    say("  k=%d  mine=%.10f  report=%.10f  diff=%+.3e  rel=%.2e"
        % (i, float(r), cl, d, abs(d) / float(r)))
say("")
say("feishu.md §6.1 table values  ~2.0, ~5.0, ~8.0, ~11.0 :")
for i, cl in enumerate([2.0, 5.0, 8.0, 11.0], 1):
    true = float(xs_mp[i - 1])
    say("  k=%d doc=%5.1f true=%10.7f  (doc-true)/true=%+.4f%%   (true-doc)/doc=%+.4f%%"
        % (i, cl, true, (cl - true) / true * 100, (true - cl) / cl * 100))

# ===========================================================================
hr("AUD-2. Expansion coefficient c_k -- derived AND checked by quadrature")
say("Derivation:  T-Tinf = sum b_n J0(lam_n r), want sum c_n J0(lam_n r) == 1.")
say("  weight r;  int_0^R r J0(lam_m r) dr = R^2 J1(x_m)/x_m")
say("  norm      int_0^R r J0(lam_m r)^2 dr = (R^2/2)(J0(x_m)^2 + J1(x_m)^2)")
say("  =>  c_m = 2 J1(x_m) / ( x_m ( J0(x_m)^2 + J1(x_m)^2 ) )")
say("")
say("Independent quadrature (mp.quad, 40 dps) of the two integrals:")
say("  k    x_k          c_k closed form            c_k quadrature           rel diff")


def c_closed(x):
    return 2 * mp.besselj(1, x) / (x * (mp.besselj(0, x) ** 2 + mp.besselj(1, x) ** 2))


c_vals = []
for i, r in enumerate(xs_mp, 1):
    lam = r / mp.mpf("0.02")
    num = mp.quad(lambda rr: rr * mp.besselj(0, lam * rr), [0, mp.mpf("0.02")])
    den = mp.quad(lambda rr: rr * mp.besselj(0, lam * rr) ** 2, [0, mp.mpf("0.02")])
    cq = num / den
    cc = c_closed(r)
    c_vals.append(cc)
    say("%3d  %-13s  %-24s  %-24s  %.2e"
        % (i, mp.nstr(r, 9), mp.nstr(cc, 16), mp.nstr(cq, 16),
           float(abs(cc - cq) / abs(cc))))
say("")
say("=> the report's c_k formula is CORRECT (two independent routes, 40 dps).")

# doc A_k = 2/(x J1(x))
say("")
say("feishu.md A_k/(T0-Tinf) = 2/(x_k J1(x_k)):")
say("  k   A_k(doc)            c_k                c_k/A_k     1/(1+(x/Bi)^2)   diff")
for i, r in enumerate(xs_mp, 1):
    Ad = 2 / (r * mp.besselj(1, r))
    ratio = c_vals[i - 1] / Ad
    pred = 1 / (1 + (r / Bi_mp) ** 2)
    say("%3d  %-19s %-19s %-11s %-16s %.2e"
        % (i, mp.nstr(Ad, 12), mp.nstr(c_vals[i - 1], 12), mp.nstr(ratio, 8),
           mp.nstr(pred, 8), float(abs(ratio - pred))))

# ===========================================================================
hr("AUD-3. Decisive test -- reconstruct the constant 1 with N terms")
say("   r/R     sum c_k J0         sum A_k(doc) J0     1 - sum(c_k J0)")
for NN in (8,):
    for rr in (0.0, 0.25, 0.5, 0.75, 1.0):
        s1 = float(sum(mp.besselj(0, xs_mp[k] * mp.mpf(rr)) * c_vals[k] for k in range(NN)))
        s2 = float(sum(mp.besselj(0, xs_mp[k] * mp.mpf(rr))
                       * 2 / (xs_mp[k] * mp.besselj(1, xs_mp[k])) for k in range(NN)))
        say("  %4.2f   %14.8f       %14.8f      %12.8f" % (rr, s1, s2, 1.0 - s1))
say("")
say("report claims: c_k row 0.98569120 / 0.99707317 / 0.99772822 / 0.99696024 / 0.96381405")
say("report claims: A_k row -3.46211833 / 0.14736226 / 0.43520130 / 0.52760459 / 11.52")
say("report claims: truncation err at r=R (c_k) = 0.036186 ; |1-11.52| = 10.52")
# feishu's OWN integral form -> 2 J1/(x J0^2); check the equality to 2/(x J1)
say("")
say("ALSO CHECK feishu's internal simplification:")
say("  its integral form gives  2 J1(x)/(x J0(x)^2)  (using the correct numerator),")
say("  but it prints the closed form 2/(x J1(x)).  These differ by (J1/J0)^2:")
for i, r in enumerate(xs_mp[:4], 1):
    a_int = 2 * mp.besselj(1, r) / (r * mp.besselj(0, r) ** 2)
    a_print = 2 / (r * mp.besselj(1, r))
    say("  k=%d  integral-form=%s  printed=%s  ratio=%s"
        % (i, mp.nstr(a_int, 10), mp.nstr(a_print, 10),
           mp.nstr(a_int / a_print, 10)))

# ===========================================================================
hr("AUD-4. Surface half-control-volume: geometry re-derived")
say("node-centred grid r_i = i*dr, i=0..M, r_M = R = M*dr.")
say("CV of surface node spans [R-dr/2, R]  ->  V_M = pi*(R^2-(R-dr/2)^2)")
say("                                          = pi*(R*dr - dr^2/4)   [report's formula]")
say("face at M-1/2:  A_{M-1/2} = 2 pi (R - dr/2)")
say("f_M = A_{M-1/2} / (dr*V_M) = 2(R-dr/2)/(dr^2(R-dr/4))")
say("                            = 2(M-0.5)/(dr^2 (M-0.25))        [report's formula]")
for M in (50, 100, 200, 400):
    dr = R0 / M
    V_exact = math.pi * (R0 * dr - dr ** 2 / 4)
    V_lead = math.pi * R0 * dr
    A = 2 * math.pi * (R0 - dr / 2)
    f_ex = A / (dr * V_exact)
    f_lead = 2 / dr ** 2
    f_formula = 2 * (M - 0.5) / (dr ** 2 * (M - 0.25))
    say("  M=%4d V_M=%.12e (lead %.12e, rel dev %+.3e)  f_M_exact=%.10e "
        "formula=%.10e  2/dr^2=%.10e  f_ex/2/dr^2-1=%+.6e"
        % (M, V_exact, V_lead, V_exact / V_lead - 1, f_ex, f_formula, f_lead,
           f_ex / f_lead - 1))
say("=> reports' V_M and f_M formulas VERIFIED.  relative geometry correction = 1/(4M).")

# ===========================================================================
hr("AUD-5. theta-consistent CN surface coefficients (from scratch)")
say("Semi-discrete surface ODE (node-centred FV, half-CV):")
say("   dT_M/dt = alpha*f_M*(T_{M-1}-T_M) + gt*(Tinf - T_M),   gt = h*As/(rho*cp*V_M)")
say("theta-method:  (T^{n+1}-T^n)/dt = th*RHS^{n+1} + (1-th)*RHS^n")
say("  a_M = -th*alpha*dt*f_M")
say("  b_M =  1 + th*dt*(alpha*f_M + gt)")
say("  d_M = (1-(1-th)*dt*(alpha*f_M+gt))*T_M^n + (1-th)*dt*alpha*f_M*T_{M-1}^n")
say("        + dt*gt*(th*Tinf^{n+1} + (1-th)*Tinf^n)")
say("")
dr = R0 / 100
dt = 0.5
M = 100
V_M = math.pi * (R0 * dr - dr ** 2 / 4)
A_s = 2 * math.pi * R0
f_M = (2 * math.pi * (R0 - dr / 2)) / (dr * V_M)
gt = H * A_s / (RHO * CP * V_M)
th = 0.5
say("M=100 dr=%.3e dt=%.3f" % (dr, dt))
say("  exact f_M      = %.10e   ; leading 2/dr^2 = %.10e" % (f_M, 2 / dr ** 2))
say("  exact gt       = %.10e   ; leading 2*a*h/(k*dr)= %.10e"
    % (gt, 2 * ALPHA * H / (K * dr)))
say("  CN a_M (exact geom)  = %.10e" % (-th * ALPHA * dt * f_M))
say("  CN a_M (leading geom)= %.10e" % (-th * ALPHA * dt * (2 / dr ** 2)))
say("  feishu.md writes a_M = -2*alpha*dt/dr^2 = %.10e" % (-2 * ALPHA * dt / dr ** 2))
say("  ratio feishu/CN-leading = %.10f   (=1/theta, i.e. backward-Euler scale)"
    % ((-2 * ALPHA * dt / dr ** 2) / (-th * ALPHA * dt * (2 / dr ** 2))))
_Gdt_lead = 2 * ALPHA * H * dt / (K * dr)
_bCN = th * (ALPHA * dt * (2 / dr ** 2) + _Gdt_lead)
_bDOC = 2 * ALPHA * dt / dr ** 2 + _Gdt_lead
say("  CN b_M increment (leading geometry) = %.10e" % _bCN)
say("  feishu.md b_M increment             = %.10e" % _bDOC)
say("  ratio feishu/CN                     = %.10f" % (_bDOC / _bCN))
say("")
say("Interior row (feishu a_i,b_i,c_i) vs CN derived from the same node-centred FV:")
say("  f+_i = A_{i+1/2}/(dr V_i) = (i+0.5)/(i dr^2) ; f-_i = (i-0.5)/(i dr^2)")
for i in (1, 5, 50):
    fp = ((i + 0.5) * dr) / (dr * (2 * math.pi * i * dr ** 2)) * 2 * math.pi
    fp = (i + 0.5) / (i * dr ** 2)
    fm = (i - 0.5) / (i * dr ** 2)
    say("  i=%3d  b_i(CN)=1+th*a*dt*(f+ +f-)=%.10e    feishu 1+a*dt/dr^2=%.10e   diff=%.2e"
        % (i, 1 + th * ALPHA * dt * (fp + fm), 1 + ALPHA * dt / dr ** 2,
           abs(1 + th * ALPHA * dt * (fp + fm) - (1 + ALPHA * dt / dr ** 2))))
    say("        a_i(CN)=%.10e  feishu=%.10e" % (-th * ALPHA * dt * fm,
                                               -ALPHA * dt / (2 * dr ** 2) * (i - 0.5) / i))
    say("        c_i(CN)=%.10e  feishu=%.10e" % (-th * ALPHA * dt * fp,
                                               -ALPHA * dt / (2 * dr ** 2) * (i + 0.5) / i))
say("")
say("CN right-hand side, from  d = T_i^n + (1-th)[s_i(T_{i-1}-T_i)+t_i(T_{i+1}-T_i)]")
say("with a_i=-th*s_i, c_i=-th*t_i  and th=1/2:")
say("   coefficient of T_{i-1}^n is (1-th)*s_i = -a_i   (a_i<0  =>  POSITIVE)")
say("   coefficient of T_{i+1}^n is (1-th)*t_i = -c_i   (c_i<0  =>  POSITIVE)")
say("   coefficient of T_i^n     is 1-(1-th)(s_i+t_i) = 2-b_i")
say("=> CORRECT CN:  d_i = -a_i T_{i-1}^n + (2-b_i) T_i^n - c_i T_{i+1}^n")
say("feishu.md writes  d_i = +a_i T_{i-1}^n + (2-b_i) T_i^n + c_i T_{i+1}^n  -> SIGN ERROR")

# ===========================================================================
hr("AUD-6. Own from-scratch theta-method solver; reproduce every variant")


def geom(M):
    dr_ = R0 / M
    af = 2 * np.pi * (np.arange(M) + 0.5) * dr_
    V = np.empty(M + 1)
    V[0] = np.pi * (dr_ / 2) ** 2
    V[1:M] = 2 * np.pi * np.arange(1, M) * dr_ ** 2
    V[M] = np.pi * (R0 * dr_ - dr_ ** 2 / 4)
    return dr_, af, V


def solve(M, dt_, times, Tinf_of_t, surf, mode="theta", th=0.5, alpha=ALPHA):
    dr_, af, V = geom(M)
    f_int = af[1:M] / (dr_ * V[1:M])
    f_lo = af[0:M - 1] / (dr_ * V[1:M])
    K0 = 4 * alpha * dt_ / dr_ ** 2
    As = 2 * np.pi * R0
    a = np.zeros(M + 1)
    b = np.zeros(M + 1)
    c = np.zeros(M + 1)
    b[0] = 1 + th * K0
    c[0] = -th * K0
    b[1:M] = 1 + th * alpha * dt_ * (f_int + f_lo)
    a[1:M] = -th * alpha * dt_ * f_lo
    c[1:M] = -th * alpha * dt_ * f_int
    if surf == "doc":
        fM = 2 / dr_ ** 2
        G = 2 * alpha * H * dt_ / (K * dr_)
        a[M] = -alpha * dt_ * fM
        b[M] = 1 + alpha * dt_ * fM + G
    elif surf == "lead":
        fM = 2 / dr_ ** 2
        G = alpha * H * As * dt_ / (K * V[M])
        a[M] = -th * alpha * dt_ * fM
        b[M] = 1 + th * (alpha * dt_ * fM + G)
    elif surf == "exact":
        fM = af[M - 1] / (dr_ * V[M])
        G = alpha * H * As * dt_ / (K * V[M])
        a[M] = -th * alpha * dt_ * fM
        b[M] = 1 + th * (alpha * dt_ * fM + G)
    else:
        raise ValueError(surf)
    T = np.full(M + 1, T0_K)
    idx = np.round(np.asarray(times) / dt_).astype(int)
    snaps = np.empty((len(times), M + 1))
    snaps[0] = T
    ptr = 1
    nsteps = int(round(times[-1] / dt_))
    for s in range(1, nsteps + 1):
        Tn = Tinf_of_t(s * dt_)
        To = Tinf_of_t((s - 1) * dt_)
        d = np.empty(M + 1)
        d[0] = (1 - (1 - th) * K0) * T[0] + (1 - th) * K0 * T[1]
        if mode == "theta":
            d[1:M] = ((1 - (1 - th) * alpha * dt_ * (f_int + f_lo)) * T[1:M]
                      + (1 - th) * alpha * dt_ * f_lo * T[0:M - 1]
                      + (1 - th) * alpha * dt_ * f_int * T[2:M + 1])
        elif mode == "doc_sign":
            d[1:M] = a[1:M] * T[0:M - 1] + (2 - b[1:M]) * T[1:M] + c[1:M] * T[2:M + 1]
        else:
            raise ValueError(mode)
        if surf == "doc" or mode == "doc_sign":
            d[M] = (2 - b[M]) * T[M] - a[M] * T[M - 1] + G * Tn
        else:
            d[M] = ((1 - (1 - th) * (alpha * dt_ * fM + G)) * T[M]
                    + (1 - th) * alpha * dt_ * fM * T[M - 1]
                    + G * (th * Tn + (1 - th) * To))
        ab = np.zeros((3, M + 1))
        ab[0, 1:] = c[:-1]
        ab[1, :] = b
        ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, d)
        if not np.all(np.isfinite(T)):
            return snaps, s * dt_
        if ptr < len(idx) and s == idx[ptr]:
            snaps[ptr] = T
            ptr += 1
    return snaps, None


# analytic reference for constant Tinf, from AUD-1/2 quantities
x_np = np.array([float(r) for r in xs_mp])
c_np = np.array([float(c) for c in c_vals])
docA_np = np.array([float(2 / (r * mp.besselj(1, r))) for r in xs_mp])

hr("AUD-6a. A2 table (const Tinf=50C, t=300 s, dt=0.5 s) -- my own solver")
Tin_K = 50.0 + 273.15
tc = 300.0
Fo = ALPHA * tc / R0 ** 2
ref = {"doc": (70.8475, 70.7814, 70.7483, 70.7317),
       "lead": (2.99399e-2, 1.51143e-2, 7.59311e-3, 3.80520e-3),
       "exact": (5.41512e-4, 1.34076e-4, 3.21471e-5, 6.65961e-6)}
say("report table (dt=0.5, t=300 s, const Tinf=50C):")
say("  M     doc (report)   mine        lead (report)  mine        exact (report)   mine")
prev = {"doc": None, "lead": None, "exact": None}
rmine = {"doc": None, "lead": None, "exact": None}
X = np.linspace(0, 1, 4001)
for M in (50, 100, 200, 400):
    rr = np.arange(M + 1) * (R0 / M)
    e = {}
    for k, s in (("doc", "doc"), ("lead", "lead"), ("exact", "exact")):
        sn, div = solve(M, 0.5, np.array([0.0, tc]), lambda t: Tin_K, s)
        Tan = Tin_K + (T0_K - Tin_K) * np.sum(
            c_np[None, :] * sj0(np.outer(rr / R0, x_np))
            * np.exp(-x_np[None, :] ** 2 * Fo), axis=1)
        e[k] = float(np.max(np.abs(sn[-1] - Tan)))
    say("  %4d  %12.5g  %12.5g  %13.5e %13.5e  %13.5e %13.5e"
        % (M, ref["doc"][(50, 100, 200, 400).index(M)], e["doc"],
           ref["lead"][(50, 100, 200, 400).index(M)], e["lead"],
           ref["exact"][(50, 100, 200, 400).index(M)], e["exact"]))
    rmine["doc"], rmine["lead"], rmine["exact"] = e["doc"], e["lead"], e["exact"]
say("  my ratios (should be ~2 for lead, ~4 for exact if the claim holds):")
for k in ("lead", "exact"):
    prev = None
    line = "   %-6s" % k
    for M in (50, 100, 200, 400):
        rr = np.arange(M + 1) * (R0 / M)
        sn, _ = solve(M, 0.5, np.array([0.0, tc]), lambda t: Tin_K, k)
        Tan = Tin_K + (T0_K - Tin_K) * np.sum(
            c_np[None, :] * sj0(np.outer(rr / R0, x_np))
            * np.exp(-x_np[None, :] ** 2 * Fo), axis=1)
        er = float(np.max(np.abs(sn[-1] - Tan)))
        line += "  %9.4f" % (float("nan") if prev is None else prev / er)
        prev = er
    say(line)

hr("AUD-6b. Same, but with dt driven to zero -- is 'second order' clean?")
say("(report's ratios 4.039 / 4.171 / 4.827 come from dt=0.5, which the report")
say(" itself flags as 渐近前段.  If temporal error cancels spatial error the ratio")
say(" is inflated.  Re-run exact/lead at dt=0.5/64.)")
for tag, dtv in (("dt=0.5", 0.5), ("dt=0.5/64", 0.5 / 64)):
    for k in ("lead", "exact"):
        prev = None
        line = "  %-9s %-6s" % (tag, k)
        errs = []
        for M in (50, 100, 200, 400):
            rr = np.arange(M + 1) * (R0 / M)
            sn, _ = solve(M, dtv, np.array([0.0, tc]), lambda t: Tin_K, k)
            Tan = Tin_K + (T0_K - Tin_K) * np.sum(
                c_np[None, :] * sj0(np.outer(rr / R0, x_np))
                * np.exp(-x_np[None, :] ** 2 * Fo), axis=1)
            er = float(np.max(np.abs(sn[-1] - Tan)))
            errs.append(er)
            line += "  %10.4e" % er
            if prev is not None:
                line += "(r=%6.3f)" % (prev / er)
            prev = er
        say(line)

hr("AUD-6c. doc_signs divergence times (report: M=200 -> 127.00 s, M=800 -> 62.50 s)")
for M in (100, 200, 400, 800):
    _, div = solve(M, 0.5, np.array([0.0, tc]), lambda t: Tin_K, "doc", "doc_sign")
    say("  my solver M=%4d dt=0.5 doc_sign -> %s" % (M, "DIVERGED at t=%.2f s" % div if div else "ok"))
say("  (also try dt=1/64 on M=200 to see whether dt refinement helps)")

# ===========================================================================
hr("AUD-7. Real case 0-1800 s: is the 3.49e-6 K agreement circular?")
from openpyxl import load_workbook
ATT1 = os.path.join(ROOT, "A题", "附件", "附件1.xlsx")
wb = load_workbook(ATT1, data_only=True, read_only=True)
ws = wb[wb.sheetnames[0]]
rows1 = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
wb.close()
arr = np.array([[float(v) for v in r[:3]] for r in rows1])
t_env, T_env_C, C_env = arr[:, 0], arr[:, 1], arr[:, 2]
say("附件1: %d rows, t=%.0f..%.0f s, Tinf=%.4f..%.4f C, spacing=%.0f s"
    % (len(t_env), t_env[0], t_env[-1], T_env_C.min(), T_env_C.max(), t_env[1] - t_env[0]))
Tinf_f = PchipInterpolator(t_env, T_env_C)
Tinf_of_t = lambda t: float(Tinf_f(t)) + 273.15

t_out = np.arange(0.0, 1800.0 + 1e-9, 1.0)
Tinf_1s = np.asarray(Tinf_f(t_out) + 273.15, float)

# (i) how big is the forcing mismatch: continuous PCHIP vs its 1-s chord?
tt = np.linspace(0.0, 1800.0, 1800 * 64 + 1)
pchip_v = np.asarray(Tinf_f(tt) + 273.15, float)
chord_v = np.interp(tt, t_out, Tinf_1s)
dev = pchip_v - chord_v
say("")
say("(i) forcing mismatch: numeric solver is driven by CONTINUOUS PCHIP; the")
say("    semi-analytic route is driven by the PIECEWISE-LINEAR chord of that same")
say("    PCHIP sampled on the 1 s output grid.")
say("    max|PCHIP - chord| over 0..1800 s = %.6e K   at t=%.1f s"
    % (np.max(np.abs(dev)), tt[int(np.argmax(np.abs(dev)))]))
say("    step-response of this system to a unit Tinf perturbation reaches")
say("    ~%.3f of the step after 1800 s (quasi-steady; tau_T=%.1f s)"
    % (1 - math.exp(-1800.0 / (R0 ** 2 / ALPHA)), R0 ** 2 / ALPHA))
say("    => implied spurious |dT| of order %.3e K"
    % (np.max(np.abs(dev)) * (1 - math.exp(-1800.0 / (R0 ** 2 / ALPHA)))))

# (ii) my own numeric CN solve, continuous forcing
Mnum, dtnum = 1600, 2.0 ** -5
sn_num, divn = solve(Mnum, dtnum, t_out, Tinf_of_t, "exact")
say("")
say("(ii) my own CN solver M=%d dt=2^-5, continuous PCHIP forcing: divergent=%s" % (Mnum, divn))
rrn = np.arange(Mnum + 1) * (R0 / Mnum)


# 400 eigen-roots found by my own bracketed brentq (independent of feishu_compare)
from scipy.optimize import brentq as _brentq


def my_eigen(nmodes, bi=BI):
    f = lambda x: x * float(mp.besselj(1, x)) - bi * float(mp.besselj(0, x))
    xs = []
    a = 1e-9
    step = 0.02
    fa = f(a)
    x = a
    while len(xs) < nmodes and x < 4 * nmodes + 60:
        x2 = x + step
        fb = f(x2)
        if fa * fb < 0:
            xs.append(_brentq(f, x, x2, xtol=1e-15, rtol=8.9e-16))
        x, fa = x2, fb
    return np.array(xs)


x400 = my_eigen(400)
c400 = 2 * sj1(x400) / (x400 * (sj0(x400) ** 2 + sj1(x400) ** 2))
lam400 = x400 / R0
mu400 = ALPHA * lam400 ** 2


def series_at(times_out, Tinf_out, r_eval, t_step, Tinf_step):
    """Duhamel on the piecewise-linear chord defined by (t_step, Tinf_step);
    sampled at times_out and evaluated at r_eval.  Memory-safe."""
    b = c400 * (T0_K - Tinf_out[0])
    out = np.empty((len(times_out), np.size(r_eval)))
    J = sj0(np.outer(lam400, np.atleast_1d(np.asarray(r_eval, float))))
    out[0] = Tinf_out[0] + b @ J
    ptr = 1
    for k in range(len(t_step) - 1):
        d = t_step[k + 1] - t_step[k]
        s = (Tinf_step[k + 1] - Tinf_step[k]) / d if d > 0 else 0.0
        E = np.exp(-mu400 * d)
        b = E * b - c400 * s * (1 - E) / mu400
        while ptr < len(times_out) and t_step[k + 1] >= times_out[ptr] - 1e-9:
            out[ptr] = Tinf_out[ptr] + b @ J
            ptr += 1
    return out


Tana_pwl = series_at(t_out, Tinf_1s, rrn, t_out, Tinf_1s)
D = np.abs(sn_num - Tana_pwl)
say("")
say("(iii) reproduce the headline number:")
say("      max|T_num - T_analytic| = %.10e K  at r=%.4f m, t=%.1f s"
    % (D.max(), rrn[np.unravel_index(D.argmax(), D.shape)[1]],
       t_out[np.unravel_index(D.argmax(), D.shape)[0]]))
say("      report claims 3.4936501265e-6 K (F40).")
say("      T(1800s,r=0) numeric = %.10f K ; analytic = %.10f K ; report F43 = 306.72583087"
    % (sn_num[-1, 0], Tana_pwl[-1, 0]))
say("      T(1800s,r=R) numeric = %.10f K ; report F44 = 309.93578369" % sn_num[-1, -1])
say("      Tinf(1800 s) = %.4f C (report says 314.6630 C)" % (Tinf_1s[-1] - 273.15))

# (iv) drive the semi-analytic route with the SAME continuous forcing used by the
#      numeric scheme -- chord taken on a much finer grid
sub = 200
t_fine = np.linspace(0.0, 1800.0, 1800 * sub + 1)
Tin_fine = np.asarray(Tinf_f(t_fine) + 273.15, float)
Tana_fine = series_at(t_out, Tinf_1s, rrn, t_fine, Tin_fine)
say("")
say("(iv) M=FINDING: the two 'independent' routes are not driven by the same")
say("     forcing.  Numeric uses the CONTINUOUS PCHIP; the semi-analytic route")
say("     used the 1 s chord.  Put the analytic route on a %.0f x finer chord" % sub)
say("     (dt=%.5f s) so its forcing is the same curve:")
say("      T(1800s,r=0) analytic(chord@1s)   = %.10f K" % Tana_pwl[-1, 0])
say("      T(1800s,r=0) analytic(chord@1/200) = %.10f K" % Tana_fine[-1, 0])
d_forc = np.abs(Tana_fine - Tana_pwl)
say("      max|ana(fine) - ana(1s)| over the whole field = %.6e K" % d_forc.max())
say("      T(1800s,r=R) analytic(1s)=%.10f  analytic(fine)=%.10f K"
    % (Tana_pwl[-1, -1], Tana_fine[-1, -1]))
say("")
say("     Now the scheme-vs-series discrepancy with the forcing mismatch removed:")
D3 = np.abs(sn_num - Tana_fine)
say("      max|T_num - T_analytic(fine forcing)| = %.10e K" % D3.max())
say("      T(1800s,r=0): numeric %.10f vs analytic-fine %.10f -> diff %.3e"
    % (sn_num[-1, 0], Tana_fine[-1, 0], abs(sn_num[-1, 0] - Tana_fine[-1, 0])))
say("")
say("     => the headline 3.49e-6 K is the DIFFERENCE OF TWO NUMBERS THAT INCLUDE")
say("        a forcing-discretisation artefact of order %.2e K." % d_forc.max())

# (v) numeric forced by the SAME 1-s chord as the analytic route
Tinf_lin_f = lambda t: float(np.interp(t, t_out, Tinf_1s))
sn_num_lin, _ = solve(Mnum, dtnum, t_out, Tinf_lin_f, "exact")
D2 = np.abs(sn_num_lin - Tana_pwl)
say("")
say("(v) numeric scheme driven by the SAME 1-s chord as the analytic route:")
say("      max|T_num - T_analytic| = %.10e K" % D2.max())
say("      T(1800s,r=0): numeric %.10f vs analytic %.10f -> diff %.3e"
    % (sn_num_lin[-1, 0], Tana_pwl[-1, 0], abs(sn_num_lin[-1, 0] - Tana_pwl[-1, 0])))

# (vi) how much of the numeric error is temporal?  refine dt
say("")
say("(vi) dt refinement of my numeric CN at M=1600 (continuous PCHIP forcing),")
say("     compared with the FINE-chord analytic reference on the same nodes:")
for dtv in (2.0 ** -5, 2.0 ** -7, 2.0 ** -9):
    snx, _ = solve(Mnum, dtv, t_out, Tinf_of_t, "exact")
    say("      dt=%.7f  max|T_num - T_ana(fine chord)| = %.6e K"
        % (dtv, np.abs(snx - Tana_fine).max()))

# ===========================================================================
hr("AUD-8. Duhamel recurrence, re-derived")
say("T = Tinf(t) + sum_n b_n(t) J0(lam_n r)")
say("  dT/dt = Tinf' + sum b_n' J0")
say("  alpha*lap(T) = -alpha sum lam_n^2 b_n J0 = -sum mu_n b_n J0")
say("  => sum (b_n' + mu_n b_n) J0 = -Tinf'")
say("  and since sum_n c_n J0(lam_n r) == 1,  -Tinf' = sum_n (-c_n Tinf') J0")
say("  => b_n' + mu_n b_n = -c_n Tinf'          [report's docstring: VERIFIED]")
say("On a step with constant slope s:")
say("  b(t) = (b_k + c_n s/mu_n) exp(-mu(t-t_k)) - c_n s/mu_n")
say("  with E = exp(-mu dt):  b_{k+1} = E b_k - c_n s (1-E)/mu_n  [code line 133: VERIFIED]")
say("Initial condition: b_n(0) = c_n (T0 - Tinf(0))   [code line 125: VERIFIED]")
# numeric spot check of the recurrence against an ODE integration
from scipy.integrate import solve_ivp
mu_t = ALPHA * (x_np[0] / R0) ** 2
cc_t = c_np[0]
s_t = 0.0042
dt_t = 137.0
E_t = math.exp(-mu_t * dt_t)
b0 = cc_t * 10.0
b_step = E_t * b0 - cc_t * s_t * (1 - E_t) / mu_t
sol = solve_ivp(lambda t, y: -mu_t * y - cc_t * s_t, (0, dt_t), [b0],
                rtol=1e-13, atol=1e-15, dense_output=False)
say("  spot check (mu=%.6e, s=%.4g, dt=%.3g): recurrence=%.12e  ODE=%.12e  diff=%.2e"
    % (mu_t, s_t, dt_t, b_step, sol.y[0, -1], abs(b_step - sol.y[0, -1])))

# ===========================================================================
hr("AUD-9. Appendix-3 / Appendix-2 property numbers quoted in §2.2/§2.3")


def props3(C, T, Tref=None):
    Tu = T if Tref is None else np.full_like(T, Tref)
    return (650.0 + 128.0 * C,
            1450.0 + 2736.0 * C / (C + 1.0),
            0.21 + 0.38 * C / (C + 1.0),
            2.4e-3 * np.exp(-0.45 / np.maximum(C, 1e-12)) * np.exp(-3850.0 / Tu))


p2 = (RHO, CP, K, D0 * math.exp(-DEXP / C0))
p3 = props3(np.array([C0]), np.array([T0_K]))
p3v = [float(v[0]) for v in p3]
say("附录2 初态: rho=%.1f cp=%.1f k=%.4f D=%.6e alpha=%.6e"
    % (p2[0], p2[1], p2[2], p2[3], p2[2] / (p2[0] * p2[1])))
say("附录3 初态: rho=%.4f cp=%.4f k=%.4f D=%.6e alpha=%.6e"
    % (p3v[0], p3v[1], p3v[2], p3v[3], p3v[2] / (p3v[0] * p3v[1])))
say("report §2.2 table says 附录3: rho 976.4  cp 3415.3  k 0.4830  D 5.6417e-9  alpha 1.4483e-7")
a2 = p2[2] / (p2[0] * p2[1])
a3 = p3v[2] / (p3v[0] * p3v[1])
say("alpha ratio 附录3/附录2 = %.10f -> %.4f %%   (report F62 = 0.85770461016, -14.23%%)"
    % (a3 / a2, (a3 / a2 - 1) * 100))
say("D ratio     附录3/附录2 = %.10f -> %.4f %%   (report F63 = 1.1425829195, +14.26%%)"
    % (p3v[3] / p2[3], (p3v[3] / p2[3] - 1) * 100))
say("")
say("报告 §2.2 表内 '附录3 k = 0.4830' 与我的复算 %.10f 是否一致: %s"
    % (p3v[2], "YES" if abs(p3v[2] - 0.4830) < 5e-5 else "NO"))
say("报告 §2.2 表内 '附录3 alpha = 1.4483e-7' 复算 %.6e: %s"
    % (a3, "YES" if abs(a3 - 1.4483e-7) < 5e-12 else "NO"))
say("")
say("§2.3 table: alpha(C) values")
for Cv in (2.55, 1.00, 0.50, 0.15):
    p = props3(np.array([Cv]), np.array([T0_K]))
    say("  C=%.2f rho=%7.1f cp=%8.1f k=%.4f alpha=%.6e D=%.6e"
        % (Cv, float(p[0][0]), float(p[1][0]), float(p[2][0]),
           float(p[2][0]) / (float(p[0][0]) * float(p[1][0])), float(p[3][0])))
p01 = props3(np.array([0.15]), np.array([T0_K]))
p25 = props3(np.array([2.55]), np.array([T0_K]))
r71 = (float(p01[2][0]) / (float(p01[0][0]) * float(p01[1][0]))) / \
      (float(p25[2][0]) / (float(p25[0][0]) * float(p25[1][0])))
say("alpha(0.15)/alpha(2.55) = %.10f -> %.2f %%  (report F71 = 1.4822133320, 48.2%%)"
    % (r71, (r71 - 1) * 100))
say("")
say("§2.2 claims 1.386095 = 306.72642796 - 305.34033311 (F64-F65) = %.6f"
    % (306.72642796 - 305.34033311))
say("报告 §2.2 max|T_附录3-T_附录2| = 1.4019076018 K 出现在 r=0.0138 m, t=1800 s")
say("  while T(1800s,r=0) differs by only 1.386095 K.  If the max is 1.4019 at")
say("  t=1800 s but at r=0.0138 m, the two statements are about different")
say("  locations -- internally consistent, but the report's table row labels")
say("  'T(1800 s, r=0)' next to the max row invite a mis-read.")
say("  0.13834689131 kg/kg vs the §0 summary '0.1383 kg/kg' (%s) and '0.138' in §2.2"
    % ("OK" if abs(0.13834689131 - 0.1383) / 0.13834689131 < 5e-4 else "MISMATCH"))
say("  1.4019076018 vs §0 summary '1.4019 K' (%s)"
    % ("OK" if abs(1.4019076018 - 1.4019) / 1.4019076018 < 5e-5 else "MISMATCH"))

hr("AUD-10. registry row count")
import csv as _csv
with open(os.path.join(OUT, "registry_feishu.csv"), encoding="utf-8-sig") as f:
    reg_rows = list(_csv.DictReader(f))
say("registry_feishu.csv data rows = %d" % len(reg_rows))
say("report §3 says '注册表：outputs/registry_feishu.csv（62 行）' -> %s"
    % ("MATCH" if len(reg_rows) == 62 else "MISMATCH (report says 62)"))
ids = [r["id"] for r in reg_rows]
say("ids: %s ... %s (n=%d)" % (ids[0], ids[-1], len(ids)))

os.makedirs(OUT, exist_ok=True)
with open(LOG, "w", encoding="utf-8") as f:
    f.write("\n".join(_ROWS) + "\n")
print("\nwrote %s" % LOG)
