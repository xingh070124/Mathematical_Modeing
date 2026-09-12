# Governing equations — Foods 2020, Adrover/Venditti/Brasiello (PMC7692062)

Retrieved verbatim, 2026-09-11. Every formula below is a mechanical transcription of the
publisher's own MathML (and cross-checked against the publisher PDF text layer and, for the
two contested equations, against the printed glyph geometry of the page).

## 0. Provenance — which URL actually yielded the text

| item | value |
|---|---|
| record | PMID **33143274** / PMCID **PMC7692062** / DOI **10.3390/foods9111577** — Foods **2020**, 9(11), 1577 |
| **text used (primary)** | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7692062/fullTextXML` — JATS + **MathML** full text. Fetched with the `markitdown` MCP converter (the `web_fetch` tool refused this content type). Local copy: `.research/refs/foods9111577_europepmc.xml`, 331 189 B, sha256 `193A5C675C610E0D…` |
| **second rendition used (cross-check)** | `https://europepmc.org/articles/PMC7692062?pdf=render` — the publisher PDF. Local copy: `.research/refs/foods9111577_epmc.pdf`, 1 153 307 B (byte size matches the `<?pdf-size 1153307?>` declared in the JATS); text layer `.research/refs/foods9111577_pdf_textlayer.txt` |
| **URLs that did NOT work** | MDPI HTML `…/2304-8158/9/11/1577` → **HTTP 403**; MDPI XML `…/9/11/1577/xml` → **HTTP 403**; PMC HTML `pmc.ncbi.nlm.nih.gov/articles/PMC7692062/` → **HTTP 403**. None of the MDPI or PMC URLs contributed any text. |
| are the equations images? | **No.** Display equations are genuine MathML in the JATS deposit and genuine text in the PDF. Nothing below was reconstructed from context. |
| toolchain | `.research/refs/extract_mathml.py` (MathML→LaTeX, pure stdlib) → `.research/refs/foods9111577_equations.txt` (52 display formulas). Re-run reproduced the file with **0 diff** (`.research/refs/verify_foods_equations.py`). Prose-with-equations dumps: `foods9111577_fulltext_prose.txt`, `foods9111577_sec2_3_prose.txt`. |

**Numbering note.** The paper numbers its equations (1)–(31) plus Appendix (A1)–(A20). Below I give
the section where each is introduced: **§3.1** = isothermal model, **§3.2** = non-isothermal model
(the section that defines the model actually reused downstream), **§4.1** = isothermal spherical
form, **§4.3** = non-isothermal spherical form, **App. A/B** = properties and asymptotics.

---

## 1. Water / mass transport PDE, coordinate system and domain

### 1a. General (vector) form

**Isothermal — Eq. (1), §3.1. Printed verbatim:**

```
∂c_w(x,t)/∂t − ∇·( J_d + v_s(x) c_w )  =  =  ∇·( D_eff ∇c_w − v_s(x) c_w ),   x ∈ V(t)
```

> ⚠ **This equation is misprinted in the published paper.** The page carries **two consecutive
> `=` glyphs** and **no `=` at all between `∂c_w/∂t` and `−∇·(…)`**. I verified this from the
> printed page geometry, not from a text extractor: on PDF page 4 both `=` glyphs sit on the
> **same baseline, y = 572.4**, at x = 270.40–278.48 and x = 284.26–292.34 (a ~5.8 pt gap,
> nothing between them), while the running text immediately before is `…+ v_s(x) c_w` ending at
> x = 260.72 and `∇·` starts at x = 295.34. The whole equation occupies one line.
> Read literally, and using `J_d = −D_eff ∇c_w`, the printed form implies `∂c_w/∂t = 0`, so it
> **cannot** be read literally. The unique algebraically consistent reading (**labelled: my
> inference, not a quotation**) is the three-member chain
> `∂c_w/∂t = −∇·(J_d + v_s c_w) = ∇·(D_eff ∇c_w − v_s c_w)`, because
> `−∇·(J_d + v_s c_w) = −∇·(−D_eff∇c_w + v_s c_w) = ∇·(D_eff∇c_w − v_s c_w)`.
> I could not determine **which** of the two `=` glyphs is the spurious one, and I found no
> erratum for this article (Europe PMC returns exactly one record — the article itself — with no
> linked correction).

**Non-isothermal — Eq. (8), §3.2. Printed verbatim (clean, unambiguous):**

