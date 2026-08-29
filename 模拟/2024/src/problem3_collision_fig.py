# -*- coding: utf-8 -*-
"""
问题三补充图：略小于最小螺距 p* 时的首次碰撞形态（真实碰撞点标注）

取 p = 0.449348 m（< p* ≈ 0.450348 m），沿盘入扫描至首次 SAT 相交时刻，
绘制整条龙形态，红高亮相交板凳对（龙头与第 18 节），并在放大插图中以 ×
标注两旋转矩形的真实交点（shapely 求交多边形）。

输出: paper/figures/fig_问题三首碰形态.png
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import problem3_solve as q3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Polygon as MplPolygon, Circle
from shapely.geometry import Polygon as ShapelyPoly

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "figures")

# ---------------- 参数与首碰构型 ----------------
def rect_vert(Ps, k):
    p0, p1 = Ps[k], Ps[k + 1]
    L = q3.HEAD_L if k == 0 else q3.BODY_L
    v = p1 - p0
    u = v / np.linalg.norm(v)
    n = np.array([-u[1], u[0]])
    c = 0.5 * (p0 + p1)
    hl, hw = L / 2, q3.WIDTH / 2
    return np.array([c + hl * u + hw * n, c + hl * u - hw * n,
                     c - hl * u - hw * n, c - hl * u + hw * n])


P = 0.449348
B = P / (2 * np.pi)
TH_END = q3.R_BOUND / B
S0 = q3.arc_len_s(B, q3.THETA0)
TOTAL = S0 - q3.arc_len_s(B, TH_END)

ds = 0.1
us = np.full(q3.N_BENCH, 0.05)
ths = Ps = pair = None
s_coll = None
s = 0.0
k = 0
n_steps = int(TOTAL / ds) + 2
best = (-1.0, None, None, None, None, None)   # (面积, s, ths, Ps, pair, th_head)
while k < n_steps:
    s = min(k * ds, TOTAL)
    th_head = TH_END if s >= TOTAL else q3.arc_len_inv(B, S0 - s)
    ths = q3.chain_thetas(B, th_head, us)
    Ps = q3.positions(B, ths)
    g, pr, coll = q3.min_gap_pos(Ps)
    if coll:
        if s_coll is None:
            s_coll = s
            pair_first = pr
        # 首碰后 3 m 窗口内追踪交叠面积最大的构型（交叠为瞬态）
        if s - s_coll <= 3.0:
            i0, j0 = pr[0] - 1, pr[1] - 1
            inter = ShapelyPoly(rect_vert(Ps, i0)).intersection(
                ShapelyPoly(rect_vert(Ps, j0)))
            if inter.area > best[0]:
                best = (inter.area, s, ths.copy(), Ps.copy(), pr, th_head)
    elif s_coll is not None and s - s_coll > 3.0:
        break
    k += 1
area, s_plot, ths, Ps, pair, th_head = best
s_coll = s_coll if s_coll is not None else s_plot
i0, j0 = pair[0] - 1, pair[1] - 1
r_head = B * th_head
print(f"p={P} m: 首碰 s={s_coll:.2f}/{TOTAL:.2f} m, 图示 s={s_plot:.2f} m "
      f"(碰撞后 {s_plot - s_coll:.2f} m), 龙头 r={r_head:.3f} m, 对={pair}")

V1 = rect_vert(Ps, i0)
V2 = rect_vert(Ps, j0)
inter = ShapelyPoly(V1).intersection(ShapelyPoly(V2))
if inter.geom_type == "Polygon":
    inter_pts = np.array(inter.exterior.coords)
    inter_area = inter.area
else:  # GeometryCollection / LineString 等
    inter_pts = np.array(inter.centroid.coords)
    inter_area = 0.0
print(f"交叠多边形面积 = {inter_area * 1e4:.2f} cm^2, 顶点 {len(inter_pts) - 1} 个")
cen = inter.centroid.coords[0]

# ---------------- 绘图 ----------------
fig, ax = plt.subplots(figsize=(8.2, 8.2))
th_grid = np.linspace(ths[0] - 0.5, ths[-1] + 3.0, 4000)
rr = B * th_grid
ax.plot(rr * np.cos(th_grid), rr * np.sin(th_grid), color="#9dc3e6", lw=0.8, zorder=1)
ax.add_patch(Circle((0, 0), q3.R_BOUND, fc="#fff2ae", ec="k", ls="--", lw=1.2, zorder=0))
ax.text(0, 0, "调头空间\n$\\oslash\\,9$ m", ha="center", va="center", fontsize=11)

for bi in range(q3.N_BENCH):
    p0, p1 = Ps[bi], Ps[bi + 1]
    Lv = q3.HEAD_L if bi == 0 else q3.BODY_L
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    n = np.array([-u[1], u[0]])
    ctr = 0.5 * (p0 + p1)
    hl, hw = Lv / 2, q3.WIDTH / 2
    corners = [ctr + hl * u + hw * n, ctr + hl * u - hw * n,
               ctr - hl * u - hw * n, ctr - hl * u + hw * n]
    is_coll = bi in (i0, j0)
    col = "#cc0000" if is_coll else ("#f6b26b" if bi == 0 else "#b6d7a8")
    ax.add_patch(MplPolygon(corners, closed=True, fc=col,
                            ec="#7f1d1d" if is_coll else "#666666",
                            lw=1.0 if is_coll else 0.3, zorder=4 if is_coll else 2))

hx, hy = Ps[0]
ax.plot(hx, hy, "k*", ms=13, zorder=5)
ax.annotate(f"龙头前把手（r = {r_head:.3f} m）", (hx, hy), textcoords="offset points",
            xytext=(16, 14), fontsize=9.5, zorder=6,
            arrowprops=dict(arrowstyle="->", lw=0.8))
ax.annotate("首次碰撞：龙头与第 18 节相交", cen, textcoords="offset points",
            xytext=(30, -40), fontsize=10, color="#cc0000", zorder=6,
            arrowprops=dict(arrowstyle="->", lw=1.2, color="#cc0000"))
ax.plot(inter_pts[:, 0], inter_pts[:, 1], "x", color="white", ms=7,
        mew=1.8, zorder=6)

# 放大插图
from mpl_toolkits.axes_grid1.inset_locator import mark_inset, inset_axes
axi = inset_axes(ax, width=3.3, height=3.3, loc="upper left",
                 bbox_to_anchor=(0.03, 0.97), borderpad=1.0)
axi.add_patch(MplPolygon(V1, closed=True, fc="#f4cccc", ec="#cc0000", lw=1.4))
axi.add_patch(MplPolygon(V2, closed=True, fc="#f4cccc", ec="#7f1d1d", lw=1.4,
                         alpha=0.75))
if inter.geom_type == "Polygon":
    axi.add_patch(MplPolygon(inter_pts, closed=True, fc="#cc0000", alpha=0.85, ec="k", lw=0.8))
axi.plot(inter_pts[:, 0], inter_pts[:, 1], "x", color="k", ms=8, mew=2)
cx0, cy0 = cen
span = 0.55
axi.set_xlim(cx0 - span, cx0 + span)
axi.set_ylim(cy0 - span, cy0 + span)
axi.set_aspect("equal")
axi.grid(alpha=0.3)
axi.tick_params(labelsize=8)
axi.set_title("碰撞局部放大（红色为交叠区，×为交点）", fontsize=9.5)
mark_inset(ax, axi, loc1=2, loc2=4, fc="none", ec="gray", lw=0.8, ls=":")

ax.set_aspect("equal")
ax.set_xlim(-9.5, 9.5)
ax.set_ylim(-9.5, 9.5)
ax.set_title(f"问题三：$p={P:.4f}\\,\\mathrm{{m}}<p^*$ 时盘入首次碰撞形态\n"
             f"（首碰于 $s={s_coll:.1f}\\,\\mathrm{{m}}$，图为碰撞后 "
             f"${s_plot - s_coll:.1f}\\,\\mathrm{{m}}$，距边界尚差 ${TOTAL - s_plot:.1f}\\,\\mathrm{{m}}$）")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.grid(alpha=0.3)
plt.tight_layout()
out = os.path.join(FIGDIR, "fig_问题三首碰形态.png")
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()

from PIL import Image, ImageChops
img = Image.open(out).convert("RGB")
bbox = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
if bbox:
    img.crop((max(0, bbox[0] - 30), max(0, bbox[1] - 30),
              min(img.width, bbox[2] + 30), min(img.height, bbox[3] + 30))).save(out)
print("[输出]", out)
