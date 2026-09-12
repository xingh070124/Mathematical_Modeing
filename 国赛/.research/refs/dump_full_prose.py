"""Dump the FULL body prose of the Foods 2020 paper (PMC7692062) with display
formulas inline in document order, so every equation can be read together with
the sentences that define it.

Output: .research/refs/foods9111577_fulltext_prose.txt
"""
import os
import sys
import xml.etree.ElementTree as ET

REF = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REF)
import extract_mathml as em  # noqa: E402

XML = os.path.join(REF, "foods9111577_europepmc.xml")
OUT = os.path.join(REF, "foods9111577_fulltext_prose.txt")
tag = em.tag


def render(el):
    out = []

    def walk(node):
        t = tag(node)
        if t in ("disp-formula", "inline-formula"):
            label, maths = "", []
            for c in node:
                if tag(c) == "label":
                    label = (c.text or "").strip()
                elif tag(c) == "math":
                    maths.append(em.conv(c))
            tex = em.tidy("".join(maths))
            out.append(("\n\n  [EQ %s] %s\n\n" % (label or "?", tex))
                       if t == "disp-formula" else "$%s$" % tex)
            if node.tail:
                out.append(node.tail)
            return
        if t in ("graphic", "fig", "table-wrap"):
            return
        if node.text:
            out.append(node.text)
        for c in node:
            walk(c)
            if c.tail:
                out.append(c.tail)

    if el.text:
        out.append(el.text)
    for c in el:
        walk(c)
        if c.tail:
            out.append(c.tail)
    return "".join(out)


def dump(f, s, depth=0):
    ttl = (s.findtext("title") or "").strip()
    if ttl:
        f.write("\n\n" + "#" * (2 + depth) + " " + ttl + "\n")
    for c in s:
        if tag(c) == "title":
            continue
        if tag(c) == "sec":
            dump(f, c, depth + 1)
        elif tag(c) in ("p", "list", "list-item", "note"):
            f.write(render(c).strip() + "\n\n")
        elif tag(c) == "disp-formula":
            f.write("\n  [EQ %s] %s\n\n"
                    % ((c.findtext("label") or "?").strip(),
                       em.tidy("".join(em.conv(m) for m in c.findall("math")))))


def main():
    root = ET.parse(XML).getroot()
    with open(OUT, "w", encoding="utf-8") as f:
        body = root.find(".//body")
        for sec in body.findall("sec"):
            dump(f, sec)
        for app in root.findall(".//back//app"):
            dump(f, app)
    print("written:", OUT)


if __name__ == "__main__":
    main()
