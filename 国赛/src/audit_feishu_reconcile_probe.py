"""
AUDIT: is src/feishu_reconcile.py's ALLOW list swallowing numbers that ought to
carry a registry source?

Reports, for model/建模方式对比.md:
  (1) the totals under the ORIGINAL allow-list;
  (2) every literal that is ALLOWed *and* is also registry-backed (i.e. could have
      been matched) -- these are the ones the allow-list is hiding;
  (3) a TIGHTENED allow-list (definitional constants only: problem-statement
      parameters, structural section/equation numbers, pure integers used as
      counts) and the resulting mismatch list.

Run: python src/audit_feishu_reconcile_probe.py
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter, defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, "model", "建模方式对比.md")
REG = os.path.join(ROOT, "outputs", "registry_feishu.csv")

NUM = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?(?![\w])")

# ---- TIGHT allow-list: only quantities GIVEN by the problem statement or the
#      cited document, plus section/equation reference numbers.  Deliberately
#      excludes everything that is an answer the report computed.
TIGHT = {
    # 附录2 / 题面 parameters
    0.36, 820.0, 2600.0, 25.0, 0.02, 2.55, 28.0, 0.89, 0.15, 8e-9, 8.0e-7,
    # 附录3 / 附录4 coefficients (as printed in the problem)
    650.0, 128.0, 1450.0, 2736.0, 0.21, 0.38, 1850.0, 2150.0, 760.0, 90.0,
    0.12, 0.20, 2.4e-3, 4.2e-4, 3850.0, 0.45, 0.30,
    # 附件1 / 文献 facts quoted verbatim
    13.3, 0.016, 0.4, 0.18, 0.011, 2020.0, 118.0, 128.0, 42.0, 2.0,
    # 阈值 from feishu.md §6.3 (quoted, not computed)
    1e-5, 5e-5, 1e-6, 1e-4,
    # pure definitional maths constants explicitly written as a formula basis
    0.5, 1.0, 2.0, 0.25, 0.75, 3.0, 4.0,
    # structural numbers: section / equation / appendix / table indices
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 24, 26, 30, 36, 40, 41, 42, 48, 49, 50, 55, 56, 57, 58, 59, 60,
    61, 62, 63, 64, 65, 70, 71, 100, 404, 627,
    # grid / algorithm settings actually used by the run
    200.0, 400.0, 800.0, 1600.0, 3200.0, 150.0, 300.0, 50.0, 150.0,
    0.0625, 0.015625, 0.1, 0.0768, 0.169,
    # C values in the property table (problem-statement operating range)
    0.50, 1.00,
}


def load_registry():
    vals = []
    with open(REG, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                vals.append((row["id"], float(row["value"]), row["quantity"]))
            except (ValueError, KeyError):
                pass
    return vals


def close(a, b, rel):
    if b == 0:
        return abs(a) < 1e-12
    return abs(a - b) / abs(b) <= rel


def main():
    reg = load_registry()
    text = open(DOC, encoding="utf-8").read()
    text = text.replace("\u2212", "-").replace("\uff0d", "-")

    # --- reproduce the ORIGINAL allow list by importing the module's literal ---
    sys.path.insert(0, os.path.join(ROOT, "src"))
    import feishu_reconcile as FR  # noqa: E402

    orig_allow = set()
    for t in FR.ALLOW:
        try:
            v = float(t)
        except ValueError:
            continue
        orig_allow.add(v)
        orig_allow.add(abs(v))
    orig_allow_abs = {abs(v) for v in orig_allow}

    print("=" * 78)
    print("PART 1 -- reproduce the original reconcile verdicts")
    print("=" * 78)
    rows = []
    for m in NUM.finditer(text):
        tok = m.group(0)
        v = float(tok)
        if v in orig_allow or abs(v) in orig_allow_abs:
            st = "ALLOW"
            rid = ""
        else:
            hit = None
            for rid_, rv, q in reg:
                if close(v, rv, 1e-2) or (rv != 0 and close(v, rv, 2e-2)):
                    hit = (rid_, rv, q)
                    break
            if hit:
                st = "MATCH" if abs(v - hit[1]) <= abs(hit[1]) * 1e-12 else "ROUNDED"
                rid = hit[0]
            else:
                st = "NO_SOURCE"
                rid = ""
        rows.append((tok, st, rid))
    c = Counter(r[1] for r in rows)
    print("total literals: %d" % len(rows))
    for k in ("MATCH", "ROUNDED", "ALLOW", "NO_SOURCE"):
        print("  %-10s %d" % (k, c.get(k, 0)))
    print("report claims: 509 literals, 0 unmatched")

    print()
    print("=" * 78)
    print("PART 2 -- literals BOTH allow-listed AND registry-backed")
    print("        (the allow-list is shadowing a real source)")
    print("=" * 78)
    shadow = defaultdict(list)
    n_shadow = 0
    for tok, st, rid in rows:
        if st != "ALLOW":
            continue
        v = float(tok)
        hit = None
        for rid_, rv, q in reg:
            if close(v, rv, 1e-2) or (rv != 0 and close(v, rv, 2e-2)):
                hit = (rid_, rv, q)
                break
        if hit is not None and abs(v) > 9.999:
            shadow[tok].append((hit[0], hit[2]))
            n_shadow += 1
    print("allow-listed literals that ALSO have a registry row within 1%%: %d" % n_shadow)
    print("(integers <=9 excluded as structural)")
    print()
    print("%-18s %-8s %s" % ("literal", "count", "registry id / quantity"))
    for tok, lst in sorted(shadow.items(), key=lambda kv: -len(kv[1])):
        ids = sorted({x[0] for x in lst})
        print("%-18s %-8d %s" % (tok, len(lst), ", ".join(ids[:6]) +
                                 (" ..." if len(ids) > 6 else "")))

    print()
    print("=" * 78)
    print("PART 3 -- TIGHTENED allow-list")
    print("=" * 78)
    unmatched = []
    for m in NUM.finditer(text):
        tok = m.group(0)
        v = float(tok)
        if v in TIGHT or abs(v) in TIGHT:
            continue
        hit = None
        for rid_, rv, q in reg:
            if close(v, rv, 1e-2) or (rv != 0 and close(v, rv, 2e-2)):
                hit = (rid_, rv, q)
                break
        if hit is None:
            unmatched.append(tok)
    print("unmatched under the tight allow-list: %d distinct %d"
          % (len(unmatched), len(set(unmatched))))
    for tok, n in Counter(unmatched).most_common():
        print("   %-18s x%d" % (tok, n))

    print()
    print("=" * 78)
    print("PART 4 -- qualitative check: does an ALLOWED literal get used as a RESULT?")
    print("=" * 78)
    checkpoints = [
        ("0.489463", "c_k/A_k ratio -- a RESULT (F14)"),
        ("11.52", "reconstruction error -- a RESULT (F16)"),
        ("70.8475", "the doc scheme error -- a RESULT (F20_M50)"),
        ("3.4936501265", "headline agreement -- a RESULT (F40)"),
        ("1.4019076018", "max|dT| app3-app2 -- a RESULT (F60)"),
        ("0.13834689131", "max|dC| app3-app2 -- a RESULT (F61)"),
        ("4.80", "F41 timing -- report §2.5 quotes it, §1.8 says not quotable"),
        ("1.2658221367", "c_1 -- a RESULT (F12)"),
        ("0.96381405", "reconstruction -- a RESULT (F1C_100)"),
        ("127.00", "divergence time -- a RESULT (F30_M200)"),
        ("6.65961", "exact_cn error -- a RESULT (F22_M400_exact)"),
    ]
    for lit, what in checkpoints:
        v = float(lit)
        in_allow = v in orig_allow or abs(v) in orig_allow_abs
        hit = None
        for rid_, rv, q in reg:
            if close(v, rv, 1e-2) or (rv != 0 and close(v, rv, 2e-2)):
                hit = (rid_, rv, q)
                break
        print("  %-16s allow=%-5s registry=%-18s %s"
              % (lit, in_allow, hit[0] if hit else "-", what))


if __name__ == "__main__":
    main()
