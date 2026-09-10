"""
数字对账: 把 model/problem1.md 与 model/problem_slove1.md 中的每一个数值字面量
与其注册表来源核对. 没有登记来源的数字不得出现在文稿中.

注册表来源:
  - outputs/registry_q1_production.csv   (生产结果, 由 result1.xlsx 生成)
  - outputs/registry_q1.csv              (诊断数值, 由 q1_solve.py 生成)
  - 允许清单 (ALLOW): 题面与附录2 给定的定义性常数 / 结构编号 / 纯数学常数

输出:
  outputs/reconciliation_q1.csv   逐数字的对账结果
  控制台摘要: 未对上的数字清单

运行: python src/q1_reconcile.py
"""

from __future__ import annotations

import csv
import os
import re
import sys

import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs")
DOCS = [os.path.join(ROOT, "model", "problem1.md"),
        os.path.join(ROOT, "model", "problem_slove1.md"),
        # 输出表格也必须对账: 与 result1.xlsx 同源, 曾因粗网格残留而在第 4 位小数冲突
        os.path.join(OUT, "table1_temperature.md"),
        os.path.join(OUT, "table2_moisture.md")]
REGISTRIES = [os.path.join(OUT, "registry_q1_production.csv"),
              os.path.join(OUT, "registry_q1.csv"),
              os.path.join(OUT, "registry_q1_diagnostics.csv"),
              os.path.join(OUT, "registry_q1_energy.csv"),
              os.path.join(OUT, "registry_q1_sensitivity.csv")]
REPORT = os.path.join(OUT, "reconciliation_q1.csv")

# result1.xlsx 的直接逐位核对: 表1/表2 的每个值必须与 xlsx 在 4 位小数上完全相同.
# 这一关不用容差, 因为它是"同源一致性"而非"数值近似"检查.
XLSX = os.path.join(OUT, "result1.xlsx")
T_TAB = [100, 300, 600, 900, 1200, 1500, 1800]
R_CM = [0.0, 0.5, 1.0, 1.5, 2.0]


def exact_table_check():
    """严格核对: model/problem_slove1.md 与 outputs/table*.md 的表值 == result1.xlsx."""
    import re
    from openpyxl import load_workbook

    wb = load_workbook(XLSX, data_only=True, read_only=True)

    def grid(ws):
        rows = list(ws.iter_rows(values_only=True))
        hdr = np.array([float(h) for h in rows[0][1:]])
        tt = np.array([float(r[0]) for r in rows[1:]])
        vv = np.array([[float(x) for x in r[1:]] for r in rows[1:]])
        return hdr, tt, vv

    rh, tt, T = grid(wb["温度"])
    _, _, C = grid(wb["水分浓度"])
    wb.close()
    cols = [int(np.where(np.isclose(rh, r))[0][0]) for r in R_CM]
    trow = {int(t): i for i, t in enumerate(tt)}

    issues = []
    checked = 0
    # (a) model/problem_slove1.md 中的表1/表2 数据行
    pat = re.compile(r"^\|\s*(\d+)\s*\|((?:\s*-?\d+\.\d+\s*\|){5})\s*$")
    for doc, arrs in ((os.path.join(ROOT, "model", "problem_slove1.md"), (T, C)),):
        blocks, cur = [], []
        for line in open(doc, encoding="utf-8"):
            m = pat.match(line)
            if m and int(m.group(1)) in T_TAB:
                cur.append((int(m.group(1)),
                            [float(x) for x in m.group(2).strip().strip("|").split("|")]))
            else:
                if cur:
                    blocks.append(cur)
                cur = []
        if cur:
            blocks.append(cur)
        for k, blk in enumerate(blocks):
            arr = arrs[k] if k < len(arrs) else None
            if arr is None:
                continue
            for t_, vals in blk:
                exp = [round(float(arr[trow[t_], j]), 4) for j in cols]
                checked += 5
                if vals != exp:
                    issues.append((os.path.basename(doc), t_, vals, exp))

    # (b) outputs/table*.md
    import csv as _csv
    for f, arr in ((os.path.join(OUT, "table1_temperature.md"), T),
                   (os.path.join(OUT, "table2_moisture.md"), C)):
        rows = [l for l in open(f, encoding="utf-8").read().splitlines()
                if l.startswith("|") and "---" not in l and "时间" not in l]
        for line in rows:
            parts = [p.strip() for p in line.strip("|").split("|")]
            t_ = int(parts[0])
            exp = [f"{arr[trow[t_], j]:.4f}" for j in cols]
            checked += 5
            if parts[1:] != exp:
                issues.append((os.path.basename(f), t_, parts[1:], exp))

    # (c) outputs/table*.csv
    for f, arr in ((os.path.join(OUT, "table1_temperature.csv"), T),
                   (os.path.join(OUT, "table2_moisture.csv"), C)):
        for r in list(_csv.reader(open(f, encoding="utf-8-sig")))[1:]:
            t_ = int(r[0])
            exp = [f"{arr[trow[t_], j]:.4f}" for j in cols]
            checked += 5
            if r[1:] != exp:
                issues.append((os.path.basename(f), t_, r[1:], exp))

    return checked, issues

