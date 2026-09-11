# Research State — 2026 国赛 A 题 · 药材烘干

Last updated: 2026-09-10 (session 3)

## Session 3 — objective and findings

**User question**: 问题一能否"用附件数据拟合出一个函数，先利用热传导方程求出解析解"？

**Answer: 温度可以，水分不行；而且"拟合"这一步不该做——它比不拟合差 10–40 倍。**

Deliverable: new §10 in `model/problem_slove1.md`; experiment `src/q1_analytic_fit.py`;
registry `outputs/registry_q1_analytic_fit.csv` (39 rows).

### Session-3 claims ledger

| # | claim | status | evidence |
|---|-------|--------|----------|
| G1 | The semi-analytic route (Bessel eigenfunction + Duhamel) is valid for the temperature field in Q1: α is constant (附录2) and the Robin BC is linear | VERIFIED | derivation + G01 |
| G2 | Analytic implementation validated against the FV production solution: max\|ΔT\| = **1.503e-05 K** at t=1800 s over the 5 output radii (two independent implementations) | VERIFIED | G01 |
| G3 | **Duhamel has a per-segment closed form for piecewise-linear T∞** ⇒ fitting is unnecessary; the raw attachment points can be substituted directly | VERIFIED | G20/G21 |
| G4 | **Fitting is WORSE than not fitting**, by 10–40×: raw piecewise-linear 4.199e-3 K vs cubic fit 4.211e-2, quadratic 4.936e-2, saturating-exponential 5.617e-2, linear 1.630e-1 K | VERIFIED | §10.2 table |
| G5 | Fit residuals propagate at ~10× attenuation through thermal inertia: T∞ fit residual 0.19–0.57 K → solution error 0.02–0.16 K | VERIFIED | G02/G03 pairs |
| G6 | **Fitting over the whole 0–14400 s is a trap**: Q1-window error rises to 0.312 K (exp) / 0.673 K (cubic) / 2.333 K (quad) / 5.410 K (linear), because the fit is dominated by later data. If fitting at all, fit only on 0–1800 s | VERIFIED | §10.3 table |
| G7 | **Moisture CANNOT use the analytic route**: freezing D at D(C₀)=4.937655e-9 gives max\|ΔC\| = **4.1913e-2 kg/kg** = **838×** the 5e-5 four-decimal threshold | VERIFIED | G10/G11 |
| G8 | The linearisation error is concentrated at the surface: 2.55e-7 (r=0) / 1.20e-5 (0.5 cm) / 6.67e-4 (1 cm) / 1.01e-2 (1.5 cm) / 4.19e-2 kg/kg (2 cm) — i.e. exactly the column 表2 cares about | VERIFIED | G12/G13 pairs |
| G9 | A mere **21 %** variation of D across the domain (ratio 0.7864 at t=1800 s) is already enough to break linearisation; D spans far more later (D(0.15)/D(2.55) = 1/266) | VERIFIED | G14 + P06b |
| G10 | **Precision caveat**: 附件1 records temperature only to 1e-3 °C, while the problem asks for 4 decimals (needs 5e-5 °C). Upstream treatment choice alone moves the answer by 1e-3 to 1e-1 K. The 4th decimal is a **reporting convention, not an attainable accuracy** — it should be read as non-significant | VERIFIED | G22 + §10.2/§10.5 |

### Session-3 bug caught and fixed

Three defects, all found by running things rather than reading them:

1. **Unit bug**: `q1_analytic_fit.py` fed 附件1's **°C** values into `series_T`,
   which expects **K**. Produced an impossible 231 K error (the whole range is only
   22 K) and — the tell — an *identical* error across all five fit forms. Fixed.
   Lesson: an error invariant across variants that should differ is a bug.
2. **False reading of a plateau**: the first version of the analytic-vs-numeric
   script refined M at fixed Δt=2⁻⁹ and got a plateau
   (4.38e-6 → 3.90e-6 → 3.78e-6, ratios 1.12/1.03/1.01). I wrote "空间二阶收敛".
   **Wrong** — the plateau 3.75e-6 K equals exactly the temporal error at that Δt,
   so it was the *time* error floor. Fixed by adding a fixed-Δt M-vs-2M comparison,
   which gives clean ratios 4.001/3.989/4.014 (genuine 2nd order).
   Lesson: to measure spatial order you must cancel the temporal error, not just
   shrink it.