$$\frac{\partial c_w(\mathbf{x},t)}{\partial t} = \nabla\cdot\left(D_{eff}(T)\,\nabla c_w - \mathbf{v}_s(\mathbf{x})\,c_w\right),$$

with `J_d = −D_eff ∇c_w` the diffusive mass flux and `(v_s c_w)` the convective term arising from
local shrinkage. This is the equation the non-isothermal model (and the CET 2021 reuse) rests on.

### 1b. One-dimensional spherical form actually solved

**§4.3, Eq. (25)** (introduced by the sentence: *"The non-isothermal model, Equations (8)–(13),
rewritten for a spherical sample in terms of the water volume fraction φ(r,t), reads as"*):

$$\frac{\partial \phi(r,t)}{\partial t}=\frac{1}{r^{2}}\frac{\partial}{\partial r}\left(r^{2}\left(D_{eff}(T)\frac{\partial \phi}{\partial r}-v_s(r)\,\phi\right)\right),\qquad r\in(0,R(t))$$

with `φ = c_w/ρ_w` the water volume fraction. The isothermal analogue is **Eq. (16), §4.1**
(same expression with `D_eff` in place of `D_eff(T)`).

### 1c. Coordinate system and domain

- **Coordinate system:** spherical, radial coordinate `r`, with the sample centre at `r = 0`.
  In the general formulation the point is `x` and the domain is the sample volume `V(t)`.
- **Domain:** **time-dependent — it is NOT the initial thickness or the initial radius.**

Quoted sentences:

> §3.1: "During the dehydration process, the sample volume *V*(*t*) and surface *S*(*t*) evolve in
> time due to sample shrinkage."

> §3.1: "The transport equation describing the space-time evolution of the pointwise water
> concentration *c*<sub>w</sub>(**x**,*t*) [g water/m³ product] inside the sample volume *V*(*t*) is an
> advection-diffusion equation accounting for the local shrinkage through the pointwise shrinkage
> velocity **v**<sub>s</sub>(**x**)"

> §4.1: "It is assumed that the spherical shape of the sample is not altered by the dehydration
> process. The sample geometry is uniquely characterized by its radius *R*(*t*) evolving in time
> from its initial value *R*<sub>0</sub> towards its asymptotic value *R*<sub>∞</sub>."

**⚠ Correction to the premise of the question.** This paper contains **no thickness at all**.
The strings `thickness`, `H_0`, `H(t)` occur **0 times** in the entire JATS XML and **0 times** in
the entire PDF text layer. The sample is a **sphere** (`sphere`/`spherical` appear 3/7 times;
`d_0` in Table 1 is a *diameter*, 5.24–5.69 cm). So the dichotomy "domain = initial thickness
`H_0` vs time-dependent `H(t)`" **does not apply to Foods 2020**.

The `H_0`/`H(t)` notation belongs to the **downstream 2021 CET paper**, whose text layer states the
domain as *"heat and mass transport along the thickness coordinate −H₀/2 ≤ x ≤ H₀/2"* (guava
slices, H₀ = 3 mm, L₀ = 30 mm) — i.e. the CET paper poses the model on the **initial thickness**.
The foods-2020 spherical equivalent of that statement is `r ∈ (0,R(t))`: **the domain is the
moving, time-dependent one.**

---

## 2. Heat / energy transport PDE

**§3.2, Eq. (9). Printed verbatim:**

$$\frac{\partial\left(\rho^{p}C_{p}^{p}\,T(\mathbf{x},t)\right)}{\partial t}=\nabla\cdot\left(k^{p}\,\nabla T-\mathbf{v}_s(\mathbf{x})\,\rho^{p}C_{p}^{p}\,T\right),$$

**§4.3, Eq. (26), one-dimensional spherical — printed verbatim:**

$$\frac{\partial\left(\rho^{p}C_{p}^{p}\,T(r,t)\right)}{\partial t}=\frac{1}{r^{2}}\frac{\partial}{\partial r}\left(r^{2}\left(k^{p}\frac{\partial \phi}{\partial r}-v_s(r)\,\rho^{p}C_{p}^{p}\,T\right)\right),\qquad r\in(0,R(t))$$

> ⚠ **Second apparent printing defect.** Eq. (26) prints `k^p ∂φ/∂r` inside the **heat** equation,
> where the conduction term should be `k^p ∂T/∂r` (compare Eq. (9), which prints `k^p ∇T`, and note
> that `∂φ/∂r` is not dimensionally a temperature gradient). Confirmed in **both** renditions:
> the deposited MathML encodes `<msup><mi>k</mi><mi>p</mi></msup> ∂ϕ/∂r`, and on PDF page 10 the
> glyphs `kp` (x = 273.42–282.32) and `∂φ` with its denominator `∂r` (x = 285.89–296.86 / 286.89–295.76)
> sit on the same line inside equation (26). **This is what is printed.** Whether it is an author
> error or a production error, and what the authors intended, I could not determine; no erratum is
> indexed. Eq. (9) is the internally consistent form.

**Lumped-temperature reduction (when `T(x,t) = T_b(t)`):**

- **§3.2, Eq. (14):**

$$\frac{d}{dt}\left(T_b\int_{V(t)}\left(\rho^{p}C_{p}^{p}\right)d\mathbf{x}\right)=\int_{S(t)}\left(-h_T(T_{av})\left(T_b-T_\infty\right)+\lambda_v(T_b)\,D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}\right)dS$$

