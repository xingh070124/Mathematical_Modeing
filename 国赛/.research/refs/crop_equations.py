"""Crop high-resolution views of the display equations from the Foods 2020 PDF
using text anchors, so the printed form of each equation can be inspected."""
import os

import fitz

REF = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(REF, "foods9111577_epmc.pdf")
OUT = os.path.join(os.path.dirname(REF), "figs_foods")
os.makedirs(OUT, exist_ok=True)

doc = fitz.open(PDF)

JOBS = [
    # (page 1-indexed, anchor phrase, extra px above, band height px @ page pts)
    (4, "pointwise water concentration", 40, 150, "eq1_eq2"),
    (4, "Robin or", 40, 210, "eq4_eq5"),
    (5, "volume of water flowing", 30, 300, "eq3_eq4"),
    (6, "simultaneous solution", 20, 320, "eq8_eq10"),
    (6, "and with the boundary conditions", 10, 300, "eq12_eq13"),
    (10, "The non-isothermal model, Equations", 20, 320, "eq25_eq27"),
    (10, "where the Relative Humidity", 20, 260, "eq28_eq29"),
]

for pno, anchor, pad, height, name in JOBS:
    page = doc[pno - 1]
    hits = page.search_for(anchor)
    if not hits:
        print("p%02d  MISS  %s" % (pno, anchor))
        continue
    r = hits[0]
    clip = fitz.Rect(page.rect.x0, max(page.rect.y0, r.y0 - pad),
                     page.rect.x1, min(page.rect.y1, r.y0 - pad + height))
    pix = page.get_pixmap(dpi=300, clip=clip)
    path = os.path.join(OUT, "foods_p%02d_%s.png" % (pno, name))
    pix.save(path)
    print("p%02d %-36s -> %s (%dx%d)" % (pno, name, os.path.basename(path),
                                         pix.width, pix.height))