3. **Second writer clobbering the deliverable tables**: `src/q1_solve.py` (a
   diagnostic) was writing its own coarse M=800/Δt=0.125 solution to
   `outputs/table*.csv`. This is the *root cause* of the stale-CSV defect the
   session-1 auditor found — I had only fixed the symptom in `q1_produce.py`.
   Now `q1_produce.py` is the sole writer of deliverable tables; `q1_solve.py`
   writes `diag_table*_M800.csv` instead. Verified by an order-robustness test.

Also hardened `src/q1_reconcile.py`: its `find_match` used a 3 % tolerance with
x/100 and x/1000 variants, which **falsely matched large integers** — step counts
230400/460800/921600 were silently "passed" by matching P09 (2368.9) and others
after ÷100. Percent-variant matching is now restricted to |x| ≤ 1000 with a 1 %
tolerance. Hardening immediately exposed 3 genuinely unsourced numbers (the 5th
Bessel root, air c_p = 1005, and a "39×" ratio), all now registered or explicitly
allow-listed as unretrieved.

### Session-3 outputs

| path | what |
|------|------|
| `model/problem_slove1.md` §10 | 拟合 + 解析解可行性 |
| `model/problem_slove1.md` §11 | 解析 vs 数值逐点对照 + 误差拆解 |
| `model/problem_slove1.md` §12 | **误差最低路线的机理**: 逐段闭式解, 不构造连续函数 |
| `src/q1_analytic_fit.py` | §10 实验 |
| `src/q1_analytic_vs_numeric.py` | §11 实验 |
| `src/q1_piecewise_exact.py` | §12 精确性验证 |
| `outputs/registry_q1_{analytic_fit,ana_vs_num,piecewise}.csv` | 三个注册表 |

### Session-3 addendum: how the lowest-error route handles 附件1

User asked: 温度误差最低的是怎么把附件1变成连续函数的?

**It never builds a continuous function.** Verified by `src/q1_piecewise_exact.py`:

| # | claim | status | evidence |
|---|-------|--------|----------|
| W1 | The per-segment Duhamel formula is **exact**, not approximate: for a strictly linear ambient, one-step recursion vs the analytic closed form differ by **0.000e+00 K**, and the closed form vs an independent DOP853 integration (rtol 1e-13) by **1.137e-13 K** | VERIFIED | W01/W02 |
| W2 | **Using 附件1's raw 31 points as breakpoints, subdividing each segment 2/4/8/16× changes the answer by exactly 0.000e+00 K** — proof there is no quadrature error at all, because each 60 s segment is exactly linear | VERIFIED | W11_sub* |
| W3 | PCHIP, by contrast, IS a quadrature approximation in this implementation: its answer drifts with Δτ (4.514e-5 → 1.935e-7 K as Δτ goes 8 → 0.25 s); 3.010e-6 K at Δτ=1 s | VERIFIED | W20_tau* |
| W4 | The PL-vs-PCHIP final-answer difference (2.320e-3 K) is **epistemic, not numerical**. Input-side they differ by 3.500e-2 K, which is **35× 附件1's own 1e-3 recording precision** | VERIFIED | W30/W31/W32 |
| W5 | Fitting is worse because it is **dimensionality reduction**: 31 points → 4 (cubic) / 3 (exp) / 2 (linear) parameters, hence systematic bias; piecewise interpolation only connects points and preserves the data's shape | VERIFIED + reasoning | W40/W41_* |

The recursion used is
`b_k(t+Δ) = E_k b_k(t) − c_k s (1−E_k)/μ_k`, `E_k = exp(−μ_k Δ)` — the exact
antiderivative of the Duhamel convolution on a segment of constant slope `s`.
No interpolation evaluation, no quadrature, no fitting.

Note recorded honestly: **PCHIP could also be integrated exactly** (polynomial ×
exponential has a closed-form antiderivative). This implementation samples it at
Δτ and reuses the linear recursion, which is why it carries the ~1e-6 K
quadrature error; extending the recursion to the quadratic slope term would
remove it for a few lines of code.

### Session-3 parser fix (self-inflicted, found by the gate)

`src/q1_reconcile.py`'s `latex_to_plain` mapped a standalone `10^{-13}` to `e-13`,
leaving a bare `e-13` whose `-13` was then scanned as a standalone number and
reported as unsourced. Fixed to emit `1e-13`, and added the magnitude
declarations (1e-7 … 1e-15) to the allow-list. This was a parser artifact, not a
document error — the markdown was correct throughout.

**Both gates pass: 1662 literals, 655 registry-backed, 1007 definitional,
0 unmatched; 210 table values bit-identical to result1.xlsx.**

---

# Session 2 state (retained)

## Objective

