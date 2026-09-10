"""
Comparison of the two modelling routes in feishu.md (问题一完整方案), audited
against the analytic Robin-cylinder series solution.

Route A -- 半解析 (semi-analytic): feishu.md §6, Bessel eigenfunction expansion
          + Duhamel for the time-varying ambient.
Route B -- 数值 (numerical):       feishu.md §5, Crank-Nicolson / BDF2.

This script does NOT trust either route as written. It:
  1. builds a machine-precision semi-analytic reference for the LINEAR heat
     equation with the real time-varying T_inf(t) from 附件1;
  2. implements the theta-method (theta=1/2 = Crank-Nicolson, theta=1 = backward
     Euler) self-consistently, in two surface treatments:
       "lead"  = leading-order half-control-volume surface (what feishu.md writes)
       "exact" = exact half-control-volume surface geometry
  3. reproduces feishu.md §5.3 exactly as written and isolates each defect;
  4. quantifies what the 解耦 (附录2) -> 耦合 (附录3) transition costs;
  5. measures the cost of each route.

Derivation used for route A (recorded so it can be checked):
  The homogeneous-Robin modes are J0(lambda_n r) with x_n J1(x_n) = Bi J0(x_n).
  Writing T = T_inf(t) + sum_n b_n(t) J0(lambda_n r) and projecting onto the
  n-th mode (weight r) gives the exact forced modal ODE
        b_n' + mu_n b_n = -c_n T_inf'(t),   mu_n = alpha lambda_n^2,
        c_n  = 2 J1(x_n) / (x_n (J0(x_n)^2 + J1(x_n)^2)),
        b_n(0) = c_n (T0 - T_inf(0)),
  because sum_n c_n J0(lambda_n r) == 1 on [0,R]. For piecewise-linear T_inf
  with slope s on a step this integrates exactly to
        b_{k+1} = E b_k - c_n s (1-E)/mu_n,   E = exp(-mu_n dt).
  (An earlier draft used b_n' = -mu_n b_n + beta_n (T_inf-T0) with
   beta_n = mu_n c_n; that forcing coefficient is WRONG by a factor -mu_n and
   was discarded.)

Run:  python src/feishu_compare.py
Out:  outputs/feishu_compare.log
      outputs/registry_feishu.csv
"""

from __future__ import annotations

import csv
import math
import os
import time

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.linalg import solve_banded, lu_factor, lu_solve
from scipy.optimize import brentq
from scipy.special import j0, j1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATT1 = os.path.join(ROOT, "A题", "附件", "附件1.xlsx")
OUTDIR = os.path.join(ROOT, "outputs")
LOG = os.path.join(OUTDIR, "feishu_compare.log")
REG = os.path.join(OUTDIR, "registry_feishu.csv")

# ---- 附录2 (问题1) ---------------------------------------------------------
RHO, CP, K_COND = 820.0, 2600.0, 0.36
H_CONV, HM = 25.0, 8.0e-7
D0, D_EXP = 7.0e-9, 0.89
T0_C, C0, R0 = 28.0, 2.55, 0.02
ALPHA_FEISHU = 1.6793e-7
ALPHA = K_COND / (RHO * CP)
T0_K = T0_C + 273.15
BI = H_CONV * R0 / K_COND

_ROWS: list[str] = []
_REG: list[dict] = []


def say(s: str = "") -> None:
    _ROWS.append(s)
    print(s, flush=True)


def add(id_, quantity, value, unit, unc, source, note=""):
    _REG.append(dict(id=id_, quantity=quantity,
                     value=("%.10e" % value) if isinstance(value, float) else str(value),
                     unit=unit, uncertainty=unc, source=source,
                     command="python src/feishu_compare.py", note=note))


def hr(t):
    say("")
    say("=" * 78)
    say(t)
    say("=" * 78)


