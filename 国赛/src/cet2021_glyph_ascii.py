# Rasterise individual glyph outlines from the flattened equations and emit ASCII bitmaps
# so the glyphs can be identified from shape rather than guessed from context.
#
# Input : docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf
# Output: outputs/cet2021_glyphs_<tag>.txt   (ASCII bitmaps, one per glyph, in x order)
import os
import numpy as np
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
OUT = "outputs"
doc = fitz.open(SRC)


def bez(p0, p1, p2, p3, n=12):
    """Sample a cubic Bezier into n+1 points."""
    t = np.linspace(0.0, 1.0, n + 1)[:, None]
    p0, p1, p2, p3 = map(np.asarray, (p0, p1, p2, p3))
    pts = ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3
    return [tuple(p) for p in pts]


def drawing_contours(dr):
    """Turn one fitz drawing into a list of contours (closed point loops)."""
    contours = []
    cur = []
    for it in dr["items"]:
        op = it[0]
        if op == "l":
            p1, p2 = it[1], it[2]
            if not cur:
                cur = [(p1.x, p1.y)]
            cur.append((p2.x, p2.y))
        elif op == "c":
            p1, p2, p3, p4 = it[1], it[2], it[3], it[4]
            if not cur:
                cur = [(p1.x, p1.y)]
            cur.extend(bez((p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y), (p4.x, p4.y)))
        elif op == "re":
            r = it[1]
            if cur:
                contours.append(cur)
                cur = []
            contours.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
        elif op == "qu":
            q = it[1]
            if cur:
                contours.append(cur)
                cur = []
            contours.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
    if cur:
        contours.append(cur)
    return contours


def rasterise(contours, W=30, H=26):
    """Even-odd fill of contours into a W x H boolean grid, bbox-normalised."""
    pts = np.array([p for c in contours for p in c], dtype=float)
    if len(pts) == 0:
        return np.zeros((H, W), bool)
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    x1, y1 = pts[:, 0].max(), pts[:, 1].max()
    w, h = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
    # normalise into [0,1] x [0,1], keep aspect ratio, centre
    s = 1.0 / max(w, h)
    nx = (pts[:, 0] - x0) * s
    ny = (pts[:, 1] - y0) * s
    offx = (1 - w * s) / 2.0
    offy = (1 - h * s) / 2.0
    norm = np.stack([nx + offx, ny + offy], axis=1)

    gy, gx = np.mgrid[0:H, 0:W]
    px = (gx + 0.5) / W
    py = (gy + 0.5) / H
    inside = np.zeros((H, W), bool)
    idx = 0
    for c in contours:
        if len(c) < 2:
            continue
        arr = np.array(c, dtype=float)
        a = arr.copy()
        b = np.roll(arr, -1, axis=0)
        ca = np.stack([(a[:, 0] - x0) * s + offx, (a[:, 1] - y0) * s + offy], axis=1)
        cb = np.stack([(b[:, 0] - x0) * s + offx, (b[:, 1] - y0) * s + offy], axis=1)
        for k in range(len(ca)):
            ay, by = ca[k, 1], cb[k, 1]
            ax, bx = ca[k, 0], cb[k, 0]
            if ay == by:
                continue
            cond = (ay > py) != (by > py)
            if not cond.any():
                continue
            xint = ax + (py - ay) * (bx - ax) / (by - ay)
            inside ^= cond & (px < xint)
    return inside


def ascii_art(mask, on="#", off="."):
    return [off + "".join(on if v else off for v in row) + off for row in mask]


def glyphs_in_band(page, y_lo, y_hi, maxw=200.0):
    drs = page.get_drawings()
    sel = []
    for d in drs:
        r = d["rect"]
        if r.width < 0.4 or r.width > maxw or r.height > 40:
            continue
        if r.y0 >= y_lo and r.y1 <= y_hi and r.x0 >= 80 and r.x1 <= 515:
            sel.append(d)
    sel.sort(key=lambda d: (round(d["rect"].y0, 1), d["rect"].x0))
    return sel


# ---- equation bands (label y known from cet2021_eqmap) ----
bands = {
    "eq1": (1, 683.0, 705.0),
    "eq2": (1, 725.0, 750.0),
    "eq3": (2, 114.0, 141.0),
    "eq4": (2, 255.0, 286.0),
    "eq5": (2, 290.0, 317.0),
    "eq10": (2, 709.0, 726.0),
    "eq11": (3, 188.0, 203.0),
}

for tag, (pno, ylo, yhi) in bands.items():
    page = doc[pno]
    gl = glyphs_in_band(page, ylo, yhi)
    lines = []
    lines.append("### %s : page %d, %d glyph outlines, y in [%.1f, %.1f]" % (tag, pno + 1, len(gl), ylo, yhi))
    for i, d in enumerate(gl):
        r = d["rect"]
        lines.append("--- glyph %d  bbox=(%.1f,%.1f,%.1f,%.1f) w=%.2f h=%.2f items=%d"
                     % (i, r.x0, r.y0, r.x1, r.y1, r.width, r.height, len(d["items"])))
        art = ascii_art(rasterise(drawing_contours(d)))
        lines.extend("    " + a for a in art)
    with open(os.path.join(OUT, "cet2021_glyphs_%s.txt" % tag), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(tag, len(gl), "glyphs ->", "outputs/cet2021_glyphs_%s.txt" % tag)