**Session 1 (done)**: audit the user-supplied "问题一完整建模思路" against the
problem statement, attachments and a verified run; fix defects; write
`model/problem1.md` and `model/problem_slove1.md`.

**Session 2 (done)**: use the Wolfram MCP to model and compute per `feishu.md`, then
compare the two pairs of modelling approaches the user selected:
  (1) 半解析 (Bessel+Duhamel, feishu.md §6) vs 数值 (CN/BDF2, feishu.md §5)
  (4) 解耦一维模型 vs 文献多物理场耦合模型 (胡众欢等 2020)
Deliverable: `model/建模方式对比.md`.

## Session-2 claims ledger

| # | claim | status | evidence |
|---|-------|--------|----------|
| F1 | feishu.md §2.1 α = 1.6793e-7 is low vs exact 1.6885553471e-7 by 0.5481 %; τ_T 2381.94 vs 2368.89 s | VERIFIED | F01–F04 |
| F2 | feishu.md §4.2 τ_C = 7.15e5 s (~8.3 天) and Le ≈ 300 are unreproducible: exact τ_C = 8.1010113580e4 s (0.9376 d), Le = 34.1975. Its "D0 = 5.593e-10" corresponds to C = 0.352199, not C₀ = 2.55 | VERIFIED | F05–F08 |
| F3 | **feishu.md §6.1 eigen table is wrong**: wrote ~2.0/5.0/8.0/11.0; true λ_kR = 1.4184725188 / 4.1664696010 / 7.2084784644 / 10.3082731535 (residuals ~1e-16) | VERIFIED | F10_*, F17_* |
| F4 | **feishu.md §6.1 A_k is wrong**: c_k/A_k = 1/(1+(x_k/Bi)²), verified to 6 digits on k=1..6; the error GROWS with k (ratio 0.489 → 0.00699) | VERIFIED | F14, F18_*, F19_*, F1A_*, F1B_* |
| F5 | With 8 terms, correct c_k reproduces the constant 1 (r=R: 0.96381405); feishu A_k gives **11.52** at r=R — error O(10) exactly where the Robin BC lives | VERIFIED | F1C_*, F1D_* |
| F6 | feishu.md §5.3 interior b_i = 1+αΔt/Δr² **is** the correct CN value; interior RHS signs are consistent with CN | VERIFIED | derivation + F21/F22 |
| F7 | **feishu.md §5.3 d_i signs ARE wrong** (+a_i, +c_i with negative a_i,c_i) → diverges: t=127.00 s at M=200, t=62.50 s at M=800 (finer grid diverges sooner) | VERIFIED | F30_M200, F30_M800 |
| F8 | **feishu.md §5.3 surface row mixes time scales**: interior CN (θ=½), surface backward-Euler (θ=1). Consequence: error plateaus at 70.7317 K (M=400) and is INSENSITIVE to Δt (F26 ≈ 0) → converges to a different boundary condition | VERIFIED | F20_*, F25_*, F26 |
| F9 | Fixing the θ scale (leading geometry) gives FIRST order (ratios 1.981/1.991/1.995); additionally fixing to the exact half-CV f_M = 2(M−0.5)/(Δr²(M−0.25)) gives SECOND order (ratios 4.039/4.171/4.827) | VERIFIED | F21_*, F22_* |
| F10 | V_M = π(R·dr − dr²/4) is the correct half-control-volume; exact_cn reaches 6.65961e-6 K at M=400, meeting feishu.md §6.3's own 1e-5 K and order-2 criteria. Only exact_cn satisfies them | VERIFIED | F22_M400_exact |
| F11 | Numerical CN vs semi-analytic Bessel+Duhamel agree to **3.4936501265e-6 K** over 0–1800 s (two independent implementations) | VERIFIED | F40, F43, F44 |
| F12 | Semi-analytic CANNOT do the moisture field: linearising D at D(C₀) gives max\|ΔC\| = 4.1861810290e-2 kg/kg (≈800× the 5e-5 threshold) | VERIFIED | F50–F53 |
| F13 | **Coupling is set by the problem statement, not chosen**: 附录2 (Q1) is decoupled; 附录3/4 (Q2–Q4) are two-way coupled. Using 附录3 properties on Q1 costs 1.4019076018 K and 0.13834689131 kg/kg | VERIFIED | F60–F65 |
| F14 | Coupling matters on Q2–Q4: freezing the Arrhenius T-factor alone shifts moisture by 7.5472916081e-2 kg/kg; α varies by 48.2 % over the drying range | VERIFIED | F70, F71, F71_pct |
| F15 | Timings are machine-dependent and run-to-run variable (~2×); deliberately NOT quoted as reconcilable values | VERIFIED (observation) | §1.8 of report |
| F16 | 胡众欢等 (2020) is NOT re-implementable: no initial/boundary conditions at all, no k, no a_w, no c_v,sat, no numerical method; validation = 2 numbers (13.3 %, 0.016) | VERIFIED from source text | `.research/hu_zhonghuan_model.md` |
| F17 | Its DOI 10.13718/j.cnki.xdzk.2020.02.015 returns HTTP 404 from CrossRef — independently re-confirmed this session | VERIFIED | `mcp__academic__get_paper_by_id` → 404 |
| F18 | The semi-analytic reference is NOT circular: session-2's `eigen()` and session-1's independently written `robin_cylinder_eigen`/`robin_cylinder_theta` agree to ≤3.6e-15 on roots, exactly on coefficients, and **5.684e-14 K** on the evaluated series (constant T∞, t=60–1800 s, r/R=0–1) | VERIFIED | `src/audit_series_cross.py` |
| F19 | **Session-1 claim C19 mixed two different Δt**: `4.0295e-2` is the Δt=0.02 s `cell` value while `4.477269727e-6` is the Δt=0.0005 s `flux` value. Same-Δt pairing at Δt=0.0005 s is `cell`=0.04037790745, `flux`=4.477269727e-6, ratio 9018.421922 | VERIFIED | `outputs/registry_q1_energy.csv` E30/E31/E32_M800_dt0.0005; C19 corrected in this file |
| F20 | Conclusion C19's order claims survive the correction (order is a property of the surface form, not of Δt) | VERIFIED | same registry rows |
| F21 | The report is internally consistent across all cross-section numbers: F65−F64 = −1.38609485 matches F65_diff; max\|dT\| F60 = 1.401907602 > \|value at r=0\| because the max sits at r=0.0138 m; percentages −14.23/+14.26/+48.2 match F62/F63/F71_pct; F50/5e-5 = 837.2× so the report's "800 倍以上" holds; convergence ratios 1.981/1.991/1.995 (→2, first order) and 4.039/4.171/4.827 (→4, second order) | VERIFIED | `src/_check_internal.py` |
| F22 | **feishu.md §6.1's eigen table values are too LARGE by 6.7–41%** (2.0/5.0/8.0/11.0 vs 1.4185/4.1665/7.2085/10.3083). An earlier draft of the report said "偏小 8–40%" — the direction was WRONG and has been corrected | VERIFIED | recomputed; report §1.3 corrected |
| F23 | The §6.1 table is **not the root set of the equation for any single Bi**: substituting back gives Bi = 5.1518 / 9.2226 / 10.9355 / 11.3595, which differ by ~2×. Table spacing is uniformly 3.0 vs true spacings 2.748/3.042/3.100 (→π). They are placeholders | VERIFIED | `scipy.special.j0/j1` evaluated in-session |

