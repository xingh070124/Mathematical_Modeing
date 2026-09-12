import fitz, re
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
raw = " ".join(" ".join(p.get_text("text").split()) for p in doc)
txt = "".join(ch if (ch.isprintable() or ch in "\n\t") else " " for ch in raw)
i = txt.find("4.2. The Estimate")
seg = txt[i:i+5400]
seg = re.sub(r"(\()\s*(\d{1,2})\s*(\))", r"\n[\2] ", seg)
open(r".research/refs/foods_sec42.txt","w",encoding="utf-8",newline="\n").write(seg)
print("ok", len(seg))
