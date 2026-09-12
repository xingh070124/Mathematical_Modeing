# Print aspect-correct ASCII pictures of named glyph candidates, with their top-3 matches,
# so the deciding glyphs can be verified by eye rather than trusted from IoU alone.
import os, pickle, sys
import numpy as np
import fitz

OUT = "outputs"
N = 48
PXPT = 32.0
sys.path.insert(0, "src")

# reuse the exact extraction used by cet2021_ocr2
import importlib.util
spec = importlib.util.spec_from_file_location("ocr2", "src/cet2021_ocr2.py")
# ocr2 runs a full pass on import; instead re-implement the small pieces here.
with open(os.path.join(OUT, "cet2021_templates2.pkl"), "rb") as fh:
    TEMPLATES = pickle.load(fh)
TM = np.array([t["mask"] for t in TEMPLATES])
TM_SUM = TM.sum(axis=(1, 2))


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
    union = g + TM_SUM - inter
    iou = np.where(union > 0, inter / np.maximum(union, 1), 0.0)
    order = np.argsort(-iou)[:3]
    return [(float(iou[k]), TEMPLATES[k]["font"], TEMPLATES[k]["char"]) for k in order]


def art(mask, maxw=56, maxh=26):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return ["<empty>"]
    sub = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = sub.shape
    step = max(1, int(np.ceil(max(w / maxw, h / maxh))))
    return ["".join("#" if sub[r:r + step, c:c + step].any() else "."
                    for c in range(0, w, step)) for r in range(0, h, step)]


def glyph_candidates(page, rect):
    from scipy import ndimage
    pix = page.get_pixmap(clip=rect, dpi=int(72 * PXPT), colorspace=fitz.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = img < 170
    lab, n = ndimage.label(ink, structure=np.ones((3, 3), int))
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
            if ox <= 0 or ox < 0.85 * max(a[2] - a[0], b[2] - b[0]):
                continue
            if max(a[1], b[1]) - min(a[3], b[3]) > 4.0 * PXPT:
                continue
            ra, rb = find(i), find(j)
            if ra != rb:
                parent[rb] = ra
    groups = {}
    for i in range(len(boxes)):
        groups.setdefault(find(i), []).append(boxes[i])
    out = []
    for bs in groups.values():
        x0 = min(b[0] for b in bs); y0 = min(b[1] for b in bs)
        x1 = max(b[2] for b in bs); y1 = max(b[3] for b in bs)
        sub = np.zeros((y1 - y0, x1 - x0), bool)
        for b in bs:
            sub[b[1] - y0:b[3] - y0, b[0] - x0:b[2] - x0] |= ink[b[1]:b[3], b[0]:b[2]]
        out.append({"x0": rect.x0 + x0 / PXPT, "y0": rect.y0 + y0 / PXPT,
                    "x1": rect.x0 + x1 / PXPT, "y1": rect.y0 + y1 / PXPT, "mask": sub})
    out.sort(key=lambda g: g["x0"])
    return out


BANDS = {
    "eq1": (1, 84.0, 682.0, 300.0, 706.0),
    "eq2": (1, 84.0, 724.0, 324.0, 750.0),
    "eq3": (2, 84.0, 113.0, 356.0, 142.0),
    "eq4": (2, 84.0, 254.0, 319.0, 286.0),
    "eq5": (2, 84.0, 289.0, 291.0, 318.0),
    "eq11": (3, 84.0, 186.0, 244.0, 205.0),
}

# which glyph ids to show, per band; "*" = all
WANT = {"eq1": [3, 16, 19, 29, 30, 39, 41, 42, 44, 46],
        "eq2": [19, 20, 21, 23, 24, 26, 27, 29, 38, 39, 40, 42],
        "eq3": [14, 17, 47, 48, 52, 53, 54],
        "eq4": [3, 18, 25, 27, 29, 40, 43, 44, 55],
        "eq5": [1, 2, 12, 19, 25, 27, 33, 35],
        "eq11": "*"}

doc = fitz.open(r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf")
sel = sys.argv[1] if len(sys.argv) > 1 else "eq1"
pno, x0, y0, x1, y1 = BANDS[sel]
gl = glyph_candidates(doc[pno], fitz.Rect(x0, y0, x1, y1))
want = WANT.get(sel, "*")
lines = ["### %s : %d candidates" % (sel, len(gl))]
for i, g in enumerate(gl):
    if want != "*" and i not in want:
        continue
    s = score(normalise_mask(g["mask"]))
    lines.append("--- g%d x=%.2f..%.2f y=%.2f..%.2f w=%.2f h=%.2f" %
                 (i, g["x0"], g["x1"], g["y0"], g["y1"], g["x1"] - g["x0"], g["y1"] - g["y0"]))
    lines.append("    top3: " + "  ".join("%s %r %.3f" % (t[1], t[2], t[0]) for t in s))
    lines.extend("    " + a for a in art(g["mask"]))
out = os.path.join(OUT, "cet2021_verify_%s.txt" % sel)
with open(out, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote", out, len(lines), "lines")
