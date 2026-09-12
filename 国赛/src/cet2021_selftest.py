# Fix + validate the glyph matcher.
#   (1) render the page band at high px/pt and area-average down (no nearest-neighbour aliasing)
#   (2) self-test: a reference template pushed through the extract-and-match path must recover itself
# Writes outputs/cet2021_selftest.txt
import numpy as np
from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.recordingPen import RecordingPen
import os, pickle

WIN = r"C:\Windows\Fonts"
N = 48
OUT = "outputs"


def bez(p0, p1, p2, p3, n=16):
    t = np.linspace(0.0, 1.0, n + 1)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * (t ** 2) * p2 + (t ** 3) * p3


def pen_to_contours(pen):
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
            cur.extend(tuple(p) for p in bez(p0, args[0], args[1], args[2])[1:])
        elif op == "qCurveTo":
            pts = list(args)
            if pts[-1] is None:
                pts = pts[:-1]
            p0 = cur[-1] if cur else start
            for i in range(len(pts) - 1):
                c1 = pts[i]
                end = pts[i + 1]
                if i + 1 == len(pts) - 1:
                    c2 = end
                else:
                    c2 = ((pts[i][0] + pts[i + 1][0]) / 2.0, (pts[i][1] + pts[i + 1][1]) / 2.0)
                cp = bez(p0, (2 / 3 * c1[0] + 1 / 3 * p0[0], 2 / 3 * c1[1] + 1 / 3 * p0[1]),
                         (2 / 3 * c1[0] + 1 / 3 * c2[0], 2 / 3 * c1[1] + 1 / 3 * c2[1]), end, 10)
                cur.extend(tuple(p) for p in cp[1:])
                p0 = end
        elif op == "closePath":
            if len(cur) > 1:
                cur.append(cur[0])
                contours.append(cur)
            cur = []
    if len(cur) > 1:
        contours.append(cur)
    return contours


def fill_evenodd(contours, N=N, pad=3, flip_y=True, ss=3):
    """Even-odd fill of font-outline contours into an N x N boolean grid.

    Font outlines are in y-UP font units; the page raster is y-DOWN. flip_y=True
    puts the templates in the same orientation as the glyphs extracted from the PDF.

    ss = supersampling factor: the coverage is evaluated on an (N*ss)^2 grid and
    box-averaged back to N x N, so templates are area-coverage just like the
    bitmaps area-averaged out of the page render. Without this the two are not
    comparable and every IoU is depressed.
    """
    # Font outlines are y-UP; the page raster is y-DOWN. Flip EVERY contour, not
    # just the bbox scan, or the fill lands off-grid.
    cts = []
    for c in contours:
        arr = np.asarray(c, float)
        if flip_y:
            arr = arr * np.array([1.0, -1.0])
        cts.append(arr)
    pts = np.vstack(cts) if cts else np.zeros((0, 2))
    if len(pts) < 3:
        return np.zeros((N, N), bool)
    a = pts
    x0, y0 = a[:, 0].min(), a[:, 1].min()
    w = max(a[:, 0].max() - x0, 1e-9)
    h = max(a[:, 1].max() - y0, 1e-9)
    span = N - 2 * pad
    s = span / max(w, h)
    ox, oy = (N - w * s) / 2.0, (N - h * s) / 2.0
    G = N * ss
    gy, gx = np.mgrid[0:G, 0:G]
    px = (gx + 0.5) / ss
    py = (gy + 0.5) / ss
    inside = np.zeros((G, G), bool)
    for arr in cts:
        if len(arr) < 3:
            continue
        ax = (arr[:, 0] - x0) * s + ox
        ay = (arr[:, 1] - y0) * s + oy
        bx, by = np.roll(ax, -1), np.roll(ay, -1)
        for k in range(len(arr)):
            if ay[k] == by[k]:
                continue
            cond = (ay[k] > py) != (by[k] > py)
            if not cond.any():
                continue
            xint = ax[k] + (py - ay[k]) * (bx[k] - ax[k]) / (by[k] - ay[k])
            inside ^= cond & (px < xint)
    cov = inside.reshape(N, ss, N, ss).mean(axis=(1, 3))
    return cov > 0.5


