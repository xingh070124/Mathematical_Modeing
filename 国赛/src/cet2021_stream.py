# Dump raw content stream of page 2 to see how the display equations are encoded.
import fitz, re

SRC = r"docs/09_CET_NonIsothermal_MovingBoundary_FoodDrying_2021.pdf"
doc = fitz.open(SRC)
page = doc[1]  # page 2 (contains eqs 1 and 2)

raw = page.read_contents().decode("latin-1")
with open(r"outputs/cet2021_page2_contentstream.txt", "w", encoding="utf-8") as fh:
    fh.write(raw)
print("content stream bytes:", len(raw))

# Count operator usage
ops = re.findall(r"(?m)(?:^|\s)(BT|ET|Tj|TJ|Tf|re|m|l|c|f|W|d0|d1|Do|BI|sh)\b", raw)
from collections import Counter
print(Counter(ops).most_common())

# List font resource switches in order
for m in re.finditer(r"/(C2_0|T1_0|TT\d+)\s+([\d.]+)\s+Tf", raw):
    print("  Tf", m.group(1), m.group(2), "at byte", m.start())
