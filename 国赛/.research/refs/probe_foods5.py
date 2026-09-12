import fitz, io
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
txt = " ".join(" ".join(p.get_text("text").split()) for p in doc)
i = txt.find("4.1. The Isothermal Approach")
open(r".research/refs/foods_sec41b.txt","w",encoding="utf-8",newline="\n").write(txt[i:i+9000])
print("ok")