## Session-2 corrections to my OWN work (recorded so they are not re-made)

- **Bug: `f_M_lead` coded as `2.0/dr` instead of `2.0/dr**2`** (dimensionally wrong
  by Δr). Produced an impossible 12.37 K error for a variant that should be ~1e-2 K.
  Caught because a 6e-4 coefficient change cannot cause a 10^6 error change in a
  convergent scheme. Fixed.
- **Bug: `solve_coupled` divided by V twice** (`h_0/V[0]` where `h_0` already
  contained `/V[0]`), which dried the whole cylinder in 1800 s (centre 0.1789 vs the
  correct 2.5499923). Caught by cross-checking against the semi-analytic solution.
- **Misread convergence ratio**: "ratio → 4" and "ratio → 2" were swapped in an
  early draft. For error ∝ h^p, doubling M divides the error by 2^p, so
  **ratio 2 ⇒ first order, ratio 4 ⇒ second order**. Corrected.
- **Wolfram `FindRoot` bracket**: passing `{x,a,b}` as a list solves a vector
  equation; must pass `{x, a, b}`. One call also produced a 569 KB output explosion
  from an unevaluated symbolic `Table`.
- Timing values were initially quoted, then removed: they cannot be reconciled
  (an unreconcilable number does not ship).

## Session-2 artefacts

