# Extract text + render pages of the CET 2021 moving-boundary paper.
# Input : docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf
# Output: outputs/cet2021_page{N}_text.txt , outputs/cet2021_page{N}.png
import os
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

doc = fitz.open(SRC)
print("PyMuPDF", fitz.__doc__.split(":")[0].strip(), "pages", doc.page_count)

for i, page in enumerate(doc):
    n = i + 1
    txt = page.get_text("text")
    with open(os.path.join(OUT, f"cet2021_page{n}_text.txt"), "w", encoding="utf-8") as fh:
        fh.write(txt)
    pix = page.get_pixmap(dpi=300)
    png = os.path.join(OUT, f"cet2021_page{n}.png")
    pix.save(png)
    print(f"page {n}: text {len(txt)} chars, png {pix.width}x{pix.height}, {os.path.getsize(png)} bytes")
