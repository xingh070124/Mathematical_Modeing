import fitz, re, io
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
txt = "\n".join(p.get_text("text") for p in doc)
txt = "".join(ch if (ch.isprintable() or ch in "\n\t") else " " for ch in txt)
out = io.StringIO()
for m in re.finditer(r"\(\s*2[3-9]\s*\)|\(\s*3[01]\s*\)", txt):
    a=max(0,m.start()-320); b=min(len(txt), m.end()+160)
    seg = " ".join(txt[a:b].split())
    out.write("=== " + m.group().strip() + " ===\n" + seg + "\n\n")
open(r".research/refs/foods_pdf_eq_context.txt","w",encoding="utf-8",newline="\n").write(out.getvalue())
print("bytes", len(out.getvalue()))
