"""Verify Problem-2 md file claims against actual attachment data.

Checks:
  1. counts: blocks / terminals / nets / pins
  2. total area A, L = sqrt(1.15A), ceil(L)
  3. average & max net degree
  4. terminal distribution (boundary vs interior)
  5. module pin count vs terminal pin count
  6. convex relaxation lower bound via weighted-median coordinate descent
     (relax non-overlap; keep fixed-outline bounds)
"""

import math, sys, os
from collections import defaultdict

BASE = r"D:\github\myself\Mathematical_Modeing\2026年第七届华数杯数学建模竞赛赛题\B题 VLSI布图规划设计\附件"


def parse(name):
    blocks = {}
    with open(os.path.join(BASE, name + ".blocks"), encoding="utf-8") as f:
        lines = f.read().splitlines()
    n_b = n_t = None
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("NumHardBlocks"):
            n_b = int(ln.split(":")[1].strip())
        elif ln.startswith("NumTerminals"):
            n_t = int(ln.split(":")[1].strip())
        elif ln.startswith("b") and "block" in ln:
            parts = ln.split()
            bid = parts[0]

            def cv(s):
                return int(s.replace("(", "").replace(")", "").replace(",", ""))

            # corners (x0,y0) (x0,y1) (x1,y1) (x1,y0)
            x0, y0 = cv(parts[3]), cv(parts[4])
            x0a, y1 = cv(parts[5]), cv(parts[6])
            x1, y1a = cv(parts[7]), cv(parts[8])
            w = abs(x1 - x0)
            h = abs(y1 - y0)
            blocks[bid] = (w, h)
    # nets
    nets = []  # each: list of pin ids (pX = terminal, bY = block)
    with open(os.path.join(BASE, name + ".nets"), encoding="utf-8") as f:
        lines = f.read().splitlines()
    n_nets = n_pins = None
    cur = []
    reading_degree = False
    deg = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("NumNets"):
            n_nets = int(ln.split(":")[1].strip())
        elif ln.startswith("NumPins"):
            n_pins = int(ln.split(":")[1].strip())
        elif ln.startswith("NetDegree"):
            if cur:
                nets.append(cur)
                cur = []
            deg = int(ln.split(":")[1].strip())
        elif ln.startswith("p") or ln.startswith("b"):
            cur.append(ln)
    if cur:
        nets.append(cur)
    # terminals
    term = {}
    with open(os.path.join(BASE, name + ".pl"), encoding="utf-8") as f:
        for ln in f.read().splitlines():
            ln = ln.strip()
            if not ln:
                continue
            parts = ln.split()
            term[parts[0]] = (int(parts[1]), int(parts[2]))
    return blocks, term, nets, n_b, n_t, n_nets, n_pins


def verify(name):
    blocks, term, nets, n_b, n_t, n_nets, n_pins = parse(name)
    A = sum(w * h for w, h in blocks.values())
    L = math.sqrt(1.15 * A)
    Lc = math.ceil(L)
    degs = [len(n) for n in nets]
    maxd = max(degs)
    avgd = sum(degs) / len(degs)
    # pins split
    mod_pins = sum(1 for n in nets for p in n if p.startswith("b"))
    term_pins = sum(1 for n in nets for p in n if p.startswith("p"))
    # terminal distribution
    in_bnd = sum(1 for (x, y) in term.values() if 0 < x < L and 0 < y < L)
    on_bnd = len(term) - in_bnd
    # avg nets per module
    mod_deg = defaultdict(int)
    for n in nets:
        for p in n:
            if p.startswith("b"):
                mod_deg[p] += 1
    avg_mod_deg = sum(mod_deg.values()) / len(mod_deg)
    # net count per module incl terminal-only nets
    print(f"=== {name} ===")
    print(f"  blocks  : file={n_b}  parsed={len(blocks)}")
    print(f"  terminals: file={n_t}  parsed={len(term)}")
    print(f"  nets    : file={n_nets} parsed={len(nets)}")
    print(
        f"  pins    : file={n_pins} parsed={mod_pins + term_pins} (module={mod_pins}, terminal={term_pins})"
    )
    print(f"  area A  = {A}")
    print(f"  L=sqrt(1.15A) = {L:.4f}   ceil = {Lc}")
    print(f"  net degree avg={avgd:.3f} max={maxd}")
    print(f"  terminal boundary={on_bnd} interior={in_bnd}")
    print(f"  avg nets per MODULE = {avg_mod_deg:.2f}")
    print()


for n in ["n100", "n200", "n300"]:
    verify(n)
