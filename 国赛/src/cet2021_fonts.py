# Inspect fonts and drawing content of the model pages to recover the typeset equations.
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)

for pno in range(doc.page_count):
    page = doc[pno]
    print(f"===== page {pno+1} =====")
    dr = page.get_drawings()
    print("  drawings:", len(dr))
    for f in page.get_fonts(full=True):
        print("   font xref=%s ext=%s type=%s basefont=%s name=%s enc=%s" % (f[0], f[1], f[2], f[3], f[4], f[5]))
