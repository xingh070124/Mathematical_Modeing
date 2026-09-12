# Audit: 问题二 交付物（`model/problem2_slove.md` + `model/problem2.md` + `outputs/result2.xlsx`）

Auditor: adversarial verification pass. Scope: the three deliverables above, the eleven
scripts listed in the brief, the nine registries, and the five logs. All numbers below
were recomputed from the primary artefacts in this session; nothing is taken from the
prose, from a log, or from a registry without an independent recomputation or a stated
reason why not.

Reproducing commands are in `src/_audit_q2_*.py` (scratch, non-production; the production
scripts and the two documents were not modified). Raw outputs: `outputs/_audit_P.log`,
`outputs/_audit_E2.log`, `outputs/_audit_reconcile_out.txt`.

**Verdict: BLOCKED — 5 blocking items.** The result is substantively sound: a from-scratch
re-run of the production configuration reproduced every one of 37 800 sampled shipped
values bit-for-bit at 4 dp, all 60 values in 表3/表4 reconcile against `result2.xlsx`, and
both headline model claims (the 17.274457 K energy-form difference and the extrema-principle
violation) were reproduced exactly from scratch. The block comes from two shipped numbers
that no source supports (§9.3 shrinkage; §5.5/§6 configuration), one provably inexact
derivation step presented as exact (§2.1), a magnitude analysis that does not describe the
variant that ran (§2.1), and an uncertainty statement whose conclusion is
convention-dependent (§7.3).

---

## 1. Verdict per central claim

| # | Claim | Verdict | Evidence (one line) |
|---|---|---|---|
| C1 | Energy-equation form | **REFUTED as a derivation; VERIFIED as a numerical effect** | `_audit_q2_A/E2/E`: the 17.274457 K gap reproduces exactly (`V11` re-run), but sympy gives `d(ρc_p)/dC − c_lρ_s = 1044(2093C+725)/(C+1)² ≠ 0` (649 134 vs 1 151 327 at C=2.55, factor 1.77), so the printed "exact cancellation" is not exact, and the 656.05 W/m³ / 0.252 magnitude does not follow from the stated 7 K (670.41 W/m³, 0.25754) nor describe the regression that ran (T absolute ⇒ ≈2.95e4 W/m³, 45× larger) |
| C2 | r=0 lumped-mass coefficient | **VERIFIED** | `_audit_q2_A`: element-by-element assembly from problem2.md §9.2's `M^e` for M=10…3200 gives `M^L_00 = Δr²/6` exactly, `M^L_MM = Δr²(3M−1)/6` exactly, `M^L_ii = Δr·r_i` to 2.1e−16, and `K_00/M_00 = 3α/Δr²` vs the exact `4α/Δr²` — ratio exactly 0.750000 for every M |
| C3 | Extrema principle | **VERIFIED** | `_audit_q2_B/L/O`: min T = 27.990477 °C (registry `V4_Tmin` = 27.990477261815) with evaporation ON, exactly 28.000000 °C with it OFF (violation 0.000000000 K); max T = 49.8888 < 50.2460 °C with 0 of 226 800 samples above the envelope; the upper bound also holds analytically because `C_R − C_∞ ≥ 0.958 kg/kg` for all t, so evaporation is a pure sink and the surface cannot cross above T∞ |
| C4 | Convergence orders | **VERIFIED (conclusion); one stated justification invalid** | `_audit_q2_K`: `sqrt(D·1 s)/Δr = 12.02` cells at M=3200 (doc ">10" ✓) and the M=3200 profile reproduces exactly (2.51983053 → k=7 2.5328633); but ">10 cells" does not follow from "still rising at node 8" — the profile is still rising at k=20 (2.54552) and only returns within 1e−5 of 2.55 at k≈58 |
| C5 | Latent heat | **VERIFIED (every number, independently reproduced); one interpretive sub-claim REFUTED** | `_audit_q2_D/N`: my own IAPWS-95 evaluation gives h_fg(28 °C) = 2434560.485584 (reg. 2434560.4856), slope −2391.009418 (reg. −2391.0094), anchored residual 109.2122 J/kg over 28–50 °C, Clapeyron dev 0.1016 J/kg. But the "0.008452 pp inconsistency" equals `(v_f/v_g)×100` to 0.4 % (0.008416 pp) — it is the neglected liquid volume, i.e. 2.1 % of the 0.40141 pp deviation, so "偏差全部来自气相非理想性" is false |
| C6 | Production uncertainty | **Arithmetic VERIFIED; the estimator UNSUPPORTED as an error estimate** | `_audit_q2_B/L`: 1.3808e−5/5e−5 = 27.616 % (doc 27.62 %), 3.8467e−5/5e−5 = 76.934 % (doc 76.93 %) — both correct. But the two inputs are *increments between refinements*, not the error of the shipped grid: Richardson-consistent estimates are T 2.76e−5 (55 %), C 5.13e−5 (**103 %, above**); sum convention C 6.83e−5 (137 %); RSS C 4.87e−5 (97 %) |
| C7 | 表3/表4 and `result2.xlsx` | **VERIFIED** | `_audit_q2_B/P`: all 60 doc table values agree with the xlsx at 4 dp (0 mismatches); structure matches the template (sheets 温度/水分浓度, row 1 = `时间\到药材中心的距离` + 0…2 cm, col A = 1…10800 s, 10800×21, no NaN); `q2_reconcile.py`'s second gate re-run compares 180 table values with 0 issues; and a **from-scratch re-run of the production config (M=1600, Δt=1/64) reproduces rows 1…1800 of the shipped file — all 37 800 values identical at 4 dp** (max raw |ΔT| = |ΔC| = 5.000e−05 = exactly the rounding half-ulp, i.e. the residual is the file's rounding, not a solve discrepancy) |

