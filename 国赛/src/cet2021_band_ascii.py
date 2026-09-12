# Render each display-equation band as a monospaced ASCII picture so the equation can be
# read off directly from the page image, layout intact.
#
# Input : docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf
# Output: outputs/cet2021_band_ascii_<tag>.txt
import os
import numpy as np
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
OUT = "outputs"
doc = fitz.open(SRC)

RAMP = " .:-=+*#%@"

# tag -> (page_index, x0, y0, x1, y1)  -- generous margins around the ink
BANDS = {
    "eq1": (1, 84.0, 682.0, 300.0, 706.0),
    "eq2": (1, 84.0, 724.0, 324.0, 750.0),
    "eq3": (2, 84.0, 113.0, 356.0, 142.0),
    "eq4": (2, 84.0, 254.0, 319.0, 286.0),
    "eq5": (2, 84.0, 289.0, 291.0, 318.0),
    "eq6": (2, 84.0, 414.0, 303.0, 442.0),
    "eq7": (2, 84.0, 445.0, 312.0, 473.0),
    "eq10": (2, 84.0, 708.0, 365.0, 727.0),
    "eq11": (3, 84.0, 187.0, 244.0, 204.0),
    "eq12": (3, 84.0, 585.0, 300.0, 606.0),
}

PXPT = 4.0      # pixels per point for the intermediate render
CHAR = 4        # pixels per ascii character cell (square -> aspect preserved)

for tag, (pno, x0, y0, x1, y1) in BANDS.items():
    page = doc[pno]
    dpi = int(72 * PXPT)
    pix = page.get_pixmap(clip=fitz.Rect(x0, y0, x1, y1), dpi=dpi,
                          colorspace=fitz.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = 255 - img  # 0 = paper, 255 = ink

    H = pix.height // CHAR
    W = pix.width // CHAR
    hh, ww = H * CHAR, W * CHAR
    blk = ink[:hh, :ww].reshape(H, CHAR, W, CHAR).max(axis=(1, 3))

    lines = []
    lines.append("### %s  page %d  band x[%.0f,%.0f] y[%.0f,%.0f]  (%d cols x %d rows, %0.2f pt per char)"
                 % (tag, pno + 1, x0, x1, y0, y1, W, H, CHAR / PXPT))
    # ruler every 10 chars = 10*CHAR/PXPT pt from x0
    step = 10
    ruler = "".join(("%-10d" % (int(round(i * CHAR / PXPT))))[:10] for i in range(0, W, step))
    lines.append(" " * 6 + ruler[:W])
    for r in range(H):
        row = blk[r]
        txt = "".join(RAMP[min(len(RAMP) - 1, int(v) * len(RAMP) // 256)] for v in row)
        lines.append("%5d %s" % (r, txt))
    with open(os.path.join(OUT, "cet2021_band_ascii_%s.txt" % tag), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(tag, "->", "outputs/cet2021_band_ascii_%s.txt" % tag, "(%dx%d)" % (W, H))
