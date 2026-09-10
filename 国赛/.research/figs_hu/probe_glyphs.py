# Probe the font-private (PUA) glyphs in the 胡众欢 (2020) PDF.
# Question: is U+E065 the nabla operator and U+E785 the partial-derivative operator?
# Method: topological. A nabla (inverted triangle outline) encloses ZERO holes.
#         A partial-derivative sign encloses EXACTLY ONE hole.
# This discriminator is font-independent, so it settles the identity without
# needing to look at the rendered page.
#
# Input : docs/基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf   (read-only)
# Output: .research/figs_hu/probe_glyphs.txt
import io, os
import fitz
import numpy as np

PDF = r'D:\github\myself\Mathematical_Modeing\国赛\docs\基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf'
OUT = r'D:\github\myself\Mathematical_Modeing\国赛\.research\figs_hu\probe_glyphs.txt'

PUA_NABLA_GUESS = '\ue065'   # hypothesised nabla
PUA_PARTIAL_GUESS = '\ue785'  # hypothesised partial

buf = io.StringIO()
def w(s=''):
    buf.write(str(s) + '\n')


def holes_in(ink):
    """Count background regions fully enclosed by ink.

    ink: 2-D bool array, True = glyph ink. Border of the array is background.
    Returns (number_of_enclosed_holes, total_ink_pixels).
    """
    h, wd = ink.shape
    if ink.sum() == 0:
        return None, 0
    # Flood fill background from the border; anything background not reached is a hole.
    from collections import deque
    bg = ~ink
    seen = np.zeros_like(bg, dtype=bool)
    dq = deque()
    for x in range(h):
        for y in (0, wd - 1):
            if bg[x, y] and not seen[x, y]:
                seen[x, y] = True; dq.append((x, y))
    for y in range(wd):
        for x in (0, h - 1):
            if bg[x, y] and not seen[x, y]:
                seen[x, y] = True; dq.append((x, y))
    while dq:
        x, y = dq.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < h and 0 <= ny < wd and bg[nx, ny] and not seen[nx, ny]:
                seen[nx, ny] = True; dq.append((nx, ny))
    holes = bg & ~seen
    # merge hole pixels into connected regions, count those of non-trivial size
    lab = np.zeros_like(holes, dtype=np.int32)
    nlab = 0
    counts = {}
    for i in range(h):
        for j in range(wd):
            if holes[i, j] and lab[i, j] == 0:
                nlab += 1
                q = deque([(i, j)]); lab[i, j] = nlab; c = 0
                while q:
                    x, y = q.popleft(); c += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < h and 0 <= ny < wd and holes[nx, ny] and lab[nx, ny] == 0:
                            lab[nx, ny] = nlab; q.append((nx, ny))
                counts[nlab] = c
    real = [k for k, c in counts.items() if c >= 9]   # ignore 1-2px speckle
    return len(real), int(ink.sum())


def probe(doc, page_no, dpi=600, max_glyphs=6):
    page = doc[page_no]
    zoom = dpi / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    raw = page.get_text('rawdict')
    results = []
    for blk in raw['blocks']:
        if blk['type'] != 0:
            continue
        for line in blk['lines']:
            for span in line['spans']:
                for ch in span['chars']:
                    c = ch['c']
                    if c not in (PUA_NABLA_GUESS, PUA_PARTIAL_GUESS):
                        continue
                    x0, y0, x1, y1 = ch['bbox']
                    # generous crop: glyph box inflated by 25 %
                    padx = 0.25 * max(1.0, x1 - x0)
                    pady = 0.25 * max(1.0, y1 - y0)
                    X0 = max(0, int((x0 - padx) * zoom)); X1 = min(pix.width, int((x1 + padx) * zoom) + 1)
                    Y0 = max(0, int((y0 - pady) * zoom)); Y1 = min(pix.height, int((y1 + pady) * zoom) + 1)
                    crop = img[Y0:Y1, X0:X1]
                    if crop.size == 0:
                        continue
                    ink = crop < 160
                    n, npx = holes_in(ink)
                    if npx == 0:
                        continue
                    results.append((c, span['font'], round(x0, 1), round(y0, 1), n, npx,
                                    int(ink.shape[0]), int(ink.shape[1])))
                    if len(results) >= max_glyphs:
                        return results
    return results


doc = fitz.open(PDF)
w('PROBE OF FONT-PRIVATE (PUA) GLYPHS IN 胡众欢 (2020)')
w('PDF: ' + os.path.basename(PDF))
w('Discriminator: enclosed-hole count.  nabla -> 0 holes ; partial -> 1 hole.')
w('Ink threshold: grey < 160, raster 600 dpi. Holes smaller than 9 px ignored.')
w()
for pno in (2, 3, 4):           # PDF pages 3, 4, 5  (= equation pages)
    for tag, guess in ((PUA_NABLA_GUESS, 'U+E065'), (PUA_PARTIAL_GUESS, 'U+E785')):
        res = probe(doc, pno, max_glyphs=6)
        # filter to the tag we want
        sel = [r for r in res if r[0] == tag]
        w('--- page %d (PDF page index %d) : %s ---' % (pno + 1, pno, guess))
        if not sel:
            w('   no samples')
        for r in sel:
            w('   font=%-18s at (%.1f,%.1f)  holes=%d  ink_px=%d  box=%dx%d'
              % (r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        w()
        break_after = True
    # also print the other one explicitly
    for tag, guess in ((PUA_PARTIAL_GUESS, 'U+E785'),):
        sel = [r for r in probe(doc, pno, max_glyphs=8) if r[0] == tag]
        w('--- page %d : %s ---' % (pno + 1, guess))
        if not sel:
            w('   no samples')
        for r in sel:
            w('   font=%-18s at (%.1f,%.1f)  holes=%d  ink_px=%d  box=%dx%d'
              % (r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        w()

w()
w('INTERPRETATION RULE (fixed before running):')
w('  U+E065 with holes==0 in all samples  => it is the nabla operator  (gradient/divergence).')
w('  U+E785 with holes==1 in all samples  => it is the partial-derivative operator.')
w('  Any mixture of hole counts within one codepoint falsifies the guess.')

io.open(OUT, 'w', encoding='utf-8').write(buf.getvalue())
print('written', OUT)
