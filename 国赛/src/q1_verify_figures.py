# -*- coding: utf-8 -*-
r"""
问题一合并图件 (fig_q1_scheme / fig_q1_results) 的渲染门总核验.

对每张图跑齐三道门, 并给出**具体数字**:
  1. 面板对齐门 —— 由出图时写下的 *.alignment.json 复算: 用 1e-9 的极小容差把
     全部可比组都变成 finding, 再取其中最大的 metric_spread_pt 作为"最大对齐偏差".
     (默认 1.5 pt 容差下 finding 为空, 看不到具体偏了多少.)
  2. 字形门   —— nature-figure/scripts/audit_pdf_text.py --min-pt 5
  3. 碰撞门   —— nature-figure/scripts/audit_figure_collisions.py

用法: python src/q1_verify_figures.py [额外要核验的图名 ...]
退出码: 0 全部通过; 1 有任一门未通过.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGD = os.path.join(ROOT, "paper", "figures")
SKILL = r"C:\Users\极光\.dsh\research-skills\nature-figure\scripts"

FIGURES = ["fig_q1_scheme", "fig_q1_results"]


def run(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def alignment_max_deviation(name):
    """由 alignment.json 里实测的面板矩形, 复算所有可比组的最大对齐偏差 (pt).

    不直接读对齐门的 finding: 默认 1.5 pt 容差下 finding 为空, 看不到偏差具体是多少;
    而把它调成极小容差后, metric_spreads_pt 只保留 6 位小数, 也读不出浮点噪声量级的
    真实偏差. 这里按对齐门同一套判据 (行/列/共享边界/沟槽) 自行复算.
    """
    path = os.path.join(FIGD, f"{name}.alignment.json")
    with open(path, encoding="utf-8") as f:
        rep = json.load(f)
    if not rep.get("auditable"):
        return None, rep.get("verdict", "NOT AUDITABLE"), (rep.get("errors", []), "-", 0)
    layout = rep["layout"]
    P = {p["id"]: p["bbox_pt"] for p in layout["panels"]}
    state = {"worst": 0.0, "where": "-", "n": 0}

    def check(vals, label):
        s = max(vals) - min(vals)
        state["n"] += 1
        if s > state["worst"]:
            state["worst"], state["where"] = s, label

    for g in layout.get("row_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        check([P[i][3] for i in ids], f"row-top[{g['id']}]")
        check([P[i][1] for i in ids], f"row-bottom[{g['id']}]")
        check([P[i][3] - P[i][1] for i in ids], f"row-height[{g['id']}]")
        order = sorted(ids, key=lambda i: P[i][0])
        if len(order) >= 3:
            check([P[i][2] - P[i][0] for i in order], f"row-width[{g['id']}]")
            check([P[b][0] - P[a][2] for a, b in zip(order, order[1:])],
                  f"row-gutter[{g['id']}]")
    for g in layout.get("column_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        check([P[i][0] for i in ids], f"col-left[{g['id']}]")
        check([P[i][2] for i in ids], f"col-right[{g['id']}]")
        check([P[i][2] - P[i][0] for i in ids], f"col-width[{g['id']}]")
        order = sorted(ids, key=lambda i: -P[i][3])
        if len(order) >= 3:
            check([P[a][1] - P[b][3] for a, b in zip(order, order[1:])],
                  f"col-gutter[{g['id']}]")
    coord = {"left": 0, "bottom": 1, "right": 2, "top": 3}
    for g in layout.get("boundary_groups", []):
        ids = [i for i in g["panels"] if i in P]
        if len(ids) < 2:
            continue
        c = coord[g["edge"]]
        check([P[i][c] for i in ids], f"shared-{g['edge']}[{g['id']}]")

    return state["worst"], rep["verdict"], (rep["summary"], state["where"], state["n"])


def main():
    figs = FIGURES + sys.argv[1:]
    ok = True
    print(f"核验图件: {', '.join(figs)}   (目录 {FIGD})")
    print("=" * 78)
    for name in figs:
        pdf = os.path.join(FIGD, f"{name}.pdf")
        print(f"\n[{name}]")
        if not os.path.exists(pdf):
            print("  缺 PDF"); ok = False; continue

        dev, verdict, extra = alignment_max_deviation(name)
        if dev is None:
            print(f"  对齐门: {verdict} -> 不可审计 {extra}")
            ok = False
        else:
            summ, where, n = extra
            flag = "PASS" if summ["fail"] == 0 and summ["warn"] == 0 else "FAIL"
            print(f"  对齐门: {verdict} ({flag}; 比较 {summ['comparisons']} 组, "
                  f"fail={summ['fail']}, warn={summ['warn']}, 豁免={summ['exemptions']})")
            print(f"          最大对齐偏差 = {dev:.6g} pt (容差 1.5 pt; 复算 {n} 项, "
                  f"最大项 {where})")
            ok &= (summ["fail"] == 0 and summ["warn"] == 0)

        rc, out = run([sys.executable, os.path.join(SKILL, "audit_pdf_text.py"),
                       pdf, "--min-pt", "5"])
        lo = [l for l in out.splitlines() if "minimum found" in l]
        print(f"  字形门: {'PASS' if rc == 0 else 'FAIL'}  {lo[0].strip() if lo else out.strip()[:80]}")
        ok &= (rc == 0)

        jout = os.path.join(FIGD, f"{name}.collision-audit.json")
        rc, out = run([sys.executable, os.path.join(SKILL, "audit_figure_collisions.py"),
                       pdf, "--json-out", jout,
                       "--overlay-pdf", os.path.join(FIGD, f"{name}.collision-audit.pdf")])
        with open(jout, encoding="utf-8") as f:
            cj = json.load(f)
        s = cj["summary"]
        print(f"  碰撞门: {cj['verdict']} (fail={s['fail']}, warn={s['warn']}, "
              f"文字框 {cj['visible_text_box_count']}, 描边 {cj['stroke_path_count']})")
        ok &= (rc == 0)

        import fitz
        d = fitz.open(pdf)
        w, h = d[0].rect.width, d[0].rect.height
        d.close()
        print(f"  页面: {w:.1f} x {h:.1f} pt = {w/72:.3f} x {h/72:.3f} in")

    print("\n" + "=" * 78)
    print("总判定:", "全部通过" if ok else "有未通过项")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