| path | what |
|------|------|
| `model/建模方式对比.md` | **the deliverable**: both comparisons |
| `src/feishu_compare.py` | Python recomputation independent of Wolfram; builds the registry |
| `src/feishu_reconcile.py` | deterministic per-literal number check vs the registry |
| `src/_diag_surface.py` | scratch diagnostic that located the f_M bug |
| `outputs/registry_feishu.csv` | 161-row numbers registry |
| `outputs/feishu_compare.log` | full run log |
| `outputs/wolfram_feishu_audit.log` | Wolfram-side raw output (constants, eigen, coefficients) |
| `outputs/reconciliation_feishu.csv` | per-literal reconciliation |
| `.research/hu_zhonghuan_model.md` | 627-line source-tagged extraction of the cited paper |
| `.research/comparison4_sources.md` | condensed facts used for comparison 4 |

## Verification status (session 2)

`src/feishu_reconcile.py`: **509 literals, 38 MATCH, 132 ROUNDED, 339 ALLOW,
0 NO_SOURCE.** Registry: 161 rows.

**The allow-list was initially too permissive and was tightened.** A probe
(`src/_check_allowlist.py`) found **45 high-precision computed values being waved
through as ALLOW** instead of being checked against the registry. The allow-list now
contains only definitional numbers — 附录2/3/4 constants, structural indices, grid
settings (M, Δt, t, r) and pure-math constants. Computed values that were being
excused were moved into the run and registered (eigenvalues and c_k/A_k for k=1..6,
the reconstruction sums, all convergence ratios, D(0.15), Bi, the 附录3 property
table, the 附录2/3 differences). Effect: registry-backed literals rose from 103 to
**170**; only one high-precision ALLOW token remains, `0.015625` = Δt = 2⁻⁶, which
is a grid setting and legitimately definitional.

## Next action

Session 2's comparison deliverable is complete and self-verified. **One outstanding
gap: the independent adversarial audit did not complete** — the delegated
`claim_auditor` was stopped before returning a report, so `model/建模方式对比.md`
is recorded as **self-verified but NOT independently audited** (§3.0 of the report
states this explicitly). If the comparison is to be submitted or defended, re-run a
full `research-audit` over it. Remaining optional work: a figure set, and extending
the same audit to 问题 2–4.

---

# Session 1 state (retained)

## Objective (session 1)

Audit the user-supplied "问题一完整建模思路" against the authoritative problem
statement, the attachment data, and a numerically verified run. Fix every defect
found. Write the corrected model and solution narrative to `model/problem1.md`
and `model/problem_slove1.md`.

## Question (scoped)

Q1: Is the proposed cylindrical 1-D radial heat + moisture diffusion model for
**问题1 (预热平衡阶段, 0–1800 s)** mathematically correct, physically consistent
with the given parameters, and numerically sound enough to produce result1.xlsx
at the required precision (4 decimals)?

## Authoritative sources retrieved

| id | source | what it fixes |
|----|--------|---------------|
| S1 | `A题/A题.pdf` → `docs/A题.md` (markitdown) | problem statement, tables 1–2, appendices 1–4 |
| S2 | `A题/附件/附件1.xlsx` (A1:C242) | T∞ 28.000→50.246 °C, C∞ 0.01963→0.05025 kg/kg, Δt=60 s, 0–14400 s |
| S3 | `A题/附件/附件2.xlsx` (A1:B146) | R 2.000→1.198 cm, Δt=1800 s, 0–259200 s |
| S4 | `A题/附件/附件3/result1.xlsx` | template: sheets 温度/水分浓度; A1="时间\到药材中心的距离"; row 1 = 0,0.1,...,2; A col = 1,2,3,… s |

## Claims ledger (all statuses verified by run unless noted)