- **§4.3, Eq. (31):**

$$\frac{d}{dt}\left(T_b\int_{0}^{R(t)}\left(\rho^{p}C_{p}^{p}\right)4\pi r^{2}dr\right)=\left(-h_T(T_{av})\left(T_b-T_\infty\right)+\lambda_v(T_b)\,\rho_w D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}\right)4\pi R^{2}(t)$$

Note this is a `d/dt` **of a volume integral** — a Leibniz-type contribution is therefore implicit
in the time derivative here (but no explicit `dR/dt` factor is written anywhere).

---

## 3. Shrinkage velocity `v_s(x,t)` and `α(c_w)` / `α_0`

**§3.1, Eq. (2):**

$$\mathbf{v}_s(\mathbf{x})=-\alpha(c_w)\,\mathbf{J}_d(\mathbf{x})/\rho_w=\alpha(c_w)\,D_{eff}\,\nabla c_w/\rho_w$$

**§3.2, Eq. (10):**

$$\mathbf{v}_s(\mathbf{x})=\alpha(c_w)\,D_{eff}(T)\,\nabla c_w/\rho_w$$

**One-dimensional spherical (§4.1 Eq. (17) and §4.3 Eq. (27))** — note the factor `α` is **not**
written here; with `v_s = α D_eff ∂φ/∂r` these correspond to `α = 1`:

$$v_s(r)=D_{eff}\frac{\partial \phi}{\partial r},\qquad v_s(r)=D_{eff}(T)\frac{\partial \phi}{\partial r}$$

where `α(c_w)` is *"a shrinkage proportionality factor, depending on the pointwise water
concentration"* (§3.1). Definition of the limiting values, **quoted verbatim (§3.1)**:

> "The shrinkage factor *α*(*c*<sub>w</sub>) is the fingerprint of the specific food material under
> investigation. The simplest case is that of a constant shrinkage factor, i.e.,
> *α*(*c*<sub>w</sub>) = *α*<sub>0</sub>. *α*<sub>0</sub> = 0 represents the case of a rigid solid
> (no shrinkage). *α*<sub>0</sub> = 1 represents the case of ideal shrinkage, in which volume
> reduction corresponds exactly to the volume of water flowing outside the sample. Values of
> *α*<sub>0</sub> less or greater than unity imply volume reduction less or greater than the
> corresponding water volume flow [14,15]."

**Value used for pears — `α = α_0 = 1` (ideal shrinkage), stated in §4.1, §4.2 and §5:**

> §4.1: "…the assumption of a constant and unitary shrinkage coefficient *α*(*c*<sub>w</sub>) =
> *α*<sub>0</sub> = 1. It must be pointed out that the assumption *α*(*c*<sub>w</sub>) = *α*<sub>0</sub>
> does not imply that the shrinkage velocity **v**<sub>s</sub>(**x**) is constant, nor in time or
> space, but rather that, according to Equation (2), the shrinkage velocity is directly proportional
> to the local concentration gradient."

> §4.2: "…implemented in the moving-boundary model by setting *α*(*φ*) = *α*<sub>0</sub> = 1."

---

## 4. Evolution of the sample surface

**General, §3.1 Eq. (4):**

$$\frac{d\mathbf{x}_b}{dt}=\mathbf{v}_s\big|_{\mathbf{x}_b}=\frac{\alpha(c_w)}{\rho_w}D_{eff}\,\nabla c_w\big|_{\mathbf{x}_b},\qquad \mathbf{x}_b\in S(t)$$

**Non-isothermal, §3.2 Eq. (11):**

