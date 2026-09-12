# Determine HOW the display equations are encoded on pages 2-3.
# Writes UTF-8 report to outputs/cet2021_howenc.txt
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)

lines = []
def w(s=""):
    lines.append(s)

# (a) hunt for Type3 font objects
found = []
for xref in range(1, doc.xref_length()):
    try:
        st = doc.xref_get_key(xref, "Subtype")
    except Exception:
        continue
    if st and "Type3" in str(st):
        found.append(xref)
w("Type3 font xrefs: %s" % found)
w("xref_length: %d" % doc.xref_length())

# (b) all text spans with bbox
for pno in (1, 2):
    page = doc[pno]
    w("\n=========== PAGE %d TEXT SPANS ===========" % (pno + 1))
    d = page.get_text("dict")
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            w("  [non-text block bbox=%s]" % (blk.get("bbox"),))
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                x0, y0, x1, y1 = sp["bbox"]
                w("  y=%7.1f x=%6.1f f=%-24s sz=%4.1f %r" % (y0, x0, sp["font"], sp["size"], sp["text"]))

# (c) drawing clusters: group wide drawings by y-band
for pno in (1, 2):
    page = doc[pno]
    drs = page.get_drawings()
    w("\n=========== PAGE %d DRAWINGS n=%d ===========" % (pno + 1, len(drs)))
    wide = [d for d in drs if d["rect"].width > 40]
    w("wide drawings (w>40): %d" % len(wide))
    for i, d in enumerate(sorted(wide, key=lambda z: (round(z["rect"].y0, 0), z["rect"].x0))[:60]):
        r = d["rect"]
        w("  %3d type=%-4s items=%3d rect=(%6.1f,%6.1f,%6.1f,%6.1f) w=%5.1f h=%5.1f"
          % (i, d["type"], len(d["items"]), r.x0, r.y0, r.x1, r.y1, r.width, r.height))

with open(r"outputs/cet2021_howenc.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote outputs/cet2021_howenc.txt", len(lines), "lines")