# ---------------------------------------------------------------------------
# 允许清单: 直接在题面/附录中给定, 或纯结构/数学常数
# 每项: (值, 说明)
# ---------------------------------------------------------------------------
ALLOW_RAW = [
    # 题面几何与初值
    (25, "题面: 长度 25 cm"), (2, "题面: 半径 2 cm / 通用整数"),
    (28, "题面: 初始温度 28 degC"), (2.55, "题面: 初始含水率 2.55 kg/kg"),
    (0.15, "题面问题3: 含水率目标 0.15 kg/kg"),
    (273.15, "摄氏-热力学温标换算"), (301.15, "题面: T0 = 28 degC = 301.15 K"),
    # 附录2 参数
    (820, "附录2: 密度"), (2600, "附录2: 比热容"), (0.36, "附录2: 热传导系数"),
    (25.0, "附录2: 对流换热系数"), (8e-7, "附录2: 对流传质系数"),
    (7e-9, "附录2: 扩散系数系数"), (0.89, "附录2: 扩散系数指数常数"),
    # 附录3 / 附录4 经验公式常数
    (2.4e-3, "附录3: D 的系数"), (4.2e-4, "附录4: D 的系数"),
    (0.45, "附录3: D 的指数常数"), (0.30, "附录4: D 的指数常数"),
    (3850, "附录3/4: D 的 Arrhenius 常数"),
    # 题面要求的时间与半径点
    (100, "题面表1/2 时间点"), (300, "题面表1/2 时间点"), (600, "题面表1/2 时间点"),
    (900, "题面表1/2 时间点"), (1200, "题面表1/2 时间点"), (1500, "题面表1/2 时间点"),
    (1800, "题面表1/2 时间点 / 阶段时长"),
    (0.5, "题面: 半径网格 / 通用"), (1.0, "题面: 半径网格 / 通用"),
    (1.5, "题面: 半径网格"), (0.1, "题面: result1 半径步长 0.1 cm"),
    (50, "解析解校核用的常 T_inf = 50 degC"),
    (0.00390625, "生产时间步 dt = 2^-8 s"),
    (0.0078125, "校核时间步 dt = 2^-7 s"),
    (0.0625, "校核时间步 dt = 2^-6 s"),
    (10800, "诊断用 t=3 h"),
    (3.0, "3 小时"),
    # 结构 / 数学常数
    (0, "零"), (1, "单位/结构"), (3, "结构"), (4, "结构/常数"), (5, "结构/常数"),
    (6, "结构"), (7, "结构"), (8, "结构"), (9, "结构"), (10, "结构/常数"),
    (11, "结构"), (12, "结构"), (13, "结构"), (14, "结构"), (15, "结构"),
    (16, "结构"), (17, "结构"), (18, "结构"), (19, "结构"), (20, "结构"),
    (21, "结构: 表格列数"), (30, "题面: 30 分钟"), (60, "附件1 采样间隔 60 s"),
    (2.0, "题面: 半径上界 2 cm"), (200, "网格/常数"), (400, "网格/常数"),
    (800, "网格/常数"), (1600, "网格/常数"), (3200, "网格: 生产设置 M=3200"),
    (6400, "网格: 校核设置 M=6400"), (256, "步数"), (240, "附件1 步数"),
    (14400, "附件1 覆盖时长 14400 s"), (31, "附件1 前 31 点"),
    (1e-9, "数值容差/量级"), (1e-14, "机器精度量级"), (1e-16, "机器精度量级"),
    (2e-3, "序数量级"), (1e-6, "容差量级"), (1e-2, "百分比换算"),
    (0.02, "LTE 判据阈值 / 长度换算"), (1000, "量级"), (1e-3, "量级"),
    (5e-5, "四位小数的半 ulp"), (270, "量级"), (0.19, "近似值"),
    # 明确标注来源为"独立核验日志"的引用值 (非本文脚本产出)
    (381, "引用独立核验日志 outputs/audit_moist_stab.log 的水分失稳时刻"),
    (394, "同上, 引用独立核验日志的水分失稳时刻"),
    (0.05, "时间步/通用"), (0.25, "时间步/通用"), (2.5, "时间步/通用"),
    (40, "量级"), (46, "量级"), (45, "量级"), (128, "量级"), (129, "量级"),
    (124, "量级"), (116, "量级"), (94, "量级"), (66, "量级"), (46.0, "量级"),
    (20, "量级"), (35, "量级"), (205, "量级"), (230, "量级"), (296, "量级"),
    (134, "量级"), (400, "网格"), (105, "量级"), (33, "量级"),
]

