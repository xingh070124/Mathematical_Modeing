import fitz, re, io
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
print("pages:", doc.page_count)
txt = "\n".join(p.get_text("text") for p in doc)
open(r".research/refs/foods9111577_pdftext.txt","w",encoding="utf-8").write(txt)
print("chars:", len(txt))
for m in re.finditer(r"\(\s*2[4-9]\s*\)|\(\s*3[01]\s*\)", txt):
    a=max(0,m.start()-260); b=min(len(txt), m.end()+120)
    seg = txt[a:b].replace("\n"," | ")
    print("=== ", m.group().strip(), " ===")
    print(seg[-420:])
    print()
