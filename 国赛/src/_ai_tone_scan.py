# -*- coding: utf-8 -*-
r"""对 paper/example.tex 做"AI 腔"体检: 只报告可疑模式的位置与计数, 不改文件.

检查项 (中文建模论文语境):
  1. 破折号 / 中文括号 / 引号 的密度
  2. \textbf 加粗数量与位置 (机械加粗是 AI 排版噪声)
  3. 套话连接词 (值得注意/综上所述/由此可见/不难发现/众所周知/首先其次最后)
  4. 否定平行 ("不是...而是", "不仅...而且", "并非...而是")
  5. 段落长度与句长分布 (句长过于均匀 = 机器味)
  6. 段首词重复 (同一小节内多段以同一词开头)
  7. 高频词 "本文/这里/我们/该/其/从而/进而/由此"

用法: python src/_ai_tone_scan.py [--top 40]
"""
from __future__ import annotations

import os
import re
import sys
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")

TOP = 40
if "--top" in sys.argv:
    TOP = int(sys.argv[sys.argv.index("--top") + 1])

raw = open(TEX, encoding="utf-8").read()
lines = raw.splitlines()

# 去掉注释行, 但保留行号
body = [(i + 1, l) for i, l in enumerate(lines) if not l.lstrip().startswith("%")]

CN = r"[\u4e00-\u9fff]"


def strip_tex(s: str) -> str:
    """粗去 LaTeX 命令, 只留可读文字."""
    s = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?", " ", s)
    s = re.sub(r"$[^$]*$", " ", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = re.sub(r"[{}$\\&_^~]", " ", s)
    return s


print("=" * 78)
print("1. 排版噪声密度")
print("=" * 78)
n_cn = len(re.findall(CN, raw))
for name, pat in [("破折号 ——", r"——"),
                  ("中文括号 （", r"（"),
                  ("英文括号 (", r"\("),
                  ("引号 “", r"“"),
                  ("加粗 \\textbf", r"\\textbf"),
                  ("公式 $$$$ 段", r"\$[^$]+\$")]:
    n = len(re.findall(pat, raw))
    print(f"  {name:14s} {n:5d}   (每千汉字 {n / max(n_cn, 1) * 1000:6.2f})")
print(f"  {'汉字总数':14s} {n_cn:5d}")

print()
print("=" * 78)
print("2. 套话 / 否定平行 / 结论腔 (逐条列出)")
print("=" * 78)
PATTERNS = [
    ("套话过渡", r"值得(注意|强调|一提)的是|综上所述|总而言之|由此可见|不难(发现|看出|理解)|"
                 r"众所周知|显而易见|换言之|换句话说|更重要的是|需要指出的是|应当指出"),
    ("否定平行", r"不是[^。；，]{0,18}而是|并非[^。；，]{0,18}而是|不仅[^。；，]{0,20}而且|"
                 r"与其说[^。；，]{0,18}不如说"),
    ("三连排比", r"([^、，。；]{2,12})、\1|既[^。；]{2,14}又[^。；]{2,14}也"),
    ("空洞形容", r"极大(地)?|显著(地)?提升|充分(地)?(体现|说明|证明)|有效地|有力地|"
                 r"全面地|深入地|高度重视|至关重要的|起到了?重要作用"),
    ("机械序列", r"^.{0,6}(首先|其次|再次|最后|第一|第二|第三)[，,、]"),
]
for label, pat in PATTERNS:
    hits = []
    for ln, l in body:
        for m in re.finditer(pat, l):
            hits.append((ln, m.group(0)))
    print(f"\n  [{label}] {len(hits)} 处")
    for ln, g in hits[:TOP]:
        print(f"    L{ln:5d}  {g}")

print()
print("=" * 78)
print("3. 高频词")
print("=" * 78)
WORDS = ["本文", "这里", "我们", "该", "其", "从而", "进而", "由此", "因此", "故",
         "可", "能", "即", "则", "说明", "表明", "给出", "得到"]
txt = strip_tex(raw)
cnt = Counter()
for w in WORDS:
    cnt[w] = txt.count(w)
for w, c in cnt.most_common():
    print(f"  {w:6s} {c:5d}   (每千汉字 {c / max(n_cn, 1) * 1000:6.2f})")

print()
print("=" * 78)
print("4. 句长分布 (仅统计汉字句, 反映是否机器般均匀)")
print("=" * 78)
sents = [s for s in re.split(r"[。；！？]", txt) if len(re.findall(CN, s)) >= 6]
lens = sorted(len(re.findall(CN, s)) for s in sents)
if lens:
    import statistics
    print(f"  句数 {len(lens)}   最短 {lens[0]}   中位 {lens[len(lens)//2]}   "
          f"均值 {statistics.mean(lens):.1f}   最长 {lens[-1]}")
    q = [lens[int(len(lens) * p)] for p in (0.1, 0.25, 0.5, 0.75, 0.9)]
    print(f"  分位 10/25/50/75/90%: {q}")
    print(f"  >=60 汉字的超长句 {sum(1 for x in lens if x >= 60)} 句")

print()
print("=" * 78)
print("5. 最长句 TOP 12 (这些最可能是需要断句的地方)")
print("=" * 78)
longest = sorted(sents, key=lambda s: -len(re.findall(CN, s)))[:12]
for s in longest:
    print(f"  [{len(re.findall(CN, s)):3d}] {s.strip()[:88]}")