---

## 2. Failure-mode table

| Mode | Verdict | Evidence |
|---|---|---|
| 1 Implementation bug passing self-review | **CLEAR** | `q2_solve.py --selftest` re-run: lumped-mass identities 2.1e−16, Jacobian-vs-central-difference 2.250e−7 for all six configurations (2.245e−7 for 附录2), frozen 9.667e−2 as designed. `q2_verify.py --only V12,V13` re-run reproduced the registry row-for-row. V11 re-run from source reproduced 17.274457 K / 0.234574 / gaps 5.2156e4 and 2.8624e−8 exactly. V4 reconstructed from scratch: 27.990477 °C with evaporation, exactly 28.000000 without. FEM coefficients re-derived by hand from problem2.md §9.2 `M^e` — every one exact. **A full from-scratch re-run of the production configuration (M=1600, Δt=1/64, 115 200 steps, 274 s) reproduced rows 1…1800 of the shipped `result2.xlsx` — 37 800/37 800 values identical at 4 dp** (`src/_audit_q2_P.py`). The `t=1 s, r=0` entry is exactly 28.0000 and C(0,t=1 s) = 2.55, consistent with R²/D = 7.09e4 s. |
| 2 Fabricated / miscited citation | **INSUFFICIENT_EVIDENCE** (non-blocking per skill rules, warning attached) | `problem2.md` §4.4(b) cites **胡众欢 2020** for "气/液双场方程 + 源项 R = K_evap(a_w c_v,sat − c_v)" — **SUPPORTED**: the local primary source (`docs/基于多物理场耦合的热风干燥模型及其验证_胡众欢.md`, eqs. 15–16) gives exactly that gas-phase equation and source term. **IAPWS-95** is real and the installed `iapws` 1.5.5 implements it, but no identifier is given. **杨历 2005** (§4.4(b), "边界含 r_l α_m(M−M_f) 潜热项") — **UNRESOLVED**: no local copy, and the web-search endpoint returned HTTP 402, so I could not resolve the identifier or the proposition. `problem2.md` line 208's "番石榴模型" claim carries no citation at all. |
| 3 Fabricated or unsourced result | **SUSPECTED** | (a) §9.3 "附件2 显示 3 h 内半径由 2.000 降到约 1.75 cm（收缩约 12 %）" — 附件2 at t = 10800 s gives **R = 1.5520 cm, shrink 22.40 %**; 1.75 cm corresponds to t ≈ 4 200 s, not 3 h. (b) §6 states production M = 800, Δt = 1/32; §7.3/§8 state M = 1600, Δt = 1/64 (= the code); §5.5 quotes a third pair (M = 1600, Δt = 1/32) that reproduces its own 13.8360 / 0.28154 %. (c) the 656.05 W/m³ / 0.252 magnitude does not describe the compared variant (see C1). (d) §7.4's per-radius counts need an undisclosed −1e−4 K threshold. |
| 4 Shortcut reliance | **CLEAR** | The two candidate shortcuts are both disclosed and scoped: `h_m`'s "flux per unit density" convention (§4.3) and the pure-water h_fg (§4.1), with a delivered sensitivity showing h_m×10 moves C(R,10800 s) from 1.00778 to 0.12668 and H_evap±20 % moves T by 0.0216 K. No-shrinkage (B7) is disclosed and is arguably within Q2's terms, since Q2 mandates 附录3 while 附件2/shrinkage is Q4's object. The one defect here is the *magnitude* of the disclosed bias, counted under mode 3. |
| 5 Bug reframed as novel insight | **SUSPECTED** | The document's headline contribution (D1/§2.1/§9.2, "精确相消") is the step that is provably not exact for the stated functions: the cancellation requires `d(ρc_p)/dC = c_lρ_s`, and sympy gives a nonzero defect that is 1.77× at C = 2.55. The document's own §2.3 reports the fact that refutes it (`EB_rhos_drift = +111.57 %`) without connecting the two. The *conclusion* survives on a corrected derivation, so this is a wrongly-justified insight, not a wrong result — but "精确相消" is asserted, not demonstrated. |
| 6 Methodology fabrication | **SUSPECTED** | §6's parameter table ("求解流程与参数") gives the production setting as M = 800 (Δr = 0.0025 cm), Δt = 1/32 s, justified as "由 §7.2 确认". §7.3 ("生产设置") and §8.1 give M = 1600, Δt = 1/64 s, matching `q2_produce.py` (`PROD_M = 1600`, `PROD_DT = 1/64`). The Methods section therefore describes a configuration that did not run, and §5.5 quotes a third one. |
| 7 Frame-lock | **CLEAR** | The question is fixed by the contest (Q2: whole process, 附录3, 表3/表4 + result2.xlsx) and the method matches it: 1-D radial, appendix-3 correlations, 3 h output on the mandated grid. The only framing choice the team owned — which energy-equation form to solve — is the one they examined most thoroughly, and the counterfactual was actually implemented and run. |

