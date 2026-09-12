# Recognise the flattened display equations: high-resolution page render ->
# connected components merged into glyph candidates -> IoU match against installed font outlines.
#
# Input : docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf
#         outputs/cet2021_templates2.pkl  (from cet2021_selftest.py)
# Output: outputs/cet2021_ocr2_<tag>.txt     glyph identifications
#         outputs/cet2021_lowconf_<tag>.txt  ASCII pictures of low-confidence glyphs
import os, pickle
import numpy as np
import fitz
from scipy import ndimage

OUT = "outputs"
N = 48
PXPT = 32.0

with open(os.path.join(OUT, "cet2021_templates2.pkl"), "rb") as fh:
    TEMPLATES = pickle.load(fh)
print("templates:", len(TEMPLATES))

TM = np.array([t["mask"] for t in TEMPLATES])


def normalise_mask(mask, N=N, pad=3):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return np.zeros((N, N), bool)
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = sub.shape
    span = N - 2 * pad
    s = span / max(w, h)
    mm, nn = max(1, int(round(w * s))), max(1, int(round(h * s)))
    out = np.zeros((nn, mm), float)
    ye = np.linspace(0, h, nn + 1).astype(int)
    xe = np.linspace(0, w, mm + 1).astype(int)
    for i in range(nn):
        r0, r1 = ye[i], max(ye[i] + 1, ye[i + 1])
        for j in range(mm):
            c0, c1 = xe[j], max(xe[j] + 1, xe[j + 1])
            out[i, j] = sub[r0:r1, c0:c1].mean()
    grid = np.zeros((N, N), bool)
    oy, ox = (N - nn) // 2, (N - mm) // 2
    grid[oy:oy + nn, ox:ox + mm] = out > 0.5
    return grid


def score(grid):
    g = grid.sum()
    inter = np.logical_and(TM, grid).sum(axis=(1, 2))
    union = g + TM.sum(axis=(1, 2)) - inter
    iou = np.where(union > 0, inter / np.maximum(union, 1), 0.0)
    order = np.argsort(-iou)[:4]
    return [(float(iou[k]), TEMPLATES[k]["font"], TEMPLATES[k]["char"]) for k in order]


def ascii_art(mask, maxw=52, maxh=26):
    """ASCII picture with SQUARE cells, so shape is not distorted."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return ["<empty>"]
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = sub.shape
    step = max(1, int(np.ceil(max(w / maxw, h / maxh))))
    rows = []
    for r in range(0, h, step):
        rows.append("".join("#" if sub[r:r + step, c:c + step].any() else "."
                            for c in range(0, w, step)))
    return rows


def glyph_candidates(page, rect):
    pix = page.get_pixmap(clip=rect, dpi=int(72 * PXPT), colorspace=fitz.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = img < 170
    lab, n = ndimage.label(ink, structure=np.ones((3, 3), int))
    sc = PXPT
    boxes = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])

    parent = list(range(len(boxes)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            if ox <= 0:
                continue
            # Merge only near-aligned parts of one glyph ('=' bars, 'i' dot, ':' dots).
            # Using 0.85 * MAX width stops a fraction rule from swallowing the
            # numerator/denominator glyphs sitting above and below it.
            if ox < 0.85 * max(a[2] - a[0], b[2] - b[0]):
                continue
            gap = max(a[1], b[1]) - min(a[3], b[3])
            if gap > 4.0 * sc:
                continue
            ra, rb = find(i), find(j)
            if ra != rb:
                parent[rb] = ra

    groups = {}
    for i in range(len(boxes)):
        groups.setdefault(find(i), []).append(boxes[i])

    out = []
    for gid, bs in groups.items():
        x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
        x1 = max(b[2] for b in bs); y1 = max(b[3] for b in bs)
        sub = np.zeros((y1 - y0, x1 - x0), bool)
        for b in bs:
            sub[b[1] - y0:b[3] - y0, b[0] - x0:b[2] - x0] |= ink[b[1]:b[3], b[0]:b[2]]
        out.append({"x0": rect.x0 + x0 / sc, "y0": rect.y0 + y0 / sc,
                    "x1": rect.x0 + x1 / sc, "y1": rect.y0 + y1 / sc, "mask": sub})
    out.sort(key=lambda g: g["x0"])
    return out


BANDS = {
    "eq1": (1, 84.0, 682.0, 300.0, 706.0),
    "eq2": (1, 84.0, 724.0, 324.0, 750.0),
    "eq3": (2, 84.0, 113.0, 356.0, 142.0),
    "eq4": (2, 84.0, 254.0, 319.0, 286.0),
    "eq5": (2, 84.0, 289.0, 291.0, 318.0),
    "eq10": (2, 84.0, 708.0, 365.0, 727.0),
    "eq11": (3, 84.0, 187.0, 244.0, 204.0),
}

doc = fitz.open(r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf")
for tag, (pno, x0, y0, x1, y1) in BANDS.items():
    page = doc[pno]
    rect = fitz.Rect(x0, y0, x1, y1)
    gl = glyph_candidates(page, rect)
    lines, low = [], []
    lines.append("### %s page %d  %d glyph candidates   (columns: id, x-range, y-range, w, h, best guess, IoU)" % (tag, pno + 1, len(gl)))
    for i, g in enumerate(gl):
        s = score(normalise_mask(g["mask"]))
        best = s[0]
        lines.append("g%-3d x=%7.2f..%7.2f y=%7.2f..%7.2f w=%5.2f h=%5.2f | %-11s %r IoU=%.3f | alt %s"
                     % (i, g["x0"], g["x1"], g["y0"], g["y1"], g["x1"] - g["x0"], g["y1"] - g["y0"],
                        best[1], best[2], best[0],
                        " ".join("%s%s%.2f" % (t[1][:7], repr(t[2]), t[0]) for t in s[1:])))
        if best[0] < 0.66 or (len(s) > 1 and s[0][0] - s[1][0] < 0.05):
            low.append("### %s g%d  best=%s %r IoU=%.3f   alts=%s   [w=%.2fpt h=%.2fpt]"
                       % (tag, i, best[1], best[2], best[0],
                          " ".join("%s%s%.2f" % (t[1][:7], repr(t[2]), t[0]) for t in s[1:]),
                          g["x1"] - g["x0"], g["y1"] - g["y0"]))
            low.extend("    " + a for a in ascii_art(g["mask"]))
            low.append("")
    with open(os.path.join(OUT, "cet2021_ocr2_%s.txt" % tag), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    with open(os.path.join(OUT, "cet2021_lowconf_%s.txt" % tag), "w", encoding="utf-8") as fh:
        fh.write("\n".join(low))
    nlow = sum(1 for x in low if x.startswith("###"))
    print("%-5s %3d glyphs, %3d low-confidence" % (tag, len(gl), nlow))
