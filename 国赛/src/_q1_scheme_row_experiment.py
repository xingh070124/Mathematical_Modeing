# -*- coding: utf-8 -*-
r"""
反证实验: 为什么 fig_q1_scheme 不采用"1x3 一行"版式 (任务书建议的 [1.5,1.0,1.0]).

只做一件事: 按 1x3 一行实际渲染, 然后跑碰撞门与字形门, 把失败项打印出来.
输出写到 outputs/_scheme_row_exp/, **不写 paper/figures** —— 这是被否掉的方案,
不应进入交付目录 (故此处直接 savefig, 不经 fig_style.save 的交付路径).

运行: python src/_q1_scheme_row_experiment.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import setup  # noqa: E402
from q1_fig_schematic import panel_a, panel_b, panel_fick  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "_scheme_row_exp")
SKILL = r"C:\Users\极光\.dsh\research-skills\nature-figure\scripts"

VARIANTS = [
    ("w150", [1.5, 1.0, 1.0], 7.4, 3.4),
    ("w200", [2.0, 1.0, 1.0], 7.4, 3.4),
    ("wide", [1.5, 1.0, 1.0], 9.6, 3.6),
]


def build(tag, ratios, w, h):
    fig = plt.figure(figsize=(w, h))
    gs = fig.add_gridspec(1, 3, left=0.010, right=0.990, bottom=0.030, top=0.870,
                          width_ratios=ratios, wspace=0.16)
    axa = fig.add_subplot(gs[0, 0]); axa.set_gid("a")
    axb = fig.add_subplot(gs[0, 1]); axb.set_gid("b")
    axc = fig.add_subplot(gs[0, 2]); axc.set_gid("c")
    panel_a(axa); panel_b(axb); panel_fick(axc)
    path = os.path.join(OUT, f"fig_q1_scheme_row_{tag}.pdf")
    fig.savefig(path)
    plt.close(fig)
    return path


def gate(cmd):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def main():
    setup()
    matplotlib.rcParams["font.sans-serif"] = list(
        matplotlib.rcParams["font.sans-serif"]) + ["DejaVu Sans"]
    os.makedirs(OUT, exist_ok=True)
    for tag, ratios, w, h in VARIANTS:
        pdf = build(tag, ratios, w, h)
        print(f"\n=== 1x3 一行  width_ratios={ratios}  figsize=({w},{h})  -> {tag}")
        rc, out = gate([sys.executable, os.path.join(SKILL, "audit_figure_collisions.py"),
                        pdf, "--json-out", pdf.replace(".pdf", ".collision.json")])
        cj = json.load(open(pdf.replace(".pdf", ".collision.json"), encoding="utf-8"))
        s = cj["summary"]
        print(f"  碰撞门: {cj['verdict']}  fail={s['fail']}  warn={s['warn']}")
        for f in cj["findings"][:8]:
            print(f"    [{f['severity']}] {f['kind']}: {f['text'][:36]!r}")
        rc2, out2 = gate([sys.executable, os.path.join(SKILL, "audit_pdf_text.py"),
                          pdf, "--min-pt", "5"])
        line = [l for l in out2.splitlines() if "minimum found" in l or "below minimum" in l]
        print(f"  字形门: {'PASS' if rc2 == 0 else 'FAIL'}  " + "; ".join(x.strip() for x in line))
        import fitz
        d = fitz.open(pdf)
        print(f"  页面: {d[0].rect.width:.1f} x {d[0].rect.height:.1f} pt")
        d.close()


if __name__ == "__main__":
    main()