Block condition: modes 3, 5 and 6 are `SUSPECTED` and mode 2 is `INSUFFICIENT_EVIDENCE`
→ **the artefact is blocked from being presented as established.**

---

## 3. Numbers reconciliation

Registry coverage: `q2_reconcile.py` was re-run in full. It scans **2 057** numeric
literals across the two documents: **585** match a registry, **1 460** are allow-listed,
**12** are unmatched — and the script exits 0 anyway (only the second gate raises). All 12
unmatched literals were verified by hand and are real; none is registered:

| Token | Where | Independent check | Status |
|---|---|---|---|
| 3.6202 / 4.8931 | §7.2(a) ratios | 6.7285e−5/1.8586e−5 = 3.6202; 3.2310e-3/6.6033e-4 = 4.8930 | MATCH, NO_REGISTRY |
| 1.9951 | §7.2(b) ratio | 1.2093e−4/6.0613e−5 = 1.99511 | MATCH, NO_REGISTRY |
| 9.667e-2 | §7.1(b) | `V12_jac_frozen` = 0.096665396 | MATCH, NO_REGISTRY |
| 14.7961 | §2.1 / §7.6(a) | 64.5646 − 49.7685 (V11 re-run) | MATCH, NO_REGISTRY |
| 4.2e-8 | §4.1/§7.8 | 0.101602/2434560.5 = 4.17e−8 | MATCH, NO_REGISTRY |
| 1.3715 | §7.7 | 33.4771 − 32.1056 = 1.3715 | MATCH, NO_REGISTRY |
| 2.53286 | §7.2(d) | M=3200 re-run, k=7 inward = 2.5328633 | MATCH, NO_REGISTRY |
| 0.1523 | §8.3(b) | 10800/70900.86 = 0.152325 | MATCH, NO_REGISTRY |

Shipped values that do **not** reconcile against their stated source:

