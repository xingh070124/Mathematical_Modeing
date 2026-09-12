# -*- coding: utf-8 -*-
r"""
问题一示意图 (fig_q1_scheme) 版式判据的测量脚本 —— 只测量, 不出图.

用途: 合并 fig_q1_model / fig_q1_fvm / fig_q1_fick 为一个 1x3 或 2 行版式前,
先用**渲染后的真实文字宽度**判断每个面板的最小可用宽度, 避免凭目测估宽.

测量的是 matplotlib 用当前字体渲染出的 window extent (px @ dpi) -> pt,
含 mathtext 与中文, 与最终 PDF 中的字号一致.

运行: python src/_q1_scheme_layout_probe.py
"""

from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig_style import setup  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# (面板, 用途说明, 字号, 文本)
ITEMS = [
    ("a", "顶部热风标注", 8.5, r"热风 $T_\infty(t),\ C_\infty(t)$"),
    ("a", "热流注释", 7.3, r"热流 $q=h\,[T_\infty-T]$（入）"),
    ("a", "质流注释", 7.3, r"质流 $j=h_m\,[C-C_\infty]$（出）"),
    ("a", "中截面标签", 7.2, r"中截面 $z=0$"),
    ("a", "尺寸标注 L", 7.5, r"$L=25\ \mathrm{cm}$"),
    ("a", "尺寸标注 R", 7.5, r"$R=2\ \mathrm{cm}$"),
    ("a", "标题", 8.5, r"(a) 物理模型：圆柱药材与第三类边界条件"),
    ("b", "界面通量标签", 8.0, r"$G_{i-\frac{1}{2}}$"),
    ("b", "控制体公式", 7.5,
     r"$V_i=\pi\left(r_{i+\frac{1}{2}}^2-r_{i-\frac{1}{2}}^2\right)$（单位轴长）"),
    ("b", "中心边界条件", 7.5, r"中心：$\partial T/\partial r=\partial C/\partial r=0$（对称）"),
    ("b", "表面温度边界", 7.5, r"表面：$-k\,\partial_r T=h\,(T-T_\infty)$，"),
    ("b", "表面水分边界", 7.5, r"$-D\,\partial_r C=h_m\,(C-C_\infty)$"),
    ("b", "节点标签", 8.0, r"$r_{M-\frac{1}{2}}$"),
    ("b", "标题", 8.5, r"(b) 一维径向求解域与节点式有限体积（图示 $M=8$）"),
    ("c", "内部标注", 7.5, r"内部：$C\approx C_0$"),
    ("c", "扩散标注", 7.3, r"浓度梯度驱动扩散 $-D(C)\,\partial_rC$"),
    ("c", "蒸发表注", 7.3, r"表面蒸发 $j=h_m\,[C-C_\infty]$"),
    ("c", "中心/表面标注", 7.5, r"$r=R$（表面）"),
    ("c", "标题", 8.5, r"(c) 水分径向扩散示意"),
]


def main():
    setup()
    dpi = 110.0
    fig = plt.figure(figsize=(7.4, 5.0), dpi=dpi)
    fig.canvas.draw()
    ren = fig.canvas.get_renderer()
    to_pt = 72.0 / dpi

    print(f"dpi={dpi:g}, 换算 1 px = {to_pt:.4f} pt")
    print(f"{'pan':>3} {'用途':<14} {'字号':>5} {'宽 pt':>8} {'宽 in':>7}  文本")
    print("-" * 100)
    widest = {}
    for pan, note, fs, txt in ITEMS:
        t = fig.text(0.0, 0.0, txt, fontsize=fs)
        bb = t.get_window_extent(ren)
        w_pt = bb.width * to_pt
        print(f"{pan:>3} {note:<14} {fs:>5.1f} {w_pt:>8.1f} {w_pt/72:>7.3f}  {txt}")
        if bb.width > widest.get(pan, (0,))[0]:
            widest[pan] = (bb.width, w_pt, txt)
        t.remove()

    print("-" * 100)
    for pan, (_, w_pt, txt) in widest.items():
        print(f"面板 ({pan}) 最宽文字: {w_pt:.1f} pt = {w_pt/72:.3f} in  <- {txt}")


if __name__ == "__main__":
    main()
