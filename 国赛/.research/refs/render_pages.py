"""Rasterise the pages of the Foods 2020 PDF that carry the governing equations,
so the printed layout can be inspected directly (resolves the doubled '=' in
Eq (1) and the k^p dphi/dr vs k^p dT/dr question in Eq (26)).

Input : .research/refs/foods9111577_epmc.pdf
Output: .research/figs_foods/pNN.png
"""
import os

import fitz

REF = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(REF, "foods9111577_epmc.pdf")
OUT = os.path.join(os.path.dirname(REF), "figs_foods")
os.makedirs(OUT, exist_ok=True)

doc = fitz.open(PDF)
print("pages:", doc.page_count)

# 1-indexed pages to render
for pno in [3, 4, 5, 6, 10, 11]:
    if pno < 1 or pno > doc.page_count:
        continue
    page = doc[pno - 1]
    txt = page.get_text()
    head = " ".join(txt.split()[:14])
    pix = page.get_pixmap(dpi=200)
    path = os.path.join(OUT, "foods_p%02d.png" % pno)
    pix.save(path)
    print("p%02d -> %s  (%dx%d)  | %s" % (pno, os.path.basename(path),
                                          pix.width, pix.height, head[:110]))
