"""问题四核心：复合矩形模块（矩形切割 + 刚性链接）表示、C4 旋转与复合 Skyline 装箱。

建模思想（《问题4_数学建模.md》修正1-6）：
  * 每个异形模块切割为若干轴平行矩形子块，子块间通过刚性链接（硬约束 G1）
    保持固定相对位移 —— 子块绝对坐标 = 锚点 + 固定偏移，链接被烘进变量；
  * C4 旋转群 r∈{0,1,2,3}，旋转作用于整个模块，子块尺寸/偏移随旋转查表变换；
  * 装箱时整模落位：放置一个模块即校验其全部子块占用格空闲且不越界。

数据结构：布尔占用位图 OCC，S≤2 子块/模块、4 模块实例规模下 O(nWH) 向量化。
"""
from __future__ import annotations

import numpy as np

from packing import lex_key


class CompoundModule:
    """复合矩形模块：子块 (w, h, a, b)，其中 (a,b) 为相对模块锚点（左下角）的局部偏移。"""

    def __init__(self, name: str, subblocks):
        # subblocks: list of (w, h, a, b)
        self.name = name
        self.subblocks = [(int(w), int(h), int(a), int(b)) for w, h, a, b in subblocks]
        self.area = sum(w * h for w, h, _, _ in self.subblocks)
        self.bbox = self._bbox(self.subblocks)

    @staticmethod
    def _bbox(subs):
        xs = [a for _, _, a, _ in subs] + [a + w for w, _, a, _ in subs]
        ys = [b for _, _, _, b in subs] + [b + h for _, h, _, b in subs]
        return max(xs) - min(xs), max(ys) - min(ys)

    # ------------------------------------------------------------------ #
    # C4 旋转（作用于整个模块）：子块尺寸与偏移随旋转查表变换
    # ------------------------------------------------------------------ #
    def rotated(self, r: int):
        """返回旋转 r∈{0,1,2,3} 后的子块列表 [(w,h,a,b), ...]。

        旋转后整体平移到非负象限，锚点仍为模块包围盒左下角。
        90°CW: (x,y)->(y,-x)；180°: (-x,-y)；270°CW: (-y,x)。
        """
        if r == 0:
            return list(self.subblocks)
        # 对所有子块角点做 C4 变换
        pts = []
        for w, h, a, b in self.subblocks:
            for cx, cy in ((a, b), (a + w, b), (a + w, b + h), (a, b + h)):
                if r == 1:
                    pts.append((cy, -cx))
                elif r == 2:
                    pts.append((-cx, -cy))
                else:
                    pts.append((-cy, cx))
        x0 = min(p[0] for p in pts)
        y0 = min(p[1] for p in pts)
        out = []
        for w, h, a, b in self.subblocks:
            corners = []
            for cx, cy in ((a, b), (a + w, b), (a + w, b + h), (a, b + h)):
                if r == 1:
                    corners.append((cy - x0, -cx - y0))
                elif r == 2:
                    corners.append((-cx - x0, -cy - y0))
                else:
                    corners.append((-cy - x0, cx - y0))
            xs = [p[0] for p in corners]
            ys = [p[1] for p in corners]
            out.append((max(xs) - min(xs), max(ys) - min(ys), min(xs), min(ys)))
        return out

    # ------------------------------------------------------------------ #
    # 占用格 / 可行性判定
    # ------------------------------------------------------------------ #
    def fits(self, r: int, x: int, y: int, occ, W: int, H: int) -> bool:
        """锚点 (x,y) + 旋转 r 时，全部子块是否空闲且不越界。"""
        for w, h, a, b in self.rotated(r):
            x0, y0 = x + a, y + b
            if x0 < 0 or y0 < 0 or x0 + w > W or y0 + h > H:
                return False
            for px in range(x0, x0 + w):
                for py in range(y0, y0 + h):
                    if (px, py) in occ:
                        return False
        return True

    def place(self, r: int, x: int, y: int, occ):
        for w, h, a, b in self.rotated(r):
            for px in range(x + a, x + a + w):
                for py in range(y + b, y + b + h):
                    occ.add((px, py))

    def unplace(self, r: int, x: int, y: int, occ):
        for w, h, a, b in self.rotated(r):
            for px in range(x + a, x + a + w):
                for py in range(y + b, y + b + h):
                    occ.discard((px, py))

    def occupied_cells(self, r: int, x: int, y: int) -> set:
        s = set()
        for w, h, a, b in self.rotated(r):
            for px in range(x + a, x + a + w):
                for py in range(y + b, y + b + h):
                    s.add((px, py))
        return s


# --------------------------------------------------------------------------- #
# 复合 Skyline 装箱（L1/L2 共用）
# --------------------------------------------------------------------------- #
def pack_compound(modules, order, rot, bound_w, bound_h, auto_rotate=False):
    """复合 Skyline 装箱：整模落位，返回 (xs, ys, rot_used, W, H) 或 None。

    Args:
        modules: list[CompoundModule]
        order:   模块序号放置顺序
        rot:     per-module 旋转 (r∈{0,1,2,3})，auto_rotate=True 时被覆盖
        bound_w/bound_h: 扫描范围上界
        auto_rotate: 每个模块在 C4 中贪心选"最低、最左"落位。
    """
    n = len(order)
    occ = set()
    xs = [0] * n
    ys = [0] * n
    rot_used = [0] * n
    for m in order:
        mod = modules[m]
        r_range = range(4) if auto_rotate else [int(rot[m])]
        best = None
        for r in r_range:
            rsubs = mod.rotated(r)
            max_x = max(a + w for w, h, a, b in rsubs)
            max_y = max(b + h for w, h, a, b in rsubs)
            # 最低、最左：逐 y 行找最左可行 x
            for y in range(max(0, bound_h - max_y) + 1):
                found = None
                for x in range(max(0, bound_w - max_x) + 1):
                    if mod.fits(r, x, y, occ, bound_w, bound_h):
                        found = x
                        break
                if found is not None:
                    cand = (y, found, r)
                    if best is None or cand[:2] < best[:2]:
                        best = cand
                    break
        if best is None:
            return None
        y, x, r = best
        xs[m], ys[m], rot_used[m] = x, y, r
        mod.place(r, x, y, occ)
    W = int(max(xs[m] + a + w for m in range(n)
                for w, h, a, b in modules[m].rotated(rot_used[m])))
    H = int(max(ys[m] + b + h for m in range(n)
                for w, h, a, b in modules[m].rotated(rot_used[m])))
    return xs, ys, rot_used, W, H


def bbox_of_modules(modules):
    """每个模块的包围盒矩形 (w, h)（B*-树对照用）。"""
    return [(m.bbox[0], m.bbox[1]) for m in modules]


def lex_cost_q4(W: int, H: int) -> int:
    """字典序目标：面积最小 → 长宽比接近 1（与问题1一致）。"""
    key = lex_key(W, H)
    return key[0] * 10_000_000 + key[1]
