import fitz
doc = fitz.open(r".research/refs/CET2187033_cetjournal.pdf")
print("pages:", doc.page_count)
for pno in range(doc.page_count):
    pg = doc[pno]
    txt = pg.get_text("text")
    drw = pg.get_drawings()
    print(f"--- page {pno+1}: textchars={len(txt)} drawings={len(drw)}")
# dump raw text of page 2 (models) and page 3
for pno in (1, 2):
    pg = doc[pno]
    print("="*30, "PAGE", pno+1, "raw text repr")
    print(repr(pg.get_text("text"))[:3000])
