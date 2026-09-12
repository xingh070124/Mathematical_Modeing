# Deliverable: text-extractable source for the Brasiello/Venditti/Adrover (2021) CET equations

**Task**: recover the governing equations of Brasiello A., Venditti C., Adrover A. (2021),
"Non-Isothermal Moving-Boundary Model for Food Drying", *Chemical Engineering Transactions*
**87**, 193–198, DOI [10.3303/CET2187033](https://doi.org/10.3303/CET2187033), whose distributed
PDF has flattened display equations.

**Verdict**: No copy of the CET paper with text-bearing equations exists in any index reachable
from here. The **direct source the CET paper cites** was retrieved with **native MathML** and is
the recommended provenance for the equations:

> Adrover A., Venditti C., Brasiello A. (2020). *A Non-Isothermal Moving-Boundary Model for
> Continuous and Intermittent Drying of Pears*. **Foods 9(11), 1577**.
> DOI [10.3390/foods9111577](https://doi.org/10.3390/foods9111577) ·
> PMC7692062 · PMID 33143274 · CC BY.
> Retrieved as JATS-XML-with-MathML from
> `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7692062/fullTextXML`
> (331,189 bytes, HTTP 200), local copy `.research/refs/foods9111577_europepmc.xml`.

MathML is text, so every formula below is a **mechanical transcription** of the publisher's
markup (converter: `.research/refs/extract_mathml.py`; output:
`.research/refs/foods9111577_equations.txt`), **independently cross-checked against the publisher
PDF** (`https://europepmc.org/articles/PMC7692062?pdf=render`, 1,153,307 bytes, 22 pp.).

---

## A. Sources and whether equations were text-extractable

| # | Source | Outcome |
|---|---|---|
| 1 | `https://www.cetjournal.it/index.php/cet/article/view/CET2187033` | HTTP 200. Landing page only — abstract + PDF hyperlink. **No equations in HTML.** |
| 2 | `https://www.aidic.it/cet/21/87/033.pdf` | HTTP **406** (IIS `StaticFileModule` rejects the request's Accept header). Not a paywall. |
| 3 | `https://www.cetjournal.it/cet/21/87/033.pdf` | HTTP 200, 677,569 B. **Downloaded.** Equations (1)–(7), (10), (11) absent from the text layer (only the labels `(1)`…`(7)` are real text); page 2 has 158 vector drawings, page 3 has 373. Equations (8), (9), (12) *do* survive as font-mangled text. **Confirms the brief's diagnosis; not usable for (1)–(7).** |
| 4 | `https://www.mdpi.com/2304-8158/9/11/1577` | HTTP **403** (Akamai "Access Denied"). |
| 5 | `https://www.mdpi.com/2304-8158/9/11/1577/xml` | HTTP **403**. |
| 6 | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7692062/fullTextXML` | **HTTP 200 — WORKED.** 52 display formulas as native MathML. ← the source used below |
| 7 | `https://europepmc.org/articles/PMC7692062?pdf=render` | HTTP 200, publisher PDF — used only to **cross-check** the MathML. |
| 8 | `https://content.openalex.org/works/W4404888944.grobid-xml` | HTTP 200 but body is `{"error":"API key required"}`. Unusable. |
| 9 | `https://api.openalex.org/works/doi:10.3303/CET2187033` | HTTP 200, metadata only (also shows CET is gold OA, and lists an IRIS Sapienza copy with `pdf_url: null`). |
| 10 | `https://iris.uniroma1.it/handle/11573/1571237` | HTTP **403** (Cloudflare). `hdl.handle.net` route refused by the fetch tool (cross-origin redirect). |
| 11 | `https://api.unpaywall.org/v2/10.1016/j.jfoodeng.2018.09.018` (Adrover *et al.* 2019, *J. Food Eng.* "General setting") | HTTP 200, `is_oa: false`, `oa_locations: []`. **Closed — no legal text copy.** |
| 12 | `https://api.unpaywall.org/v2/10.1111/jfpe.13178` (1-D vs 2-D approaches) | HTTP 200, `is_oa: false`. Closed. |
| 13 | `https://downloads.hindawi.com/journals/ijce/2019/3926897.pdf` (+ 3 Wiley mirrors) | All HTTP **403** (Cloudflare). Chayote 1-D paper is gold OA but unreachable from here. |
| 14 | `https://api.semanticscholar.org/graph/v1/paper/DOI:10.3303/CET2187033` | HTTP **404** — the CET paper is not in Semantic Scholar. |
| 15 | `https://api.semanticscholar.org/graph/v1/paper/DOI:10.1155/2019/3926897` | HTTP 200 — confirms gold OA, but the PDF host is the Cloudflare-blocked one. |
| 16 | `https://api.core.ac.uk/v3/search/works?...` | HTTP **500** (API key required). |
| 17 | `https://api.fatcat.wiki/...`, `https://scholar.archive.org/...` | Transport failure (host unreachable). |
| 18 | `https://europepmc.org/api/fulltextRepo?...` | HTTP **403**. |
| 19 | `web_search` tool | **Unavailable** — DeepSeek API returned HTTP 402 (insufficient balance). No general web search was possible; all retrieval above is direct HTTP/API. |

**Conclusion for A:** the equations below were genuinely **text-extractable** (MathML), not inferred.
The only inference is the coordinate reduction noted in D.

---

## B. Governing equations — verbatim (Foods 2020, PMC7692062)

Notation as defined in that paper: `c_w(x,t)` water concentration [kg/m³], `φ = c_w/ρ_w` water
volume fraction, `J_d = −D_eff ∇c_w` diffusive mass flux, `v_s` pointwise shrinkage velocity,
`x_b ∈ S(t)` a point of the sample boundary, `n` outward normal, `α(c_w)` shrinkage
proportionality factor, `ρ^p`,`C_p^p`,`k^p` product density / specific heat / thermal conductivity,
`h_m`,`h_T` mass and heat transfer coefficients, `M_w` water molecular weight, `R_g` gas constant,
`p_v(T)` saturated vapour pressure, `RH` relative humidity, `T_av=(T_b+T_∞)/2`.

### B1. Mass / water transport PDE

**Coordinate-free (general) form — Eq. (8):**
```latex
\frac{\partial c_w(\mathbf{x},t)}{\partial t}
=\nabla\cdot\left(D_{eff}(T)\,\nabla c_w-\mathbf{v}_s(\mathbf{x})\,c_w\right)
,\qquad \mathbf{x}\in V(t)
```
Isothermal counterpart, written via the diffusive flux, **Eq. (1)** (verbatim, including the
paper's doubled `=`):
```latex
\frac{\partial c_w(\mathbf{x},t)}{\partial t}
-\nabla\cdot\left(\mathbf{J}_d+\mathbf{v}_s(\mathbf{x})\,c_w\right)
=\nabla\cdot\left(D_{eff}\,\nabla c_w-\mathbf{v}_s(\mathbf{x})\,c_w\right)
,\qquad \mathbf{x}\in V(t)
\qquad\text{where } \mathbf{J}_d=-D_{eff}\nabla c_w
```
Coordinate system (stated in §3 and §4.3): `x ∈ V(t)` is the *shrinking* sample domain with
boundary `S(t)`; the paper's own numerical realisation is **spherical**, `r ∈ (0, R(t))`:
```latex
\frac{\partial \phi(r,t)}{\partial t}
=\frac{1}{r^{2}}\frac{\partial}{\partial r}
\left(r^{2}\left(D_{eff}(T)\frac{\partial \phi}{\partial r}-v_s(r)\,\phi\right)\right)
,\qquad r\in(0,R(t)) \tag{25}
```

### B2. Energy / heat transport PDE

**General — Eq. (9):**
```latex
\frac{\partial\left(\rho^{p}C_p^{p}\,T(\mathbf{x},t)\right)}{\partial t}
=\nabla\cdot\left(k^{p}\nabla T-\mathbf{v}_s(\mathbf{x})\,\rho^{p}C_p^{p}\,T\right)
```
**Spherical — Eq. (26), exactly as printed:**
```latex
\frac{\partial\left(\rho^{p}C_p^{p}\,T(r,t)\right)}{\partial t}
=\frac{1}{r^{2}}\frac{\partial}{\partial r}
\left(r^{2}\left(k^{p}\frac{\partial \phi}{\partial r}-v_s(r)\,\rho^{p}C_p^{p}\,T\right)\right)
,\qquad r\in(0,R(t)) \tag{26}
```
> ⚠ **Eq. (26) is defective as published.** The conduction term reads
> `k^{p}\,\partial\phi/\partial r`, but the conduction flux must be `k^{p}\,\partial T/\partial r`
> (compare Eq. (9), which correctly has `k^{p}\nabla T`). I confirmed the defect appears in **both**
> the publisher PDF and the Europe PMC XML — it is a typo in the paper, not an extraction artefact.
> Do not copy it into a model.

The paper itself states the coupling (verbatim, §3.2): *"The heat transport equation Equation (9)
is coupled to the mass transport equation Equation (8) not only through the boundary condition
Equation (13) but also through the shrinkage-convective term (v_s(x) ρ^p C_p^p T)."*

### B3. Point-wise shrinkage velocity `v_s` and the factor `α`

**General — Eq. (10)** (isothermal counterpart Eq. (2) is the same with `D_eff` not `T`-dependent):
```latex
\mathbf{v}_s(\mathbf{x})=\alpha(c_w)\,D_{eff}(T)\,\nabla c_w/\rho_w
```
```latex
\text{Eq. (2):}\quad \mathbf{v}_s(\mathbf{x})
=-\alpha(c_w)\,\mathbf{J}_d(\mathbf{x})/\rho_w
=\alpha(c_w)\,D_{eff}\,\nabla c_w/\rho_w
```
**Spherical, with ideal shrinkage `α=α₀=1` — Eq. (27):**
```latex
v_s(r)=D_{eff}(T)\frac{\partial \phi}{\partial r}
```
Values: `α₀=0` ⇒ rigid solid (no shrinkage); `α₀=1` ⇒ *ideal* shrinkage
(volume reduction = volume of water leaving). §4.1 (verbatim): *"It must be pointed out that the
assumption α(c_w) = α₀ does not imply that the shrinkage velocity v_s(x) is constant, nor in time
or space, but rather that, according to Equation (2), the shrinkage velocity is directly
proportional to the local concentration gradient."*

### B4. Sample-surface evolution `dx_b/dt`

**General — Eq. (11):**
```latex
\frac{d\mathbf{x}_b}{dt}=\mathbf{v}_s\big|_{\mathbf{x}_b}
=\frac{\alpha(c_w)}{\rho_w}D_{eff}(T_b)\,\nabla c_w\big|_{\mathbf{x}_b}
,\qquad \mathbf{x}_b\in S(t)
```
**Spherical — Eq. (27):**
```latex
\frac{dR(t)}{dt}=v_s(R(t))=D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}
```

### B5. Symmetry boundary condition at the centre

The coordinate-free section prints **no** symmetry condition; it appears in the spherical reduction:

**Eq. (28a) (mass):**
```latex
\frac{\partial \phi}{\partial r}\Big|_{r=0}=0
```
**Eq. (29a) (heat):**
```latex
\frac{\partial T}{\partial r}\Big|_{r=0}=0
```

### B6. Mixed / Robin / "evaporative" boundary condition at the moving surface — and the boundary-velocity question

**Mass, general — Eq. (12):**
```latex
-D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}
=h_m(T_{av})\,M_w
\left(\frac{p_v(T_b)}{R_gT_b}RH_b-\frac{p_v(T_\infty)}{R_gT_\infty}RH_\infty\right)
```
**Mass, spherical — Eq. (28b):**
```latex
-D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}
=h_m(T_{av})\frac{M_w}{\rho_w}
\left(\frac{p_v(T_b)}{R_gT_b}RH_b-\frac{p_v(T_\infty)}{R_gT_\infty}RH_\infty\right)
```
**Heat, general — Eq. (13):**
```latex
-k^{p}\,\nabla T\cdot\mathbf{n}\big|_{\mathbf{x}_b}
=h_T(T_{av})\left(T_b-T_\infty\right)
-\lambda_v(T_b)\,D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}
```
**Heat, spherical — Eq. (29b):**
```latex
-k^{p}\frac{\partial T}{\partial r}\Big|_{R(t)}
=h_T(T_{av})\left(T_b-T_\infty\right)
-\lambda_v(T_b)\,\rho_w\,D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}
```
with, from §4.3 (verbatim), `RH_b = RH|_{R(t)} = RH(φ_b, T_b)` evaluated from desorption isotherms,
and `T_b = T(R(t),t)`.

#### **ANSWER to the boundary-velocity question: NO velocity term appears in it.**

**No term proportional to `dx_b/dt` or to `v_s` at the surface appears in any of Eqs. (12), (13),
(28) or (29).** There is no `ρ^p C_p^p (\mathbf{v}_s\cdot\mathbf{n})T` contribution and no
Leibniz-rule term. The boundary conditions are pure flux balances written directly in the moving
frame. Two places absorb the domain motion instead:

1. **In the PDEs**, through the convective term `−∇·(v_s c_w)` (mass) and
   `−∇·(v_s ρ^p C_p^p T)` (heat), Eqs. (8)–(10).
2. **In the numerics** — §3.3 (verbatim): *"PDE equations and boundary conditions describing the
   one-dimensional shrinkage dynamics and sample dehydration have been numerically solved using
   finite elements method (FEM) in Comsol Multiphysics 3.5. The convection–diffusion package
   coupled with ALE (Arbitrary Lagrangian Eulerian) moving mesh has been adopted with Free
   Displacement induced by boundary velocity conditions."*
   The ALE moving mesh is precisely why no explicit surface-velocity term is needed in the
   flux condition.

**The one place a Leibniz / moving-domain term DOES appear** is the lumped (spatially-averaged)
energy balance, **not** the Robin condition:

**Eq. (14) (general):**
```latex
\frac{d}{dt}\left(T_b\int_{V(t)}\left(\rho^{p}C_p^{p}\right)d\mathbf{x}\right)
=\int_{S(t)}\left(-h_T(T_{av})\left(T_b-T_\infty\right)
+\lambda_v(T_b)\,D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}\right)dS
```
**Eq. (31) (spherical):**
```latex
\frac{d}{dt}\left(T_b\int_{0}^{R(t)}\left(\rho^{p}C_p^{p}\right)4\pi r^{2}dr\right)
=\left(-h_T(T_{av})\left(T_b-T_\infty\right)
+\lambda_v(T_b)\,\rho_w\,D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}\right)4\pi R^{2}(t)
```
Here the left-hand side is `d/dt` of an integral over the moving volume `V(t) = (0,R(t))` — that is
the domain-motion contribution. **My own check (inference, not a quotation):** Eqs. (29) and (31)
are mutually consistent. From (29),
`−k^p ∂T/∂r|_R = h_T(T_b−T_∞) − λ_v ρ_w D_eff ∂φ/∂r|_R`; applying the divergence theorem to (26)
gives `d/dt(T_b∫ρC_p dV) = 4πR² k^p ∂T/∂r|_R`, which rearranges exactly to (31).

### B7. Effective water diffusivity `D_eff` — shrinkage correction?

**Concentration-dependent form — Eq. (3):**
```latex
D_{eff}(\phi,T)=D_{\phi_0}(T)\exp\left(-\beta\,\frac{\phi_0-\phi}{\phi_0-\phi_\infty}\right)
,\qquad \beta\ge 0,\qquad \phi=c_w/\rho_w
```
**Arrhenius form actually used — Eq. (24):**
```latex
D_{eff}(T)=D_0\,e^{-\frac{E}{R_gT}}
,\qquad D_0=4.00012\times10^{-5}\ \mathrm{m^2/s}
,\qquad E/R_g=-3872.63\ \mathrm{K}
```

**Answer: `D_eff` is NOT corrected for shrinkage by any factor in the transport equation.**

- The paper sets **β = 0**, so `D_eff(φ,T) = D_{φ0}(T)` — a function of **temperature alone**.
  §3.2, verbatim: *"In the present formulation it has been assumed that the effective water
  diffusivity is solely a function of the temperature and independent of the local water
  concentration, i.e., β = 0."* §4.3 adds: *"Indeed, there is no need to introduce a
  concentration-dependent diffusion coefficient, Equation (3), that would require the estimate of
  the β parameter. For this reason, we set β = 0 also for all the subsequent simulations of
  intermittent dehydration."* Abstract: *"an effective water diffusivity D_eff(T) that depends
  exclusively on the local temperature."*
- Shrinkage enters the **flux**, not `D_eff`: via the advection term `v_s c_w` and the moving
  boundary. (This is exactly the point the brief's paper makes about `D_eff`.)
- **The only shrinkage-geometry factor in the paper is not a correction to `D_eff` but a term in
  the formula used to *estimate* `D_eff` from the asymptotic dehydration-rate curve — Eq. (21):**
```latex
J(t)=D_{eff}(T_\infty)\,\frac{\pi^{2}}{R_0^{2}}\left(\frac{V_\infty}{V_0}\right)^{-2/3}X_r(t)
```
  with the asymptotic volume ratio, Eq. (19): `V_∞/V_0 = 1 − φ₀(1 − X_∞/X_0) ≃ 0.1`.
  Eq. (21) is derived in Appendix B (not extracted here).

### B8. Supporting relations (all verbatim, Appendix A / §3)

```latex
C=\frac{p}{R_gT}=\frac{p_v(T)}{R_gT}\frac{p}{p_v(T)}=\frac{p_v(T)}{R_gT}\,RH   \tag{6}
```
```latex
h_T(T_{av},d)=\frac{Nu(T_{av},d)\,k^{air}(T_{av})}{d},\qquad
h_m(T_{av},d)=\frac{Sh(T_{av},d)\,D_v^{air}(T_{av})}{d}   \tag{A10}
```
```latex
Nu(T_{av},d)=2+0.6\,Re^{1/2}Pr^{1/3}
=2+\left(\frac{U_\infty d}{\nu_{air}(T_{av})}\right)^{1/2}
\left(\frac{\nu_{air}(T_{av})}{D_T^{air}(T_{av})}\right)^{1/3}   \tag{A11}
```
```latex
Sh(T_{av},d)=2+0.6\,Re^{1/2}Sc^{1/3}
=2+\left(\frac{U_\infty d}{\nu_{air}(T_{av})}\right)^{1/2}
\left(\frac{\nu_{air}(T_{av})}{D_v^{air}(T_{av})}\right)^{1/3}   \tag{A12}
```
Density / heat capacity / conductivity of the product — Eqs. (A5)–(A7):
```latex
\rho^{p}=\rho^{w}\phi+\rho^{s}(1-\phi),\qquad
C_p^{p}=C_p^{w}x_w+C_p^{s}(1-x_w),\quad x_w=\phi\,(\rho^{w}/\rho^{p}),\qquad
\frac{1}{k^{p}}=\frac{\phi}{k^{w}}+\frac{1-\phi}{k^{s}}
```
Solid-phase correlations — Eqs. (A8), (A9), **as printed**:
```latex
k^{s}[\mathrm{W}/(\mathrm{m\,K})]=2.01\times10^{-1}+1.39\times10^{-3}-4.33\times10^{-6}T^{2},
\quad T[{}^{\circ}\mathrm{C}]   \tag{A8}
```
```latex
C_p^{s}[\mathrm{J}/(\mathrm{g\,K})]=1.5488+1.9625\times10^{-3}T-5.9399\times10^{-6}T^{2},
\quad T[{}^{\circ}\mathrm{C}]   \tag{A9}
```
> ⚠ **Eq. (A8) is also defective as published** — the linear term is missing its `T`:
> `1.39×10⁻³` should be `1.39×10⁻³ T`. Confirmed in the publisher PDF, so it is a paper typo.
> Cross-check: the **CET 2021 paper's Eq. (8)** (which *does* survive in the CET text layer, see D3)
> reads `k_s[W/(m K)] = 2.01×10^{-1} + 1.39×10^{-3} T − 4.33×10^{-6} T², T[°C]` — i.e. the CET
> paper has the correct form of the same correlation.

---

## C. Section / equation numbers in the retrieved source

*Foods* **2020, 9(11), 1577** — Adrover, Venditti, Brasiello.

| Content | Section | Equation |
|---|---|---|
| Mass PDE (with `J_d`; isothermal) | 3.1 Isothermal Moving-Boundary Model | (1) |
| `v_s = −α J_d/ρ_w` (isothermal) | 3.1 | (2) |
| `D_eff(φ,T)` concentration-dependent | 3.1 | (3) |
| `dx_b/dt = v_s|_{x_b}` (isothermal) | 3.1 | (4) |
| Mass Robin BC (isothermal) | 3.1 | (5) |
| Vapour concentration `C = p/(R_g T)` | 3.1 | (6) |
| `RH_b = RH|_{x_b} = DI(c_w(x_b,t),T_∞)` | 3.1 | (7) |
| Mass PDE, general | 3.2 Non-Isothermal Moving-Boundary Model | (8) |
| Heat PDE, general | 3.2 | (9) |
| `v_s = α(c_w)D_eff(T)∇c_w/ρ_w` | 3.2 | (10) |
| `dx_b/dt = v_s|_{x_b}` | 3.2 | (11) |
| Mass Robin BC, general | 3.2 | (12) |
| Heat Robin BC, general | 3.2 | (13) |
| Lumped/moving-domain energy balance | 3.2 | (14) |
| ALE / Comsol FEM details | **3.3 Numerical Issues** | — |
| Ideal-shrinkage volume relation | 4.1 | (15) |
| Spherical mass PDE, isothermal | 4.1 | (16)–(18) |
| `V_∞/V_0 ≃ 0.1` | 4.2 | (19) |
| Dehydration rate `J(t)` | 4.2 | (20) |
| `J = D_eff(π²/R_0²)(V_∞/V_0)^{−2/3} X_r` | 4.2 | **(21)** |
| `D_eff(T)=D_0 e^{−E/(R_gT)}` | 4.2 | **(24)** |
| Spherical mass PDE, non-isothermal | 4.3 The Non-Isothermal Approach | **(25)** |
| Spherical heat PDE, non-isothermal | 4.3 | **(26)** |
| `v_s(r)`, `dR/dt` | 4.3 | **(27)** |
| Symmetry + mass Robin BC | 4.3 | **(28)** |
| Symmetry + heat Robin BC | 4.3 | **(29)** |
| Volume-averaged `<D_eff(t)>` | 4.3 | **(30)** |
| Lumped energy balance (moving domain) | 4.3 | **(31)** |
| `ρ^p, C_p^p, k^p` mixtures | Appendix A | (A5)–(A7) |
| `k^s`, `C_p^s` correlations | Appendix A | (A8), (A9) |
| `h_T`, `h_m` | Appendix A | (A10) |
| `Nu`, `Sh` correlations | Appendix A | (A11), (A12) |

**Crosswalk CET ↔ Foods (the CET paper states its own dependence on this source).** CET §3
(verbatim from the CET text layer): *"The moving-boundary model developed in Adrover et al., 2020
for non-isothermal drying consists of a system of two advection-diffusion partial differential
equations for mass and energy transport, coupled with an equation for the boundary evolution, the
material being assumed homogeneous and isotropic."* The CET abstract likewise states the model *"is
here improved"*/*"added to"* that source. Hence CET (1)–(7) correspond to Foods (8)–(13)
[general form] and to Foods (25)–(29) [spherical realisation]; CET (6)–(7) correspond to Foods
(A11)–(A12). **This mapping is my inference from the two texts, not a printed correspondence
table.**

---

## D. Where the exact formula could NOT be determined

**D1. The CET paper's own equations (1)–(7) in their 1-D cartesian form — NOT RECOVERABLE.**
Verified by direct inspection of the downloaded PDF with PyMuPDF: page 2 carries 158 vector
drawings and page 3 carries 373, and at the positions of labels `(1)`–`(7)` the text layer contains
**only the labels** — no equation body. (Labels located: (1) p.2 y=687.9, (2) p.2 y=731.9,
(3) p.3 y=122.4, (4) p.3 y=273.7, (5) p.3 y=305.8, (6) p.3 y=430.3, (7) p.3 y=461.4.) Since the
journal distributes a single PDF, any further copy of this article will carry the same defect.
Therefore I cannot report the CET paper's exact 1-D cartesian layout, term ordering, or its exact
symbol for the centre plane.

What the CET paper *does* say textually about those equations (verbatim from the CET text layer):
* *"In the one-dimensional formulation that can be adopted for Guava slices (heat and mass transport
  along the thickness coordinate −H₀/2 ≤ x ≤ H₀/2), the transport equations for the water content
  c_w(x,t) [g water/m³] and the sample temperature T(x,t) read as: (1) (2)"* — so the coordinate
  system is `x ∈ [−H₀/2, H₀/2]`.
* *"The velocity v_s(x,t) is the point-wise shrinkage velocity (3) affecting both the heat and mass
  transport equations and controlling the temporal evolution of the sample surface x_b(t)."*
* *"further enforcing the symmetry boundary conditions at ⟨unreadable inline image⟩ and the mixed
  boundary conditions at x_b(t) also referred to as Robin or 'evaporative' or third order boundary
  condition"* — the centre-plane symbol itself is a flattened inline image, hence unreadable; the
  coordinates imply `x = 0`.
* *"The boundary condition (5) takes into account both heat transfer resistance and heat subtracted
  for water evaporation at the air/sample interface (Carslaw and Jaeger, 1959), λ_v(T_b) being the
  heat of water evaporation evaluated at T_b."* — i.e. the CET paper describes its BC (5) as having
  exactly the **two** terms of Foods Eq. (13)/(29); it does **not** describe a third,
  surface-velocity term. This is textual evidence, not proof of the printed formula.

**D2. Any 1-D cartesian reduction I state is MY reduction, not a quotation.** The Foods paper's
general form is coordinate-free and its realisation is spherical. A slab form follows mechanically
by `∇ → ∂/∂x` with `x` the thickness coordinate, but **nothing in the retrieved literature prints
it**, so I am not asserting it as sourced. Treat any cartesian rewrite as unverified until the CET
equation bodies can be imaged/OCR'd.

**D3. Bonus — three CET equations ARE recoverable from the CET text layer** (they were set as
mangled-font text rather than outlines). Between them these are useful because they are
**independent of the Foods paper**:

```latex
k_{s}[\mathrm{W}/(\mathrm{m\,K})]=2.01\times10^{-1}+1.39\times10^{-3}T-4.33\times10^{-6}T^{2},
\qquad T[{}^{\circ}\mathrm{C}]  \tag{CET 8}
```
```latex
C_{ps}[\mathrm{J}/(\mathrm{g\,K})]=1.5488+1.9625\times10^{-3}T-5.9399\times10^{-6}T^{2},
\qquad T[{}^{\circ}\mathrm{C}]  \tag{CET 9}
```
```latex
D_{eff}(T)\ [\mathrm{m^2/s}]=D_0\exp\!\left(-E/(RT)\right),
\quad D_0=\exp(14.63)\ [\mathrm{m^2/s}],
\quad E/R=11095\ [\mathrm{K}]  \tag{CET 12}
```
(CET eq. 12's inline form is quoted above; **the surrounding flattened display body means I cannot
rule out additional structure** in that equation beyond this inline summary.) The CET Eq. (12)
coefficients are internally consistent with the CET paper's own Table 2:
`exp(14.63 − 11095/298.15) = 1.56×10⁻¹⁰` vs Table 2's `1.557×10⁻¹⁰` at 25 °C, and
`exp(14.63 − 11095/313.15) = 9.24×10⁻¹⁰` vs Table 2's `9.258×10⁻¹⁰` at 40 °C (my arithmetic;
note the 30 °C row, `2.877×10⁻¹⁰`, is *not* reproduced by this fit — `exp(14.63 − 11095/303.15) =
2.62×10⁻¹⁰` — which is an inconsistency inside the CET paper that I did not resolve).

**D4. Not attempted / not obtained:** Appendix B of the Foods paper (derivation of Eq. 21) — the
retrieved XML contains it but I did not transcribe it, as the brief did not ask for it. Adrover,
Brasiello & Ponso (2019) *J. Food Eng.* **244**, 178–191 — closed access, no OA copy exists per
Unpaywall, so its equations were not retrieved at all.

---

## Artefacts

| Path | What it is |
|---|---|
| `.research/refs/foods9111577_europepmc.xml` | Europe PMC JATS+MathML full text (raw input, 331,189 B) |
| `.research/refs/foods9111577_epmc.pdf` | Publisher PDF (raw input, 1,153,307 B) — cross-check |
| `.research/refs/CET2187033_cetjournal.pdf` | CET 2021 PDF (raw input, 677,569 B) — the defective one |
| `.research/refs/extract_mathml.py` | MathML → LaTeX converter (stdlib only, no network) |
| `.research/refs/foods9111577_equations.txt` | All 52 display formulas as LaTeX, with labels |
| `.research/refs/dump_sections.py` | Section-level reading copy with formulas inline |
| `.research/refs/foods9111577_sections.txt` | Foods §3–§4.3 prose with equations inline |
| `.research/refs/CET2187033_textlayer.txt` | Full text layer of the CET PDF (shows the gaps) |
| `.research/refs/foods_pdf_eq_context.txt` | PDF-side context for Eqs. (23)–(31) |
| `.research/refs/foods_appA.txt` | PDF-side context for Eqs. (A8)–(A12) |
| `.research/refs/probe_cet.py`, `probe_cet2.py`, `probe_foods*.py` | The inspection commands |

Reproduce the extraction:
```
cd D:\github\myself\Mathematical_Modeing\国赛
python .research\refs\extract_mathml.py
python .research\refs\dump_sections.py
python .research\refs\probe_cet2.py
```
