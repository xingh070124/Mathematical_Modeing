"""问题一/二 结果图表优化：三组布局图拼成单张出版级图 + 收敛图拼接。

遵循 nature-figure 约定：
  * 单张图一个核心结论——Q1：三组芯片均实现高密度近方形紧凑布局；
    Q2：三组芯片在固定正方形轮廓内总 HPWL 最小且受边界 Terminal 引力影响。
  * 白色背景、模块色一致（tab20 低饱和）、crimson 虚线轮廓、Terminal 红色点；
  * 直接标注（不用图例），导出 PNG/PDF/SVG/TIFF（PNG 600dpi 供 LaTeX）。

输出到 paper/figures/：
  q1_layout_combined.png/pdf/svg/tiff   Q2_layout_combined.png/pdf/svg/tiff
  q1_conv_combined.png                  q2_conv_combined.png  （拼接现有收敛图）
"""
from __future__ import annotations

import os
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager
from PIL import Image

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 项目根
RES1 = os.path.join(BASE, "result", "question 1")
RES2 = os.path.join(BASE, "result", "question 2")
ATT = os.path.join(BASE, "附件")
FIG = os.path.join(BASE, "paper", "figures")

# ---------- 中文字体（西文保持 Arial 风格） ----------
_avail = {f.name for f in font_manager.fontManager.ttflist}
_cjk = next((n for n in ["Microsoft YaHei", "SimHei", "DengXian", "SimSun",
                         "Noto Sans CJK SC"] if n in _avail), "sans-serif")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [_cjk, "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "axes.unicode_minus": False,
})


# ---------- 数据读取 ----------
def load_placement(path):
    blocks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if not p or p[0].startswith("#"):
                continue
            blocks.append((p[0], int(p[1]), int(p[2]), int(p[3]), int(p[4])))
    return blocks


def load_terminals(name):
    pos = []
    with open(os.path.join(ATT, f"{name}.pl"), encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 3:
                pos.append((int(p[1]), int(p[2])))
    return pos


def load_q1_metrics():
    with open(os.path.join(RES1, "q1_summary.json"), encoding="utf-8") as f:
        return {r["dataset"]: r for r in json.load(f)}


def load_q2_metrics():
    with open(os.path.join(RES2, "q2_summary.json"), encoding="utf-8") as f:
        return {r["dataset"]: r for r in json.load(f)}


# ---------- 布局面板 ----------
def draw_panel(ax, blocks, terminals, W, H, title, info):
    n = len(blocks)
    cmap = plt.get_cmap("tab20")
    norm = plt.Normalize(0, max(n, 1))
    ax.add_patch(Rectangle((0, 0), W, H, facecolor="#f4f4f4",
                           edgecolor="none", zorder=0))           # die 底色
    for i, (_name, x, y, w, h) in enumerate(blocks):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=cmap(norm(i)),
                               edgecolor="#2b2b2b", linewidth=0.4,
                               zorder=2, alpha=0.92))
    if terminals:
        ax.scatter([t[0] for t in terminals], [t[1] for t in terminals],
                   s=7, c="#d62728", marker="o", zorder=3,
                   edgecolors="#1f1f1f", linewidths=0.25)
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, edgecolor="#c00000",
                           linewidth=1.5, linestyle=(0, (4, 2)), zorder=3))
    m = 0.025 * max(W, H)
    ax.set_xlim(-m, W + m)
    ax.set_ylim(-m, H + m)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=8.5, pad=3)
    ax.text(0.5, -0.045, info, transform=ax.transAxes, ha="center",
            va="top", fontsize=6.6)


def build_layout_figure(datasets, metrics, placement_dir, terminals_fn,
                        q1, out_prefix):
    """三组布局图拼成 1×3 单张图。terminals_fn: 返回终端列表或 None。"""
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.15))
    for ax, name in zip(axes, datasets):
        blocks = load_placement(os.path.join(placement_dir,
                                             f"q{1 if q1 else 2}_{name}_placement.txt"))
        W, H = (metrics[name]["W"], metrics[name]["H"]) if q1 \
            else (metrics[name]["Lhat"], metrics[name]["Lhat"])
        if q1:
            asp = max(W, H) / min(W, H)
            info = (f"{name}  {W}×{H}  面积{metrics[name]['area']:,}"
                    f"  密度{metrics[name]['density']*100:.1f}%"
                    f"  长宽比{asp:.3f}")
        else:
            info = (f"{name}  L={W}  总HPWL={metrics[name]['hpwl']:,.0f}"
                    f"  gap={metrics[name]['gap_pct']:.1f}%  可行")
        draw_panel(ax, blocks, terminals_fn(name) if terminals_fn else None,
                   W, H, name, info)
    fig.subplots_adjust(wspace=0.12)
    title = "问题一  三组芯片模块摆放（轮廓面积最小·长宽比接近1）" if q1 \
        else "问题二  三组芯片模块摆放（固定正方形轮廓内总HPWL最小）"
    fig.suptitle(title, fontsize=9, fontweight="bold", y=0.98)
    save_multi(fig, out_prefix)


# ---------- 导出 ----------
def save_multi(fig, prefix):
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(f"{prefix}.png", dpi=600, bbox_inches="tight")
    fig.savefig(f"{prefix}.pdf", bbox_inches="tight")
    fig.savefig(f"{prefix}.svg", bbox_inches="tight")
    fig.savefig(f"{prefix}.tiff", dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {os.path.basename(prefix)} (.png/.pdf/.svg/.tiff)")


# ---------- 收敛图拼接（复用既有单数据收敛图） ----------
def stitch_convergence(names, res_dir, out_path, prefix, h_px=1150):
    imgs = []
    for name in names:
        p = os.path.join(res_dir, f"{prefix}_{name}_convergence.png")
        im = Image.open(p).convert("RGB")
        im = im.resize((int(im.width * h_px / im.height), h_px),
                       Image.LANCZOS)
        imgs.append(im)
    gap = 24
    canvas = Image.new("RGB", (sum(i.width for i in imgs) + gap * (len(imgs) - 1),
                               h_px), "white")
    x = 0
    for im in imgs:
        canvas.paste(im, (x, 0))
        x += im.width + gap
    os.makedirs(FIG, exist_ok=True)
    canvas.save(out_path, dpi=(600, 600))
    print(f"saved {os.path.basename(out_path)}")


def main():
    datasets = ["n100", "n200", "n300"]
    q1 = load_q1_metrics()
    q2 = load_q2_metrics()
    # 问题一 / 问题二 布局拼图（不含 Terminal）
    build_layout_figure(datasets, q1, RES1, None, True, os.path.join(FIG, "q1_layout_combined"))
    build_layout_figure(datasets, q2, RES2, load_terminals, False,
                        os.path.join(FIG, "q2_layout_combined"))
    # 收敛图拼接
    stitch_convergence(datasets, os.path.join(BASE, "result", "question 1"),
                       os.path.join(FIG, "q1_conv_combined.png"), "q1")
    stitch_convergence(datasets, os.path.join(BASE, "result", "question 2"),
                       os.path.join(FIG, "q2_conv_combined.png"), "q2")


if __name__ == "__main__":
    main()
