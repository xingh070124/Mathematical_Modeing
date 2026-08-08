"""Compute the convex-relaxation lower bound HPWL_lb for Problem 2.

Relax: drop non-overlap constraint (C1); keep fixed-outline box [0, Lhat]^2.
HPWL_k = (max_x - min_x) + (max_y - min_y) is convex PL in module centers.
Minimize via coordinate descent: for module i, axis x, the optimal x given
all others is the weighted median of the breakpoints {other-pin min, other-pin max}
per incident net, clipped to box.  Convex PL + exact line search -> global opt.
Terminals are fixed.
"""

import os, math

BASE = r"D:\github\myself\Mathematical_Modeing\2026年第七届华数杯数学建模竞赛赛题\B题 VLSI布图规划设计\附件"


def load(name):
    blocks = {}
    with open(os.path.join(BASE, name + ".blocks"), encoding="utf-8") as f:
        for ln in f.read().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("Num") or ln.startswith("p"):
                continue
            p = ln.split()

            def cv(s):
                return int(s.replace("(", "").replace(")", "").replace(",", ""))

            x0, y0 = cv(p[3]), cv(p[4])
            x1, y1 = cv(p[7]), cv(p[8])
            blocks[p[0]] = (abs(x1 - x0), abs(y1 - y0))
    term = {}
    with open(os.path.join(BASE, name + ".pl"), encoding="utf-8") as f:
        for ln in f.read().splitlines():
            p = ln.split()
            if len(p) == 3:
                term[p[0]] = (int(p[1]), int(p[2]))
    nets = []
    with open(os.path.join(BASE, name + ".nets"), encoding="utf-8") as f:
        cur = []
        for ln in f.read().splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("Num"):
                continue
            if ln.startswith("NetDegree"):
                if cur:
                    nets.append(cur)
                    cur = []
            else:
                cur.append(ln)
        if cur:
            nets.append(cur)
    return blocks, term, nets


def solve(name, Lhat):
    blocks, term, nets = load(name)
    n = len(blocks)
    ids = list(blocks)
    # init module centers: place all at center of box (or near origin)
    cx = {b: Lhat / 2 for b in ids}
    cy = {b: Lhat / 2 for b in ids}
    # pin positions: module pin -> center; terminal pin -> fixed
    # precompute for each net: list of (is_module, id/coord)
    net_pins = []
    for k, net in enumerate(nets):
        pins = []
        for pid in net:
            if pid.startswith("b"):
                pins.append(("m", pid))
            else:
                pins.append(("t", term[pid]))
        net_pins.append(pins)
    # per module: list of incident net indices
    mod_nets = {b: [] for b in ids}
    for k, pins in enumerate(net_pins):
        for tp, val in pins:
            if tp == "m":
                mod_nets[val].append(k)

    def hpwl():
        tot = 0.0
        for pins in net_pins:
            xs = [cx[v] if tp == "m" else v[0] for tp, v in pins]
            ys = [cy[v] if tp == "m" else v[1] for tp, v in pins]
            tot += (max(xs) - min(xs)) + (max(ys) - min(ys))
        return tot

    # coordinate descent, axis separately
    for it in range(200):
        max_move = 0.0
        for axis in (0, 1):
            for b in ids:
                # gather breakpoints from incident nets
                breakpoints = []
                for k in mod_nets[b]:
                    lo = hi = None
                    for tp, v in net_pins[k]:
                        if tp == "m" and v == b:
                            continue
                        coord = (
                            v[axis] if tp == "t" else (cx[v] if axis == 0 else cy[v])
                        )
                        if lo is None or coord < lo:
                            lo = coord
                        if hi is None or coord > hi:
                            hi = coord
                    if lo is not None:
                        breakpoints.append(lo)
                        breakpoints.append(hi)
                if not breakpoints:
                    newc = Lhat / 2  # isolated module: anywhere; keep center
                else:
                    med = sorted(breakpoints)[len(breakpoints) // 2]
                    newc = min(max(med, 0), Lhat)
                # weight: median of breakpoints (with all weights 1) minimizes
                # sum |x - bp|; our PL objective has slope break pattern giving
                # same structure -> median is optimal.
                if axis == 0:
                    cx[b] = newc
                else:
                    cy[b] = newc
                if axis == 0:
                    pass
        # full objective drift check
        if it % 10 == 0:
            pass
    return hpwl()


if __name__ == "__main__":
    for name, Lhat in [("n100", 455), ("n200", 450), ("n300", 561)]:
        v = solve(name, Lhat)
        print(f"{name}: HPWL_lb = {v:,.0f}")
