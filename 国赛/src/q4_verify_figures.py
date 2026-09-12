# -*- coding: utf-8 -*-
"""
q4_verify_figures.py -- 问题四图件的三道渲染门总核验 (nature-figure 契约).

  1. 面板对齐门  —— 由出图时写下的 *.alignment.json 复算最大对齐偏差 (pt)
  2. 字形门      —— audit_pdf_text.py   最低字号 5 pt
  3. 碰撞门      —— audit_figure_collisions.py

退出码: 0 全部通过; 1 有任一门未通过.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGD = os.path.join(ROOT, "paper", "figures")
SKILL = os.path.expanduser(r"~\.dsh\research-skills\nature-figure\scripts")
FIGURES = ["fig_q4_schematic", "fig_q4_shrink", "fig_q4_results", "fig_q4_verify"]


def run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def alignment_stats(name):
    """读 alignment.json, 复算最大对齐偏差与分组数."""
    path = os.path.join(FIGD, f"{name}.alignment.json")
    if not os.path.exists(path):
        return None, "NO JSON", 0
    with open(path, encoding="utf-8") as f:
        rep = json.load(f)
    if not rep.get("auditable"):
        return None, rep.get("verdict", "NOT AUDITABLE"), 0
    layout = rep["layout"]
    P = {p["id"]: p["bbox_pt"] for p in layout["panels"]}
    worst = {"v": 0.0, "where": "-", "n": 0}

    def chk(vals, label):
        s = max(vals) - min(vals)
        worst["n"] += 1
        if s > worst["v"]:
            worst["v"], worst["where"] = s, label

    for g in layout.get("row_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        chk([P[i][3] for i in ids], f"row-top[{g['id']}]")
        chk([P[i][1] for i in ids], f"row-bottom[{g['id']}]")
        chk([P[i][3] - P[i][1] for i in ids], f"row-height[{g['id']}]")
    for g in layout.get("column_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        chk([P[i][0] for i in ids], f"col-left[{g['id']}]")
        chk([P[i][2] for i in ids], f"col-right[{g['id']}]")
    coord = {"left": 0, "bottom": 1, "right": 2, "top": 3}
    for g in layout.get("boundary_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        chk([P[i][coord[g["edge"]]] for i in ids], f"shared-{g['edge']}[{g['id']}]")
    return worst, rep.get("verdict", "?"), len(P)


def main():
    print("=" * 74)
    print("问题四图件渲染门核验 (q4_verify_figures.py)")
    print("=" * 74)
    fails = []
    for name in FIGURES:
        pdf = os.path.join(FIGD, f"{name}.pdf")
        print(f"\n[{name}]")
        if not os.path.exists(pdf):
            print("  !! PDF 不存在")
            fails.append(f"{name}: no pdf")
            continue
        # 1 对齐门
        w, verdict, npan = alignment_stats(name)
        if w is None:
            print(f"  对齐门: {verdict}")
            if verdict != "NOT APPLICABLE":
                fails.append(f"{name}: alignment {verdict}")
        else:
            ok = w["v"] <= 1.5
            print(f"  对齐门: {'PASS' if ok else 'FAIL'}  "
                  f"最大偏差 {w['v']:.4f} pt (容差 1.5) @ {w['where']}; "
                  f"比较 {w['n']} 组, {npan} 面板")
            if not ok:
                fails.append(f"{name}: alignment {w['v']:.3f} pt")
        # 2 字形门
        rc, out = run([sys.executable, os.path.join(SKILL, "audit_pdf_text.py"),
                       pdf, "--min-pt", "5"])
        lo = [l for l in out.splitlines() if "FAIL" in l or "fail" in l]
        print(f"  字形门: {'PASS' if rc == 0 else 'FAIL'}  "
              f"{lo[0].strip()[:70] if lo else out.strip().splitlines()[-1][:70]}")
        if rc != 0:
            fails.append(f"{name}: glyph floor")
        # 3 碰撞门
        jout = os.path.join(FIGD, f"{name}.collision-audit.json")
        rc, out = run([sys.executable,
                       os.path.join(SKILL, "audit_figure_collisions.py"), pdf,
                       "--json-out", jout,
                       "--overlay-pdf", os.path.join(FIGD,
                                                     f"{name}.collision-audit.pdf")])
        try:
            with open(jout, encoding="utf-8") as f:
                cj = json.load(f)
            s = cj.get("summary", {})
            print(f"  碰撞门: {cj.get('verdict')} (fail={s.get('fail')}, "
                  f"warn={s.get('warn')}, rc={rc})")
            if rc == 1:
                for f_ in cj.get("findings", []):
                    if f_.get("severity") == "FAIL":
                        print(f"      FAIL: {f_.get('kind')} "
                              f"{str(f_.get('detail', ''))[:90]}")
                fails.append(f"{name}: collision FAIL")
        except Exception as e:
            print(f"  碰撞门: 无法读取 JSON ({e}); rc={rc}")
            fails.append(f"{name}: collision not auditable")
    print("\n" + "=" * 74)
    if fails:
        print("未通过: " + "; ".join(fails))
        return 1
    print("全部图件通过三道渲染门 [OK]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