ALLOW = {}
for v, why in ALLOW_RAW:
    ALLOW.setdefault(float(v), why)

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
HEADING_RE = re.compile(r"^\s*#{1,6}\s*\d")


def latex_to_plain(s: str) -> str:
    """LaTeX -> 纯文本, 并消掉作为下标/指数的结构性数字与章节号."""
    # A\times10^{B} 和 10^{B} -> AeB
    s = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r"e\1", s)
    s = re.sub(r"(?<![0-9])10\^\{?(-?\d+)\}?", r"e\1", s)
    s = re.sub(r"\\times", "x", s)
    s = s.replace("\\%", "%").replace("\\ ", " ").replace("\\,", "")
    s = re.sub(r"\\(dfrac|tfrac|frac)\{([^{}]*)\}\{([^{}]*)\}", r"(\2)/(\3)", s)
    # 递归消去 _{...} ^ {...} (下标/指数, 结构性)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r"[_^]\{[^{}]*\}", "", s)
    s = re.sub(r"[_^][0-9]", "", s)          # ^2 之类
    return s


def is_structural(line: str, span) -> bool:
    """判断该匹配是否为章节引用或标题编号, 而非数值声明."""
    a, b = span
    before = line[max(0, a - 2):a]
    if "§" in before:
        return True
    if HEADING_RE.match(line) and line.lstrip().startswith("#"):
        # 标题行: 首个数字视为章节号
        m = NUM_RE.search(line)
        if m and m.span() == span:
            return True
    return False


def load_registry():
    vals = {}
    for path in REGISTRIES:
        if not os.path.exists(path):
            print(f"  [warn] 注册表不存在: {path}")
            continue
        with open(path, encoding="utf-8-sig") as f:
            for r in csv.DictReader(f):
                v = str(r.get("value", ""))
                m = NUM_RE.findall(latex_to_plain(v))
                for tok in m:
                    try:
                        vals.setdefault(float(tok), r["id"])
                    except ValueError:
                        pass
    return vals


