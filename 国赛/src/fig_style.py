"""论文图公用样式: 统一配色、中文标签、可编辑文字的矢量导出."""

from __future__ import annotations

import os

import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "figures")

# 统一调色板 (色盲友好: Blue-Orange 主轴 + 点缀色)
C = {
    "ink": "#000000",
    "blue": "#2166ac",        # 主色: 温度/热流/+10% 扰动
    "lightblue": "#92c5de",
    "red": "#b2182b",         # 对比色: 水分/质流/噪声
    "lightred": "#f4a582",
    "orange": "#e08214",
    "teal": "#01665e",
    "purple": "#762a83",
    "grey": "#7f7f7f",
    "lightgrey": "#d9d9d9",
    "faint": "#f0f0f0",
    "band": "#fff3d6",        # 强调带 (问题1时段)
}
# 每条 QoI / 序列的固定用色 (tab 风格, 图间保持一致)
SERIES = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2"]

# 兼容旧脚本的灰度引用 (线稿/中性元素仍用灰)
GREY = {"ink": "#000000", "dark": "#404040", "mid": "#9e9e9e",
        "light": "#cfcfcf", "faint": "#f0f0f0"}


def setup():
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["SimHei", "Microsoft YaHei", "Arial"],
        "mathtext.fontset": "stix",
        "font.size": 8,
        "axes.titlesize": 8.5,
        "axes.labelsize": 8,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "axes.linewidth": 0.8,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "legend.frameon": False,
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "axes.unicode_minus": False,
        "figure.dpi": 110,
    })


def save(fig, name):
    """PDF (LaTeX 用) + PNG (预览用) 双格式导出到 paper/figures/."""
    os.makedirs(FIGDIR, exist_ok=True)
    fig.savefig(os.path.join(FIGDIR, f"{name}.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(FIGDIR, f"{name}.png"), dpi=300, bbox_inches="tight")
    print(f"saved: paper/figures/{name}.pdf|.png")