$$\frac{d\mathbf{x}_b}{dt}=\mathbf{v}_s\big|_{\mathbf{x}_b}=\frac{\alpha(c_w)}{\rho_w}D_{eff}(T_b)\,\nabla c_w\big|_{\mathbf{x}_b},\qquad \mathbf{x}_b\in S(t)$$

**One-dimensional spherical, §4.1 Eq. (17) and §4.3 Eq. (27)** (verified from page-10 glyph layout):

$$\frac{dR(t)}{dt}=v_s(R(t))=D_{eff}\,\frac{\partial \phi}{\partial r}\Big|_{R(t)},\qquad
\frac{dR(t)}{dt}=v_s(R(t))=D_{eff}(T_b)\,\frac{\partial \phi}{\partial r}\Big|_{R(t)}$$

---

## 5. Symmetry boundary condition at the sample centre

**§4.3 Eqs. (28)–(29), first line of each** (also §4.1 Eq. (18)):

$$\frac{\partial \phi}{\partial r}\Big|_{r=0}=0,\qquad \frac{\partial T}{\partial r}\Big|_{r=0}=0$$

The general vector formulation of §3.1–§3.2 does **not** write a symmetry condition explicitly;
it appears only once the problem is reduced to the spherical 1-D form.

---

## 6. Mixed / Robin / "evaporative" boundary condition at the moving surface — **does it contain a boundary-velocity term?**

### **Answer: NO.** 

As printed, **none** of the mixed boundary conditions contains any term involving the boundary
velocity `dx_b/dt` or `v_s(x_b)`. There is no explicit Leibniz-rule / domain-motion term in any
Robin boundary condition of this paper. Verified in both renditions and, for Eq. (28), from the
glyph geometry of page 10.

**§3.1, Eq. (5) — isothermal, general form, printed verbatim:**

$$-D_{eff}\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}=h_m M_w\left(C|_{\mathbf{x}_b}-C_\infty\right)\;=\;=\;h_m M_w\frac{p_v(T_\infty)}{R_g T_\infty}\left(RH_b-RH_\infty\right)$$

(Same doubled `=` artifact as in Eq. (1). The chain
reading is unambiguous here, because Eq. (6), `C = (p_v(T)/R_gT)·RH`, makes the second and third
members equal; the printed form has one relation too many, not too few.)

**§3.2, Eq. (12) — non-isothermal, general form:**

$$-D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}=h_m(T_{av})\,M_w\left(\frac{p_v(T_b)}{R_g T_b}RH_b-\frac{p_v(T_\infty)}{R_g T_\infty}RH_\infty\right)$$

**§4.3, Eq. (28), second line — the 1-D spherical form actually solved:**

$$-D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}=h_m(T_{av})\frac{M_w}{\rho_w}\left(\frac{p_v(T_b)}{R_g T_b}RH_b-\frac{p_v(T_\infty)}{R_g T_\infty}RH_\infty\right)$$

Left-hand side: the diffusive water flux only. Right-hand side: the convective mass-transfer driving
force only. **No `dx_b/dt`, no `v_s(R(t))` term.** The isothermal spherical analogue is Eq. (18).

**Heat-flux boundary condition, §3.2 Eq. (13) and §4.3 Eq. (29):**

$$-k^{p}\,\nabla T\cdot\mathbf{n}\big|_{\mathbf{x}_b}=h_T(T_{av})\left(T_b-T_\infty\right)-\lambda_v(T_b)\,D_{eff}(T_b)\,\nabla c_w\cdot\mathbf{n}\big|_{\mathbf{x}_b}$$

$$-k^{p}\frac{\partial T}{\partial r}\Big|_{R(t)}=h_T(T_{av})\left(T_b-T_\infty\right)-\lambda_v(T_b)\,\rho_w D_{eff}(T_b)\frac{\partial \phi}{\partial r}\Big|_{R(t)}$$

The evaporative sink `λ_v D_eff ∂φ/∂r` is proportional to the **local water flux**, not to the
boundary velocity. There is no velocity term here either.

**Where the boundary motion *does* enter — three places, none of them a Robin BC:**

1. the shrinkage-convective term inside the PDEs: `−v_s c_w` (Eqs. 1, 8, 16, 25) and
   `−v_s ρ^p C_p^p T` (Eqs. 9, 26);
