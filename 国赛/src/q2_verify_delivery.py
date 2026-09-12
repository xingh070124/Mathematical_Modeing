# -*- coding: utf-8 -*-
"""
交付前总核验: 一次性跑齐 paper / 图件 / 数字三方面的全部关卡, 输出单一结论.

关卡:
  A. LaTeX  : example.tex 编译日志中无 error / undefined / overfull / missing character
  B. 图件   : 5 张图 × 3 道渲染门 (面板对齐 / 字号下限 / 碰撞)
  C. 数字   : q2_reconcile.py 的四道对账门

用法: python src/q2_verify_delivery.py
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGD = os.path.join(ROOT, "paper", "figures")
SKILL = r"C:\Users\极光\.dsh\research-skills\nature-figure\scripts"
# 问题二的 3 张 + 问题一的 2 张合并图 (session 10/11 由 5 张与 3 张合并而来)
FIGS = ["fig_q1_scheme", "fig_q1_results",
        "fig_q2_coupling", "fig_q2_mechanism", "fig_q2_results",
        "fig_q4_schematic", "fig_q4_shrink", "fig_q4_results", "fig_q4_verify"]

# 允许指定 build 前缀: 并发编译时, example.log/example.pdf 会被其它进程覆盖,
# 用 `xelatex -jobname=iso` 产出私有件后可在这里传入, 例如
#   python src/q2_verify_delivery.py --build paper/iso
BUILD = os.path.join(ROOT, "paper", "example")
for _i, _a in enumerate(sys.argv):
    if _a == "--build" and _i + 1 < len(sys.argv):
        BUILD = sys.argv[_i + 1]
        if not os.path.isabs(BUILD):
            BUILD = os.path.join(ROOT, BUILD)
LOG = BUILD + ".log"
PDF = BUILD + ".pdf"

fails = []


def head(t):
    print("\n" + "=" * 78)
    print(t)
    print("=" * 78)


def _problem_pages(doc):
    """按小节标题锚点测量每个问题占用的页数."""
    anchors = ["问题一模型的建立与求解", "问题二模型的建立与求解",
               "问题三模型的建立与求解", "问题四模型的建立与求解",
               "模型评价与推广"]
    pos = {}
    for i, page in enumerate(doc):
        t = page.get_text().replace("\n", "")
        for k in anchors:
            if k in t and k not in pos:
                pos[k] = i + 1
    out = {}
    for a, b in zip(anchors, anchors[1:]):
        if a in pos and b in pos:
            out[a.replace("模型的建立与求解", "")] = pos[b] - pos[a]
    return out


# ---------------------------------------------------------------- A. LaTeX
head("A. LaTeX 编译日志")
log = LOG
if not os.path.exists(log):
    print(f"  [!] 未找到 {os.path.basename(log)} — 请先编译 (或传 --build)")
    fails.append("A: no log")
else:
    txt = open(log, encoding="utf-8", errors="replace").read()
    pats = {
        "error": r"! (?:LaTeX|Package|Class) Error",
        "undefined ref": r"LaTeX Warning: Reference .* undefined",
        "undefined cite": r"LaTeX Warning: Citation .* undefined",
        "overfull": r"Overfull \\hbox",
        "missing char": r"Missing character",
    }
    for name, pat in pats.items():
        n = len(re.findall(pat, txt))
        flag = "OK " if n == 0 else "!! "
        print(f"  {flag}{name:16s} {n}")
        if n:
            fails.append(f"A: {name} x{n}")
    pdf = PDF
    if os.path.exists(pdf):
        import fitz
        d = fitz.open(pdf)
        print(f"  OK 页数              {d.page_count}")
        t = "".join(p.get_text() for p in d).replace("\n", "")
        # 注意 1: PDF 抽文本会丢 "阻尼 Newton" 里中英文之间的空格, 故关键字不带空格.
        # 注意 2: 小节标题不写死字面量 —— 标题会被改写 (session 9/12 已两度改名),
        #         写死会使核验脚本误报"内容缺失"; 改为从 .tex 源码统计小节数与标题.
        for k in ("问题二模型的建立与求解", "18.45", "10.81", "1.71",
                  "干燥前沿", "阻尼Newton", "6204"):
            c = t.count(k)
            flag = "OK " if c else "!! "
            print(f"  {flag}关键内容 {k:20s} {c}")
            if not c:
                fails.append(f"A: missing text {k}")
        # §5.2 的小节数: 从 **.tex 源码**统计最可靠 —— 从 PDF 抽文本会被正文中
        # 出现的 "5.2.x" 字样干扰(如正文引用了 §5.2.3), 源码里的 \subsubsection 无歧义.
        import re as _re
        _tex = open(os.path.join(ROOT, "paper", "example.tex"),
                    encoding="utf-8").read()
        _seg = _tex[_tex.index("\\subsection{问题二模型的建立与求解}"):
                    _tex.index("\\subsection{问题三模型的建立与求解}")]
        subs = _re.findall(r"\\subsubsection\{([^}]*)\}", _seg)
        nsub = len(subs)
        print(f"  {'OK ' if nsub == 6 else '!! '}§5.2 小节数         {nsub} (期望 6)")
        for s_ in subs:
            print(f"       - {s_}")
        if nsub != 6:
            fails.append(f"A: §5.2 小节数 {nsub} != 6")
        # 篇幅约束: 每个问题不超过 6 页
        pages = _problem_pages(d)
        for name, npg in pages.items():
            ok = npg <= 6
            print(f"  {'OK ' if ok else '!! '}篇幅 {name:8s} {npg} 页 (上限 6)")
            if not ok:
                fails.append(f"A: {name} 篇幅 {npg} 页 > 6")
        # 摘要必须在一页之内: 关键词标记须出现在第 1 页
        kw_page = None
        for i, page in enumerate(d):
            t = page.get_text().replace("\n", "").replace(" ", "")
            if "关键词" in t or "关键字" in t:
                kw_page = i + 1
                break
        kw_ok = kw_page == 1
        print(f"  {'OK ' if kw_ok else '!! '}摘要单页          关键词出现在第 {kw_page} 页")
        if not kw_ok:
            fails.append(f"A: 摘要超出一页 (关键词在第 {kw_page} 页)")
        d.close()

# ---------------------------------------------------------------- B. 图件
head("B. 图件渲染门 (对齐 / 字号 / 碰撞)")
for n in FIGS:
    pdf = os.path.join(FIGD, f"{n}.pdf")
    if not os.path.exists(pdf):
        print(f"  !! {n}: 缺少 {pdf}")
        fails.append(f"B: missing {n}.pdf")
        continue
    aj = os.path.join(FIGD, f"{n}.alignment.json")
    align = "?"
    if os.path.exists(aj):
        align = json.load(open(aj, encoding="utf-8")).get("verdict", "?")
    r = subprocess.run([sys.executable, os.path.join(SKILL, "audit_pdf_text.py"),
                        pdf, "--min-pt", "5"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    m = re.search(r"below minimum:\s*(\d+)", r.stdout or "")
    below = m.group(1) if m else "?"
    r2 = subprocess.run([sys.executable, os.path.join(SKILL,
                        "audit_figure_collisions.py"), pdf],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    m2 = re.search(r"verdict:\s*(REVIEW REQUIRED|FIX BEFORE DELIVERY|PASS|NOT AUDITABLE)",
                   (r2.stdout or "") + (r2.stderr or ""))
    coll = m2.group(1) if m2 else "?"
    m3 = re.search(r"summary:\s*(\d+) fail", (r2.stdout or "") + (r2.stderr or ""))
    nfail = m3.group(1) if m3 else "?"
    ok = (align == "PASS" and below == "0" and coll in ("PASS", "REVIEW REQUIRED")
          and nfail == "0")
    print(f"  {'OK ' if ok else '!! '}{n:22s} 对齐={align:8s} 低于字号下限={below}"
          f"  碰撞={coll:16s} (fail={nfail})")
    if not ok:
        fails.append(f"B: {n} align={align} below={below} coll={coll} fail={nfail}")

# ---------------------------------------------------------------- C. 数字
head("C. 数字对账门")
r = subprocess.run([sys.executable, os.path.join(ROOT, "src", "q2_reconcile.py")],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", cwd=ROOT)
out = (r.stdout or "") + (r.stderr or "")
for line in out.splitlines():
    if any(k in line for k in ("未对上", "逐位一致", "通过", "对到注册表",
                               "允许清单", "扫描数值字面量", "纳入对账",
                               "注册表条目")):
        print("  " + line.strip())
bad = re.search(r"未对上:\s*(\d+)", out)
if bad and bad.group(1) != "0":
    fails.append(f"C: unmatched={bad.group(1)}")
if "失败" in out:
    fails.append("C: gate reported failure")
print(f"\n  reconcile 退出码 = {r.returncode}")

# ---------------------------------------------------------------- D. 问题四
head("D. 问题四结果对账门 (表6 / result4.xlsx / table6.csv)")
r4 = subprocess.run([sys.executable, os.path.join(ROOT, "src", "q4_reconcile.py")],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", cwd=ROOT)
out4 = (r4.stdout or "") + (r4.stderr or "")
for line in out4.splitlines():
    s_ = line.strip()
    if s_.startswith(("OK ", "!!", "问题四结果对账", "未通过", "数据行数",
                      "首列半径", "末列", "工作表名")):
        print("  " + s_)
if r4.returncode != 0:
    fails.append("D: q4_reconcile 未通过")
if r.returncode != 0:
    fails.append(f"C: exit {r.returncode}")

# ---------------------------------------------------------------- 结论
head("总核验结论")
if fails:
    print(f"  {len(fails)} 项未过:")
    for f in fails:
        print(f"    - {f}")
    raise SystemExit(1)
print(f"  全部通过: LaTeX 干净 / {len(FIGS)} 张图过三道渲染门 / "
      f"数字对账门 0 未对上。")
