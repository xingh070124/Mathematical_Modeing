# Recover the flattened display equations by shape-matching each glyph outline
# against reference outlines rendered from the fonts actually installed on this machine.
#
# Input : docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf
# Output: outputs/cet2021_ocr_<tag>.txt   (glyph-by-glyph identification with IoU)
#         outputs/cet2021_templates.pkl   (cached reference templates)
import os
import pickle
import numpy as np
import fitz
from scipy import ndimage
from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.recordingPen import RecordingPen

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
WIN = r"C:\Windows\Fonts"
OUT = "outputs"
N = 40  # match grid is N x N

# ----------------------------------------------------------------------------- raster
def fill_evenodd(contours, N=N, pad=3):
    """Even-odd fill of closed contours into an N x N boolean grid, aspect preserved."""
    pts = [p for c in contours for p in c]
    if len(pts) < 3:
        return np.zeros((N, N), bool), (0.0, 0.0)
    a = np.asarray(pts, float)
    x0, y0 = a[:, 0].min(), a[:, 1].min()
    x1, y1 = a[:, 0].max(), a[:, 1].max()
    w, h = max(x1 - x0, 1e-9), max(y1 - y0, 1e-9)
    span = N - 2 * pad
    s = span / max(w, h)
    ox = (N - w * s) / 2.0
    oy = (N - h * s) / 2.0

    gy, gx = np.mgrid[0:N, 0:N]
    px = gx + 0.5
    py = gy + 0.5
    inside = np.zeros((N, N), bool)
    for c in contours:
        if len(c) < 3:
            continue
        arr = np.asarray(c, float)
        ax = (arr[:, 0] - x0) * s + ox
        ay = (arr[:, 1] - y0) * s + oy
        bx = np.roll(ax, -1)
        by = np.roll(ay, -1)
        for k in range(len(arr)):
            if ay[k] == by[k]:
                continue
            cond = (ay[k] > py) != (by[k] > py)
            if not cond.any():
                continue
            xint = ax[k] + (py - ay[k]) * (bx[k] - ax[k]) / (by[k] - ay[k])
            inside ^= cond & (px < xint)
    return inside, (s, ox, oy)


def bez(p0, p1, p2, p3, n=14):
    t = np.linspace(0.0, 1.0, n + 1)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3


def pen_to_contours(pen):
    """Convert a RecordingPen value stream into closed contours."""
    contours, cur, start = [], [], None
    for op, args in pen.value:
        if op == "moveTo":
            if len(cur) > 1:
                contours.append(cur)
            start = args[0]
            cur = [start]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "curveTo":
            p0 = cur[-1] if cur else start
            pts = bez(p0, args[0], args[1], args[2])
            cur.extend(tuple(p) for p in pts[1:])
        elif op == "qCurveTo":
            pts = list(args)
            if pts[-1] is None:      # TrueType implied on-curve
                pts = pts[:-1]
            p0 = cur[-1] if cur else start
            for i in range(len(pts) - 1):
                c1 = pts[i]
                c2 = pts[i + 1] if i + 1 == len(pts) - 1 else ((pts[i][0] + pts[i + 1][0]) / 2.0,
                                                              (pts[i][1] + pts[i + 1][1]) / 2.0)
                end = pts[i + 1]
                cp = bez(p0, (2 / 3 * c1[0] + 1 / 3 * p0[0], 2 / 3 * c1[1] + 1 / 3 * p0[1]),
                         (2 / 3 * c1[0] + 1 / 3 * end[0], 2 / 3 * c1[1] + 1 / 3 * end[1]), end, 10)
                cur.extend(tuple(p) for p in cp[1:])
                p0 = end
        elif op == "closePath":
            if len(cur) > 1:
                cur.append(cur[0])
            if len(cur) > 1:
                contours.append(cur)
            cur = []
    if len(cur) > 1:
        contours.append(cur)
    return contours


def pdf_drawing_contours(dr):
    contours, cur = [], []
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
            cur.extend(tuple(p) for p in bez((p1.x, p1.y), (p2.x, p2.y), (p3.x, p3.y), (p4.x, p4.y))[1:])
        elif op == "re":
            r = it[1]
            if len(cur) > 1:
                contours.append(cur)
            cur = []
            contours.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)])
    if len(cur) > 1:
        contours.append(cur)
    return contours


# ------------------------------------------------------------------- reference templates
FONTS = [
    ("times.ttf", "Times"), ("timesi.ttf", "Times-It"), ("timesbd.ttf", "Times-Bd"),
    ("timesbi.ttf", "Times-BdIt"), ("cambria.ttc", "Cambria"), ("cambriai.ttf", "Cambria-It"),
    ("cambriab.ttf", "Cambria-Bd"), ("symbol.ttf", "Symbol"), ("MTExtra.ttf", "MTExtra"),
    ("euclid.ttf", "Euclid"), ("euclidi.ttf", "Euclid-It"), ("euclidb.ttf", "Euclid-Bd"),
]

RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x370, 0x3FF), (0x2000, 0x22FF), (0x2A00, 0x2AFF)]