| Value | Claimed as | Reconciliation | Detail |
|---|---|---|---|
| 656.0475 W/m³, ratio 0.25202 | §2.1 S_false | **MISMATCH** | 4186×7×275.0423×8.3185e−5 = 670.41 W/m³; ratio 670.41/2603.1272 = **0.25754**. The registry value requires T−T_ref = **6.8500 K**, which appears only as `Tmean − TrefK = 308.0 − 301.15` in `q2_energy_algebra.py`; the text says "~7 K". |
| 2603.1272 W/m³ | §2.1 主项 ρc_p∂_tT | **ROUNDED/soft** | = ρc_p(C=1.5) × an assumed 1e−3 K/s. ρc_p(C₀) = 3.3347e6 is 28 % larger; an average dT/dt over 0–1800 s is ≈1.15e−2 K/s. Registry labels it "量级估计" — the text presents it as "主项". |
| 13.8360, 0.28154 % | §5.5 boundary diagonal @ "生产设置 M=1600, Δt=1/32" | **MISMATCH with the production setting** | 13.8360 is exactly M=1600, Δt=1/32. At the actual production Δt = 1/64 the diagonal is 27.1720 and the ratio 0.14336 %. §6 additionally claims M=800, Δt=1/32 (diagonal 27.1664). |
| 1.75 cm / 12 % | §9.3 附件2 shrinkage | **NO_SOURCE / MISMATCH** | 附件2: R(10800 s) = 1.5520 cm ⇒ 22.40 %. R = 1.75 cm occurs at t ≈ 4 200 s. |
| 72 / 632 / 800 / 2417 / 0 | §7.4 decrease counts | **CONDITIONAL** | Reproduce only with the undocumented threshold ΔT < −1e−4 K (`q2_derive.py` line 254). At ΔT < 0: 134 / 710 / 888 / 2935 / **10**. |
| 109.2122 J/kg | §4.1 calibration residual | **MATCH but mislabelled in the registry** | Value is right for 28–50 °C (recomputed 109.2122). `registry_q2_latent_heat_rows.csv` labels row `LH_resid28` as the **20–50 °C** residual, whose true value is 169.30 J/kg. |

All other headline numbers reconciled: 27.9905 / 49.8888 / 50.2460 (§7.4), 0.108180 (§7.6b),
5.2156e4 / 2.8624e−8 (§7.5), 17.2745 / 14.7961 (§7.6a), 7.0274e−6 (§7.6c), 1.0072e−5 (§7.6d),
3.000 iterations (§7.6e), 1.391422 / 1.3715 (§7.7), the whole of table §7.8, and both
uncertainty percentages. Counts add up: V12 reports 101 registry rows; the production
registry has 123 rows; `result2.xlsx` is 10800×21 with no NaN and contiguous times.

---

## 4. Blocking items

1. **§9.3 shrinkage figure is wrong — 12 % should be 22.4 %.** 附件2 row t = 10800 s gives
   R = 1.5520 cm (verified by reading `A题/附件/附件2.xlsx` directly). The document quotes
   1.75 cm / 12 %, which is the state at t ≈ 4 200 s. This is the model's largest disclosed
   geometric assumption and it is understated by ~1.9×.
   *To clear:* replace with "3 h 内半径由 2.000 降至 1.552 cm（收缩 22.4 %，附件2）" and
   restate the known bias accordingly, or state the time at which 1.75 cm occurs.

2. **The document states three different production configurations.** §6: M = 800,
   Δt = 1/32. §7.3/§8.1: M = 1600, Δt = 1/64 (this is what the code ran, and what
   produced `result2.xlsx`). §5.5: M = 1600, Δt = 1/32.
   *To clear:* set §6's table to M = 1600, Δt = 1/64 (691 200 steps) and either recompute
   §5.5 at Δt = 1/64 (diagonal 27.1720, ratio 0.14336 %) or label the passage explicitly as
   an illustrative Δt.

3. **"精确相消" is not exact for 附录3's functions.** The expansion
   `∂[ρc_p(T−T_ref)]/∂t = ρ_s(c_s+c_lC)∂_tT + c_l(T−T_ref)ρ_s∂_tC` requires
   `d(ρc_p)/dC = c_lρ_s`. Sympy: `d(ρc_p)/dC − c_lρ_s = 1044(2093C+725)/(C+1)² ≠ 0`
   (C = 2.55: 649 134 vs 1 151 327). The identity holds only for constant ρ_s, and
   `ρ = 650+128C = ρ_s(1+C)` would require ρ_s = 650 and ρ_s = 128 simultaneously. The
   document's own §2.3 reports the refuting fact (`EB_rhos_drift = +111.57 %`) without
   connecting it. The **conclusion stands** — with a constant dry-bulk density ρ_d the
   cancellation is exact and gives the same equation — but the printed requirement is not
   met, and because the cancellation fails the resulting equation depends on the arbitrary
   T_ref (an unclosed-derivation tell).
   *To clear:* present the derivation with `ρ_d := ρc_p/(c_s+c_lC)` as the dry bulk density,
   state that 附录3 makes ρ_d C-dependent (so the mixture reading is exact only in the ρc_p
   combination), and delete or qualify "精确相消".

