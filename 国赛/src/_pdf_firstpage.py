# -*- coding: utf-8 -*-
r"""用 PyMuPDF (fitz) 抽取 PDF 第 1 页文字, 用于核对题录.

markitdown 走 pdfminer, 对没有 ToUnicode 映射的字体只能给出 (cid:NNN);
PyMuPDF 走 MuPDF, 对字体的处理路径不同, 有些文件能读出来. 本脚本对每个文件
打印第 1 页前 2500 字, 以及整篇的可抽取文字总量, 便于判断"能不能读".

用法: python src/_pdf_firstpage.py <pdf1> [pdf2 ...]
"""
from __future__ import annotations

import os
import sys

import fitz

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for arg in sys.argv[1:]:
    path = arg if os.path.isabs(arg) else os.path.join(ROOT, arg)
    print("=" * 78)
    print(path)
    print("=" * 78)
    try:
        d = fitz.open(path)
    except Exception as e:                                   # noqa: BLE001
        print(f"  !! 打不开: {e}")
        continue
    total = 0
    for p in d:
        total += len(p.get_text().strip())
    print(f"  页数 {d.page_count}   全篇可抽文字总量 {total} 字符")
    t = d[0].get_text()
    print(f"  第 1 页抽出 {len(t.strip())} 字符, 前 2500 字如下:")
    print("-" * 78)
    print(t[:2500])
    d.close()
    print()