2. the boundary-evolution ODEs (Eqs. 4, 11, 17, 27) quoted in §4 above;
3. the lumped thermal ODE (Eqs. 14, 31), which is a `d/dt` of a volume integral and therefore
   carries a Leibniz-type contribution implicitly.

> **Interpretation (labelled: inference).** The paper poses the mass balance in the *water volume
> fraction* `φ = c_w/ρ_w` with an explicit shrinkage-convective flux `−v_s φ` inside the PDE. That
> is a standard way to absorb the interface motion into the transport equation, leaving a pure
> flux-matching (Robin) condition at the interface. This is a structural explanation of *why* no
> boundary-velocity term appears — it is **not** a claim made in the paper.

---

## 7. Effective water diffusivity `D_eff`

**General form — §3.1, Eq. (3):**

$$D_{eff}(\phi,T)=D_{\phi_0}(T)\exp\left(-\beta\frac{\phi_0-\phi}{\phi_0-\phi_\infty}\right),\qquad \beta\ge 0,\qquad \phi=c_w/\rho_w$$

`φ_0` = initial water volume fraction; `D_φ0` and `D_∞ = D_φ0 exp(−β)` are the effective
diffusivities at the beginning and at the end of drying.

**Does it depend only on temperature? YES, in the model as applied — `β = 0` is assumed.**

> §3.2: "In the present formulation it has been assumed that the effective water diffusivity is
> solely a function of the temperature and independent of the local water concentration, i.e.,
> *β* = 0 in Equation (3)."

> §4.3: "Indeed, there is no need to introduce a concentration-dependent diffusion coefficient,
> Equation (3), that would require the estimate of the *β* parameter. For this reason, we set
> *β* = 0 also for all the subsequent simulations of intermittent dehydration."

**Explicit temperature dependence — §4.2, Eq. (24):**

$$D_{eff}(T)=D_0\,e^{-\frac{E}{R_g T}},\qquad D_0=4.00012\times10^{-5}\ \mathrm{m^2/s},\qquad E/R_g=-3872.63\ \mathrm{K}$$

Estimated values (§4.2): `D_eff(40 °C) = 1.703×10⁻¹⁰ m²/s`, `D_eff(50 °C) = 2.497×10⁻¹⁰ m²/s`.

**Is it corrected for shrinkage?** In the governing PDE — **no**: `D_eff` is not multiplied by any
shrinkage factor. Shrinkage is carried entirely by the convective velocity `v_s`. There is however
**one place where an explicit shrinkage factor multiplies `D_eff`**, namely the asymptotic
*estimation* of `D_eff` — **§4.2 Eq. (21)** and **App. B Eq. (A20)**:

$$J(t)=D_{eff}(T_\infty)\frac{\pi^{2}}{R_0^{2}}\left(\frac{V_\infty}{V_0}\right)^{-2/3}X_r(t)$$

$$J=\theta(T_\infty)X_r=D_{eff}(T_\infty)\frac{\pi^{2}}{R_\infty^{2}}X_r=D_{eff}(T_\infty)\frac{\pi^{2}}{R_0^{2}}\left(\frac{V_\infty}{V_0}\right)^{-2/3}X_r$$

The exact shrinkage factor is therefore **`(V_∞/V_0)^(−2/3)`**, which equals **`(R_0/R_∞)²`** via Eq. (A13),
`R_∞/R_0 = (V_∞/V_0)^{1/3}`. Note it corrects the **length scale** (`R_0 → R_∞`), not `D_eff` itself.
For pears `V_∞/V_0 ≃ 0.1` (Eq. (19)). The derivation explicitly assumes the convective-shrinkage
term is negligible asymptotically — App. B item 3: *"the convective-shrinkage contribution
D_eff (∂φ/∂r) φ is negligible compared to the diffusive term −D_eff ∂φ/∂r, and a purely diffusive
transport equation can be adopted"*.

---

## 8. Section ⇄ equation index (traceability)

