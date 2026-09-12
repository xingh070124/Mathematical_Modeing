# Render one equation band as a fine ASCII picture (2 chars per point) to resolve layout.
import numpy as np
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
RAMP = " .:-=+*#%@"
PXPT = 8.0
CHAR = 4

BANDS = {
    "eq11": (3, 84.0, 186.0, 244.0, 205.0),
    "eq3": (2, 84.0, 113.0, 356.0, 142.0),
}

doc = fitz.open(SRC)
for tag, (pno, x0, y0, x1, y1) in BANDS.items():
    page = doc[pno]
    pix = page.get_pixmap(clip=fitz.Rect(x0, y0, x1, y1), dpi=int(72 * PXPT),
                          colorspace=fitz.csGRAY, alpha=False)
    ink = 255 - np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    H, W = pix.height // CHAR, pix.width // CHAR
    blk = ink[:H * CHAR, :W * CHAR].reshape(H, CHAR, W, CHAR).max(axis=(1, 3))
    per_char = CHAR / PXPT           # pt per char
    lines = ["### %s page %d  %.3f pt per char; label x is (col * %.3f + %.1f)" % (tag, pno + 1, per_char, per_char, x0)]
    # x ruler every 5 chars
    ruler = ""
    for c in range(0, W, 5):
        s = "%d" % round(c * per_char + x0)
        ruler += s.ljust(5)
    lines.append("      " + ruler[:W])
    for r in range(H):
        lines.append("%5d %s" % (r, "".join(RAMP[min(9, int(v) * 10 // 256)] for v in blk[r])))
    with open("outputs/cet2021_fine_%s.txt" % tag, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(tag, "->", W, "x", H)
