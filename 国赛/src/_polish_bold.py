# -*- coding: utf-8 -*-
r"""机械加粗清理 —— 去掉句中对**普通词**的加粗.

判定标准 (只删这一档, 不碰术语与结论):
  * 被加粗的是虚词/否定词/程度词/普通形容词或动词, 如 不会、任意、正、低于、渐近;
  * 加粗出现在句子中间, 起"标点式强调"作用, 删掉后句子信息量不变.
保留: 方法名 (物质坐标、事件定位、阻尼 Newton)、模型选择结论 (非保守形式、
物质坐标)、以及结果性判断 (逐位一致、相差仅 …).

用法: python src/_polish_bold.py [--dry-run]
"""
from __future__ import annotations

import os
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, "paper", "example.tex")
DRY = "--dry-run" in sys.argv

PAIRS = [
    ("方程\\textbf{不会}残留含收缩速率的项", "方程不会残留含收缩速率的项"),
    ("离散框架\\textbf{完全同构}", "离散框架完全同构"),
    ("下式在\\textbf{任意}基准下精确成立", "下式在任意基准下精确成立"),
    ("表面温度在最初阶段\\textbf{低于初温}", "表面温度在最初阶段低于初温"),
    ("温度场的形态与问题一\\textbf{明显不同}", "温度场的形态与问题一明显不同"),
    ("而问题二中\\textbf{先增后减}", "而问题二中先增后减"),
    ("水分场的形态同样与问题一\\textbf{质的不同}", "水分场的形态同样与问题一质的不同"),
    ("说明其\\textbf{量级}", "说明其量级"),
    ("决定蒸发项权重而\\textbf{温度依赖}影响很小", "决定蒸发项权重而温度依赖影响很小"),
    ("（扩散\\textbf{推动力}）", "（扩散推动力）"),
    ("的特征时间\\textbf{渐近}逼近环境水平", "的特征时间渐近逼近环境水平"),
    ("\\textbf{低于}四位小数阈值", "低于四位小数阈值"),
    ("是环境外推中\\textbf{占主导}的敏感性", "是环境外推中占主导的敏感性"),
    ("共同界定了该前提的\\textbf{裕度}", "共同界定了该前提的裕度"),
    ("\\textbf{精确}推进，不需要任何数值求积", "精确推进，不需要任何数值求积"),
    ("轴向穿透\\textbf{自窒息}", "轴向穿透自窒息"),
    ("均为\\textbf{正}，", "均为正，"),
]


def main() -> int:
    src = open(TEX, encoding="utf-8", newline="").read()
    before = src.count("\\textbf")
    bad = [(o, src.count(o)) for o, _ in PAIRS if src.count(o) != 1]
    if bad:
        print("!! 匹配数不为 1, 中止:")
        for o, n in bad:
            print(f"   {n} 次  {o!r}")
        return 1
    out = src
    for o, n in PAIRS:
        out = out.replace(o, n, 1)
    after = out.count("\\textbf")
    print(f"\\textbf 计数: {before} -> {after}  (本次删除 {len(PAIRS)} 处)")
    if DRY:
        print("--dry-run: 未写文件")
        return 0
    bak = TEX + time.strftime(".bak_bold_%Y%m%d_%H%M%S")
    open(bak, "w", encoding="utf-8", newline="").write(src)
    open(TEX, "w", encoding="utf-8", newline="").write(out)
    chk = open(TEX, encoding="utf-8", newline="").read()
    ok = chk.count("\\textbf") == after
    print(f"备份 {os.path.basename(bak)};  回读校验 {'OK' if ok else '!! 失败'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