| # | claim | status | evidence |
|---|-------|--------|----------|
| C1 | α = k/(ρc_p) = 1.688555e-7 m²/s; the user's stated 1.679e-7 is low by 0.569 % | VERIFIED | `--selftest` P01/P02 |
| C2 | D(C)=7e-9·exp(−0.89/C): D(2.55)=4.9377e-9; D(0.15)=1.855e-11; D(0.0331)=1.471e-20 m²/s; span 3.36e11 | VERIFIED | P03–P06 |
| C3 | Thermal Bi = 1.389 (>0.1 ⇒ radial T gradients are not negligible); R²/α = 2368.9 s | VERIFIED | P07/P09 |
| C4 | **Interior diagonal b_i in the proposed scheme is WRONG.** Their own stated difference formula gives b_i = −2/Δr² (row sum 0); they wrote b_i = α(2i+1)/(2iΔr²), i.e. the T_{i+1} coefficient. Deficit = exactly |a_i|; row sum becomes −(1−2i)/(2iΔr²)α ≠ 0 | VERIFIED (sympy + run) | S01–S04 |
| C5 | Consequence: the implied operator is anti-dissipative, max Re λ = **+16.816 s⁻¹** (correct operator: 3.9e-16) | VERIFIED | E1 |
| C6 | The proposed scheme **diverges for every Δt tested** (0.0005 … 0.1 s). Growth law is **1/(1−Δt·λ)**, i.e. (1−Δtλ)^(−n) — NOT (1+Δtλ)^n (that form is off by 53 orders at Δt=0.05). Overflow at t≈8.7 s for Δt=0.1 s; reducing Δt only *delays* it (t≈40 s at Δt=5e-4). No usable Δt exists: overflow persists up to Δt≈3 s, and beyond that (Δt ≳ 7.4683 s) the solution is a persistent sign-alternating oscillation of amplitude ±14–30 K (physical ≈301.15 K) — still meaningless | VERIFIED | S2, E1, dt-scan; growth law confirmed numerically |
| C7 | r=0 node coefficients (b_0=1/Δt+4α/Δr², c_0=−4α/Δr²) are **CORRECT** | VERIFIED | derivation + S3 |
| C8 | Surface node coefficients (a_M=−2α/Δr², b_M=2α/Δr²+2αh/(kΔr)+1/Δt) **are the correct leading-order node-centred half-control-volume coefficients.** V_M → πRΔr (HALF ring, not 2πRΔr), so f_M⁻ = A_{M−1/2}/V_M → 2/Δr and a_M → −2α/Δr², exactly as written. Relative deviation from the exact half-CV value is 1/(4M) (3.13e-4 at M=800) | **VERIFIED CORRECT** (this claim was asserted wrong, withdrawn, re-asserted wrong, and finally settled correct — see corrections list) | analytic derivation + numeric check |
| C9 | Moisture surface convective coefficients likewise correct to leading order (g_m = A_s h_m/V_M → 2h_m/Δr, no D factor) | VERIFIED | derivation |
| C10 | **Node-value diffusivity is non-conservative**: discrete water balance residual is 10.1 % of the surface flux and does NOT shrink with refinement (10.10/10.12/10.12 % at M=100/200/400). Face-averaged D gives 1e-14 | VERIFIED | E2 |
| C11 | Practical impact of C10 on Q1: max |ΔC| = 6.35e-2 kg/kg at t=1800 s (2.5 % of C₀), grid-independent; at t=3 h it is 0.68 kg/kg | VERIFIED | D3 |
| C12 | Corrected scheme is 2nd order in space (empirical 2.02→2.28) and 1st order in time | VERIFIED | S4, S5 |
| C13 | Corrected scheme validated against the analytic Robin-cylinder series (Carslaw–Jaeger form): max |T_FV−T_exact| → 4.5e-6 K at M=800/Δt=2⁻¹¹; the earlier 2.36e-4 K "plateau" was purely implicit-Euler temporal error | VERIFIED | S8, S9, E3 |
| C14 | Semi-implicit lagged D vs fully nonlinear (BDF): max |ΔT| = 5.9e-5 K, |ΔC| = 5.3e-6 kg/kg at M=200 | VERIFIED | S15/S16 |
| C15 | Ambient C∞ is noisy: 80 of 240 steps decrease; |median Δ|/std = 0.51 (noise ≈ 2× trend). Within 0–1800 s the 31 points are monotone, so Q1 is insensitive: linear-vs-pchip changes T(1800 s) by 4.8e-4 K and C by 1.2e-7 | VERIFIED | P16/P17, S7 |
| C16 | 1-D radial is **exactly** valid on the mid-plane z=0 (∂/∂z=0 by symmetry), independent of L/R; the L/R=12.5 heuristic is only needed to argue the ends do not leak inward | INFERENCE (analytic symmetry argument) | — |
| C17 | h_m = 8e-7 m/s is ~4 orders below the value implied by the heat/mass-transfer analogy (≈ h/(ρ_air c_p,air) ≈ 0.023 m/s). Flagged as a physical-consistency note; NOT changed, since 附录2 fixes it | INFERENCE (order-of-magnitude, analogy from memory, not retrieved) | — |
| C18 | For 附录2, D has no T-dependence ⇒ heat and moisture decouple in Q1. In 附录3/4 D = f(C,T) (Arrhenius) ⇒ they couple in Q2–Q4. The user's blanket "相互独立" is only true for Q1 | VERIFIED from S1 | — |
| C19 | The user's surface form (dropping the $O(\Delta r)$ geometry factors) converges **only first order** in space. **CORRECTED (session 2):** the original statement quoted `4.029e-2` for M=800 alongside `4.477e-6`, but those are **different Δt** — 4.0295e-2 is the **Δt=0.02 s** `cell` value, while 4.477269727e-6 is the **Δt=0.0005 s** `flux` value. Same-Δt pairing at Δt=0.0005 s: `cell` = 0.04037790745 K, `flux` = 4.477269727e-6 K, ratio 9018.421922 (registry rows E31/E30/E32_M800_dt0.0005). The order conclusion is unchanged: dropping the O(Δr) geometry is first order, keeping the exact half-CV is second order. At M=800 the first-order error is ~3 orders above the 5e-5 four-decimal threshold; ≈0.01 K still remains at M=3200. **Precision improvement, not an error in the user's formula** — the leading terms agree | VERIFIED (values re-checked against `outputs/registry_q1_energy.csv`) | E4; independent: `outputs/audit_extra.log`, `outputs/audit_orders.log` |
| C20 | Production run (M=3200, Δt=2⁻⁸ s) discrete uncertainty: T < 3.742e-6 K, C < 1.171e-5 kg/kg; both below 5e-5 ⇒ 4-decimal reporting is safe | VERIFIED | `outputs/q1_production.log` |
| C21 | Centre moisture is unchanged over 1800 s: C(r=0) 2.550000 → 2.549992 (relative change 3.01e-6); only a surface shell dries; volume-average falls 10.12 % | VERIFIED | q1_run.log §S9 |

