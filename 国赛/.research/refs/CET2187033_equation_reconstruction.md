# Reconstruction record — display equations of CET 2021, 87, 193-198

Brasiello A., Venditti C., Adrover A. (2021). "Non-Isothermal Moving-Boundary Model for
Food Drying". *Chemical Engineering Transactions* **87**, 193-198. DOI 10.3303/CET2187033

Source PDF: `docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf`
(sha-less; 677,569 B; 6 pages; producer "Acrobat Distiller 11.0 (Windows)" from PScript5).

## 1. Why the equations had to be reconstructed

`markitdown` returns the paper's prose but for every display equation only its number:
`(1)`, `(2)`, … The equation **bodies are not text**. Verified mechanically:

| check | result |
|---|---|
| embedded images on pages 2-6 (`page.get_images`) | **0** — so not raster images |
| Type3 fonts anywhere in the file | **none** |
| vector drawing objects on page 2 / page 3 | 158 / 373 |
| text spans inside the eq (1)/(2) band (p2, y 670-740) | only the prose tail `read as:` and the labels `(1)`,`(2)` |
| union bbox of ink in that band | `(85.08, 684.48, 319.98, 747.30)` — the equation area |
| path items in that ink | 1385 |
| `ActualText` / structure-tree alternative layer | none (`StructTreeRoot` present but carries no math) |

So the display equations were **flattened to glyph outlines** by the print/Distiller
pipeline. There is no text layer to extract, in this file or in the publisher's copy
(a second retrieval of `https://www.cetjournal.it/cet/21/87/033.pdf` reproduced the
identical defect: same drawing counts, same operator counts).

## 2. Method used

Each glyph outline was rasterised from the page and identified by IoU shape-matching
against outlines rendered from the fonts installed on this machine, then the glyph
sequence was reassembled by x-position and y-class (baseline / subscript / superscript).

Scripts (all run from the working directory):

| script | role |
|---|---|
| `src/cet2021_extract.py` | page text + PNG renders (PNG unusable: this model has no image input) |
| `src/cet2021_stream.py` | content-stream operator census |
| `src/cet2021_band.py` | proves the equation band is vector ink, not text |
| `src/cet2021_eqmap.py` | maps each label `(n)` to its ink band |
| `src/cet2021_selftest.py` | builds font templates at `outputs/cet2021_templates2.pkl` + **self-test** |
| `src/cet2021_ocr2.py` | per-glyph identification → `outputs/cet2021_ocr2_<tag>.txt` |
| `src/cet2021_verify.py` | ASCII pictures of the deciding glyphs → `outputs/cet2021_verify_<tag>.txt` |
| `src/cet2021_fine.py` | fine ASCII of a whole band → `outputs/cet2021_fine_<tag>.txt` |
| `src/cet2021_filltest.py` | standalone check of the even-odd glyph fill |

Controls that make the reading trustworthy rather than plausible:

* **Self-test** (`outputs/cet2021_selftest.txt`): reference outlines pushed through the
  extract-then-match path recover themselves **28/30 top-1 exact**. Two known and fixed
  bugs were caught this way and by `cet2021_filltest.py`: (a) font outlines are y-**up**
  while the page raster is y-down, so every template was vertically flipped; (b) a stale
  loop variable caused each glyph to be filled from only its last contour.
* **Widths as a cross-check**: the `ff` pair in Times-Italic fuses into one component of
  ~5.0 pt; `D_eff` measures 14.3 pt here vs 14.4 pt in eq (1).
* **Independent second source** (see §4).

Absolute IoU stays at ~0.6-0.8 because the PDF's embedded outlines are from a different
font revision than the local files; the **rank** is what is reliable, which is why every
low-confidence glyph was checked by eye as ASCII.

## 3. Equations as recovered

Coordinate: 1-D along the slice thickness. The paper's prose names the interval
`-H0/2 <= x <= H0/2`; the printed equations are posed on the **half** interval
`0 < x < x_b(t)`.

**(1)** water (mass) transport — page 3 (printed p. 194), label y=687.9

```
dc_w(x,t)/dt = d/dx ( D_eff(T) dc_w/dx - v_s(x,t) c_w ) ,   0 < x < x_b(t)
```

