# Extract the embedded Type1 font programs for the two PUA-carrying fonts and read
# their cleartext /CharStrings glyph names.
# A Type1 font keeps the glyph-name table in clear text before the eexec section,
# so if the subset preserved meaningful names (/nabla, /partialdiff, ...) the
# identity of U+E065 and U+E785 is settled without rendering anything.
import io, os, re, zlib
import fitz

PDF = r'D:\github\myself\Mathematical_Modeing\国赛\docs\基于多物理场耦合的热风干燥模型及其验证_胡众欢.pdf'
OUT = r'D:\github\myself\Mathematical_Modeing\国赛\.research\figs_hu\font_programs.txt'

buf = io.StringIO()
def w(s=''):
    buf.write(str(s) + '\n')

doc = fitz.open(PDF)

for xref, label in ((49, 'DY2+ZBUIIt-2  (carries U+E065)'),
                    (138, 'DY27+ZBUIIv-27 (carries U+E785)')):
    w('=' * 70)
    w('FONT xref %d : %s' % (xref, label))
    w('=' * 70)
    fd_obj = doc.xref_object(xref)
    m = re.search(r'/FontDescriptor (\d+) 0 R', fd_obj)
    if not m:
        w('  no FontDescriptor'); continue
    fdx = int(m.group(1))
    fdo = doc.xref_object(fdx)
    w('  FontDescriptor %d:' % fdx)
    for line in fdo.splitlines():
        w('    ' + line)
    m2 = re.search(r'/FontFile\s*(\d+) 0 R', fdo) or re.search(r'/FontFile3\s*(\d+) 0 R', fdo)
    if not m2:
        w('  NO EMBEDDED FONT PROGRAM -> cannot read glyph names from this font.')
        w()
        continue
    ffx = int(m2.group(1))
    w('  FontFile xref %d' % ffx)
    raw = doc.xref_stream(ffx)
    if raw is None:
        w('  stream unreadable'); w(); continue
    w('  raw length = %d bytes' % len(raw))
    # Type1: cleartext until 'eexec'. FontFile3 (CFF) is binary -> names differ.
    head = raw[:4000]
    try:
        txt = head.decode('latin-1')
    except Exception:
        txt = ''
    if 'eexec' in raw[:6000].decode('latin-1', 'replace'):
        cut = raw.index(b'eexec')
        clear = raw[:cut].decode('latin-1', 'replace')
        w('  Type1 cleartext header found, %d bytes before eexec.' % cut)
        w('  --- /CharStrings block (cleartext glyph names) ---')
        i = clear.find('/CharStrings')
        w(clear[i:i + 2000] if i >= 0 else '  (/CharStrings marker not found in cleartext)')
        w()
        w('  --- search for meaningful names anywhere in cleartext ---')
        for kw in ('nabla', 'partial', 'gradient', 'diff', 'Del', 'rho', 'mu', 'lambda',
                   'alpha', 'epsilon', 'sigma', 'nabla', 'partialdiff'):
            hits = [m.start() for m in re.finditer(kw, clear, re.I)]
            if hits:
                w('    %-12s : %d hits, first context: %r'
                  % (kw, len(hits), clear[max(0, hits[0] - 40):hits[0] + 40]))
    else:
        w('  No eexec -> probably CFF/TrueType. First 200 bytes hex:')
        w('  ' + raw[:200].hex())
    w()

w('NOTE: if the glyph names are sequential placeholders (/A /B /C ...), this route')
w('is also inconclusive and the identity must be settled from the rendered page.')

io.open(OUT, 'w', encoding='utf-8').write(buf.getvalue())
print('written', OUT)