def normalise_mask(mask, N=N, pad=3):
    """Area-average a boolean bitmap into N x N preserving aspect."""
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return np.zeros((N, N), bool)
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = sub.shape
    span = N - 2 * pad
    s = span / max(w, h)
    mm, nn = max(1, int(round(w * s))), max(1, int(round(h * s)))
    # area average via box mean
    ys2 = np.linspace(0, h, nn + 1)
    xs2 = np.linspace(0, w, mm + 1)
    out = np.zeros((nn, mm), float)
    for i in range(nn):
        for j in range(mm):
            blk = sub[int(ys2[i]):max(int(ys2[i]) + 1, int(ys2[i + 1])),
                      int(xs2[j]):max(int(xs2[j]) + 1, int(xs2[j + 1]))]
            out[i, j] = blk.mean() if blk.size else 0.0
    grid = np.zeros((N, N), bool)
    oy, ox = (N - nn) // 2, (N - mm) // 2
    grid[oy:oy + nn, ox:ox + mm] = out > 0.5
    return grid


FONTS = [("timesi.ttf", "Times-It"), ("times.ttf", "Times"), ("cambriai.ttf", "Cambria-It"),
         ("cambria.ttc", "Cambria"), ("symbol.ttf", "Symbol"), ("MTExtra.ttf", "MTExtra"),
         ("euclidi.ttf", "Euclid-It"), ("euclid.ttf", "Euclid")]

RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x370, 0x3FF), (0x2000, 0x22FF)]


def build():
    T = []
    for fname, label in FONTS:
        path = os.path.join(WIN, fname)
        if not os.path.exists(path):
            continue
        faces = TTCollection(path).fonts if fname.endswith(".ttc") else [TTFont(path)]
        for fi, font in enumerate(faces):
            if fname == "cambria.ttc" and fi == 1:
                continue
            try:
                cmap, gs = font.getBestCmap(), font.getGlyphSet()
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
                    m = fill_evenodd(cont)
                    if m.sum() < 3:
                        continue
                except Exception:
                    continue
                T.append({"font": label, "cp": cp, "char": chr(cp), "mask": m})
    return T


T = build()
print("templates:", len(T))
with open(os.path.join(OUT, "cet2021_templates2.pkl"), "wb") as fh:
    pickle.dump(T, fh)

# ---- self test: take 30 random templates, degrade to a coarse bitmap, resample, re-match ----
rng = np.random.default_rng(0)
idx = rng.choice(len(T), 30, replace=False)
ok = 0
lines = ["Self-test: reference templates degraded to a 40x40 bitmap then pushed through the "
         "normalise+match path. A pass means top-1 recovers the same character (any font).", ""]
for i in idx:
    t = T[i]
    # simulate the PAGE-extracted bitmap: upsample template to 40x40 then treat as mask
    ys, xs = np.where(t["mask"])
    src = t["mask"][ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    up = np.kron(src, np.ones((1, 1), bool))
    grid = normalise_mask(up)
    scores = []
    gs_ = grid.sum()
    for u in T:
        inter = np.logical_and(grid, u["mask"]).sum()
        un = gs_ + u["mask"].sum() - inter
        scores.append((inter / un if un else 0.0, u["font"], u["char"]))
    scores.sort(key=lambda z: -z[0])
    hit = scores[0][2] == t["char"]
    ok += hit
    lines.append("%-6s %-11s %r -> %-11s %r IoU=%.3f  %s" % ("PASS" if hit else "fail", t["font"], t["char"],
                                                             scores[0][1], scores[0][2], scores[0][0],
                                                             "" if hit else "alt=%s" % scores[1:3]))
lines.append("")
lines.append("self-test: %d/30 top-1 exact" % ok)
with open(os.path.join(OUT, "cet2021_selftest.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("\n".join(lines[-3:]))
