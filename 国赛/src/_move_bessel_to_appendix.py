# -*- coding: utf-8 -*-
"""
_move_bessel_to_appendix.py -- 把「Bessel 特征函数交叉验证」小节从问题一的建模
部分移到附录, 使问题一建模部分满足篇幅要求, 同时保留全部内容与验证覆盖。

做法 (全部带断言, 不做正则批量改写):
  1. 按**唯一内容标记**定位该小节的行区间 [start, end);
  2. 从建模部分整段切除;
  3. 把其余节的 `\\subsubsection{...}` + `\\label{sec:tempverify}` 改写成附录的
     `\\section{...}` + `\\label{app:tempverify}`;
  4. 在切除处留下一句指向附录的引路语;
  5. 把整段插入 `\\begin{appendices}` 内、原 `\\section{附录：结果文件与源程序}` 之前。

只跑一次; 运行后请用 q1_reconcile.py 复核 (其锚点已同步更新)。

运行: python src/_move_bessel_to_appendix.py
"""

from __future__ import annotations

import io
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "paper", "example.tex")

START = r"\subsubsection{温度场的交叉验证：Bessel特征函数展开解析解}"
END = r"\subsubsection{求解某一时刻下药材各个位置的水分浓度}"
APP_ANCHOR = r"\section{附录：结果文件与源程序}"
BEG_APP = r"\begin{appendices}"

POINTER = (
    r"\S\ref{sec:tempsolve}的有限体积解还经一条不依赖离散过程的\textbf{解析途径}"
    r"（Bessel 特征函数展开配合 Duhamel 逐段闭式积分）逐点交叉验证，"
    r"其推导、前五阶特征根与偏差归因见附录~\ref{app:tempverify}。"
)


def main():
    lines = io.open(P, encoding="utf-8").read().splitlines(keepends=True)

    # ---- 定位 (断言唯一) ----
    si = [i for i, l in enumerate(lines) if l.startswith(START)]
    ei = [i for i, l in enumerate(lines) if l.startswith(END)]
    ai = [i for i, l in enumerate(lines) if l.startswith(APP_ANCHOR)]
    bi = [i for i, l in enumerate(lines) if l.startswith(BEG_APP)]
    assert len(si) == 1, f"起始标记不唯一: {len(si)}"
    assert len(ei) == 1, f"结束标记不唯一: {len(ei)}"
    assert len(ai) == 1, f"附录锚点不唯一: {len(ai)}"
    assert len(bi) == 1, f"appendices 唯一性: {len(bi)}"
    s, e, a = si[0], ei[0], ai[0]
    assert s < e < a, f"顺序错误 s={s} e={e} a={a}"
    print(f"  定位: Bessel 小节 行 {s+1}..{e}  ({e-s} 行); 附录锚点 行 {a+1}")

    block = lines[s:e]

    # ---- 改写成附录节 ----
    assert block[0].startswith(START), "块首不是预期标题"
    new_head = r"\section{附录：温度场解析解的交叉验证（Bessel 特征函数展开）}" + "\n"
    block = [new_head] + block[1:]
    # 把 \label{sec:tempverify} 改成附录标签
    lab = [i for i, l in enumerate(block) if l.strip() == r"\label{sec:tempverify}"]
    assert len(lab) == 1, f"sec:tempverify 标签不唯一: {len(lab)}"
    block[lab[0]] = r"\label{app:tempverify}" + "\n"

    # ---- 切除 + 留引路语 ----
    tip = "\n" + POINTER + "\n"
    rest = lines[:s] + [tip] + lines[e:]

    # ---- 插入附录 (重新定位, 因为行号已变) ----
    bi2 = [i for i, l in enumerate(rest) if l.startswith(BEG_APP)]
    assert len(bi2) == 1, "插入时 appendices 不唯一"
    ins = bi2[0] + 1
    assert rest[ins].strip() == "", "appendices 后应紧跟空行"
    out = rest[:ins + 1] + block + ["\n"] + rest[ins + 1:]

    io.open(P, "w", encoding="utf-8", newline="").write("".join(out))
    print(f"  已移动: {len(block)} 行 -> appendices 第 {ins+2} 行前")
    print(f"  文件行数: {len(lines)} -> {len(out)}")


if __name__ == "__main__":
    main()
