# Is the equation area on page 2 covered by vector drawings (outlines) rather than text?
import fitz

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)
page = doc[1]

# equation region on page 2: after "read as:" (y~667) up to beyond "(2)" (y~732)
x0, y0, x1, y1 = 80.0, 670.0, 525.0, 740.0
clip = fitz.Rect(x0, y0, x1, y1)
print("equation band:", clip)

words = page.get_text("words", clip=clip)
print("\nTEXT words found in band:", len(words))
for wd in words:
    print("   ", wd[:5])

drs = page.get_drawings()
inside = [d for d in drs if fitz.Rect(d["rect"]).intersects(clip)]
print("\nVECTOR drawings intersecting band:", len(inside))
tot_items = sum(len(d["items"]) for d in inside)
print("total path items in those drawings:", tot_items)

# how much of the band is covered by vector ink?
cover = fitz.Rect()
for d in inside:
    cover |= fitz.Rect(d["rect"])
print("union bbox of vector ink in band:", cover)

# and the "(1)" / "(2)" labels
print("\nwords near labels:")
for wd in page.get_text("words"):
    if 680 < wd[1] < 740 and wd[0] > 500:
        print("   ", wd[:5])
