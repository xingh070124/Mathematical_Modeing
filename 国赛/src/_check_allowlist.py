"""Audit the allow-list itself: which ALLOWed literals carry high precision and
therefore SHOULD have had a registry source instead of being waved through?"""
import collections
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "outputs", "reconciliation_feishu.csv")

rows = list(csv.DictReader(open(REP, encoding="utf-8-sig")))
print("counts:", dict(collections.Counter(r["status"] for r in rows)))

sus = collections.Counter()
for r in rows:
    if r["status"] != "ALLOW":
        continue
    t = r["literal"]
    mant = t.split("e")[0].split("E")[0].replace("-", "").replace(".", "")
    if len(mant) >= 6 and ("e" in t.lower() or "." in t):
        sus[t] += 1
print("\nALLOW tokens with >=6 significant digits "
      "(candidates that should be registry-backed):")
for t, n in sus.most_common():
    print("  %-20s x%d" % (t, n))
print("total suspicious:", sum(sus.values()))

# how many ALLOWed literals are integers (grids, section numbers, M values)?
ints = sum(1 for r in rows if r["status"] == "ALLOW"
           and re.fullmatch(r"-?\d+", r["literal"]))
print("\nALLOWed pure integers (grids/indices/M/geometry):", ints)
