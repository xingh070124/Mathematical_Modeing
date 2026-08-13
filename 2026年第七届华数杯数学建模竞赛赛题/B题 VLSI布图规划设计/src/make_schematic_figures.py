"""评审建议补充图：
  * 总体数学逻辑图（LB-UB 闭环）：paper/figures/logic_flow.png
  * 问题三 L-可行性曲线（三组）：paper/figures/q3_feasibility.png
"""
from __future__ import annotations

import os
import sys
import math
import json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
DATA = os.path.join(BASE, "附件")
RES3 = os.path.join(BASE, "result", "question 3")
FIG = os.path.join(BASE, "paper", "figures")
sys.path.insert(0, HERE)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from data_io import load_dataset                    # noqa: E402
from hpwl import NetIndex                           # noqa: E402
from config import SCENARIOS                        # noqa: E402
from solve_q3 import feasible_oracle                # noqa: E402


def _fonts():
    names = {f.name for f in font_manager.fontManager.ttflist}
    cjk = next((n for n in ["Microsoft YaHei", "SimHei", "SimSun"] if n in names),
               "sans-serif")
    plt.rcParams.update({"font.sans-serif": [cjk, "Arial"],
                         "axes.unicode_minus": False})


def build_logic_figure():
    _fonts()
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#EAF2FB", ec="#2b6cb0"):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                           fc=fc, ec=ec, lw=1.4, zorder=2)
        ax.add_patch(p)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                fontsize=9.5, zorder=3)

    def arrow(x1, y1, x2, y2, color="#333333", ls="-", rad=0.0):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                            mutation_scale=16, color=color, lw=1.6,
                            linestyle=ls, connectionstyle=f"arc3,rad={rad}",
                            zorder=1)
        ax.add_patch(a)

    box(0.4, 5.0, 3.2, 0.9, "原问题\n（矩形/异形装箱·HPWL·死区比例）")
    box(5.6, 5.0, 3.2, 0.9, "数学模型\n（整数坐标·析取约束·凸目标）", fc="#EDF8E9", ec="#2f855a")
    box(0.4, 2.6, 2.8, 1.0, "下界 LB\n（面积/边长/凸松弛）", fc="#FEF9E7", ec="#b7791f")
    box(5.6, 2.6, 2.8, 1.0, "上界 UB\n（启发式可行解）", fc="#FDE8E8", ec="#c53030")
    box(3.6, 4.4, 2.2, 0.7, "搜索（初解→元启发）")
    box(0.7, 1.2, 3.4, 0.8, "最优性差距 gap=(UB−LB)/LB", fc="#F5EFFB", ec="#6b46c1")
    box(5.7, 1.2, 3.0, 0.8, "最终结论\n（最佳已知解+gap，或精确最优）")

    arrow(3.6, 5.45, 5.6, 5.45)          # 原问题→模型
    arrow(4.7, 4.4, 2.0, 3.6, color="#b7791f")   # 模型→LB
    arrow(4.7, 4.4, 7.0, 3.6, color="#c53030")   # 模型→UB
    arrow(2.4, 2.6, 3.1, 4.4, rad=0.25, color="#b7791f")   # LB 回搜索
    arrow(7.0, 3.6, 5.6, 4.4, rad=-0.25, color="#c53030")  # UB 回搜索
    arrow(2.0, 2.6, 2.4, 2.0, color="#6b46c1")   # LB→gap
    arrow(7.0, 2.6, 6.0, 2.0, color="#6b46c1")   # UB→gap
    arrow(2.4, 1.2, 5.7, 1.6)                    # gap→结论
    ax.set_title("总体数学逻辑：从启发式求解到可验证定界", fontsize=12,
                 fontweight="bold", pad=10)
    fig.tight_layout()
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, "logic_flow.png"), dpi=300)
    plt.close(fig)
    print("saved logic_flow.png")


def build_q3_feasibility(names, budget_ils=3.0):
    _fonts()
    with open(os.path.join(RES3, "q3_summary.json"), encoding="utf-8") as f:
        meta = {r["dataset"]: r for r in json.load(f)}
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.6))
    for ax, name in zip(axes, names):
        ds = load_dataset(DATA, name)
        net = NetIndex(ds.names, ds.nets, ds.terminal_pos)
        widths = np.asarray(ds.widths, dtype=np.int64)
        heights = np.asarray(ds.heights, dtype=np.int64)
        Lstar = meta[name]["L_star"]
        L_lb = meta[name]["L_lb"]
        L_ub = meta[name]["L_ub0"]
        Ls = list(range(max(2, L_lb - 2), min(Lstar + 3, L_ub) + 1))
        feas = []
        for L in Ls:
            st, _ = feasible_oracle(ds, widths, heights, net, L,
                                    SCENARIOS["Q3"], seed=2026,
                                    budget_ils=budget_ils)
            feas.append(1.0 if st == "feasible" else
                        (0.0 if st == "infeasible" else 0.5))
        for L, fv in zip(Ls, feas):
            color = ("#38a169" if fv == 1.0 else
                     "#e53e3e" if fv == 0.0 else "#dd6b20")
            ax.bar(L, fv, width=0.9, color=color, alpha=0.85)
        ax.axvline(L_lb, color="#b7791f", ls="--", lw=1.4,
                   label=f"下界 L_lb={L_lb}")
        ax.axvline(Lstar, color="#2b6cb0", ls="-", lw=1.8,
                   label=f"L*={Lstar}")
        ax.set_ylim(-0.05, 1.15)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["不可行", "未知", "可行"])
        ax.set_xlabel("轮廓边长 L")
        ax.set_title(name, fontsize=9)
        ax.legend(fontsize=7, loc="upper left")
        ax.grid(alpha=0.3, axis="y")
    fig.suptitle("问题三 三组芯片的 L-可行性曲线", fontsize=11, fontweight="bold")
    fig.tight_layout()
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(os.path.join(FIG, "q3_feasibility.png"), dpi=300)
    plt.close(fig)
    print("saved q3_feasibility.png")


if __name__ == "__main__":
    build_logic_figure()
    build_q3_feasibility(["n100", "n200", "n300"])