def read_att1():
    from openpyxl import load_workbook
    wb = load_workbook(ATT1, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    rows = [r for r in ws.iter_rows(min_row=2, values_only=True) if r[0] is not None]
    wb.close()
    a = np.array([[float(v) for v in r[:3]] for r in rows])
    return a[:, 0], a[:, 1], a[:, 2]


# ---------------------------------------------------------------------------
# eigenproblem  x J1(x) = Bi J0(x)
# ---------------------------------------------------------------------------
def eigen(Bi, n_modes):
    f = lambda x: x * j1(x) - Bi * j0(x)
    hi = 4.0 * n_modes + 40.0
    grid = np.linspace(1e-8, hi, 300 * (n_modes + 20))
    vals = f(grid)
    xs = []
    for k in range(len(grid) - 1):
        if vals[k] * vals[k + 1] < 0:
            xs.append(brentq(f, grid[k], grid[k + 1], xtol=1e-15, rtol=8.9e-16))
        if len(xs) >= n_modes:
            break
    x = np.array(xs)
    lam = x / R0
    c = 2.0 * j1(x) / (x * (j0(x) ** 2 + j1(x) ** 2))
    return x, lam, c


def series_T(times, Tinf_vals, r_eval, n_modes=400, T0=T0_K):
    """Route A: exact semi-analytic solution of the linear heat equation."""
    x, lam, c = eigen(BI, n_modes)
    mu = ALPHA * lam ** 2
    b = c * (T0 - Tinf_vals[0])
    dt = np.diff(times)
    snaps = np.empty((len(times), n_modes))
    snaps[0] = b
    for k in range(len(dt)):
        d = dt[k]
        s = (Tinf_vals[k + 1] - Tinf_vals[k]) / d if d > 0 else 0.0
        E = np.exp(-mu * d)
        b = E * b - c * s * (1.0 - E) / mu
        snaps[k + 1] = b
    J = j0(np.outer(lam, np.atleast_1d(r_eval)))
    return Tinf_vals[:, None] + snaps @ J, snaps, lam


# ---------------------------------------------------------------------------
# theta-method for the linear heat equation, node-centred FV
# ---------------------------------------------------------------------------
def build_geom(M):
    dr = R0 / M
    r = np.arange(M + 1) * dr
    af = (2.0 * np.pi * (np.arange(M) + 0.5) * dr)      # face areas i+1/2, i=0..M-1
    V = np.empty(M + 1)
    V[0] = np.pi * (dr / 2.0) ** 2
    V[1:M] = 2.0 * np.pi * np.arange(1, M) * dr ** 2
    V[M] = np.pi * (R0 * dr - dr ** 2 / 4.0)
    return dr, r, af, V


def build_theta(M, dt, theta, surface):
    """Node-centred FV theta-method for  dT/dt = alpha * lap(T)  with Robin BC.

    surface in {"lead_doc", "lead_cn", "exact_cn"}:
      lead_doc : exactly what feishu.md §5.3 writes -- leading-order geometry
                 (a_M = -2*alpha*dt/dr^2) but on the BACKWARD-EULER theta-scale,
                 while its interior row is on the CN scale.  This is the defect.
      lead_cn  : theta-consistent scale, same leading-order geometry
                 (f_M = 2/dr).  Isolates the theta-scale defect alone.
      exact_cn : theta-consistent AND exact half-control-volume surface geometry,
                 f_M = A_{M-1/2}/(dr*V_M) = 2(M-0.5)/(dr*(M-0.25)).

    Surface node ODE:  dT_M/dt = alpha*f_M*(T_{M-1}-T_M) + g*(T_inf - T_M)
      with g = A_s*h/(rho*cp*V_M).
    """
    dr, r, af, V = build_geom(M)
    f_int = af[1:M] / (dr * V[1:M])
    f_lo = af[0:M - 1] / (dr * V[1:M])
    f_M_lead = 2.0 / dr ** 2                        # BUGFIX: was 2/dr
    f_M_exact = af[M - 1] / (dr * V[M])
    K = 4.0 * ALPHA * dt / dr ** 2                      # r=0 operator
    A_s = 2.0 * np.pi * R0
    g_lead = ALPHA * H_CONV * A_s / (K_COND * V[M])     # = 2*alpha*h/(k*dr) * (1/(1-1/(4M)))
    a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
    b[0] = 1.0 + theta * K
    c[0] = -theta * K
    b[1:M] = 1.0 + theta * ALPHA * dt * (f_int + f_lo)
    a[1:M] = -theta * ALPHA * dt * f_lo
    c[1:M] = -theta * ALPHA * dt * f_int
    if surface == "lead_doc":
        afM, Gdt = f_M_lead, 2.0 * ALPHA * H_CONV * dt / (K_COND * dr)
        a[M] = -ALPHA * dt * afM
        b[M] = 1.0 + ALPHA * dt * afM + Gdt
    else:
        afM = f_M_lead if surface == "lead_cn" else f_M_exact
        Gdt = ALPHA * dt * H_CONV * A_s / (K_COND * V[M])
        a[M] = -theta * ALPHA * dt * afM
        b[M] = 1.0 + theta * (ALPHA * dt * afM + Gdt)
    return dr, (a, b, c), (f_int, f_lo, K, afM, Gdt, dt, surface), theta


def step_T(T, coef, geo, theta, Tinf_new, mode, Tinf_old=None):
    a, b, c = coef
    f_int, f_lo, K, afM, Gdt, dt, surface = geo
    if Tinf_old is None:
        Tinf_old = Tinf_new
    M = len(T) - 1
    m = M
    d = np.empty(M + 1)
    d[0] = (1.0 - (1.0 - theta) * K) * T[0] + (1.0 - theta) * K * T[1]
    if mode == "doc_signs":
        d[1:m] = a[1:m] * T[0:m - 1] + (2.0 - b[1:m]) * T[1:m] + c[1:m] * T[2:m + 1]
    else:
        d[1:m] = ((1.0 - (1.0 - theta) * ALPHA * dt * (f_int + f_lo)) * T[1:m]
                  + (1.0 - theta) * ALPHA * dt * f_lo * T[0:m - 1]
                  + (1.0 - theta) * ALPHA * dt * f_int * T[2:m + 1])
    if mode in ("doc_full", "doc_surf") or surface == "lead_doc":
        # exactly feishu.md's surface row: fully implicit, source = Gdt*Tinf^{n+1}
        d[m] = (2.0 - b[m]) * T[m] - a[m] * T[m - 1] + Gdt * Tinf_new
    else:
        d[m] = ((1.0 - (1.0 - theta) * (ALPHA * dt * afM + Gdt)) * T[m]
                + (1.0 - theta) * ALPHA * dt * afM * T[m - 1]
                + Gdt * (theta * Tinf_new + (1.0 - theta) * Tinf_old))
    ab = np.zeros((3, M + 1))
    ab[0, 1:] = c[:-1]
    ab[1, :] = b
    ab[2, :-1] = a[1:]
    return solve_banded((1, 1), ab, d)


def solve_T(M, dt, times, Tinf_at, theta=0.5, surface="exact_cn", mode="theta"):
    dr, coef, geo, th = build_theta(M, dt, theta, surface)
    idx = np.round(np.asarray(times) / dt).astype(int)
    T = np.full(M + 1, T0_K)
    snaps = np.empty((len(times), M + 1))
    snaps[0] = T
    ptr = 1
    nsteps = int(round(times[-1] / dt))
    for s in range(1, nsteps + 1):
        T = step_T(T, coef, geo, th, Tinf_at(s * dt), mode,
                   Tinf_old=Tinf_at((s - 1) * dt))
        if not np.all(np.isfinite(T)):
            return dr, snaps, s * dt, ptr
        if ptr < len(idx) and s == idx[ptr]:
            snaps[ptr] = T
            ptr += 1
    return dr, snaps, None, ptr


# ---------------------------------------------------------------------------
# 附录2 vs 附录3 property closures
# ---------------------------------------------------------------------------
def props_app2(C, T):
    return (np.full_like(C, RHO), np.full_like(C, CP), np.full_like(C, K_COND),
            D0 * np.exp(-D_EXP / np.maximum(C, 1e-12)))


def props_app3(C, T, T_ref=None):
    """附录3.  T_ref given -> freeze the Arrhenius temperature factor at T_ref
    (used to measure how much the T -> D feedback actually matters)."""
    T_use = T if T_ref is None else np.full_like(T, T_ref)
    return (650.0 + 128.0 * C,
            1450.0 + 2736.0 * C / (C + 1.0),
            0.21 + 0.38 * C / (C + 1.0),
            2.4e-3 * np.exp(-0.45 / np.maximum(C, 1e-12)) * np.exp(-3850.0 / T_use))


def solve_coupled(M, dt, times, Tinf_at, Cinf_at, props):
    """Backward Euler, node-centred FV, variable coefficients lagged one step.

    Node-centred control volumes (see build_geom):
      V_0 = pi*(dr/2)^2,  V_i = 2*pi*i*dr^2,  V_M = pi*(R*dr - dr^2/4)
      A_{i+1/2} = 2*pi*(i+1/2)*dr,  i = 0..M-1
    Face geometric factors  f+_i = A_{i+1/2}/(dr*V_i),  f-_i = A_{i-1/2}/(dr*V_i).

    Interior:  dT_i/dt = [k+ f+ (T_{i+1}-T_i) - k- f- (T_i-T_{i-1})]/(rho_i cp_i)
    Surface M: dT_M/dt = [-k- f- (T_M-T_{M-1}) + h A_s (Tinf-T_M)]/(rho_M cp_M V_M)
    Same structure for C with D and h_m (no rho*cp).
    Properties (rho, cp, k, D) are evaluated from the previous step's C, T.
    """
    dr, r, af, V = build_geom(M)
    fp = np.zeros(M + 1)          # face i+1/2
    fm = np.zeros(M + 1)          # face i-1/2
    fp[0] = af[0] / (dr * V[0])
    for i in range(1, M):
        fp[i] = af[i] / (dr * V[i])
        fm[i] = af[i - 1] / (dr * V[i])
    fm[M] = af[M - 1] / (dr * V[M])
    A_s = 2.0 * np.pi * R0
    T = np.full(M + 1, T0_K)
    C = np.full(M + 1, C0)
    idx = np.round(np.asarray(times) / dt).astype(int)
    snaps_T = np.empty((len(times), M + 1))
    snaps_C = np.empty((len(times), M + 1))
    snaps_T[0] = T
    snaps_C[0] = C
    ptr = 1
    nsteps = int(round(times[-1] / dt))
    for s in range(1, nsteps + 1):
        rho, cp, kk, DD = props(C, T)
        rc = rho * cp
        kf = 2.0 * kk[:-1] * kk[1:] / (kk[:-1] + kk[1:])       # face i+1/2, i=0..M-1
        Df = 2.0 * DD[:-1] * DD[1:] / (DD[:-1] + DD[1:])
        Tinf = Tinf_at(s * dt)
        Cinf = Cinf_at(s * dt)
        # ---- heat ----
        a = np.zeros(M + 1); b = np.zeros(M + 1); c = np.zeros(M + 1)
        rhsT = T / dt
        Kp0 = kf[0] * fp[0] / rc[0]
        b[0] = 1.0 / dt + Kp0
        c[0] = -Kp0
        Kp = kf[1:M] * fp[1:M] / rc[1:M]
        Km = kf[0:M - 1] * fm[1:M] / rc[1:M]
        a[1:M] = -Km
        b[1:M] = 1.0 / dt + Kp + Km
        c[1:M] = -Kp
        KmM = kf[M - 1] * fm[M] / rc[M]
        gh = H_CONV * A_s / (rc[M] * V[M])
        a[M] = -KmM
        b[M] = 1.0 / dt + KmM + gh
        rhsT[M] += gh * Tinf
        ab = np.zeros((3, M + 1)); ab[0, 1:] = c[:-1]; ab[1, :] = b; ab[2, :-1] = a[1:]
        T = solve_banded((1, 1), ab, rhsT)
        # ---- moisture (lagged D) ----
        a[:] = 0.0; b[:] = 0.0; c[:] = 0.0
        rhsC = C / dt
        Dp0 = Df[0] * fp[0]
        b[0] = 1.0 / dt + Dp0
        c[0] = -Dp0
        Dp = Df[1:M] * fp[1:M]
        Dm = Df[0:M - 1] * fm[1:M]
        a[1:M] = -Dm
        b[1:M] = 1.0 / dt + Dp + Dm
        c[1:M] = -Dp
        DmM = Df[M - 1] * fm[M]
        gm = HM * A_s / V[M]
        a[M] = -DmM
        b[M] = 1.0 / dt + DmM + gm
        rhsC[M] += gm * Cinf
        ab = np.zeros((3, M + 1)); ab[0, 1:] = c[:-1]; ab[1, :] = b; ab[2, :-1] = a[1:]
        C = solve_banded((1, 1), ab, rhsC)
        if not (np.all(np.isfinite(T)) and np.all(np.isfinite(C))):
            return dr, snaps_T, snaps_C, s * dt, ptr
        if ptr < len(idx) and s == idx[ptr]:
            snaps_T[ptr] = T
            snaps_C[ptr] = C
            ptr += 1
    return dr, snaps_T, snaps_C, None, ptr


# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    t_env, T_env_C, C_env = read_att1()
    say("附件1: %d 点, t=%.0f..%.0f s, Tinf=%.3f..%.3f C, Cinf=%.5f..%.5f kg/kg"
        % (len(t_env), t_env[0], t_env[-1], T_env_C.min(), T_env_C.max(),
           C_env.min(), C_env.max()))
    Tinf_f = PchipInterpolator(t_env, T_env_C)
    Cinf_f = PchipInterpolator(t_env, C_env)

    def Tinf_at(t):
        return float(Tinf_f(t)) + 273.15

    def Cinf_at(t):
        return float(Cinf_f(t))

    # ---------------- A0 constants ---------------------------------------
    hr("A0. feishu.md 常数核对")
    say("alpha 精确 = %.10e m^2/s ; feishu 文中 %.4e ; 相对偏差 %.4f %%"
        % (ALPHA, ALPHA_FEISHU, (ALPHA_FEISHU - ALPHA) / ALPHA * 100))
    say("Bi = %.6f ; tau_T(精确 alpha) = %.2f s ; tau_T(feishu alpha) = %.2f s"
        % (BI, R0 ** 2 / ALPHA, R0 ** 2 / ALPHA_FEISHU))
    d25 = D0 * math.exp(-D_EXP / C0)
    say("D(C0=2.55) = %.10e m^2/s ; tau_C(C0) = %.6e s = %.4f 天 = %.2f h"
        % (d25, R0 ** 2 / d25, R0 ** 2 / d25 / 86400, R0 ** 2 / d25 / 3600))
    say("Le(C0) = alpha/D(C0) = %.4f   (feishu 文中写 Le ~ 300)" % (ALPHA / d25))
    c_at = brentq(lambda C: D0 * math.exp(-D_EXP / C) - 5.593e-10, 1e-3, C0)
    say("使 D = 5.593e-10 的 C = %.6f  (feishu 把 5.593e-10 称为 D0)" % c_at)
    say("1800 s / tau_C = %.6f  -> 预热窗口内水分几乎不动" % (1800.0 / (R0 ** 2 / d25)))
    add("F09", "D(C=0.15) (问题3 判据处)", D0 * math.exp(-D_EXP / 0.15), "m^2/s", "解析精确",
        "附录2", "用于说明 D 的跨度")
    add("F0A", "热 Biot 数 Bi = hR/k", BI, "-", "解析精确", "附录2")
    for i, (q, v, u, src, nt) in enumerate([
            ("alpha (精确)", ALPHA, "m^2/s", "附录2", ""),
            ("feishu alpha 相对偏差", (ALPHA_FEISHU - ALPHA) / ALPHA * 100, "%", "feishu §2.1", "文中 1.6793e-7"),
            ("tau_T (精确 alpha)", R0 ** 2 / ALPHA, "s", "附录2", ""),
            ("tau_T (feishu alpha)", R0 ** 2 / ALPHA_FEISHU, "s", "feishu §4.2", ""),
            ("D(C0=2.55)", d25, "m^2/s", "附录2", ""),
            ("tau_C = R^2/D(C0)", R0 ** 2 / d25, "s", "附录2", ""),
            ("Le = alpha/D(C0)", ALPHA / d25, "-", "附录2", "feishu 写 ~300"),
            ("使 D=5.593e-10 的 C", c_at, "kg/kg", "附录2", "feishu 标为 D0")]):
        add("F0%d" % (i + 1), q, v, u, "解析精确", src, nt)

    # ---------------- A1 eigen + coefficient ------------------------------
    hr("A1. 本征值与展开系数 (feishu.md §6.1 式(11))")
    x, lam, c = eigen(BI, 8)
    say("lambda_k R (k=1..8) = " + ", ".join("%.10f" % v for v in x))
    say("feishu §6.1 表写 ~2.0, ~5.0, ~8.0, ~11.0  -> 全部不符")
    say("残差 max|x J1 - Bi J0| = %.3e" % np.max(np.abs(x * j1(x) - BI * j0(x))))
    docA = 2.0 / (x * j1(x))
    say("")
    say("  k   x_k          c_k (正确)        A_k (feishu)     c_k/A_k     1/(1+(x/Bi)^2)")
    for k in range(6):
        say("%3d %10.6f  %16.10f %16.10f %12.6f %14.6f"
            % (k + 1, x[k], c[k], docA[k], c[k] / docA[k], 1.0 / (1.0 + (x[k] / BI) ** 2)))
    add("F10", "本征值 lambda_1 R", float(x[0]), "-", "解析", "式(11) 数值求根")
    add("F11", "本征值 lambda_2 R", float(x[1]), "-", "解析", "式(11) 数值求根")
    add("F12", "正确展开系数 c_1", float(c[0]), "-", "闭式", "解析")
    add("F13", "feishu A_1/(T0-Tinf)", float(docA[0]), "-", "feishu §6.1", "")
    add("F14", "c_1 / A_1(feishu)", float(c[0] / docA[0]), "-", "解析", "比值")
    resid = x * j1(x) - BI * j0(x)
    add("F17", "max|x J1 - Bi J0| (前8个根)", float(np.max(np.abs(resid))), "-",
        "解析", "式(11) 求根残差")
    for k in range(1, 9):
        add("F10_%d" % k, "本征值 lambda_%d R" % k, float(x[k - 1]), "-", "解析", "式(11) 数值求根")
        add("F17_%d" % k, "根 lambda_%d R 处 x J1 - Bi J0 残差" % k, float(resid[k - 1]), "-",
            "解析", "式(11) 求根残差")
    for k in range(1, 7):
        add("F18_%d" % k, "正确展开系数 c_%d" % k, float(c[k - 1]), "-", "闭式", "解析")
        add("F19_%d" % k, "feishu A_%d/(T0-Tinf)" % k, float(docA[k - 1]), "-", "feishu §6.1", "")
        add("F1A_%d" % k, "c_%d / A_%d(feishu)" % (k, k), float(c[k - 1] / docA[k - 1]), "-",
            "解析", "比值")
        add("F1B_%d" % k, "1/(1+(x_%d/Bi)^2)" % k, float(1.0 / (1.0 + (x[k - 1] / BI) ** 2)),
            "-", "解析", "预测比值")
    say("")
    say("决定性检验 —— 用 8 项重构常数 theta=1:")
    for rr in (0.0, 0.25, 0.5, 0.75, 1.0):
        s1 = float(np.sum(c * j0(x * rr)))
        s2 = float(np.sum(docA * j0(x * rr)))
        say("  r/R=%.2f   Sum c_k J0 = %12.8f   Sum A_k(feishu) J0 = %14.8f" % (rr, s1, s2))
        add("F1C_%d" % int(rr * 100), "用正确 c_k 重构常数1 (8项, r/R=%.2f)" % rr, s1, "-",
            "解析", "截断误差")
        add("F1D_%d" % int(rr * 100), "用 feishu A_k 重构常数1 (8项, r/R=%.2f)" % rr, s2, "-",
            "feishu §6.1", "")
    add("F15", "重构常数1误差(8项,r=R), 正确 c_k", abs(1.0 - float(np.sum(c * j0(x)))), "-", "解析", "截断")
    add("F16", "重构常数1误差(8项,r=R), feishu A_k", abs(1.0 - float(np.sum(docA * j0(x)))), "-", "解析", "feishu §6.1")

    # ---------------- A2 scheme variants vs analytic ----------------------
    hr("A2. §5.3 格式各变体 vs 解析级数解 (纯导热, 常 Tinf=50C, t=300 s)")
    t_const_K = 50.0 + 273.15
    tc = 300.0
    t_g = np.array([0.0, tc])
    Tinf_c = lambda t: t_const_K
    say("Bi=%.6f  Fo(t=300s)=%.6f" % (BI, ALPHA * tc / R0 ** 2))
    say("  M    dt     lead_doc      ratio  lead_cn       ratio  exact_cn      ratio")
    prev = {"ld": None, "lc": None, "ex": None}
    xa, la, ca = eigen(BI, 400)
    Fo = ALPHA * tc / R0 ** 2
    for M in (50, 100, 200, 400):
        dt = 0.5
        r = np.arange(M + 1) * (R0 / M)
        s_ld = solve_T(M, dt, t_g, Tinf_c, 0.5, "lead_doc")[1][-1]
        s_lc = solve_T(M, dt, t_g, Tinf_c, 0.5, "lead_cn")[1][-1]
        s_ex = solve_T(M, dt, t_g, Tinf_c, 0.5, "exact_cn")[1][-1]
        Tan = t_const_K + (T0_K - t_const_K) * np.sum(
            ca[None, :] * j0(np.outer(r / R0, xa)) * np.exp(-xa ** 2 * Fo), axis=1)
        e = {k: float(np.max(np.abs(v - Tan))) for k, v in
             [("ld", s_ld), ("lc", s_lc), ("ex", s_ex)]}
        say("%5d %6.3f  %11.5e %7s  %11.5e %7s  %11.5e %7s"
            % (M, dt, e["ld"], "-" if prev["ld"] is None else "%.3f" % (prev["ld"] / e["ld"]),
               e["lc"], "-" if prev["lc"] is None else "%.3f" % (prev["lc"] / e["lc"]),
               e["ex"], "-" if prev["ex"] is None else "%.3f" % (prev["ex"] / e["ex"])))
        add("F20_M%d_leaddoc" % M, "feishu 表面(逐字,θ尺度不一致) vs 解析 max|dT| (M=%d,dt=%.3f)" % (M, dt), e["ld"], "K", "解析级数 400 项", "A2")
        add("F21_M%d_leadcn" % M, "CN尺度+leading几何 表面 vs 解析 max|dT| (M=%d,dt=%.3f)" % (M, dt), e["lc"], "K", "解析级数 400 项", "A2")
        add("F22_M%d_exact" % M, "CN尺度+精确半CV 表面 vs 解析 max|dT| (M=%d,dt=%.3f)" % (M, dt), e["ex"], "K", "解析级数 400 项", "A2")
        for tag, key, lbl in (("leaddoc", "ld", "逐字"), ("leadcn", "lc", "leading几何"),
                              ("exact", "ex", "精确半CV")):
            if prev[key] is not None:
                add("F24_M%d_%s" % (M, tag),
                    "%s 误差比 (M=%d, 相对上一档 M=%d)" % (lbl, M, M // 2),
                    float(prev[key] / e[key]), "-", "解析", "A2",
                    "≈2 一阶, ≈4 二阶")
        prev = {"ld": e["ld"], "lc": e["lc"], "ex": e["ex"]}
    say("")
    say("误差比 ≈2 => 一阶 (error ∝ 1/M);  ≈4 => 二阶 (error ∝ 1/M²).")
    say("  lead_doc(逐字) -> lead_cn 的差别 = 表面时间离散尺度 (后向Euler vs CN)")
    say("  lead_cn -> exact_cn 的差别 = 表面 O(dr) 几何因子 f_M = A_{M-1/2}/(dr*V_M)")

    hr("A2b. 时间步细化 (固定 M, 排除空间误差混淆)")
    M = 100
    r = np.arange(M + 1) * (R0 / M)
    Tan = t_const_K + (T0_K - t_const_K) * np.sum(
        ca[None, :] * j0(np.outer(r / R0, xa)) * np.exp(-xa ** 2 * Fo), axis=1)
    for dt in (1.0, 0.25, 0.0625, 0.015625):
        row = []
        for surf in ("lead_doc", "lead_cn", "exact_cn"):
            e = float(np.max(np.abs(solve_T(M, dt, t_g, Tinf_c, 0.5, surf)[1][-1] - Tan)))
            row.append(e)
            add("F25_M%d_dt%s_%s" % (M, ("%g" % dt).replace(".", "p"), surf),
                "时间步细化 M=%d dt=%g %s" % (M, dt, surf), e, "K", "解析级数 400 项", "A2b")
        say("  M=%d dt=%9.6f  lead_doc %.6e  lead_cn %.6e  exact_cn %.6e" % (M, dt, *row))
        if dt == 1.0:
            e_ld_1 = row[0]
        if dt == 0.015625:
            add("F26", "逐字格式误差对 dt 的敏感度 |err(dt=1)-err(dt=1/64)| (M=%d)" % M,
                abs(e_ld_1 - row[0]), "K", "解析级数 400 项", "A2b",
                "≈0 说明误差不是时间离散误差")

    hr("A3. feishu §5.3 逐字实现 (其 d_i 符号 + 其表面尺度) —— 是否发散")
    for M in (200, 800):
        dr, sn, div, _ = solve_T(M, 0.5, t_g, Tinf_c, 0.5, "lead_doc", "doc_signs")
        say("M=%4d dt=0.5 doc_signs(其符号) -> %s"
            % (M, ("DIVERGED at t=%.2f s" % div) if div else "ok"))
        add("F30_M%d" % M, "feishu 原始格式 M=%d dt=0.5 发散时刻" % M,
            div if div else float("nan"), "s", "数值", "A3", "未发散则 nan")

    # ---------------- B real Q1 case --------------------------------------
    hr("B. 真实算例 0-1800 s (附件1 时变 Tinf) —— 半解析 vs 数值")
    t_out = np.arange(0.0, 1800.0 + 1e-9, 1.0)
    Tinf_out = np.asarray(Tinf_f(t_out) + 273.15, float)

    Mnum, dtnum = 1600, 2.0 ** -5
    r = np.arange(Mnum + 1) * (R0 / Mnum)
    t0 = time.perf_counter()
    Tnum_snaps = solve_T(Mnum, dtnum, t_out, Tinf_at, 0.5, "exact_cn")[1]
    t_num = time.perf_counter() - t0
    say("数值 CN M=%d dt=2^-5=%.7f s : %.2f s wall" % (Mnum, dtnum, t_num))

    t0 = time.perf_counter()
    Tana, bsnap, lamA = series_T(t_out, Tinf_out, r, n_modes=400)
    t_ana = time.perf_counter() - t0
    say("半解析 400 项 Bessel+Duhamel (含全部 r 点) : %.3f s wall" % t_ana)

    diff = np.abs(Tnum_snaps - Tana)
    ij = np.unravel_index(diff.argmax(), diff.shape)
    say("max|T_数值 - T_半解析| = %.6e K  (r=%.4f m, t=%.1f s)"
        % (diff.max(), r[ij[1]], t_out[ij[0]]))
    say("T(1800s) 中心/表面: 数值 %.6f / %.6f K ; 半解析 %.6f / %.6f K"
        % (Tnum_snaps[-1, 0], Tnum_snaps[-1, -1], Tana[-1, 0], Tana[-1, -1]))
    say("Tinf(1800 s) = %.4f C" % Tinf_out[-1])
    add("F40", "max|T_数值 - T_半解析| (0-1800s)", float(diff.max()), "K", "运行", "B", "M=1600,dt=2^-5")
    add("F41", "T 数值耗时 (M=1600,dt=2^-5)", t_num, "s", "运行", "B")
    add("F42", "T 半解析耗时 (400 项)", t_ana, "s", "运行", "B")
    add("F43", "T(1800s,r=0) 数值", float(Tnum_snaps[-1, 0]), "K", "运行", "B")
    add("F44", "T(1800s,r=R) 数值", float(Tnum_snaps[-1, -1]), "K", "运行", "B")

    # ---------------- B2 moisture: can route A be used at all? ------------
    hr("B2. 半解析路线能否用于水分方程? (非线性 D(C))")
    Md = 400
    dt_d = 0.5
    r4 = np.arange(Md + 1) * (R0 / Md)
    D_lin = float(D0 * math.exp(-D_EXP / C0))
    Bi_m = HM * R0 / D_lin
    say("Bi_m = hm R / D(C0) = %.6f" % Bi_m)
    # semi-analytic with D frozen at D(C0)
    xm = eigen(Bi_m, 400)
    xxm, llm, ccm = xm
    mu_m = D_lin * llm ** 2
    Cinf_out = np.asarray(Cinf_f(t_out), float)
    bm = ccm * (C0 - Cinf_out[0])
    snaps_b = np.empty((len(t_out), len(llm)))
    snaps_b[0] = bm
    for k in range(len(t_out) - 1):
        dd = t_out[k + 1] - t_out[k]
        s = (Cinf_out[k + 1] - Cinf_out[k]) / dd
        E = np.exp(-mu_m * dd)
        bm = E * bm - ccm * s * (1.0 - E) / mu_m
        snaps_b[k + 1] = bm
    C_lin = Cinf_out[:, None] + snaps_b @ j0(np.outer(llm, r4))
    # true nonlinear
    _, _, Cnl_snaps, divC, _ = solve_coupled(Md, dt_d, t_out, Tinf_at, Cinf_at, props_app2)
    say("非线性(C(1800s)) 中心/表面 = %.8f / %.8f" % (Cnl_snaps[-1, 0], Cnl_snaps[-1, -1]))
    say("线性化 D=D(C0)  C(1800s) 中心/表面 = %.8f / %.8f" % (C_lin[-1, 0], C_lin[-1, -1]))
    dC = float(np.max(np.abs(C_lin - Cnl_snaps)))
    say("max|C_线性化半解析 - C_真实非线性| = %.6e kg/kg  (C0=%.2f)" % (dC, C0))
    add("F50", "max|C_线性化 - C_非线性| (0-1800s)", dC, "kg/kg", "运行", "B2")
    add("F51", "C(1800s,r=0) 非线性", float(Cnl_snaps[-1, 0]), "kg/kg", "运行", "B2")
    add("F52", "C(1800s,r=R) 非线性", float(Cnl_snaps[-1, -1]), "kg/kg", "运行", "B2")
    add("F53", "Bi_m = hm R / D(C0)", Bi_m, "-", "解析", "B2")

    # ---------------- C 解耦(附录2) vs 耦合(附录3) ------------------------
    hr("C. 解耦(附录2 常数物性) vs 耦合(附录3 物性随 C,T 变) —— 同一窗口 0-1800 s")
    _, T2_s, C2_s, div2, _ = solve_coupled(Md, dt_d, t_out, Tinf_at, Cinf_at, props_app2)
    _, T3_s, C3_s, div3, _ = solve_coupled(Md, dt_d, t_out, Tinf_at, Cinf_at, props_app3)
    say("附录2 (解耦): 发散=%s" % (div2 or "否"))
    say("附录3 (耦合): 发散=%s" % (div3 or "否"))
    dT = float(np.max(np.abs(T3_s - T2_s)))
    dCc = float(np.max(np.abs(C3_s - C2_s)))
    iT = np.unravel_index(np.abs(T3_s - T2_s).argmax(), T3_s.shape)
    say("max|T_附录3 - T_附录2| = %.6f K  (r=%.4f m, t=%.0f s)" % (dT, r4[iT[1]], t_out[iT[0]]))
    say("max|C_附录3 - C_附录2| = %.6e kg/kg" % dCc)
    say("T(1800s) 中心: 附录2 %.6f K, 附录3 %.6f K, 差 %.6f K"
        % (T2_s[-1, 0], T3_s[-1, 0], T3_s[-1, 0] - T2_s[-1, 0]))
    say("C(1800s) 中心: 附录2 %.8f, 附录3 %.8f kg/kg, 差 %.3e"
        % (C2_s[-1, 0], C3_s[-1, 0], C3_s[-1, 0] - C2_s[-1, 0]))
    p2 = props_app2(np.array([C0]), np.array([T0_K]))
    p3 = props_app3(np.array([C0]), np.array([T0_K]))
    say("初态物性:  附录2 rho=%.1f cp=%.1f k=%.4f D=%.4e alpha=%.4e"
        % (p2[0][0], p2[1][0], p2[2][0], p2[3][0], p2[2][0] / (p2[0][0] * p2[1][0])))
    say("           附录3 rho=%.1f cp=%.1f k=%.4f D=%.4e alpha=%.4e"
        % (p3[0][0], p3[1][0], p3[2][0], p3[3][0], p3[2][0] / (p3[0][0] * p3[1][0])))
    for tag, p, src in (("app2", p2, "附录2"), ("app3", p3, "附录3")):
        add("F80_%s_rho" % tag, "%s 初态 rho" % src, float(p[0][0]), "kg/m^3", "解析", src)
        add("F80_%s_cp" % tag, "%s 初态 cp" % src, float(p[1][0]), "J/(kg K)", "解析", src)
        add("F80_%s_k" % tag, "%s 初态 k" % src, float(p[2][0]), "W/(m K)", "解析", src)
        add("F80_%s_D" % tag, "%s 初态 D" % src, float(p[3][0]), "m^2/s", "解析", src)
        add("F80_%s_alpha" % tag, "%s 初态 alpha" % src,
            float(p[2][0] / (p[0][0] * p[1][0])), "m^2/s", "解析", src)
    say("alpha 比 (附录3/附录2) = %.6f  (%.3f%%)"
        % ((p3[2][0] / (p3[0][0] * p3[1][0])) / ALPHA,
           ((p3[2][0] / (p3[0][0] * p3[1][0])) / ALPHA - 1) * 100))
    say("D 比 (附录3/附录2) = %.6f" % (p3[3][0] / p2[3][0]))
    add("F60", "max|T_附录3 - T_附录2| (0-1800s)", dT, "K", "运行", "C")
    add("F61", "max|C_附录3 - C_附录2| (0-1800s)", dCc, "kg/kg", "运行", "C")
    add("F62", "alpha 比 附录3/附录2 (初态)", float((p3[2][0] / (p3[0][0] * p3[1][0])) / ALPHA), "-", "解析", "C")
    add("F63", "D 比 附录3/附录2 (初态)", float(p3[3][0] / p2[3][0]), "-", "解析", "C")
    add("F64", "T(1800s,r=0) 附录2", float(T2_s[-1, 0]), "K", "运行", "C")
    add("F65", "T(1800s,r=0) 附录3", float(T3_s[-1, 0]), "K", "运行", "C")
    add("F60_r", "max|T_附录3-T_附录2| 出现位置 r", float(r4[iT[1]]), "m", "运行", "C")
    add("F60_t", "max|T_附录3-T_附录2| 出现时刻 t", float(t_out[iT[0]]), "s", "运行", "C")
    add("F65_diff", "T(1800s,r=0) 附录3 - 附录2", float(T3_s[-1, 0] - T2_s[-1, 0]), "K",
        "运行", "C")
    add("F67_diff", "C(1800s,r=0) 附录3 - 附录2", float(C3_s[-1, 0] - C2_s[-1, 0]), "kg/kg",
        "运行", "C")
    add("F62_pct", "alpha 比 附录3/附录2 的相对变化", float((p3[2][0] / (p3[0][0] * p3[1][0]))
                                                          / ALPHA * 100 - 100), "%", "解析", "C")
    add("F63_pct", "D 比 附录3/附录2 的相对变化", float(p3[3][0] / p2[3][0] * 100 - 100), "%",
        "解析", "C")

    hr("C2. 交叉验证: 附录2 耦合求解器 vs 已验证的半解析解")
    T_ana_Md = series_T(t_out, Tinf_out, r4, n_modes=400)[0]
    dval = float(np.max(np.abs(T2_s - T_ana_Md)))
    say("半解析 T(1800s) 中心 = %.6f K ; 附录2 耦合求解器 = %.6f K ; 差 = %.3e K"
        % (T_ana_Md[-1, 0], T2_s[-1, 0], abs(T2_s[-1, 0] - T_ana_Md[-1, 0])))
    say("半解析 T(1800s) 表面 = %.6f K ; 附录2 耦合求解器 = %.6f K ; 差 = %.3e K"
        % (T_ana_Md[-1, -1], T2_s[-1, -1], abs(T2_s[-1, -1] - T_ana_Md[-1, -1])))
    say("全时段 max|T_附录2耦合 - T_半解析| = %.3e K" % dval)
    add("F66", "max|T_附录2耦合 - T_半解析| (0-1800s)", dval, "K", "运行", "C2")
    say("水分: C(1800s) 中心 = %.8f ; 表面 = %.8f kg/kg" % (C2_s[-1, 0], C2_s[-1, -1]))
    say("(对照: 前一版求解器因系数多除一个 V 而给出中心 0.1789 —— 已修正)")
    add("F67", "C(1800s,r=R) 附录2 (本文求解器)", float(C2_s[-1, -1]), "kg/kg", "运行", "C2")
    add("F68", "C(1800s,r=0) 附录2 (本文求解器)", float(C2_s[-1, 0]), "kg/kg", "运行", "C2")

    hr("C3. 附录3 内部: T->D 反馈(耦合)到底值多少?")
    _, T3f_s, C3f_s, div3f, _ = solve_coupled(Md, dt_d, t_out, Tinf_at, Cinf_at, props_app3)
    _, T3b_s, C3b_s, div3b, _ = solve_coupled(
        Md, dt_d, t_out, Tinf_at, Cinf_at,
        lambda C, T: props_app3(C, T, T_ref=T0_K))
    dCf = float(np.max(np.abs(C3f_s - C3b_s)))
    say("完整 D=f(C,T) vs 冻结 Arrhenius 温度因子 (T=T0):  max|dC| = %.6e kg/kg" % dCf)
    say("  说明: 该项即'热-湿双向耦合'在 0-1800 s 内的净效应")
    add("F70", "附录3 内 T->D 反馈效应 max|dC| (0-1800s)", dCf, "kg/kg", "运行", "C3")
    say("")
    say("Q2/Q3 (附录3) 物性随 C 的变化范围 (C 由 2.55 降到 0.15):")
    for Cv in (2.55, 1.00, 0.50, 0.15):
        p = props_app3(np.array([Cv]), np.array([T0_K]))
        say("  C=%.2f : rho=%7.1f  cp=%8.1f  k=%.4f  alpha=%.4e  D=%.4e"
            % (Cv, p[0][0], p[1][0], p[2][0], p[2][0] / (p[0][0] * p[1][0]), p[3][0]))
        tg = ("%g" % Cv).replace(".", "p")
        add("F81_C%s_rho" % tg, "附录3 C=%g 时 rho" % Cv, float(p[0][0]), "kg/m^3", "解析", "附录3")
        add("F81_C%s_cp" % tg, "附录3 C=%g 时 cp" % Cv, float(p[1][0]), "J/(kg K)", "解析", "附录3")
        add("F81_C%s_k" % tg, "附录3 C=%g 时 k" % Cv, float(p[2][0]), "W/(m K)", "解析", "附录3")
        add("F81_C%s_alpha" % tg, "附录3 C=%g 时 alpha" % Cv,
            float(p[2][0] / (p[0][0] * p[1][0])), "m^2/s", "解析", "附录3")
        add("F81_C%s_D" % tg, "附录3 C=%g 时 D" % Cv, float(p[3][0]), "m^2/s", "解析", "附录3")
    p01 = props_app3(np.array([0.15]), np.array([T0_K]))
    p25 = props_app3(np.array([2.55]), np.array([T0_K]))
    say("  alpha(C=0.15)/alpha(C=2.55) = %.4f  (即干燥过程中热扩散系数变化 %.1f%%)"
        % ((p01[2][0] / (p01[0][0] * p01[1][0])) / (p25[2][0] / (p25[0][0] * p25[1][0])),
           100 * ((p01[2][0] / (p01[0][0] * p01[1][0])) / (p25[2][0] / (p25[0][0] * p25[1][0])) - 1)))
    add("F71", "附录3 alpha(C=0.15)/alpha(C=2.55)",
        float((p01[2][0] / (p01[0][0] * p01[1][0])) / (p25[2][0] / (p25[0][0] * p25[1][0]))),
        "-", "解析", "C3")
    add("F71_pct", "附录3 alpha(C=0.15)/alpha(C=2.55) 的相对变化",
        float((p01[2][0] / (p01[0][0] * p01[1][0])) / (p25[2][0] / (p25[0][0] * p25[1][0]))
              * 100 - 100), "%", "解析", "C3")

    # ---------------- D cost ---------------------------------------------
    hr("D. 成本对比")
    for M in (200, 400, 800):
        t0 = time.perf_counter()
        solve_T(M, 2.0 ** -5, t_out, Tinf_at, 0.5, "exact")
        say("数值 CN M=%4d : %7.2f s" % (M, time.perf_counter() - t0))
    for nm in (50, 200, 400):
        t0 = time.perf_counter()
        series_T(t_out, Tinf_out, np.array([0.0, R0]), n_modes=nm)
        say("半解析 %4d 项 : %7.3f s" % (nm, time.perf_counter() - t0))

    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(_ROWS) + "\n")
    with open(REG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "quantity", "value", "unit",
                                          "uncertainty", "source", "command", "note"])
        w.writeheader()
        for r_ in _REG:
            w.writerow(r_)
    print("\nwrote %s\nwrote %s" % (LOG, REG))


if __name__ == "__main__":
    main()
