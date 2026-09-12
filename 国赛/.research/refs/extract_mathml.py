"""Extract MathML display formulas from a Europe PMC / JATS full-text XML and
convert them to LaTeX verbatim.

Input : .research/refs/foods9111577_europepmc.xml   (PMC7692062, DOI 10.3390/foods9111577)
Output: .research/refs/foods9111577_equations.txt

Pure-stdlib. No network. The conversion is mechanical element->LaTeX; it does not
"reconstruct" anything, so the printed output is a faithful transcription of the
publisher's MathML.
"""
import re
import sys
import xml.etree.ElementTree as ET

XML = r".research/refs/foods9111577_europepmc.xml"
OUT = r".research/refs/foods9111577_equations.txt"

MML = "{http://www.w3.org/1998/Math/MathML}"

BOLD_CMD = {
    "bold": r"\mathbf",
    "bold-italic": r"\boldsymbol",
    "italic": r"\mathit",
    "normal": r"\mathrm",
}


def tag(el):
    return el.tag.split("}")[-1] if isinstance(el.tag, str) else ""


def conv(el):
    """Recursively convert a MathML node to a LaTeX string."""
    t = tag(el)
    kids = list(el)
    text = (el.text or "").strip()

    if t == "math":
        return "".join(conv(k) for k in kids)

    if t in ("mrow", "mstyle", "mphantom", "mpadded"):
        return "".join(conv(k) for k in kids)

    if t == "mi":
        s = text
        variant = el.get("mathvariant")
        # single-letter identifiers are italic by convention; leave greek/other alone
        if variant in BOLD_CMD and variant != "italic":
            return BOLD_CMD[variant] + "{" + s + "}"
        return s

    if t == "mn":
        return text

    if t == "mtext":
        return r"\text{" + text + "}"

    if t == "mo":
        s = text
        # stretchy fence handling is done by mfenced; here just normalise
        return s

    if t == "mspace":
        return " "

    if t == "mfrac":
        num, den = (conv(k) for k in kids[:2])
        return r"\frac{" + num + "}{" + den + "}"

    if t == "msup":
        base_el, sup_el = kids[0], kids[1]
        base = conv(base_el)
        sup = conv(sup_el)
        # empty base + degree sign  ->  ^\circ
        if tag(base_el) == "mrow" and not list(base_el) and not (base_el.text or "").strip():
            base = ""
        if sup == "\u2218":
            sup = r"\circ"
        if not base:
            return "{}^" + ("{" + sup + "}" if len(sup) > 1 else sup)
        return base + "^" + ("{" + sup + "}" if len(sup) > 1 else sup)

    if t == "msub":
        base = conv(kids[0])
        sub = conv(kids[1])
        return base + "_" + ("{" + sub + "}" if len(sub) > 1 else sub)

    if t == "msubsup":
        base = conv(kids[0])
        sub = conv(kids[1])
        sup = conv(kids[2])
        return (base + "_" + ("{" + sub + "}" if len(sub) > 1 else sub)
                + "^" + ("{" + sup + "}" if len(sup) > 1 else sup))

    if t == "mfenced":
        op = el.get("open", "(")
        cl = el.get("close", ")")
        inner = "".join(conv(k) for k in kids)
        return r"\left" + op + inner + r"\right" + cl

    if t == "msqrt":
        return r"\sqrt{" + "".join(conv(k) for k in kids) + "}"

    if t == "mroot":
        return (r"\sqrt[" + conv(kids[1]) + "]{" + conv(kids[0]) + "}")

    if t == "mover":
        base = conv(kids[0])
        over = conv(kids[1])
        if over in ("\u2192", "\u00af", "-"):
            sym = {"\u2192": r"\rightarrow", "\u00af": r"\bar", "-": r"\bar"}[over]
            if sym == r"\bar":
                return r"\bar{" + base + "}"
            return base + r"\rightarrow"
        return base + "^{" + over + "}"

    if t == "munder":
        return conv(kids[0]) + "_{" + conv(kids[1]) + "}"

    if t == "munderover":
        return (conv(kids[0]) + "_{" + conv(kids[1]) + "}^{" + conv(kids[2]) + "}")

    if t == "mtable":
        rows = []
        for tr in kids:
            rows.append(" & ".join("".join(conv(c) for c in tr) for tr in tr))
        return r"\begin{array}{l}" + r" \\ ".join(rows) + r"\end{array}"

    if t == "semantics":
        return conv(kids[0])

    if t in ("annotation", "annotation-xml"):
        return ""

    # unknown: recurse so nothing is silently dropped
    return "".join(conv(k) for k in kids)


def tidy(s):
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace(" = = ", " = ").replace("=  =", "= =")
    s = re.sub(r"\\left\s*", r"\\left", s)
    s = re.sub(r"\\right\s*", r"\\right", s)
    s = re.sub(r"\s+([,;])", r"\1", s)
    return s


def strip_ns(root):
    for el in root.iter():
        if isinstance(el.tag, str) and el.tag.startswith("{"):
            el.tag = el.tag.split("}", 1)[1]


def main():
    tree = ET.parse(XML)
    root = tree.getroot()

    lines = []
    lines.append("# Equations extracted verbatim from Europe PMC full-text XML")
    lines.append("# source file : .research/refs/foods9111577_europepmc.xml")
    lines.append("# record      : PMC7692062 / PMID 33143274 / DOI 10.3390/foods9111577")
    lines.append("# title       : A Non-Isothermal Moving-Boundary Model for Continuous")
    lines.append("#               and Intermittent Drying of Pears (Adrover, Venditti, Brasiello, Foods 2020)")
    lines.append("")

    n = 0
    for el in root.iter():
        if tag(el) in ("disp-formula", "inline-formula"):
            if tag(el) == "inline-formula":
                continue
            label = ""
            maths = []
            for c in el:
                if tag(c) == "label":
                    label = (c.text or "").strip()
                elif tag(c) == "math":
                    maths.append(conv(c))
            if not maths:
                continue
            n += 1
            latex = tidy("".join(maths))
            lines.append("--- " + (label or "(no label)"))
            lines.append(latex)
            lines.append("")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("display formulas found:", n)
    print("written:", OUT)


if __name__ == "__main__":
    main()
