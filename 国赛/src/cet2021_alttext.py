# Look for any recoverable alternate representation of the equations:
# marked-content ActualText, structure tree, embedded files, OLE objects.
import fitz, re

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)

lines = []
def w(s=""):
    lines.append(str(s))

w("PDF metadata: %s" % doc.metadata)
w("has /StructTreeRoot: %s" % bool(doc.xref_get_key(doc.pdf_catalog(), "StructTreeRoot")))
w("embedded files (doc.embfile_count): %s" % doc.embfile_count())

for pno in range(doc.page_count):
    raw = doc[pno].read_contents().decode("latin-1")
    w("\n--- page %d: %d bytes" % (pno + 1, len(raw)))
    for pat in ("ActualText", "Alt", "MCID", "BMC", "BDC", "EMC"):
        n = raw.count(pat)
        if n:
            w("   contains %s x%d" % (pat, n))

# any object anywhere mentioning ActualText or an OLE/Equation object?
hits = 0
for xref in range(1, doc.xref_length()):
    try:
        obj = doc.xref_object(xref, compressed=False)
    except Exception:
        continue
    if "ActualText" in obj or "Equation" in obj or "OLE" in obj:
        w("xref %d mentions ActualText/Equation/OLE: %s" % (xref, obj[:300]))
        hits += 1
w("total suspicious xrefs: %d" % hits)

with open(r"outputs/cet2021_alttext.txt", "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("done;", len(lines), "lines -> outputs/cet2021_alttext.txt")
