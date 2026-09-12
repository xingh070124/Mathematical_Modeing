"""Dump the RAW MathML of selected display formulas and check terminology.

Purpose: the mechanical MathML->LaTeX converter can hide structure (e.g. a doubled
'=' or a wrong symbol). This script prints the untouched publisher MathML for the
equations that matter, so the LaTeX in foods9111577_equations.txt can be audited
against what MDPI/PMC actually deposited.

Also greps the XML for slab/thickness terminology (H_0, H(t)) to test whether the
paper ever poses the model on a thickness domain.
"""
import os
import re
import xml.etree.ElementTree as ET

REF = os.path.dirname(os.path.abspath(__file__))
XML = os.path.join(REF, "foods9111577_europepmc.xml")

WANT = {"(1)", "(3)", "(5)", "(8)", "(9)", "(10)", "(11)", "(12)", "(13)",
        "(15)", "(16)", "(24)", "(25)", "(26)", "(27)", "(28)", "(29)", "(31)"}
MML = "{http://www.w3.org/1998/Math/MathML}"


OUT = os.path.join(REF, "foods9111577_rawmathml_dump.txt")


def main():
    import io
    import sys as _s
    _s.stdout = io.TextIOWrapper(open(OUT, "wb"), encoding="utf-8", errors="replace")
    print("=" * 78)
    print("RAW MathML for selected display formulas")
    print("=" * 78)
    raw = open(XML, encoding="utf-8").read()
    root = ET.fromstring(raw)
    for el in root.iter():
        if el.tag.split("}")[-1] != "disp-formula":
            continue
        lab = (el.findtext("label") or "").strip()
        if lab not in WANT:
            continue
        print("\n" + "-" * 78)
        print("EQUATION %s -- raw deposited MathML:" % lab)
        print(ET.tostring(el, encoding="unicode"))

    print("\n\n" + "=" * 78)
    print("TERMINOLOGY CHECK")
    print("=" * 78)
    for pat in ["thickness", "slab", "H_0", "H(t)", "plate", "cylinder",
                "sphere", "spherical", "R_0", "geometr"]:
        hits = [m.start() for m in re.finditer(re.escape(pat), raw, re.I)]
        print("%-12s %d hit(s)" % (pat, len(hits)))
    # show the context of slab/thickness if present
    for pat in ["thickness", "slab"]:
        for m in re.finditer(re.escape(pat), raw, re.I):
            s = max(0, m.start() - 260)
            frag = re.sub(r"<[^>]+>", " ", raw[s:m.start() + 260])
            print("\n[%s] ...%s..." % (pat, re.sub(r"\s+", " ", frag)))

    print("\n\n" + "=" * 78)
    print("ALPHA / SHRINKAGE SENTENCES")
    print("=" * 78)
    for m in re.finditer(r"ideal shrinkage|shrinkage factor|rigid solid|"
                         r"alpha|α", raw):
        s = max(0, m.start() - 320)
        frag = re.sub(r"<[^>]+>", " ", raw[s:m.start() + 320])
        print("\n...%s..." % re.sub(r"\s+", " ", frag))


if __name__ == "__main__":
    main()
