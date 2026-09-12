# Map each numbered display equation: its label position and the vector-ink band that carries it.
import fitz, re

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)

lines = []
def w(s=""):
    lines.append(str(s))

for pno in range(doc.page_count):
    page = doc[pno]
    words = page.get_text("words")
    labels = [(wd[0], wd[1], wd[4]) for wd in words if re.fullmatch(r"\(\d+\)", wd[4])]
    if not labels:
        continue
    drs = page.get_drawings()
    # only keep glyph-ish drawings: small filled paths
    drs = [d for d in drs if d["rect"].width < 200 and d["rect"].height < 40 and d["rect"].width > 0.4]
    w("===== page %d : %d labels, %d glyph-scale drawings" % (pno + 1, len(labels), len(drs)))
    for (lx, ly, lab) in sorted(labels, key=lambda z: z[1]):
        # ink within the vertical band centred on the label
        band = fitz.Rect(80, ly - 8, 512, ly + 14)
        sel = [d for d in drs if fitz.Rect(d["rect"]).intersects(band)]
        if sel:
            u = fitz.Rect()
            for d in sel:
                u |= fitz.Rect(d["rect"])
            n_items = sum(len(d["items"]) for d in sel)
            w("  %-5s label at y=%7.2f x=%6.1f | ink paths=%3d items=%4d bbox=(%6.1f,%6.1f,%6.1f,%6.1f) w=%6.1f h=%5.1f"
              % (lab, ly, lx, len(sel), n_items, u.x0, u.y0, u.x1, u.y1, u.width, u.height))
        else:
            w("  %-5s label at y=%7.2f x=%6.1f | NO vector ink in band" % (lab, ly, lx))

with open(r"outputs/cet2021_eqmap.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("\n".join(lines))
