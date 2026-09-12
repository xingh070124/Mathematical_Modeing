import fitz, io, json
doc = fitz.open(r".research/refs/CET2187033_cetjournal.pdf")
out = io.StringIO()
for pno in range(doc.page_count):
    pg = doc[pno]
    out.write(f"===== PAGE {pno+1} =====\n")
    out.write(pg.get_text("text"))
    out.write("\n")
open(r".research/refs/CET2187033_textlayer.txt","w",encoding="utf-8").write(out.getvalue())
print("wrote textlayer", len(out.getvalue()))
# locate equation number labels and surrounding spans
for pno in range(doc.page_count):
    pg = doc[pno]
    d = pg.get_text("dict")
    for b in d["blocks"]:
        if b.get("type")!=0: continue
        for l in b["lines"]:
            s = "".join(sp["text"] for sp in l["spans"])
            if s.strip() in {"(1)","(2)","(3)","(4)","(5)","(6)","(7)"}:
                print(f"label {s.strip()} on page {pno+1} at y={l['bbox'][1]:.1f} x={l['bbox'][0]:.1f}")
