# -*- coding: utf-8 -*-
"""恢复被 PowerShell Set-Content 以 GBK 误解码的 UTF-8 源文件.

变换: original(utf-8 bytes) --GBK decode--> mojibake(str) --utf-8 encode--> 当前文件
反变换: 当前文件 --utf-8 decode--> mojibake --GBK encode--> 原始 bytes --utf-8 decode--> original
"""
import io
import os
import sys

p = sys.argv[1]
raw = io.open(p, "rb").read()
s = raw.decode("utf-8")            # -> mojibake string
s = s.lstrip("\ufeff")             # 去掉 Set-Content 写入的 BOM
try:
    orig = s.encode("cp936").decode("utf-8")
except Exception as e:
    print("FAILED:", e)
    # 逐字符诊断
    bad = []
    for ch in set(s):
        try:
            ch.encode("gbk")
        except Exception:
            bad.append(ch)
    print("unmappable chars:", bad[:40], "count", len(bad))
    sys.exit(1)
io.open(p, "w", encoding="utf-8", newline="").write(orig)
print("recovered:", p, len(orig), "chars")
