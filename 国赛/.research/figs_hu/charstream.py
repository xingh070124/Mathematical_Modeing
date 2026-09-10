# Print the raw character stream of the equation region of 胡众欢 (2020) page 3
# (PDF index 2 = printed p.119), with codepoints and x/y positions, so that the
# exact glyph sequence of equations (1) and (2) can be read off the text layer
# without any rendering. This settles whether a middle dot exists between the two
# nabla glyphs of the second viscous term of eq (2).
import io
import fitz

PDF = r'D:\github\myself\Mathematical_Modeing\国赛\docs\基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf'
OUT = r'D:\github\myself\Mathematical_Modeing\国赛\.research\figs_hu\charstream_p3.txt'
NABLA = '\ue065'
PART = '\ue785'

doc = fitz.open(PDF)
buf = io.StringIO()
def w(s=''):
    buf.write(str(s) + '\n')


def name(c):
    u = ord(c)
    if c == NABLA:
        return 'NABLA?'
    if c == PART:
        return 'PARTIAL?'
    if u == 0xB7:
        return 'MIDDOT'
    if 0xFF01 <= u <= 0xFF5E:
        return 'FW:' + chr(u - 0xFEE0)
    return c


for pno in (2, 3, 4, 5):
    page = doc[pno]
    chars = []
    for blk in page.get_text('rawdict')['blocks']:
        if blk['type'] != 0:
            continue
        for line in blk['lines']:
            for span in line['spans']:
                for ch in span['chars']:
                    x0, y0, x1, y1 = ch['bbox']
                    chars.append((round(y0, 1), round(x0, 1), ch['c'], round(y1 - y0, 1),
                                  round(x1 - x0, 1), span['size']))
    chars.sort()
    w('=' * 78)
    w('PDF page index %d (printed p.%d)  -- %d characters' % (pno, pno + 117, len(chars)))
    w('=' * 78)
    # group into visual rows: same y0 within 3 pt
    rows = []
    for c in chars:
        if rows and abs(c[0] - rows[-1][0][0]) <= 3.0:
            rows[-1].append(c)
        else:
            rows.append([c])
    for r in rows:
        r.sort(key=lambda t: t[1])
        txt = ''.join(name(t[2]) for t in r)
        # only show rows that contain an operator of interest or are equation rows
        if any(t[2] in (NABLA, PART, '\u00b7') for t in r) or '(' in txt or '＝' in txt or '=' in txt:
            w('y=%7.1f | %s' % (r[0][0], txt))
    w()

w()
w('LEGEND: NABLA? = U+E065 ; PARTIAL? = U+E785 ; MIDDOT = U+00B7 (a real middle dot,')
w('        which the text layer DOES carry where the producer typed one).')
w('Read the eq.(2) row: whatever sits between the two NABLA? glyphs in the second')
w('viscous term is the complete truth the text layer can give.')

io.open(OUT, 'w', encoding='utf-8').write(buf.getvalue())
print('written', OUT)
