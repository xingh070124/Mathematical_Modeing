# -*- coding: utf-8 -*-
"""
绘制问题一/二/三求解算法流程图（黑白配色，论文印刷友好）

输出（覆盖/新建）:
  paper/figures/fig_算法流程图.png        问题一
  paper/figures/fig_问题二算法流程.png     问题二
  paper/figures/fig_问题三算法流程.png     问题三（新建）

实现: 像素坐标制（1 数据单位 = 1 像素），先绘制文本并用 renderer 实测其
像素尺寸，再据此确定框高与布局，避免行高估算误差。
风格: 白底黑框黑字，起止框浅灰底，判断框菱形，箭头黑色。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun"]
plt.rcParams["axes.unicode_minus"] = False

DPI = 200
W = 2150                 # 画布宽（px）
HMAX = 3600              # 画布高上限（px，底部留白会被 tight 裁掉）
FS = 10.5                # 正文字号(pt)
PAD_Y = 26               # 框内上下留白(px)
GAP = 66                 # 框间箭头间距(px)
CX = W // 2

BLACK = "#000000"
GRAY = "#d9d9d9"


class Chart:
    def __init__(self, title):
        self.title = title
        self.nodes = {}
        self.order = []
        self.arrows = []       # (a, b, label, side)  side: 'right'/'left' 标签偏移
        self.poly = []         # (pts, label, lx, ly, lha)

    def add(self, name, text, kind="proc", w=1560, cx=CX):
        self.nodes[name] = dict(text=text, kind=kind, w=w, cx=cx)
        self.order.append(name)
        return name

    def arrow(self, a, b, label=None, ldx=14, side="left"):
        self.arrows.append((a, b, label, ldx, side))

    def layout(self):
        """第一遍：放置文本并实测尺寸，确定各节点像素位置（存入 self.nodes）。"""
        self.fig = plt.figure(figsize=(W / DPI, HMAX / DPI), dpi=DPI)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, HMAX)
        self.ax.axis("off")
        self.ax.text(CX, HMAX - 56, self.title, ha="center", va="center",
                     fontsize=17, fontweight="bold", color=BLACK)
        y = HMAX - 130
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        for name in self.order:
            n = self.nodes[name]
            t = self.ax.text(n["cx"], y, n["text"], ha="center", va="center",
                             fontsize=FS, color=BLACK, linespacing=1.45)
            bb = t.get_window_extent(renderer)
            tw, th = bb.width, bb.height
            if n["kind"] in ("start", "end"):
                h = th + 44
                w = max(200, tw + 90)
            elif n["kind"] == "dec":
                h = 2.35 * th + 46
                w = max(n["w"] * W / 2150.0, 2.05 * tw + 90)
            else:
                h = th + 2 * PAD_Y
                w = max(n["w"], tw + 70)
            y -= GAP + h / 2
            n.update(cy=y, h=h, w=w, tw=tw, th=th, artist=t)
            y -= h / 2

    def render(self, path):
        ax = self.ax
        for name in self.order:
            n = self.nodes[name]
            cx, cy, w, h, kind = n["cx"], n["cy"], n["w"], n["h"], n["kind"]
            if kind in ("start", "end"):
                ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                            boxstyle="round,pad=2,rounding_size=14",
                                            fc=GRAY, ec=BLACK, lw=1.6,
                                            mutation_scale=DPI / 100.0))
            elif kind == "dec":
                ax.add_patch(Polygon([(cx, cy + h / 2), (cx + w / 2, cy),
                                      (cx, cy - h / 2), (cx - w / 2, cy)],
                                     closed=True, fc="white", ec=BLACK, lw=1.6))
            else:
                ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h,
                                            boxstyle="round,pad=2,rounding_size=9",
                                            fc="white", ec=BLACK, lw=1.6,
                                            mutation_scale=DPI / 100.0))
            n["artist"].set_position((cx, cy))

        def edge(p1, p2, label=None, lpos=None):
            ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>",
                                         mutation_scale=22, color=BLACK,
                                         lw=1.6, shrinkA=0, shrinkB=0))
            if label:
                lpos = (lpos[0], lpos[1] + 6)
                ax.text(*lpos, label, fontsize=10.5, color=BLACK,
                        ha="left", va="center")

        for a, b, label, ldx, side in self.arrows:
            A, B = self.nodes[a], self.nodes[b]
            p1 = (A["cx"], A["cy"] - A["h"] / 2)
            p2 = (B["cx"], B["cy"] + B["h"] / 2)
            lpos = None
            if label:
                lpos = (p1[0] + (ldx if side == "left" else -ldx),
                        (p1[1] + p2[1]) / 2)
                if side == "right":
                    lpos = (p1[0] + ldx, (p1[1] + p2[1]) / 2)
            edge(p1, p2, label, lpos)

        for pts, label, lx, ly, lha in self.poly:
            if pts:
                for i in range(len(pts) - 1):
                    last = i == len(pts) - 2
                    ax.add_patch(FancyArrowPatch(pts[i], pts[i + 1],
                                                 arrowstyle="-|>" if last else "-",
                                                 mutation_scale=22, color=BLACK,
                                                 lw=1.6, shrinkA=0, shrinkB=0))
            if label:
                ax.text(lx, ly, label, fontsize=10.5, color=BLACK,
                        ha=lha, va="center")

        plt.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white",
                    pad_inches=0.15)
        plt.close()
        print("[输出]", path)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGDIR = os.path.join(ROOT, "paper", "figures")

# ================= 问题一 =================
f = Chart("问题一求解算法流程图")
f.add("s", "开始", "start")
f.add("in", "输入参数：螺距 $p$=0.55 m、板长 $L$、孔距板端 0.275 m、\n"
            "初始极角 $\\theta_0$=32$\\pi$（第 16 圈）、龙头速度 $v_0$=1 m/s、$t\\in$[0, 300] s")
f.add("arc", "对每个时刻 $t$：二分法求解弧长积分方程\n"
             "$t=\\int_{\\theta_1(t)}^{32\\pi} b\\sqrt{\\alpha^2+1}\\,\\mathrm{d}\\alpha$，得龙头极角 $\\theta_1(t)$")
f.add("init", "初始化：$P_1=P(\\theta_1(t))$ 为龙头前把手，$i=1$")
f.add("d1", "$i\\leq$ 223 ？\n（未到龙尾后把手）", "dec")
f.add("circle", "以 $P_i$ 为圆心、两孔中心距 $d_i$ 为半径作圆\n"
                "（$d_1$=2.86 m，$d_2$~$d_{224}$=1.65 m）")
f.add("cross", "求圆与螺线交点（Brent 法解 $\\|P(\\theta)-P_i\\|=d_i$），\n"
               "取极角最接近 $\\theta_i$ 且位于龙头后方者 → $P_{i+1}$")
f.add("step", "$i\\leftarrow i+1$，返回判定", w=680)
f.add("vel", "求各把手速度（双方法互验）：\n"
             "① 中心差分 $v_i=\\|P_i(t+\\Delta t)-P_i(t-\\Delta t)\\|/(2\\Delta t)$；\n"
             "② 速度分解递推 $v_{i+1}=v_i\\,(T(\\theta_i)\\cdot e_i)/(T(\\theta_{i+1})\\cdot e_i)$")
f.add("sat", "实体碰撞检测（宽相 AABB + 精相“顶点包含∪SAT”）：\n"
             "确认 0~300 s 全程非相邻板凳最小间隙 > 0")
f.add("out", "输出：每秒 224 个把手的位置与速度\n（写入 result1.xlsx 的位置表 / 速度表）")
f.add("e", "结束", "end")
for a, b in [("s", "in"), ("in", "arc"), ("arc", "init"), ("init", "d1"),
             ("d1", "circle"), ("circle", "cross"), ("cross", "step"),
             ("d1", "vel"), ("vel", "sat"), ("sat", "out"), ("out", "e")]:
    f.arrow(a, b, "是" if a == "d1" else None, ldx=16)
f.layout()
D1, ST = f.nodes["d1"], f.nodes["step"]
f.poly.append(([(ST["cx"] - ST["w"] / 2, ST["cy"]), (180, ST["cy"]),
                (180, D1["cy"]), (D1["cx"] - D1["w"] / 2, D1["cy"])],
               None, 0, 0, "left"))
f.render(os.path.join(FIGDIR, "fig_算法流程图.png"))

# ================= 问题二 =================
f = Chart("问题二碰撞检测算法流程（宽相 + 精相 + 二分 + CCD）")
f.add("s", "开始", "start")
f.add("in", "输入：时刻 $t$ 全部 224 个把手位置")
f.add("rect", "构建 223 个板凳旋转矩形与外接包围盒 AABB")
f.add("broad", "【宽相 Broad phase】AABB 预筛选，\n"
               "剔除相距过远的板凳对（每对仅 $O(1)$ 次比较）")
f.add("d1", "AABB 可能重叠？", "dec")
f.add("narrow", "【精相 Narrow phase】（相邻板凳 $j-i=1$ 铰接，跳过）\n"
                "① 顶点包含检测（覆盖“完全包含”退化情形）\n"
                "② 分离轴定理 SAT（覆盖全部相交情形）")
f.add("d2", "碰撞？", "dec")
f.add("bis", "大步长扫描定位首个碰撞区间 [$t_{lo}$ 无碰撞, $t_{hi}$ 有碰撞]，\n"
             "二分收缩：$t_{mid}=(t_{lo}+t_{hi})/2$，至 $<10^{-3}$ s")
f.add("ccd", "CCD 黄金分割在临界区间内搜索 $\\min g(t)$，\n"
             "连续精化“恰碰撞”时刻（消除隧道效应）")
f.add("out", "输出：盘入终止时刻 $t^{*}$、首次碰撞对、\n全龙位置与速度（result2.xlsx）")
f.add("e", "结束", "end")
for a, b in [("s", "in"), ("in", "rect"), ("rect", "broad"), ("broad", "d1"),
             ("d1", "narrow"), ("narrow", "d2"), ("d2", "bis"), ("bis", "ccd"),
             ("ccd", "out"), ("out", "e")]:
    f.arrow(a, b)
f.layout()
D1, D2, RC = f.nodes["d1"], f.nodes["d2"], f.nodes["rect"]
x_r = 1880
f.poly.append(([(D1["cx"] + D1["w"] / 2, D1["cy"]), (x_r, D1["cy"]),
                (x_r, RC["cy"]), (RC["cx"] + RC["w"] / 2, RC["cy"])],
               "否（跳过该对）", D1["cx"] + D1["w"] / 2 + 30, D1["cy"] + 34, "left"))
f.poly.append(([(D2["cx"] + D2["w"] / 2, D2["cy"]), (x_r, D2["cy"]),
                (x_r, f.nodes["bis"]["cy"]),
                (f.nodes["bis"]["cx"] + f.nodes["bis"]["w"] / 2, f.nodes["bis"]["cy"])],
               None, 0, 0, "left"))
f.poly.append((None, "是（记录碰撞对）", D2["cx"] + D2["w"] / 2 + 30, D2["cy"] - 44, "left"))
x_l = 270
f.poly.append(([(D2["cx"] - D2["w"] / 2, D2["cy"]), (x_l, D2["cy"]),
                (x_l, RC["cy"]), (RC["cx"] - RC["w"] / 2, RC["cy"])],
               "否（扫描下一时刻）", x_l + 16, D2["cy"] + 44, "left"))
f.render(os.path.join(FIGDIR, "fig_问题二算法流程.png"))

# ================= 问题三 =================
f = Chart("问题三最小螺距搜索算法流程（可行性单调 + 二分）")
f.add("s", "开始", "start")
f.add("in", "输入：螺距区间 [$lo$, $hi$]=[0.30, 1.70] m、精度 $tol$=10$^{-4}$ m、\n"
            "采样步长 $ds$（粗 0.5 m / 细 0.1 m）、调头空间半径 $R$=4.5 m")
f.add("mid", "取中点 $mid\\leftarrow(lo+hi)/2$，确定盘入终点 $\\theta_{end}=9\\pi/mid$")
f.add("sim", "龙头自 $\\theta_0$=32$\\pi$ 盘入至 $\\theta_{end}$（每 $ds$ 米采样）：\n"
             "牛顿迭代逆推 224 把手 → AABB 宽相 + SAT 精相判定")
f.add("d1", "全程无碰撞？\n（含龙头恰达边界的终点构型）", "dec")
f.add("no", "不可行：记录首碰位置与板凳对\n$lo\\leftarrow mid$", w=640, cx=560)
f.add("yes", "可行：\n$hi\\leftarrow mid$", w=520, cx=1640)
f.add("d2", "$hi-lo<tol$ ？", "dec")
f.add("out", "输出：$p^{*}=(lo+hi)/2\\approx 0.4503$ m、临界碰撞对\n"
             "（龙头与相邻圈第 18~20 节）、临界形态与验证表")
f.add("e", "结束", "end")
for a, b in [("s", "in"), ("in", "mid"), ("mid", "sim"), ("sim", "d1"),
             ("d2", "out"), ("out", "e")]:
    f.arrow(a, b)
f.layout()
D1, NO, YE, D2, MID = (f.nodes["d1"], f.nodes["no"], f.nodes["yes"],
                       f.nodes["d2"], f.nodes["mid"])
f.poly.append(([(D1["cx"] - D1["w"] / 2, D1["cy"]),
                (NO["cx"] + NO["w"] / 2, NO["cy"])], None, 0, 0, "left"))
f.poly.append((None, "否", D1["cx"] - D1["w"] / 2 - 44, D1["cy"] + 54, "center"))
f.poly.append(([(D1["cx"] + D1["w"] / 2, D1["cy"]),
                (YE["cx"] - YE["w"] / 2, YE["cy"])], None, 0, 0, "left"))
f.poly.append((None, "是", D1["cx"] + D1["w"] / 2 + 44, D1["cy"] + 54, "center"))
f.poly.append(([(NO["cx"], NO["cy"] - NO["h"] / 2),
                (NO["cx"], D2["cy"] + 60), (D2["cx"] - D2["w"] / 2, D2["cy"])],
               None, 0, 0, "left"))
f.poly.append(([(YE["cx"], YE["cy"] - YE["h"] / 2),
                (YE["cx"], D2["cy"] + 60), (D2["cx"] + D2["w"] / 2, D2["cy"])],
               None, 0, 0, "left"))
x_loop = 150
f.poly.append(([(D2["cx"] - D2["w"] / 2, D2["cy"]), (x_loop, D2["cy"]),
                (x_loop, MID["cy"]), (MID["cx"] - MID["w"] / 2, MID["cy"])],
               None, 0, 0, "left"))
f.poly.append((None, "否（继续二分）", x_loop - 12, (D2["cy"] + MID["cy"]) / 2, "right"))
f.render(os.path.join(FIGDIR, "fig_问题三算法流程.png"))

# ---- 后处理：裁掉四周留白（tight bbox 对整幅 axes 不生效） ----
from PIL import Image, ImageChops
for name in ["fig_算法流程图.png", "fig_问题二算法流程.png", "fig_问题三算法流程.png"]:
    p = os.path.join(FIGDIR, name)
    img = Image.open(p).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox:
        m = 30
        box = (max(0, bbox[0] - m), max(0, bbox[1] - m),
               min(img.width, bbox[2] + m), min(img.height, bbox[3] + m))
        img.crop(box).save(p)
        print("[裁边]", name, "->", box)
print("done")