**(2)** energy transport — page 3, label y=731.9

```
d(rho^p C_p^p T(x,t))/dt = d/dx ( k^p dT/dx - v_s(x,t) rho^p C_p^p T ) ,   0 < x < x_b(t)
```

**(3)** shrinkage velocity and surface evolution — page 4, label y=122.4. Three `=`
signs: a two-statement chain separated by a comma.

```
v_s(x,t) = alpha(c_w) ( D_eff(T) / rho_w ) dc_w/dx ,
dx_b/dt  = v_s|_{x_b(t)} = ( D_eff(T_b) / rho_w ) alpha(c_w) dc_w/dx |_{x_b(t)}
```

**(4)** mass (Robin / "evaporative") BC — page 4, label y=273.7

```
-D_eff(T_b) dc_w/dx|_{x_b} = h_m(T_av) M_w [ p_v(T_b)/(R_g T_b) RH_b - p_v(T_inf)/(R_g T_inf) RH_inf ]
```

**(5)** heat BC — page 4, label y=305.8

```
-k^p dT/dx|_{x_b} = h_T(T_av)(T_b - T_inf) - lambda_v(T_b) D_eff(T_b) dc_w/dx|_{x_b}
```

**(12)** effective diffusivity — survives as (mangled) text, no reconstruction needed

```
D_eff(T) [m2/s] = D_0 exp(-E/(R T)),   D_0 = exp(14.63) [m2/s],   E/R = 11095 K
```

**(6),(7),(8),(9),(10)** also survive as text (Sh/Nu correlations; k_s and C_ps
polynomials; the modified-Anderson isotherm).

**(11)** — the asymptotic thickness/volume-ratio relation — is **read but not trusted**;
see §5.

## 4. Independent corroboration

The equations are not recovered from this PDF alone. The companion paper that the CET
paper names in its own §3 as the origin of the model —

> Adrover A., Venditti C., Brasiello A. (2020). "A Non-Isothermal Moving-Boundary Model
> for Continuous and Intermittent Drying of Pears". *Foods* **9**(11), 1577.
> DOI 10.3390/foods9111577. PMC7692062. PMID 33143274.

— was retrieved with **native MathML** (Europe PMC full-text XML,
`https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7692062/fullTextXML`) and
cross-checked against the publisher PDF. Its equations (8), (9), (10), (11), (12), (13)
and (25)-(29) match the reconstruction above term for term. Note the companion paper is
**spherical** (`r in (0,R(t))`); the CET paper is the 1-D slab reduction, so the forms
differ by `grad -> d/dx` and by the absence of the angular terms — that correspondence is
mine, not printed in either paper.

## 5. The one equation I do not trust: (11)

Glyph sequence on page 4 (label y=191.5), by x-position:

`V_inf / V_0 = H_inf / H_0 ( AR - 1 + H_inf/H_0 )^2 / AR^2`

read as `V_inf/V_0 = (H_inf/H_0) * (AR - 1 + H_inf/H_0)^2 / AR^2`.

**This reading fails its own arithmetic check.** At `AR = 10` and `H_inf/H_0 = 1/3`
it returns `0.290`, but the paper's text states that `H_inf/H_0 = 1/3` corresponds to
`V_inf/V_0 = 0.2`. Something in my glyph grouping is therefore wrong, and the exact
grouping of (11) is **unresolved**. (Supporting that the text is arithmetically coherent:
the paper's `alpha_0 = 0.83` follows exactly from `alpha_0 = (1 - H_inf/H_0)/phi_w(0)
= (1 - 1/3)/0.8 = 0.8333` with `phi_w(0) = 1 - V_inf/V_0 = 0.8` — checked by hand.)

Nothing in the six answers below depends on (11) except the reported value `alpha_0 = 0.83`,
which is given in the paper's own text and is reproduced by the check above.

## 6. Provenance of the quoted prose

All quotations are from `docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.md`,
the MarkItDown conversion, read against the PDF's own text layer
(`outputs/cet2021_page{2,3}_text.txt`). Line numbers of the Markdown are **not** cited as
evidence; section and equation numbers are.

Symbols lost to the flattening are marked `[ ]` in quotations rather than guessed.
