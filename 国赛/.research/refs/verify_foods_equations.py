"""Independent re-check of the Foods 2020 (PMC7692062) equation extraction.

1. Re-extracts every <disp-formula> from the Europe PMC JATS/MathML XML using the
   same mechanical MathML->LaTeX converter as extract_mathml.py, writing a recheck
   file, then diffs it against the previously produced foods9111577_equations.txt.
2. Dumps the full prose of Section 3 (and 2) with display formulas inline in
   document order, so equations can be read together with the sentences that
   define the domain, alpha(c_w), and D_eff.

Pure stdlib. No network.
"""
import difflib
import os
import sys
import xml.etree.ElementTree as ET

REF = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, REF)
import extract_mathml as em  # noqa: E402

XML = os.path.join(REF, "foods9111577_europepmc.xml")
OLD = os.path.join(REF, "foods9111577_equations.txt")
NEW = os.path.join(REF, "foods9111577_equations_recheck.txt")
PROSE = os.path.join(REF, "foods9111577_sec2_3_prose.txt")

tag = em.tag


def render(el):
    """Document-order plain text for an element, with formulas rendered."""
    out = []

    def walk(node):
        t = tag(node)
        if t in ("disp-formula", "inline-formula"):
            label = ""
            maths = []
            for c in node:
                if tag(c) == "label":
                    label = (c.text or "").strip()
                elif tag(c) == "math":
                    maths.append(em.conv(c))
            tex = em.tidy("".join(maths))
            if t == "disp-formula":
                out.append("\n\n  [EQ %s] %s\n\n" % (label or "?", tex))
            else:
                out.append("$%s$" % tex)
            if node.tail:
                out.append(node.tail)
            return
        if t in ("graphic", "table-wrap", "fig"):
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


def main():
    tree = ET.parse(XML)
    root = tree.getroot()

    # ---- pass 1: mechanical re-extraction, diff vs previous artefact ----
    lines = [
        "# Equations extracted verbatim from Europe PMC full-text XML",
        "# source file : .research/refs/foods9111577_europepmc.xml",
        "# record      : PMC7692062 / PMID 33143274 / DOI 10.3390/foods9111577",
        "# title       : A Non-Isothermal Moving-Boundary Model for Continuous",
        "#               and Intermittent Drying of Pears (Adrover, Venditti, Brasiello, Foods 2020)",
        "",
    ]
    n = 0
    for el in root.iter():
        if tag(el) != "disp-formula":
            continue
        label, maths = "", []
        for c in el:
            if tag(c) == "label":
                label = (c.text or "").strip()
            elif tag(c) == "math":
                maths.append(em.conv(c))
        if not maths:
            continue
        n += 1
        lines.append("--- " + (label or "(no label)"))
        lines.append(em.tidy("".join(maths)))
        lines.append("")
    with open(NEW, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("re-extracted display formulas:", n)

    old = open(OLD, encoding="utf-8").read().splitlines()
    new = open(NEW, encoding="utf-8").read().splitlines()
    diff = list(difflib.unified_diff(old, new, "existing", "recheck", lineterm="", n=0))
    print("DIFF existing vs recheck: %d hunk line(s)" % len(diff))
    for d in diff:
        print("   " + d)

    # ---- pass 2: prose of sections 2 and 3 with formulas inline ----
    body = root.find(".//body")
    keep = []
    for sec in body.findall("sec"):
        title = (sec.findtext("title") or "").strip()
        if title.startswith(("2.", "3.")):
            keep.append(sec)

    with open(PROSE, "w", encoding="utf-8") as f:
        for sec in keep:
            def dump(s, depth=0):
                ttl = (s.findtext("title") or "").strip()
                if ttl:
                    f.write("\n\n" + "#" * (2 + depth) + " " + ttl + "\n")
                for c in s:
                    if tag(c) == "title":
                        continue
                    if tag(c) == "sec":
                        dump(c, depth + 1)
                    elif tag(c) in ("p", "list", "list-item", "note"):
                        f.write(render(c).strip() + "\n\n")
                    elif tag(c) == "disp-formula":
                        f.write("\n  [EQ %s] %s\n\n"
                                % ((c.findtext("label") or "?").strip(),
                                   em.tidy("".join(em.conv(m) for m in c.findall("math")))))
            dump(sec)
    print("prose written:", PROSE)


if __name__ == "__main__":
    main()
