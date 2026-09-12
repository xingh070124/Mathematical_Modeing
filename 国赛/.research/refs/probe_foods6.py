import fitz, io, re
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
txt = " ".join(" ".join(p.get_text("text").split()) for p in doc)
i = txt.find("4.2. The Estimate")
seg = txt[i:i+5200]
seg = re.sub(r"(\()\s*(\d{1,2})\s*(\))", r"\n[\2] ", seg)
open(r".research/refs/foods_sec42.txt","w",encoding="utf-8",newline="\n").write(seg)
print("ok")
