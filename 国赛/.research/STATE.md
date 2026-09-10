# Research State — 2026 国赛 A 题 · 药材烘干

Last updated: 2026-09-10

## Objective

Audit the user-supplied "问题一完整建模思路" (model + discretization + boundary
conditions + numerical scheme) against the authoritative problem statement
(`A题/A题.pdf`, converted to `docs/A题.md`), against the actual attachment data,
and against a numerically verified run. Fix every defect found. Write the
corrected model and solution narrative to
`model/problem1.md` and `model/problem_slove1.md`.

## Question (scoped for this session)

Q1: Is the proposed cylindrical 1-D radial heat + moisture diffusion model for
**问题1 (预热平衡阶段, 0–1800 s)** mathematically correct, physically
consistent with the given parameters, and numerically sound enough to produce
result1.xlsx at the required precision (4 decimals)?

## Authoritative sources retrieved

| id | source | what it fixes |
|----|--------|---------------|
| S1 | `A题/A题.pdf` → `docs/A题.md` (markitdown) | problem statement, tables 1–2, appendices 1–4 |
| S2 | `A题/附件/附件1.xlsx` (Sheet1, A1:C242) | T∞(t) 28.000→50.165 °C, C∞(t) 0.01963→0.04986 kg/kg, t=0..14400 s, Δt=60 s |
| S3 | `A题/附件/附件2.xlsx` (Sheet1, A1:B146) | R(t) 2.000→1.198 cm, t=0..259200 s, Δt=1800 s |
| S4 | `A题/附件/附件3/result1.xlsx` | template: sheets 温度 / 水分浓度; A1 = "时间\到药材中心的距离"; row 1 = 0,0.1,...,2 cm; A col starts t=1 s |

## Claims ledger

| # | claim | status | source / command |
|---|-------|--------|------------------|
| C1 | D(C)=7e-9·exp(-0.89/C); at C=2.55 → 4.92e-9 m²/s; at C=0.0331 → 1.4e-21 m²/s | verified by computation | `src/q1_solve.py --selftest` |
| C2 | α = k/(ρc_p) = 0.36/(820·2600) = 1.6883e-7 m²/s | to verify | run |
| C3 | Interior finite-volume coefficients a_i,b_i,c_i as given by user are correct | to verify | symbolic re-derivation + run |
| C4 | User's surface node (i=M) coefficient b_M is WRONG (factor 2 on the h term); correct FV value is b_M = 1/Δt + (4α/Δr²)(1+hΔr/k) | to verify | run |
| C5 | C∞ from 附件1 is used as the surface moisture boundary value; needs a physical-consistency check vs 0.15 kg/kg target of Q3 | open | run |
| C6 | h_m = 8e-7 m/s is 4 orders below the convective value implied by the heat-transfer analogy | open (flagged, not "fixed") | run + estimate |
| C7 | Truncating at L/R=12.5 to 1-D radial is defensible for 30 min with the given α | to verify | analytic Biot/Fourier estimate |
| C8 | D(C) formula is also needed implicitly for Q2/Q3 (附录3), where D has an Arrhenius T-dependence → temperature and moisture couple in Q2/Q3 but not in Q1 | verified from S1 | read S1 |

## Artefacts

| path | what |
|------|------|
| `docs/A题.md` | markitdown conversion of the problem statement (derived; cite pages of the PDF, not this file) |
| `.research/STATE.md` | this file |
| `src/q1_solve.py` | problem-1 solver: heat + nonlinear moisture, explicit user scheme vs corrected FV scheme, convergence study |
| `model/problem1.md` | model document (deliverable) |
| `model/problem_slove1.md` | solution/numerics document (deliverable) |

## Ruled out / not to be repeated

- (nothing yet)

## Next action

Run `src/q1_solve.py` self-test + convergence study; then write the two model
documents with only registry-backed numbers.