## Corrections to my own earlier claims (recorded so they are not re-made)

- "Surface coefficients are 2× too large" — first asserted, then **withdrawn**, now
  **re-established with a mechanism**: they are too large by 2× in the *diffusion*
  term, and the consequence (O(Δr) boundary error of ~0.04 K at M=800) is real.
  The withdrawal was correct about the mechanism I first proposed (a cell-centred
  control volume) being wrong for the *interior*, but the surface conclusion stands.
- §5 of `problem_slove1.md` initially quoted "4.5e-6 K vs 9.5e-5 K"; the 9.5e-5
  figure was **not** from a run of the cell variant — it was a misread of a
  different comparison. Replaced with the real E4 numbers.
- Registry rows S25/S26 were mislabelled (centre values under surface labels);
  fixed by adding explicit centre/surface/ratio rows (S23c_*, S23s_*, S23r_*, S23q_*).

## Numbers reconciliation

`src/q1_reconcile.py` scans both documents for every numeric literal and checks it
against the four registries or the definitional allow-list. Current status:
**986 literals, 288 registry-backed, 694 definitional, 0 unmatched.**

Registries:
- `outputs/registry_q1_production.csv` — from `result1.xlsx` (92 rows)
- `outputs/registry_q1.csv` — main diagnostics (76+ rows)
- `outputs/registry_q1_diagnostics.csv` — stability/conservation (from D-section)
- `outputs/registry_q1_energy.csv` — eigenvalues/mass balance/limits (from E-section)

## Artefacts

| path | what |
|------|------|
| `docs/A题.md` | markitdown conversion of the problem statement (derived; cite PDF pages) |
| `src/q1_solve.py` | main solver + symbolic check + convergence + analytic/MOL validation + registry |
| `src/q1_diagnostics.py` | D1 analytic-truncation vs FV error; D2 stability scan; D3 node-D vs face-D |
| `src/q1_energy_check.py` | E1 operator eigenvalues + dt scan; E2 discrete mass balance; E3 dt→0 limit; E4 surface-coefficient variants |
| `src/q1_produce.py` | production run, writes `outputs/result1.xlsx` |
| `src/q1_registry.py` | builds the production registry FROM result1.xlsx |
| `src/q1_reconcile.py` | deterministic check: every numeric literal in both documents vs registries |
| `outputs/result1.xlsx` | **the deliverable**: 温度 / 水分浓度, 1800×21 each |
| `outputs/table1_temperature.md`, `outputs/table2_moisture.md` | 表1 / 表2 |
| `outputs/registry_q1*.csv` | 4 registries (production / diagnostics / diagnostics-D / energy) |
| `outputs/reconciliation_q1.csv` | per-literal reconciliation report |
| `outputs/audit_*.log` | independent auditor's runs (separate context) |
| `model/problem1.md` | model document (deliverable) |
| `model/problem_slove1.md` | solution/numerics document (deliverable) |

## Ruled out / withdrawn