| Eq. | content | section |
|---|---|---|
| (1) | water PDE, isothermal, general — **misprinted** | §3.1 |
| (2) | `v_s(x) = −α(c_w) J_d/ρ_w = α(c_w) D_eff ∇c_w/ρ_w` | §3.1 |
| (3) | `D_eff(φ,T)` with `β` | §3.1 |
| (4) | `dx_b/dt` | §3.1 |
| (5) | Robin/evaporative mass BC, isothermal, general — doubled `=` | §3.1 |
| (6) | `C = (p_v(T)/R_g T)·RH` | §3.1 |
| (7) | `RH_b = DI(c_w(x_b,t),T_∞)` | §3.1 |
| (8) | **water PDE, non-isothermal (the one reused)** | §3.2 |
| (9) | **heat PDE, non-isothermal** | §3.2 |
| (10) | `v_s(x) = α(c_w) D_eff(T) ∇c_w/ρ_w` | §3.2 |
| (11) | `dx_b/dt`, non-isothermal | §3.2 |
| (12) | Robin mass BC, non-isothermal | §3.2 |
| (13) | heat-flux BC with evaporative sink | §3.2 |
| (14) | lumped `T_b(t)` ODE (Leibniz-type `d/dt` of volume integral) | §3.2 |
| (15) | ideal-shrinkage relation `1−V(t)/V_0 = φ_0(1−X(t)/X_0)` | §4.1 |
| (16) | water PDE, isothermal, spherical, `r∈(0,R(t))` | §4.1 |
| (17) | `v_s(r)` and `dR/dt`, isothermal spherical | §4.1 |
| (18) | symmetry + Robin mass BC, isothermal spherical | §4.1 |
| (19) | `V_∞/V_0 ≃ 0.1` | §4.1 |
| (20)–(23) | dehydration rate `J(t)`, best-fit `X(t)/X_0` | §4.2 |
| (21) | `J(t)` **with the shrinkage factor `(V_∞/V_0)^(−2/3)`** | §4.2 |
| (24) | **`D_eff(T) = D_0 exp(−E/R_gT)`** | §4.2 |
| (25) | water PDE, non-isothermal spherical, `r∈(0,R(t))` | §4.3 |
| (26) | heat PDE, non-isothermal spherical — prints `k^p ∂φ/∂r` | §4.3 |
| (27) | `v_s(r)` and `dR/dt`, non-isothermal spherical | §4.3 |
| (28) | symmetry + Robin mass BC, non-isothermal spherical | §4.3 |
| (29) | symmetry + heat-flux BC, non-isothermal spherical | §4.3 |
| (30) | volume-averaged `⟨D_eff(t)⟩` | §4.3 |
| (31) | lumped `T_b(t)` ODE, spherical | §4.3 |
| (A1)–(A12) | sorption isotherm, ρ^p, C_p^p, k^p, `h_T`, `h_m`, Nu, Sh | App. A |
| (A13)–(A20) | asymptotic analysis; (A20) contains the shrinkage factor | App. B |

---

## 9. What I could NOT determine exactly

1. **The intended reading of Eq. (1).** The published equation carries two consecutive `=` signs on
   one line and omits the relation after `∂c_w/∂t`; read literally it is algebraically impossible.
   I could not determine which glyph is spurious, and there is no indexed erratum. I quote the
   printed form verbatim and separately give the consistent chain reading **as inference**.
   Same artifact, but harmless, in Eq. (5).
2. **Whether Eq. (26)'s `k^p ∂φ/∂r` is an author error, a production error, or intentional.** It is
   printed that way in both the MathML deposit and the PDF; I did not obtain the authors' LaTeX or
   any correction notice, so I cannot say what was intended.
3. **Whether `α` is implicitly 1 in Eqs. (17) and (27).** Those two equations omit the factor `α`
   while every other statement about pears sets `α = α_0 = 1`. That they correspond to `α = 1` is my
   inference from consistency, not something the equations say.
4. **The MDPI HTML/XML rendition.** Both returned HTTP 403 to every fetch method available to me,
   so I cannot report what MDPI's own HTML shows. I did not use any MDPI URL for text.
5. **Whether the upstream `h_m`, `h_T`, `ρ^p`, `C_p^p`, `k^p` correlations are correctly transcribed
   for the purpose of reimplementing them** — I extracted all of them (App. A, Eqs. A1–A12) but
   verified only against the two renditions of this one paper, not against their cited sources.
6. **The CET 2021 reuse itself.** The 2021 Chemical Engineering Transactions paper (DOI
   10.3303/CET2187033, local copy `.research/refs/CET2187033_cetjournal.pdf`)
   prints its equations **as images** — its text layer contains only the equation *numbers*
   `(1)`…`(10)`, no formula text. So I could not cross-check how it restates the Foods-2020
   equations, nor verify its reuse of them. Its prose does state the domain as the thickness
   coordinate `−H₀/2 ≤ x ≤ H₀/2` and refers to a moving surface `x_b(t)`, and it repeats the
   `α₀ = 0` rigid / `α₀ = 1` ideal-shrinkage definitions.