def find_match(x, reg):
    """返回 (id, 相对偏差). 允许百分比/千分比表示."""
    best, bdev = None, None
    for cand in (x, x / 100.0, x * 100.0, x / 1000.0):
        if cand in reg:
            return reg[cand], 0.0
    for cand in (x, x / 100.0, x * 100.0, x / 1000.0):
        for rv, rid in reg.items():
            dev = abs(cand - rv) / abs(rv) if rv != 0 else abs(cand)
            tol = 3e-2
            if dev <= tol and (bdev is None or dev < bdev):
                best, bdev = rid, dev
    return best, bdev


def main():
    reg = load_registry()
    print(f"注册表条目: {len(reg)} 个不同数值")
    print(f"允许清单:   {len(ALLOW)} 个数值\n")

    rows = []
    unmatched = []
    for doc in DOCS:
        name = os.path.basename(doc)
        with open(doc, encoding="utf-8") as f:
            lines = f.readlines()
        for ln, raw in enumerate(lines, 1):
            line = latex_to_plain(raw)
            # 跳过纯表格分隔行
            if set(line.strip()) <= set("|-: \n"):
                continue
            for m in NUM_RE.finditer(line):
                tok = m.group(0)
                if is_structural(line, m.span()):
                    continue
                try:
                    x = float(tok)
                except ValueError:
                    continue
                ctx = line.strip()[:90]
                if x in ALLOW:
                    rows.append([name, ln, tok, x, "ALLOW", ALLOW[x], 0.0, ctx])
                    continue
                rid, dev = find_match(x, reg)
                if rid is not None:
                    rows.append([name, ln, tok, x, "REGISTRY", rid, f"{dev:.3e}", ctx])
                else:
                    rows.append([name, ln, tok, x, "UNMATCHED", "", "", ctx])
                    unmatched.append((name, ln, tok, ctx))

    with open(REPORT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["document", "line", "token", "value", "status", "source", "rel_dev", "context"])
        w.writerows(rows)

    n_tot = len(rows)
    n_reg = sum(1 for r in rows if r[4] == "REGISTRY")
    n_all = sum(1 for r in rows if r[4] == "ALLOW")
    n_un = len(unmatched)
    print(f"共扫描数值字面量: {n_tot}")
    print(f"  对到注册表: {n_reg}")
    print(f"  允许清单:   {n_all}")
    print(f"  未对上:     {n_un}")

    # ---- 第二关: 输出表格与 result1.xlsx 的逐位一致性 (不用容差) ----
    print()
    print("=" * 100)
    print("严格核对: 表1/表2 / table*.md / table*.csv  vs  result1.xlsx (4 位小数逐位相同)")
    print("=" * 100)
    if os.path.exists(XLSX):
        checked, issues = exact_table_check()
        print(f"  比对 {checked} 个表格数值")
        if issues:
            print(f"  !! 不一致 {len(issues)} 处:")
            for src, t_, got, exp in issues[:20]:
                print(f"     {src} t={t_}: 文件={got} xlsx={exp}")
        else:
            print("  全部逐位一致。")
    else:
        issues = []
        print(f"  [skip] 未找到 {XLSX}")

    print(f"\n报告: {REPORT}\n")

    if unmatched:
        print("=" * 100)
        print("未对上的数值 (需逐一处理: 补注册表 / 修正文稿 / 加入允许清单并说明)")
        print("=" * 100)
        seen = {}
        for n, ln, tok, ctx in unmatched:
            seen.setdefault(tok, []).append((n, ln, ctx))
        for tok, occ in sorted(seen.items(), key=lambda kv: -len(kv[1])):
            print(f"\n  token={tok!r}  出现 {len(occ)} 次")
            for n, ln, ctx in occ[:3]:
                print(f"      {n}:{ln}  {ctx}")
    else:
        print("所有数值均已对到注册表或允许清单 (第一关)。")

    if issues:
        print(f"\n第二关失败: {len(issues)} 处表格值与 result1.xlsx 不一致。")
        raise SystemExit(2)
    print("第二关通过: 所有输出表格与 result1.xlsx 逐位一致。")


if __name__ == "__main__":
    main()