4. **The S_false magnitude describes a different variant than the one compared.** The
   implemented "conservative" form uses absolute T —
   `RT = (MT·T − MLg·ρ_o·c_p,o·T_old)/Δt + KT` (`q2_solve.py` line 206) with T in K from
   0 K, not from 28 °C. For that variant the omitted term is `c_l·T·ρ_s·∂_tC ≈ 2.95e4 W/m³`
   at T ≈ 308 K — 45× the quoted 656.05 W/m³ and ≈11× the quoted main term. So the number
   used to corroborate the 17.27 K gap is not the term that produces it.
   *To clear:* either state the 656 W/m³ figure as belonging to a `(T − 28 °C)`-referred
   variant (and note the implemented one is 0 K-referred), or change the code's conservative
   variant to use `(T − T_0)` and re-run V11. In both cases reconcile "~7 K" with the
   implicit 6.85 K.

5. **The moisture uncertainty claim is convention-dependent.** §7.3 converts two
   *increments between successive refinements* into "error of the shipped solution" by
   taking the larger. For a 1st-order time and 2nd-order space scheme the production errors
   are ≈2× the time increment and ≈4/3× the space increment: **T = 2.76e−5 K (55 % of the
   threshold), C = 5.13e−5 kg/kg (103 % — above the threshold)**. Sum convention:
   C = 6.83e−5 (137 %). RSS: C = 4.87e−5 (97 %). Only the max convention supports
   "水分 76.93 % < 100 %".
   *To clear:* report the refined estimate alongside the increment and state plainly that
   the moisture field's 4th decimal is not guaranteed at M = 1600 — which the document
   already implies by recommending M = 3200. Fixing this needs no new run.

---

## 5. Non-blocking defects

1. §7.4's per-radius decrease counts are produced with an undocumented filter
   (`Δt < −1e−4 K`, `q2_derive.py` line 254). Without it the inner total is 10, not 0.
   Disclose the threshold or report "≤10 of 10 799 samples at r ≤ 1.0 cm, all with
   |ΔT| < 1e−4 K".
2. `q2_reconcile.py`'s first gate leaves 12 unmatched literals and exits 0. Gate 2 has
   teeth (`raise SystemExit(2)`); gate 1 does not.
3. `registry_q2_latent_heat_rows.csv` row `LH_resid28` mislabels 109.2122 J/kg as the
   20–50 °C residual (true: 169.30 J/kg). The document's 28–50 °C wording is right.
4. §4.1(iv) says "最小二乘" but only the slope is fitted; the intercept is pinned at the
   IAPWS h_fg(28 °C). A genuine 2-parameter least-squares fit of 28–50 °C gives
   a = 2 501 577.8 J/kg with max residual 80.2 J/kg, so the reported 109.2 J/kg is 36 %
   larger than the least-squares residual. Say "斜率由最小二乘给出，截距锚定于 28 °C".
5. §4.1(ii) "CC 的偏差**全部**来源于气相非理想性": the 0.008452 pp residual it cites
   equals (v_f/v_g)×100 to within 0.4 % (0.008416 pp at 50 °C; 0.001735 vs 0.001741 pp at
   20 °C), i.e. it *is* the neglected liquid specific volume — 2.1 % of the 0.40141 pp
   deviation. Reword to "97.9 % 来自气相非理想性，其余 2.1 % 恰为被略去的 v_f/v_g 项".
6. §4.1(ii) presents "精确 Clapeyron 复现 IAPWS-95 的 h_fg 到 0.1016 J/kg —— 式 (5) 的推导正确".
   Clapeyron is a thermodynamic identity satisfied exactly by any consistent EOS, and the
   residual is insensitive to the difference step (0.1016 J/kg at h = 1e−2 K, 0.0588 at
   h = 1e−4 K) — so this verifies the library and the differencing, not the model. Relabel
   as a consistency check.
