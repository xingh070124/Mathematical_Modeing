"""Reconstruct the printed 2-D layout of display equations from PDF word boxes.

For a flattened 1-D text extraction, a two-line display is indistinguishable from a
one-line display with a doubled relation. Word bounding boxes resolve it: if the two
'=' glyphs sit at different y (different baseline), the equation is a TWO-LINE display
and the doubled '=' is a line-break artifact. If they share a baseline, the equation is
printed on ONE line with a genuinely doubled '='.

Output: .research/refs/foods9111577_layout.txt
"""
import io
import os
import sys

import fitz

REF = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(REF, "foods9111577_epmc.pdf")
OUT = os.path.join(REF, "foods9111577_layout.txt")
sys.stdout = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8", errors="replace")

doc = fitz.open(PDF)

REGIONS = [
    (4, 430, 620, "Equation (1)-(2) region, page 4"),
    (10, 300, 560, "Equations (25)-(29) region, page 10"),
]


def show(pno, y0, y1, title):
    page = doc[pno - 1]
    words = page.get_text("words")     # x0,y0,x1,y1,word,block,line,word_no
    sel = [w for w in words if y0 <= w[1] <= y1]
    sel.sort(key=lambda w: (round(w[1], 1), w[0]))
    print("\n" + "=" * 78)
    print("%s  (page %d, y %.0f-%.0f)" % (title, pno, y0, y1))
    print("=" * 78)
    cur_y = None
    for w in sel:
        y = round(w[1], 1)
        if cur_y is None or abs(y - cur_y) > 2.0:
            print("\n[baseline y=%7.2f] " % y)
            cur_y = y
        print("   x=%7.2f..%7.2f  %r" % (w[0], w[2], w[4]))
    # explicit test on '=' glyphs
    eqs = [w for w in sel if w[4] == "="]
    print("\n--'=' glyphs in region: %d" % len(eqs))
    for w in sorted(eqs, key=lambda w: (w[1], w[0])):
        print("   y=%7.2f x=%7.2f..%7.2f" % (w[1], w[0], w[2]))
    print("-- two '=' on same baseline? %s"
          % (len({round(w[1], 1) for w in eqs}) < len(eqs)))


for pno, y0, y1, title in REGIONS:
    show(pno, y0, y1, title)
