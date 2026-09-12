# Minimal standalone diagnostic: does the even-odd fill produce a sane mask for a known glyph?
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

N = 40


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
                c1, end = pts[i], pts[i + 1]
                c2 = end if i + 1 == len(pts) - 1 else ((pts[i][0] + pts[i + 1][0]) / 2.0,
                                                        (pts[i][1] + pts[i + 1][1]) / 2.0)
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


def fill(contours, flip_y, N=N, pad=3):
    cts = []
    for c in contours:
        arr = np.asarray(c, float)
        if flip_y:
            arr[:, 1] = -arr[:, 1]
        cts.append(arr)
    pts = np.vstack(cts)
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    w = max(pts[:, 0].max() - x0, 1e-9)
    h = max(pts[:, 1].max() - y0, 1e-9)
    span = N - 2 * pad
    s = span / max(w, h)
    ox, oy = (N - w * s) / 2.0, (N - h * s) / 2.0
    gy, gx = np.mgrid[0:N, 0:N]
    px, py = gx + 0.5, gy + 0.5
    inside = np.zeros((N, N), bool)
    for arr in cts:
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
    return inside


def art(m):
    ys, xs = np.where(m)
    if len(ys) == 0:
        return ["<EMPTY>"]
    sub = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return ["".join("#" if v else "." for v in row) for row in sub]


font = TTFont(r"C:\Windows\Fonts\times.ttf")
gs = font.getGlyphSet()
cmap = font.getBestCmap()

for ch in "Ac=il":
    pen = RecordingPen()
    gs[cmap[ord(ch)]].draw(pen)
    cont = pen_to_contours(pen)
    npts = sum(len(c) for c in cont)
    m_up, m_dn = fill(cont, False), fill(cont, True)
    print("=== %r contours=%d pts=%d ink_up=%d ink_down=%d" % (ch, len(cont), npts, m_up.sum(), m_dn.sum()))
    a_up, a_dn = art(m_up), art(m_dn)
    for i in range(max(len(a_up), len(a_dn))):
        left = a_up[i] if i < len(a_up) else ""
        right = a_dn[i] if i < len(a_dn) else ""
        print("   %-22s | %s" % (left, right))
