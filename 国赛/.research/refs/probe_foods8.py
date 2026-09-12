import fitz, re
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
raw = " ".join(" ".join(p.get_text("text").split()) for p in doc)
txt = "".join(ch if (ch.isprintable() or ch in "\n\t") else " " for ch in raw)
out=[]
for key in ["2.01", "1.5488", "Nu(Tav", "Sh(Tav"]:
    for m in re.finditer(re.escape(key), txt):
        a=max(0,m.start()-200); b=min(len(txt), m.end()+300)
        out.append("### "+key+" ###\n"+txt[a:b]+"\n")
open(r".research/refs/foods_appA.txt","w",encoding="utf-8",newline="\n").write("\n".join(out))
print("ok")
