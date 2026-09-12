import fitz, re, io
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
txt = "\n".join(p.get_text("text") for p in doc)
out = io.StringIO()
for m in re.finditer(r"\(\s*2[3-9]\s*\)|\(\s*3[01]\s*\)", txt):
    a=max(0,m.start()-300); b=min(len(txt), m.end()+140)
    seg = txt[a:b].replace("\n"," | ")
    out.write("=== " + m.group().strip() + " ===\n" + seg + "\n\n")
open(r".research/refs/foods_pdf_eq_context.txt","w",encoding="utf-8").write(out.getvalue())
print("ok")
