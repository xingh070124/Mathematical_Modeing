"""Structural test: which display formulas contain an EM SPACE (U+2003) inside
<mo>? MDPI appears to use an em space as a line-break marker inside a flattened
mrow. If the em space occurs exactly in the equations that print a doubled '=',
that identifies it as the break marker rather than a stray relation.
"""
import os
import re
import unicodedata

REF = os.path.dirname(os.path.abspath(__file__))
XML = os.path.join(REF, "foods9111577_europepmc.xml")
OUT = os.path.join(REF, "foods9111577_emspace.txt")
import io
import sys as _s
_s.stdout = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8", errors="replace")
raw = open(XML, encoding="utf-8").read()

SPACES = {
    "\u2002": "EN SPACE",
    "\u2003": "EM SPACE",
    "\u2009": "THIN SPACE",
    "\u200a": "HAIR SPACE",
    "\u00a0": "NO-BREAK SPACE",
}

# split into display formulas
forms = re.findall(r"<disp-formula.*?</disp-formula>", raw, re.S)
print("display formulas in XML: %d" % len(forms))
print()
for f in forms:
    lab = re.search(r"<label>(.*?)</label>", f)
    lab = lab.group(1) if lab else "?"
    found = {}
    for ch, name in SPACES.items():
        n = f.count(">" + ch + "<")
        if n:
            found[name] = n
    if found:
        # show the immediate neighbourhood of the em space
        ctx = ""
        for m in re.finditer(">\u2003<", f):
            s = max(0, m.start() - 220)
            ctx += "      ..." + re.sub(r"<[^>]+>", "|", f[s:m.start() + 220]) + "\n"
        print("EQ %-6s %s" % (lab, found))
        if ctx:
            print(ctx)
print()
print("total <mo> </mo> (em space, U+2003):", raw.count(">\u2003<"))
print("total double equals '==':", raw.count("<mo>=</mo><mo>\u2003</mo><mo>=</mo>"))
