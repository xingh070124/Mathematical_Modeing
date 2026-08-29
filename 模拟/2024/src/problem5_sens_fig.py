# -*- coding: utf-8 -*-
"""问题 5 灵敏度与鲁棒性图（依赖 problem5_sensitivity.json + _mc_R_grid.npy）."""
import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib
matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "figures")
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial"],
    "axes.unicode_minus": False,
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "axes.spines.right": False, "axes.spines.top": False,
    "axes.linewidth": 0.8, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "legend.frameon": False, "legend.fontsize": 7,
    "lines.linewidth": 1.2, "savefig.dpi": 300,
})
C_BLUE, C_ORANGE, C_GREEN = "#0072B2", "#E69F00", "#009E73"
C_VERM, C_SKY, C_GRAY, C_DARK = "#D55E00", "#56B4E9", "#7F7F7F", "#2B2B2B"

with open(os.path.join(ROOT, "src", "problem5_sensitivity.json"),
          encoding="utf-8") as f:
    RES = json.load(f)

fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5),
                         gridspec_kw={"width_ratios": [1, 1.1, 1.15]})

# ---- (a) D_body 灵敏度 ----
ax = axes[0]
ds = RES["sens_D_body"]
xs = np.arange(3)
vals = [d["v_star"] for d in ds]
labs = [d["case"].replace("D_body", "D\n") for d in ds]
bars = ax.bar(xs, vals, width=0.55, color=[C_SKY, C_BLUE, C_ORANGE])
for x, v in zip(xs, vals):
    ax.annotate(f"{v:.4f}", (x, v), textcoords="offset points",
                xytext=(0, 3), ha="center", fontsize=6.5)
ax.axhline(RES["baseline"]["v_star"], color=C_VERM, lw=0.8, ls=(0, (4, 2)))
ax.set_xticks(xs, labs, fontsize=7)
ax.set_ylim(1.240, 1.253)
ax.set_ylabel(r"$v^{*}$ (m/s)")
ax.set_title(r"(a) 弦长 $D_{\rm body}\pm5\%$", fontsize=8)

# ---- (b) k 灵敏度 ----
ax = axes[1]
ks = RES["sens_k"]
xs = np.arange(len(ks))
vals = [k["v_star"] for k in ks]
ax.plot(xs, vals, "o-", color=C_BLUE, ms=5)
for x, kx in zip(xs, ks):
    ax.annotate(f"{kx['v_star']:.3f}", (x, kx["v_star"]),
                textcoords="offset points", xytext=(0, 5), ha="center",
                fontsize=6.5)
ax.set_xticks(xs, [f"k={k['k']:g}" for k in ks], fontsize=7)
ax.set_ylabel(r"$v^{*}$ (m/s)")
ax.set_title(r"(b) 半径比 $k=R_1/R_2$", fontsize=8)

# ---- (c) 蒙特卡洛超限概率 ----
ax = axes[2]
mc = RES["monte_carlo"]
xs = np.arange(len(mc))
vals = [100.0 * m["p_over_2"] for m in mc]
colors = [C_BLUE, C_SKY, C_GREEN, C_ORANGE]
ax.bar(xs, vals, width=0.58, color=colors)
for x, m, v in zip(xs, mc, vals):
    ax.annotate(f"{v:.1f}%", (x, v), textcoords="offset points",
                xytext=(0, 3), ha="center", fontsize=7)
ax.set_xticks(xs, [f"$\\bar v$={m['v_bar_pct']:.2f}$v^*$\n"
                   f"$\\sigma$={m['sigma']:.0%}" for m in mc], fontsize=6.5)
ax.set_ylabel("超限概率 P($\\max_i v_i>2$) (%)")
ax.set_ylim(0, 80)
ax.set_title("(c) 速度扰动蒙特卡洛（N=2000）", fontsize=8)

fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "fig_问题五灵敏度鲁棒性.png"),
            bbox_inches="tight")
print("[图] fig_问题五灵敏度鲁棒性.png")
