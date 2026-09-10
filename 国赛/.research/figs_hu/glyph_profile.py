# Decide the identity of the two font-private glyphs U+E065 and U+E785 in 胡众欢 (2020).
#
# Discriminator: the horizontal ink-envelope width profile, correlated with the
# downward direction.
#   * A nabla (gradient) glyph is a TRIANGLE: its envelope widens monotonically
#     from the apex at the top to the base at the bottom. r = +1.
#   * A partial-derivative glyph is a rounded loop high on the glyph with a single
#     descending stroke on the right: its envelope is widest near the top and
#     narrows towards the bottom. r <= 0.
# References are rendered with the SAME pipeline from matplotlib's mathtext
# (DejaVu/STIX), so the statistic is compared like with like. The comparison is
# of the SIGN and rough magnitude of r, not of pixel-identical shapes, so
# font-style differences do not matter.
#
# Inputs : docs/基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf   (read only)
# Outputs: .research/figs_hu/glyph_profile.txt   (numbers)
#          .research/figs_hu/glyph_profile.png   (reference sheet, for a human)
import io, os
import numpy as np
import fitz

PDF = r'D:\github\myself\Mathematical_Modeing\国赛\docs\基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf'
OUTTXT = r'D:\github\myself\Mathematical_Modeing\国赛\.research\figs_hu\glyph_profile.txt'
OUTPNG = r'D:\github\myself\Mathematical_Modeing\国赛\.research\figs_hu\glyph_profile.png'

PUA = {'U+E065': '\ue065', 'U+E785': '\ue785'}

buf = io.StringIO()
def w(s=''):
    buf.write(str(s) + '\n')


def tight(ink):
    ys, xs = np.where(ink)
    if len(ys) == 0:
        return None
    return ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def profile_r(ink):
    """Correlation of the horizontal envelope width with the downward direction."""
    t = tight(ink)
    if t is None or t.shape[0] < 4:
        return None
    widths = []
    for row in t:
        idx = np.where(row)[0]
        widths.append(0.0 if len(idx) == 0 else float(idx.max() - idx.min() + 1))
    widths = np.array(widths)
    n = len(widths)
    y = np.arange(n, dtype=float)
    if widths.std() < 1e-9:
        return None
    r = float(np.corrcoef(y, widths)[0, 1])
    return r, n, t.shape[1], widths


def mirror_iou(ink):
    t = tight(ink)
    if t is None:
        return None
    f = t[:, ::-1]
    h = min(t.shape[0], f.shape[0]); wd = min(t.shape[1], f.shape[1])
    a = t[:h, :wd]; b = f[:h, :wd]
    inter = np.logical_and(a, b).sum(); uni = np.logical_or(a, b).sum()
    return float(inter) / float(uni) if uni else None


# ---------- references ----------
def render_ref(sym, px=400):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(2, 2), dpi=px / 2.0)
    fig.text(0.5, 0.5, sym, fontsize=120, ha='center', va='center')
    fig.canvas.draw()
    arr = np.asarray(fig.canvas.buffer_rgba())[:, :, :3]
    plt.close(fig)
    g = arr.mean(axis=2)
    ink = g < 128
    return tight(ink)


refs = {}
for name, s in (('nabla  $\\nabla$', r'$\nabla$'),
                ('partial $\\partial$', r'$\partial$'),
                ('Delta  $\\Delta$', r'$\Delta$'),
                ('delta  $\\delta$', r'$\delta$')):
    try:
        refs[name] = render_ref(s)
    except Exception as e:
        w('reference render failed for %s: %r' % (name, e))

w('REFERENCE GLYPHS (matplotlib mathtext / DejaVu)')
w('%-22s %8s %8s %8s %8s' % ('glyph', 'r(width)', 'mirrorIoU', 'h', 'w'))
for name, t in refs.items():
    r = profile_r(t)
    mi = mirror_iou(t)
    w('%-22s %8.3f %8.3f %8d %8d' % (name, r[0] if r else float('nan'),
                                     mi if mi is not None else float('nan'),
                                     t.shape[0], t.shape[1]))
w()

# ---------- glyphs from the PDF ----------
doc = fitz.open(PDF)
samples = {'U+E065': [], 'U+E785': []}
for pno in (2, 3, 4, 5):
    page = doc[pno]
    zoom = 600.0 / 72.0
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    for blk in page.get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for line in blk['lines']:
            for span in line['spans']:
                for ch in span['chars']:
                    tag = None
                    for k, v in PUA.items():
                        if ch['c'] == v:
                            tag = k
                    if tag is None:
                        continue
                    x0, y0, x1, y1 = ch['bbox']
                    pad = 0.10 * max(1.0, x1 - x0)
                    X0 = max(0, int((x0 - pad) * zoom)); X1 = min(pix.width, int((x1 + pad) * zoom) + 1)
                    Y0 = max(0, int((y0 - pad) * zoom)); Y1 = min(pix.height, int((y1 + pad) * zoom) + 1)
                    crop = img[Y0:Y1, X0:X1]
                    if crop.size == 0:
                        continue
                    t = tight(crop < 160)
                    if t is None or t.size < 100:
                        continue
                    samples[tag].append((pno + 1, span['font'], round(x0, 1), round(y0, 1), t))

w('GLYPHS MEASURED FROM THE PDF (600 dpi, ink = grey < 160)')
w('%-8s %6s %-18s %8s %8s %8s %8s' % ('code', 'page', 'font', 'r(width)', 'mirrorIoU', 'h', 'w'))
stats = {}
for tag in ('U+E065', 'U+E785'):
    rs, ms = [], []
    for (pno, font, x, y, t) in samples[tag]:
        r = profile_r(t); mi = mirror_iou(t)
        if r is None:
            continue
        rs.append(r[0]); ms.append(mi)
        w('%-8s %6d %-18s %8.3f %8.3f %8d %8d' % (tag, pno, font, r[0], mi, t.shape[0], t.shape[1]))
    stats[tag] = (rs, ms)
    w('%-8s n=%d  r(width): mean %.3f  min %.3f  max %.3f   mirrorIoU mean %.3f'
      % (tag, len(rs), np.mean(rs), np.min(rs), np.max(rs), np.mean(ms)))
    w()

w()
w('DECISION RULE (fixed before running):')
w('  r(width) > 0 and mirrorIoU high  => triangle-shaped  => nabla  => U+E065 is the')
w('                                     gradient/divergence operator.')
w('  r(width) <= 0                    => loop-high, tail-down => partial => U+E785')
w('                                     is the partial-derivative operator.')
w('  Both codes giving the same sign falsifies this discriminator.')

io.open(OUTTXT, 'w', encoding='utf-8').write(buf.getvalue())
print('written', OUTTXT)

# also save a contact sheet of the actual crops so a human can confirm at a glance
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    n = max(len(samples['U+E065']), len(samples['U+E785']))
    fig, axes = plt.subplots(2, min(n, 8), figsize=(1.4 * min(n, 8), 3.4))
    if min(n, 8) == 1:
        axes = axes.reshape(2, 1)
    for row, tag in enumerate(('U+E065', 'U+E785')):
        for col in range(min(n, 8)):
            ax = axes[row, col]
            ax.axis('off')
            if col < len(samples[tag]):
                ax.imshow(samples[tag][col][4], cmap='gray_r')
            if col == 0:
                ax.set_ylabel(tag, fontsize=8)
    fig.suptitle('left: glyphs pulled from the PDF   (rows = U+E065, U+E785)', fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPNG, dpi=140)
    print('written', OUTPNG)
except Exception as e:
    print('contact sheet skipped:', repr(e))
