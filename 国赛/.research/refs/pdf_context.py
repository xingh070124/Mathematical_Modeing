"""Print exact UTF-8 context around key equations in the Foods 2020 PDF text layer,
and audit terminology. Avoids the console-codepage mojibake."""
import os
import re

REF = os.path.dirname(os.path.abspath(__file__))
PDFTXT = os.path.join(REF, "foods9111577_pdf_textlayer.txt")
OUT = os.path.join(REF, "foods9111577_pdf_context.txt")

t = open(PDFTXT, encoding="utf-8", errors="replace").read()

with open(OUT, "w", encoding="utf-8") as f:
    for pat in [r"\(25\)", r"\(26\)", r"\(27\)", r"\(28\)", r"\(29\)",
                r"\(1\)", r"\(5\)", r"\(8\)", r"\(9\)", r"\(12\)", r"\(13\)",
                r"\(14\)", r"\(31\)"]:
        ms = list(re.finditer(pat, t))
        f.write("\n" + "=" * 76 + "\n%s  (%d hits)\n" % (pat, len(ms)) + "=" * 76 + "\n")
        for m in ms[:2]:
            s = max(0, m.start() - 900)
            frag = re.sub(r"[ \t]+", " ", t[s:m.start() + 120])
            f.write("\n--- ctx ---\n" + frag + "\n")

    f.write("\n" + "=" * 76 + "\nTERMINOLOGY in PDF text layer\n" + "=" * 76 + "\n")
    for p in ["thickness", "H(t)", "slab", "= =", "sphere", "spherical",
              "R(t)", "R\n0", "dx_b", "ideal shrinkage", "alpha"]:
        n = len(re.findall(re.escape(p), t))
        f.write("%-18s %d\n" % (p, n))

    # the two-'=' occurrences with context, to confirm the published layout
    f.write("\n--- all '= =' occurrences with context ---\n")
    for m in re.finditer(re.escape("= ="), t):
        s = max(0, m.start() - 160)
        f.write("\n>>> " + re.sub(r"\s+", " ", t[s:m.start() + 160]) + "\n")

print("written:", OUT)