7. §7.2(a) reads the max-norm ratios 3.6202 / 4.8931 as "趋近 4，即空间二阶收敛". The
   temperature ratio 3.62 is the signature of the r=0 lumped-mass defect (the document
   measures ~3.4–3.5 for that scheme in §7.6(c)); the moisture ratio exceeds 4. The
   2nd-order claim is adequately supported by two independent lines (Bessel 4.31/4.05;
   moisture surface ΔC 4.93→4.20→4.04), but the wording should attribute the 3.62.
8. §7.2(d)'s ">10 个网格" is right but the cited evidence does not establish it: the
   profile is still rising at k = 7, at k = 20 (2.54552) and only returns to within 1e−5
   of 2.55 at k ≈ 58. The correct support is `sqrt(Dt)/Δr = 0.007511/0.000625 = 12.02`
   cells (which the registry already has as `MD_delta_ratio = 12.0178`).
   Also "第 8 个节点" in §7.2(d) means the registry's k = 7 (2.5328633); the registry's
   k = 8 is 2.5343283. Same phrase, two different nodes.
9. `q2_moist_diag.py`'s docstring states `sqrt(Dt) = 0.00375 cm` at t = 1 s; it is
   0.0075 cm (factor 2). The value printed at run time is correct.
10. §4.2's `h(T∞−T_R)` column: 337.5 vs 25×(41.5130−28) = 337.83; the t = 3600 row's 487.5
    implies T_R = 28 °C. Fine for an order-of-magnitude table, but the assumed T_R should
    be stated.
11. §7.7's k relative difference: 0.48296/0.36 − 1 = 34.16 %, printed as 34.15 %.
12. IAPWS-95 is cited without an identifier — add IAPWS R6-95(2018) and note iapws 1.5.5.
    `problem2.md` line 208's "番石榴模型" claim carries no citation.
13. The pure-water h_fg is applied to a hygroscopic herbal material; a desorption enthalpy
    exceeds h_fg. Numerically immaterial (the document's own ±20 % H_evap sensitivity is
    0.0216 K), but it should be named as assumption B9's limitation rather than presented
    as thermodynamically closed.
14. §7.5's "热量收支有缺口是正确的" is a post-hoc reading: Σ M_i T_i with absolute T is not
    the physical enthalpy. The numbers (5.2156e4, 2.8624e−8) are real; the interpretation
    should be tied to the corrected derivation in blocking item 3.

---

## 6. What I could not check

- **The full 3-h production run at M = 1600, Δt = 1/64** (691 200 steps, ~30 min per the
  brief). I re-ran the same configuration for **t ≤ 1800 s** (115 200 steps, 274 s) and
  reproduced rows 1…1800 of the shipped file exactly at 4 dp — so the *solver* is
  confirmed against the shipped grid, not merely the doc against the grid. Rows
  1801…10800 were not independently re-solved; their values are registry- and
  log-sourced, cross-checked for internal closure (water inventory from the published
  grid gives 45.79 % loss vs the documented 45.7545 % at M=1600 vs the 0.1 cm grid,
  consistent within the two grids' discretisation).
- **V0–V9 and V11 as a batch.** The log reports 12 cases in 373 s across 6 processes. I
  re-ran V12/V13 directly and reconstructed V4 (both arms) and V11 from the source equations
  at the stated configurations; I did not re-run V0, V5–V9 as a batch. V8/V9's numbers are
  registry- and log-sourced.
- **杨历 2005** — no local copy; the web-search endpoint returned HTTP 402 (insufficient
  balance for the search provider), so the identifier and the proposition it is attached to
  remain unresolved. The IAPWS-95 standard text itself was likewise not retrieved; I checked
  the installed implementation only.
- **The contest's intent regarding shrinkage in Q2.** 附件2 is described globally in 附录1
  while Q4 names it explicitly; whether Q2 is expected to use it is a scope judgement I
  cannot settle from the problem statement. This affects how blocking item 1 should be
  framed, not whether the 12 % figure is wrong.
- **Time-series plots** (`paper/figures/fig_q2_*`) were not audited — they are outside the
  three deliverables named in the brief, and their `.svg` companions are 43 MB each.
