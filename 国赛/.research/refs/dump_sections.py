"""Dump model sections of Foods 2020 (PMC7692062) as readable prose with
LaTeX display equations inline. Handles JATS mixed content (text + tail).
"""
import io
import xml.etree.ElementTree as ET

from extract_mathml import conv, tag, tidy

XML = r".research/refs/foods9111577_europepmc.xml"
OUT = r".research/refs/foods9111577_sections.txt"

WANT = [
    "sec3-foods-09-01577",
    "sec3dot1-foods-09-01577",
    "sec3dot2-foods-09-01577",
    "sec3dot3-foods-09-01577",
    "sec4dot3-foods-09-01577",
]


def render(el, out):
    t = tag(el)

    if t == "disp-formula":
        maths = "".join(conv(c) for c in el if tag(c) == "math")
        label = ""
        for c in el:
            if tag(c) == "label":
                label = (c.text or "").strip()
        out.write("\n\n    [" + (label or "?") + "]  " + tidy(maths) + "\n")
        return

    if t == "inline-formula":
        maths = "".join(conv(c) for c in el if tag(c) == "math")
        out.write("$" + tidy(maths) + "$")
        return

    if t == "title":
        out.write("\n\n### " + "".join(el.itertext()).strip() + "\n\n")
        return

    if t == "label":
        return

    if el.text:
        out.write(el.text)
    for c in el:
        render(c, out)
        if c.tail:
            out.write(c.tail)


def main():
    root = ET.parse(XML).getroot()
    out = io.StringIO()
    for s in root.iter():
        if tag(s) == "sec" and s.get("id") in WANT:
            render(s, out)
    txt = out.getvalue()
    open(OUT, "w", encoding="utf-8").write(txt)
    print("bytes:", len(txt))
    print(OUT)


if __name__ == "__main__":
    main()
