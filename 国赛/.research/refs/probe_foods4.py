import fitz, io, re
doc = fitz.open(r".research/refs/foods9111577_epmc.pdf")
txt = " ".join(" ".join(p.get_text("text").split()) for p in doc)
out = io.StringIO()
for key in ["V∞", "V0", "2/3"]:
    pass
i = txt.find("4.1. The Isothermal Approach")
out.write("### SECTION 4.1\n" + txt[i:i+4200] + "\n\n")
j = txt.find("V∞/V0")
out.write("### around V-inf/V-0 ###\n" + txt[max(0,j-1500):j+1500] + "\n")
open(r".research/refs/foods_sec41.txt","w",encoding="utf-8",newline="\n").write(out.getvalue())
print("ok", len(out.getvalue()))