def build_templates():
    cache = os.path.join(OUT, "cet2021_templates.pkl")
    if os.path.exists(cache):
        with open(cache, "rb") as fh:
            return pickle.load(fh)
    templates = []
    for fname, label in FONTS:
        path = os.path.join(WIN, fname)
        if not os.path.exists(path):
            continue
        faces = TTCollection(path).fonts if path.lower().endswith(".ttc") else [TTFont(path)]
        for face_i, font in enumerate(faces):
            if fname == "cambria.ttc" and face_i == 1:
                label_i = "CambriaMath"
            else:
                label_i = label
            try:
                cmap = font.getBestCmap()
                gs = font.getGlyphSet()
            except Exception:
                continue
            if not cmap:
                continue
            for cp, gname in cmap.items():
                if not any(lo <= cp <= hi for lo, hi in RANGES):
                    continue
                try:
                    pen = RecordingPen()
                    gs[gname].draw(pen)
                    cont = pen_to_contours(pen)
                    if not cont:
                        continue
                    m, _ = fill_evenodd(cont)
                    if m.sum() < 3:
                        continue
                except Exception:
                    continue
                templates.append({"font": label_i, "cp": cp, "char": chr(cp), "mask": m})
    with open(cache, "wb") as fh:
        pickle.dump(templates, fh)
    return templates


TEMPLATES = build_templates()
print("templates:", len(TEMPLATES))


# ------------------------------------------------------------------------- page glyphs
def glyph_boxes(page, rect, pxpt=8.0):
    """Connected ink components on the band, merged into glyph candidates."""
    pix = page.get_pixmap(clip=rect, dpi=int(72 * pxpt), colorspace=fitz.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = img < 160
    lab, n = ndimage.label(ink, structure=np.ones((3, 3), int))
    if n == 0:
        return [], ink, pxpt

    sc = pxpt  # px per pt
    boxes = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        boxes.append([xs.min(), ys.min(), xs.max() + 1, ys.max() + 1])

    # union-find merge: strongly x-overlapping components stacked vertically = one glyph
    parent = list(range(len(boxes)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            ox = min(a[2], b[2]) - max(a[0], b[0])
            if ox <= 0:
                continue
            wmin = min(a[2] - a[0], b[2] - b[0])
            if ox < 0.7 * wmin:
                continue
            gap = max(a[1], b[1]) - min(a[3], b[3])
            if gap > 2.5 * sc:      # >2.5 pt vertical gap -> different glyphs
                continue
            union(i, j)

    groups = {}
    for i in range(len(boxes)):
        groups.setdefault(find(i), []).append(boxes[i])

    out = []
    for gid, bs in groups.items():
        x0 = min(b[0] for b in bs)
        y0 = min(b[1] for b in bs)
        x1 = max(b[2] for b in bs)
        y1 = max(b[3] for b in bs)
        sub = np.zeros((y1 - y0, x1 - x0), bool)
        for b in bs:
            sub[b[1] - y0:b[3] - y0, b[0] - x0:b[2] - x0] |= (ink[b[1]:b[3], b[0]:b[2]])
        out.append({"x0": rect.x0 + x0 / sc, "y0": rect.y0 + y0 / sc,
                    "x1": rect.x0 + x1 / sc, "y1": rect.y0 + y1 / sc, "mask": sub})
    out.sort(key=lambda g: (g["x0"]))
    return out, ink, sc


def match(mask, topk=5):
    m, _ = fill_evenodd([], N=N)  # placeholder
    # normalise the extracted bitmap the same way (bbox-fit into N x N)
    ys, xs = np.where(mask)
    h, w = mask.shape
    span = N - 6
    s = span / max(w, h)
    grid = np.zeros((N, N), bool)
    nn = max(1, int(round(h * s)))
    mm = max(1, int(round(w * s)))
    ys2 = (np.arange(nn) * (h / nn)).astype(int).clip(0, h - 1)
    xs2 = (np.arange(mm) * (w / mm)).astype(int).clip(0, w - 1)
    small = mask[np.ix_(ys2, xs2)]
    oy = (N - nn) // 2
    ox = (N - mm) // 2
    grid[oy:oy + nn, ox:ox + mm] = small

    scores = []
    gsum = grid.sum()
    for t in TEMPLATES:
        tm = t["mask"]
        inter = np.logical_and(grid, tm).sum()
        union = gsum + tm.sum() - inter
        if union:
            scores.append((inter / union, t["font"], t["char"], t["cp"]))
    scores.sort(key=lambda z: -z[0])
    return scores[:topk]


BANDS = {
    "eq1": (1, 84.0, 682.0, 300.0, 706.0),
    "eq2": (1, 84.0, 724.0, 324.0, 750.0),
    "eq3": (2, 84.0, 113.0, 356.0, 142.0),
    "eq4": (2, 84.0, 254.0, 319.0, 286.0),
    "eq5": (2, 84.0, 289.0, 291.0, 318.0),
}

for tag, (pno, x0, y0, x1, y1) in BANDS.items():
    page = doc_page = fitz.open(SRC)[pno]
    rect = fitz.Rect(x0, y0, x1, y1)
    gl, ink, sc = glyph_boxes(page, rect)
    lines = ["### %s  page %d  band x[%.0f,%.0f] y[%.0f,%.0f]  %d glyph candidates" % (tag, pno + 1, x0, x1, y0, y1, len(gl))]
    for i, g in enumerate(gl):
        tops = match(g["mask"])
        best = tops[0]
        lines.append("g%-3d x=%7.2f..%7.2f y=%7.2f..%7.2f  w=%5.2f h=%5.2f | BEST %-11s %r IoU=%.3f | alt: %s"
                     % (i, g["x0"], g["x1"], g["y0"], g["y1"], g["x1"] - g["x0"], g["y1"] - g["y0"],
                        best[1], best[2], best[0],
                        ", ".join("%s%r%.2f" % (t[1][:6], t[2], t[0]) for t in tops[1:4])))
    with open(os.path.join(OUT, "cet2021_ocr_%s.txt" % tag), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(tag, len(gl), "glyph candidates")
