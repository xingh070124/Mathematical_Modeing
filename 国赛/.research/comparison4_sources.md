# Comparison 4 input — 胡众欢等 (2020) 多物理场耦合热风干燥模型
# Source: docs/txt/基于多物理场耦合的热风干燥模型及其验证_胡众欢.txt
# Full extraction (627 lines, source-line tagged): .research/hu_zhonghuan_model.md

## Bibliographic (retrieved; DOI unverified)
胡众欢, 杨明金, 杨卓然, 杨玲. 基于多物理场耦合的热风干燥模型及其验证.
西南大学学报(自然科学版), 2020, 42(2): 118-128.
DOI 10.13718/j.cnki.xdzk.2020.02.015  <- CrossRef returns HTTP 404. UNVERIFIED DOI.

## What the model is
3-D drying-chamber multiphysics PDE system, 22 equations (1)-(22), COMSOL.
- external hot-air flow: continuity (1) + momentum (2)
- porous-medium internal flow: volume-averaged continuity (3) + momentum (4)/(6) + Darcy term (5)
- air property closure: ideal-gas density (7), Sutherland viscosity (8)
- energy: external (9), internal with effective properties (10), mixing laws (11)(12), saturation closure (13)
- gas-phase transfer: external (14), internal (15) + evaporation source (16)
- total velocity composition (17)-(20)
- liquid-phase transfer (21) + Darcy velocity (22)
Material: rapeseed (油菜籽) bed in a 0.4 m cube chamber. Geometry/material DIFFERENT
from the exam problem (cylinder, L=25 cm, R=2 cm).

## Coupling mechanism (authors' own account)
1. density rho_a = f(T) via (7), fed into (1)(2)(3)(6)
2. viscosity mu = f(T) via (8)
3. velocity -> energy: u_a from flow solution into (9)(10)
4. velocity -> mass: u_a into (14)(15)(20)
5. pressure -> Darcy velocity (22)
6. phase change: evaporation R is +R in (15), -R in (21), and gamma*I in energy (10)
   (paper writes +gamma I while its own text says evaporation ABSORBS heat -> sign error I1)
7. external<->internal linked via Darcy + Fick

## CRITICAL: reproducibility gaps (evidence for comparison 4)
G1  NO initial conditions and NO boundary conditions anywhere in the paper
    (no wall/inlet/outlet/symmetry/interface/initial T).
G4  permeability k has no value (needed by eqs 5,6,22)
G5  water activity a_w and saturated vapour concentration c_v,sat have neither values
    nor functional forms -> eq (16) cannot be evaluated; no sorption isotherm
G6  internal heat source q has no value
G7  I (eq 10) and R (eq 16) have no stated conversion, and differ in units
G9  numerical method entirely absent: no mesh, no time step, no discretization, no
    solver, no tolerance, no turbulence model, no CPU time, no grid independence
G2  no equation converting c_l/c_v to dry-basis moisture content -- yet dry-basis
    moisture is the validated quantity
G10 validation = exactly two numbers: max relative error 13.3%, absolute error 0.016
    (at the 2nd measurement point). No RMSE/R2/MAE, no data table, no time axis.
G13 no grid/timestep independence study -> 13.3% cannot be separated into model vs
    discretization error
G14 no shrinkage (authors mention Kumar et al. do shrinkage; own model has no such term)
G16 D is a CONSTANT in Table 1 (no T or C dependence) -> internal heat/mass coupling
    is one-way via the evaporation source only

## The authors' own downgrade of the coupling
"The strong coupling relation between the flow field and other fields is transformed
into a weak coupling relation, sacrificing a certain amount of calculation accuracy,
but this method avoids the transient calculation of the flow field, greatly saving
computational cost..." (lines 505-508). This claim is NOT quantified in the paper.

## Self-consistent initial-value triple (independently verified by our extraction)
eps = 0.3769, S_l = 0.3265, c_l = 6823.5 mol/m3
  reproduce dry-basis X = 0.179216, matching the paper's stated experimental
  17.92 % d.b. to 5 significant figures.
This is the most directly reusable result in the paper.

## Internal inconsistencies found (paper's own, not conversion artefacts)
I1  eq (10) prints +gamma I although the text says evaporation absorbs heat
I2  Table 1 air density 1.205 kg/m3 is a 20 C value, not the 55 C operating value
    (eq (7) gives 1.0763 kg/m3 at 328.15 K)
I3  Table 1 air viscosity 1.81e-5 is a 20 C value; eq (8) gives 1.9763e-5 at 328.15 K
    (9.2% discrepancy); the minus sign is also missing in the printed table
I4  geometry/mass check: 0.18x0.18 m tray x 0.011 m x 685.41 kg/m3 = 244.3 g
    vs the stated 200 g sample (18% discrepancy)
I5  eq (20) composition of (17)+(18)+(19) should give - (M/rho) D grad c_a, not + c_v
I7  symbol mu used for both air viscosity and liquid water viscosity