- Hypothesis "surface coefficients are 2× too large" — **WRONG, twice.** I asserted
  it, withdrew it, then re-asserted it with an "exact half-CV" derivation, and that
  second derivation was also wrong: I took V_M → 2πRΔr (a FULL ring) when the
  half-CV at the boundary is V_M = πΔr(R−Δr/4) → **πRΔr**, giving f_M⁻ → 2/Δr and
  a_M → −2α/Δr² — exactly the user's coefficient. Settled by direct numeric
  comparison: −2α/Δr² / a_M^exact = 1/(1−1/(4M)) (3.13e-4 at M=800). Lesson: at a
  boundary node the control volume is half a cell, so the factor is πRΔr, not 2πRΔr.
- Hypothesis "the user's scheme is stable but converges to the wrong solution" —
  WRONG. It is anti-dissipative and divergent.
- Hypothesis "instability threshold is Δt < Δr²/α ≈ 0.059 s" — WRONG. There is
  no stable Δt; reduction only delays the overflow.
- Hypothesis "the surface term is negligible (<1e-4 K)" — WRONG. Dropping the
  O(Δr) geometry factor costs first-order boundary accuracy: 0.040 K at M=800.
- §5 of `problem_slove1.md` quoted "4.5e-6 K vs 9.5e-5 K"; the 9.5e-5 figure was
  never produced by a run. Replaced with the real E4 numbers.
- Registry rows S25/S26 were mislabelled (centre values under surface labels);
  split into explicit S23c_/S23s_/S23r_/S23q_ rows.

## Verification status (final)

- **Gate 1 — numbers registry:** `python src/q1_reconcile.py` → 1190 numeric
  literals; 409 registry-backed, 781 definitional, **0 unmatched**.
- **Gate 2 — table/xlsx identity (no tolerance):** 210 table values across
  `model/problem_slove1.md`, `outputs/table*.md`, `outputs/table*.csv` all match
  `outputs/result1.xlsx` **bit-for-bit at 4 decimals**. This gate was added after
  the independent audit found the `.csv` files stale from a coarse run (3e-4 K /
  1e-4 kg/kg conflict that gate 1 could not see, because it only scanned the two
  `.md` files). Both defects are fixed and the gate now exits 2 if they recur.
- `outputs/result1.xlsx`: 1800×21 both sheets; T monotone in t and inside
  [28, T∞(1800)]; C monotone decreasing and ≤ C0.
- Production discrete uncertainty (M=3200, Δt=2⁻⁸ s): T < 3.742e-6 K,
  C < 1.171e-5 kg/kg — both below the 5e-5 four-decimal threshold.

## Audit adjudication (the independent context reached a partly different verdict)

Two of its blocking claims were **checked against faithful re-implementations and
refuted**:

- It claimed `E4`'s "cell" variant was not a faithful implementation of the user's
  surface row. I implemented that row literally
  (a_M = −2α/Δr², b_M = 1/Δt + 2α/Δr² + 2αh/(kΔr), both truncated) and got
  **identical** errors (ratio 1.000 at M=200/400/800/1600). E4's attribution stands.
- It claimed `E5`'s moisture blow-up times came from a scheme with an extra defect.
  I tested all four (face/nodal × user/fixed diagonal) combinations: blow-up is
  **787.8 / 805.0 / 817.3 s** under both faithful variants and never occurs with the
  repaired diagonal. E5's attribution stands. Its own reported 381–394 s did not
  reproduce.

Its other two claims were **accepted and fixed**: the stale CSVs (above), and the
divergence-threshold wording. On the threshold it was right and I was wrong: the
user operator has **66 positive eigenvalues**, λ ∈ [0.267798, 16.816152] s⁻¹, and
amplitude growth is set by λ_min⁺, so the overflow-stopping threshold is
2/λ_min⁺ = **7.4683 s**, not 2/λ_max = 0.1189 s. Verified by direct Δt scan
(overflow at 0.5/1/2/3 s; finite but meaningless from ≈5 s on).

## Out of scope / unverified

The audit pass also wrote `src/q1_fig_*.py`, `src/fig_style.py`,
`src/q1_sensitivity.py`, `src/q1_sens_registry.py`, several `src/audit_*.py`, and
rendered figures under `paper/figures/`. These were **not** requested, are not
referenced by either deliverable, and I have **not** verified them (this model
cannot view images). Treat them as unreviewed extras. A stray duplicate
`model/problem1_v1.md` was removed (byte-identical to `model/problem1.md`).

## Next action

Deliverables complete and reconciled. Optional next: apply the same audit to
问题 2–4, where D = f(C,T) makes the fields genuinely coupled (see
`model/problem1.md` §7.4) and the semi-implicit lag needs revisiting.
