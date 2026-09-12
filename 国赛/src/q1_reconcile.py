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
        os.path.join(ROOT, "model", "温度场两种解法.md"),
        # 输出表格也必须对账: 与 result1.xlsx 同源, 曾因粗网格残留而在第 4 位小数冲突
        os.path.join(OUT, "table1_temperature.md"),
        os.path.join(OUT, "table2_moisture.md")]
REGISTRIES = [os.path.join(OUT, "registry_q1_production.csv"),
              os.path.join(OUT, "registry_q1.csv"),
              os.path.join(OUT, "registry_q1_diagnostics.csv"),
              os.path.join(OUT, "registry_q1_energy.csv"),
              os.path.join(OUT, "registry_q1_sensitivity.csv"),
              os.path.join(OUT, "registry_q1_analytic_fit.csv"),
              os.path.join(OUT, "registry_q1_ana_vs_num.csv"),
              os.path.join(OUT, "registry_q1_piecewise.csv"),
              os.path.join(OUT, "registry_q1_uncertainty.csv"),
              os.path.join(OUT, "registry_feishu.csv"),
              os.path.join(OUT, "registry_q1_smooth.csv")]
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


TEX = os.path.join(ROOT, "paper", "example.tex")


def xval_range(lines):
    """定位 example.tex 中「温度场交叉验证」节的行区间 [i0, i1).

    该节原在「问题一模型的建立与求解」之内（以 `\\subsubsection{...}` 开头、以下一个
    `\\subsubsection{求解某一时刻下药材各个位置的水分浓度}` 结尾）。为把问题一的建模
    部分压到 6 页，它已整体移入附录（以附录 `\\section` 开头、以
    `\\section{附录：结果文件与源程序}` 结尾）。

    **两种形态都必须支持**：只认其中一种时，另一种会让本关返回「未定位到交叉验证节」
    而被**静默跳过**（不是报错），于是 50 个表格值悄悄失去校验 —— 这正是本函数存在的
    理由。调用方若拿到 (None, None) 应给出显式提示。
    """
    for i, l in enumerate(lines):
        if l.startswith(r"\section{附录：温度场解析解的交叉验证"):
            for j in range(i + 1, len(lines)):
                if lines[j].startswith(r"\section{附录：结果文件与源程序}"):
                    return i, j
            return i, len(lines)
    # 回退：旧形态（仍在问题一建模部分内）
    i0 = next((i for i, l in enumerate(lines)
               if "交叉验证：Bessel特征函数展开解析解" in l), None)
    if i0 is None:
        return None, None
    i1 = next((i for i, l in enumerate(lines)
               if i > i0
               and l.startswith(r"\subsubsection{求解某一时刻下药材各个位置的水分浓度")),
              None)
    return (i0, i1) if i1 is not None else (None, None)


def tex_xval_check():
    """第三关: paper/example.tex 交叉验证节的三个表 与注册表逐位一致.

    与第二关同理, 这是"同源一致性"检查而非数值近似检查, 故容差按各表在文稿中
    书写的有意义位数给定 (不套用宽松的百分比容差):
      表 11 特征根 x_k : 书写 10 位有效数字 -> 相对容差 1e-9
      表 11 展开系数 c_k: 书写  6~7 位有效数字 -> 相对容差 1e-5
      表 11 衰减率 mu_k: 书写  5 位有效数字 -> 相对容差 1e-4
      表 D 偏差       : 书写  3 位有效数字 -> 相对容差 6e-3
    """
    if not os.path.exists(TEX):
        return 0, [], "tex 不存在"

    lines = open(TEX, encoding="utf-8").read().splitlines()
    i0, i1 = xval_range(lines)
    if i0 is None or i1 is None:
        return 0, [], "未定位到交叉验证节"
    reg = {}
    for path in REGISTRIES:
        if not os.path.exists(path):
            continue
        for r in csv.DictReader(open(path, encoding="utf-8-sig")):
            reg.setdefault(r["id"], r["value"])

    def fields(line):
        """把 tex 表行按 & 拆开, 每段取第一个数值."""
        out = []
        for part in line.split("&"):
            p = latex_to_plain(part)
            m = NUM_RE.search(p)
            if m:
                try:
                    out.append(float(m.group(0)))
                except ValueError:
                    pass
        return out

    issues = []
    checked = 0
    seg = list(enumerate(lines[i0:i1], i0 + 1))

    for ln, raw in seg:
        s = raw.strip()
        if not s or s.startswith("\\") or "toprule" in s or "midrule" in s or "bottomrule" in s:
            continue
        if "&" not in s:
            continue
        if "\\\\" not in s:
            continue
        vals = fields(s)

        # --- 表 A: 4 个字段, 首列为阶数 1..5 ---
        if len(vals) == 4 and vals[0] == int(vals[0]) and 1 <= vals[0] <= 5:
            k = int(vals[0])
            # 容差按文稿实际书写位数: x_k 10 位有效数字; c_k 6~7 位; mu_k 5 位.
            for col, tol, pref in ((1, 1e-9, "S3x_"), (2, 1e-5, "S3c_"), (3, 1e-4, "S3m_")):
                rv = float(reg.get(f"{pref}{k}", "nan"))
                tv = vals[col]
                checked += 1
                rel = abs(tv - rv) / abs(rv) if rv else abs(tv)
                if not (rel <= tol):
                    issues.append((f"表11 k={k} {pref}", tv, rv, f"rel={rel:.2e}"))
            continue

        # --- 表 D: 6 个字段, 首列为时间 (键名沿用注册表的半径标签) ---
        if len(vals) == 6 and vals[0] in (100, 300, 600, 900, 1200, 1500, 1800):
            t_ = int(vals[0])
            for j, rc in enumerate(["0", "0.5", "1.0", "1.5", "2.0"]):
                rv = float(reg.get(f"HD_T{t_}_r{rc}", "nan")) * 1e6   # K -> 1e-6 K
                tv = vals[1 + j]
                checked += 1
                rel = abs(tv - rv) / abs(rv) if rv else abs(tv)
                if not (rel <= 6e-3):
                    issues.append((f"表D t={t_} r={rc}", tv, rv, f"rel={rel:.2e}"))
    return checked, issues, ""


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
    # 时间步实验的步数 = 1800/Δt, 属实验网格设置 (结构性, 非测算值)
    (28800, "步数 = 1800/0.0625 s, §11.3 时间收敛实验设置"),
    (57600, "步数 = 1800/0.03125 s, §11.3 时间收敛实验设置"),
    (115200, "步数 = 1800/0.015625 s, §11.3 时间收敛实验设置"),
    (230400, "步数 = 1800/0.0078125 s, §11.3 时间收敛实验设置"),
    (460800, "步数 = 1800/0.00390625 s, §11.3 时间收敛实验设置"),
    (921600, "步数 = 1800/0.001953125 s, §11.3 时间收敛实验设置"),
    # 空气物性: 来自教科书常识/记忆, 未检索原始文献. 仅用于 §7.2 的量级论证,
    # 不进入任何计算结果. 与 claims ledger 的 C17 一致标注为 INFERENCE.
    (1005, "[未检索] 空气定压比热 c_p,a ≈ 1005 J/(kg·K), 凭记忆的教科书值, 仅作量级论证"),
    (0.05, "时间步/通用"), (0.25, "时间步/通用"), (2.5, "时间步/通用"),
    (40, "量级"), (46, "量级"), (45, "量级"), (128, "量级"), (129, "量级"),
    (124, "量级"), (116, "量级"), (94, "量级"), (66, "量级"), (46.0, "量级"),
    (20, "量级"), (35, "量级"), (205, "量级"), (230, "量级"), (296, "量级"),
    (134, "量级"), (400, "网格"), (105, "量级"), (33, "量级"),
    # 数值量级/容差 (以 1eN 形式书写的数量级声明, 非测算值)
    (1e-7, "数值量级"), (1e-8, "数值量级"), (1e-11, "数值量级"),
    (1e-12, "数值量级/收敛判据"), (1e-13, "数值量级/ODE 容差"),
    (1e-15, "数值量级/机器精度"), (1e-10, "数值量级/积分容差"),
    # 结构性数字: 年份 / 模态数 / 时间窗标签 / 网格标签
    (2026, "年份: 2026 高教社杯"), (120, "模态数 / 级数项数"),
    (99, "时间窗标签 t=10..99 s"), (599, "时间窗标签 t=100..599 s"),
    (9, "时间窗标签 t=1..9 s"),
    (0.03125, "时间步 Δt = 2^-5 s"), (0.015625, "时间步 Δt = 2^-6 s"),
    (0.02500, "网格尺寸 Δr = 0.0250 mm (表格标签)"),
    (0.01250, "网格尺寸 Δr = 0.0125 mm (表格标签)"),
    (0.0125, "网格尺寸 Δt = 0.0125 s / Δr = 0.0125 mm"),
    (0.125, "时间步 Δt = 0.125 s (诊断设置)"),
    (853, "[已由 G11=838.25 推出] '超过 838 倍' 附近的口头表述, 见 G11"),
    # --- 被对照的"原方案/用户原文"数值: 不是本文产出, 仅用于指出差异 ---
    (1.679e-7, "原始建模思路中写出的 alpha 值, 用于对照 (实为 1.6886e-7)"),
    # --- 附录2 公式中的常数 (带符号形式) ---
    (-0.89, "附录2 D 公式中的指数常数 -0.89"),
    # --- 纯结构/编号: 章节号、软件版本号、注册表 ID 区间、公式系数常数 ---
    (9.3, "章节号 §9.2—9.3"), (3.12, "软件版本 Python 3.12.3"),
    (1.18, "软件版本 scipy 1.18.1"), (3.1, "软件版本 openpyxl 3.1.2"),
    (44, "注册表 ID 区间 E40–E44"),
    (-4, "离散系数中的常数 -4 (中心节点 b0/c0 的因子)"),
    (0.001953125, "时间步 Δt = 2^-9 s (实验设置)"),
    # --- 已撤销实验的历史记录值: 保留在 §11.3 的更正中, 用于说明误读陷阱 ---
    #     这些数字来自当时的实际运行, 该实验已从代码中移除; 标注为历史记录.
    (4.38e-6, "已撤销实验的历史记录 (M-加密平台, 见 §11.3 更正)"),
    (3.90e-6, "已撤销实验的历史记录 (同上)"),
    (3.78e-6, "已撤销实验的历史记录 (同上)"),
    (1.03, "已撤销实验的历史记录 (收敛比值 1.12/1.03/1.01)"),
    (1.01, "已撤销实验的历史记录 (同上)"),
    (1.12, "已撤销实验的历史记录 (同上)"),
]

ALLOW = {}
for v, why in ALLOW_RAW:
    ALLOW.setdefault(float(v), why)

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?")
HEADING_RE = re.compile(r"^\s*#{1,6}\s*\d")


def latex_to_plain(s: str) -> str:
    r"""LaTeX -> 纯文本, 并消掉作为下标/指数的结构性数字与章节号.

    同时清理 LaTeX 命令中**不表示测量值**的数字 (环境名、标签、间距、
    占位符、列宽、版面参数), 否则 \ding{228} 的 228、\hspace*{1em} 的 1、
    p{0.72\textwidth} 的 0.72、\renewcommand{\arraystretch}{1.38} 的 1.38
    都会被当成待核对数值而误报.
    这些命令在 Markdown 中不出现, 故对本函数原有的 .md 使用者无影响.
    """
    # --- LaTeX 命令清理 (对 .md 无副作用) ---
    s = re.sub(r"\\(ding|phantom)\{[^{}]*\}", "", s)          # \ding{228}, \phantom{-}
    s = re.sub(r"\\(hspace|vspace|hskip|vskip)\*?\{[^{}]*\}", "", s)
    s = re.sub(r"\\(begin|end)\{[^{}]*\}", "", s)             # 环境名
    s = re.sub(r"\\(label|ref|eqref|cite|cref)\{[^{}]*\}", "", s)  # 标签/引用
    # 版面参数: \renewcommand{\arraystretch}{1.38} / \setlength{\x}{3em}
    # 整条命令一起消掉 —— 比把 1.38 放进允许清单更彻底, 因为后者只掩盖症状.
    s = re.sub(r"\\(renewcommand|newcommand|providecommand|setlength|addtolength)"
               r"\*?\{[^{}]*\}(?:\{[^{}]*\})?", "", s)
    s = re.sub(r"\\(textwidth|linewidth|columnwidth|textheight)", "", s)
    # tabular 列定义: 去掉 @{} 与 p{宽度}, 否则列宽数字 (如 p{0.72\textwidth} 的 0.72)
    # 会被当成待核对数值 (已实测发生).
    s = re.sub(r"@\{\}", "", s)
    s = re.sub(r"p\{[^{}]*\}", "", s)
    s = re.sub(r"\\quad|\\qquad", " ", s)
    s = re.sub(r"\\(left|right|bigl|bigr|Bigl|Bigr)\b", "", s)
    # A\times10^{B} 和 10^{B} -> AeB / 1eB
    s = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r"e\1", s)
    # 独立的 10^{B} 必须补上前导 1, 否则会留下裸的 "e-13",
    # 其 "-13" 会被 NUM_RE 当成一个独立数字而误报 (已实测发生过).
    s = re.sub(r"(?<![0-9])10\^\{?(-?\d+)\}?", r"1e\1", s)
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


def _written_tol(tok: str) -> float:
    """由 token 的书写精度推出允许的绝对偏差.

    原理: 文稿中写出的数字是对注册值的**四舍五入**. 若 token 写了 k 位小数,
    则舍入误差不超过最后一位的半个单位, 即 0.5*10^-k. 取 1.5 倍余量以容纳
    注册值本身也被舍入的情形.

    这比"固定百分比容差"严格得多, 且能挡住大数误配: 例如 token '70.9236'
    只允许 |偏差| <= 7.5e-5, 不会误配到相差 0.41 的无关注册值.
    """
    s = tok.strip().lower()
    if "e" in s:
        mant, _, exp = s.partition("e")
        try:
            e = int(exp)
        except ValueError:
            return 0.0
        dec = len(mant.split(".")[1]) if "." in mant else 0
        return 0.5 * (10.0 ** (-dec)) * (10.0 ** e) * 1.5
    dec = len(s.split(".")[1]) if "." in s else 0
    return 0.5 * (10.0 ** (-dec)) * 1.5


def find_match(x, reg, tok=None, pct=False):
    """返回 (id, 偏差), 或 (None, None).

    匹配规则 (经多次误配事故后加固):
      1. 精确命中;
      2. 按 token 书写精度限定的绝对容差匹配 (见 _written_tol);
      3. 仅当 pct=True (即该数字在原文中紧邻 '%') 时, 才尝试 x/100 —— 
         注册表存的是小数, 文稿可能写成百分数.

    绝不做无条件的 /100、/1000 变体匹配: 那会把大整数与小量误配到无关注册值
    (实测两次: 步数 230400↔P09, 70.9236↔E3_T中心_max).
    """
    if x in reg:
        return reg[x], 0.0
    if pct:
        cand = x / 100.0
        if cand in reg:
            return reg[cand], 0.0
        tol = _written_tol(tok) / 100.0 if tok else 5e-7
        best, bdev = None, None
        for rv, rid in reg.items():
            d = abs(cand - rv)
            if d <= tol and (bdev is None or d < bdev):
                best, bdev = rid, d
        if best is not None:
            return best, bdev
    tol = _written_tol(tok) if tok else 5e-5
    best, bdev = None, None
    for rv, rid in reg.items():
        d = abs(x - rv)
        if d <= tol and (bdev is None or d < bdev):
            best, bdev = rid, d
    return best, bdev


def main():
    reg = load_registry()
    print(f"注册表条目: {len(reg)} 个不同数值")
    print(f"允许清单:   {len(ALLOW)} 个数值\n")

    rows = []
    unmatched = []

    # 文档清单 = md 文档 (全文) + tex 的交叉验证节 (仅该节, 避免把全文历史数字卷入)
    scan_targets = [(d, None, None) for d in DOCS]
    tex_path = os.path.join(ROOT, "paper", "example.tex")
    if os.path.exists(tex_path):
        tl = open(tex_path, encoding="utf-8").read().splitlines()
        i0, i1 = xval_range(tl)
        if i0 is not None and i1 is not None:
            scan_targets.append((tex_path, i0, i1))
            print(f"  tex 交叉验证节: 行 {i0+1}..{i1} ({i1-i0} 行) 纳入第一关扫描")
        else:
            print("  [warn] 未能定位 tex 交叉验证节 —— 该节数值未纳入第一关扫描")

    for doc, lo, hi in scan_targets:
        name = os.path.basename(doc) + ("(交叉验证节)" if lo is not None else "")
        with open(doc, encoding="utf-8") as f:
            lines = f.readlines()
        if lo is not None:
            lines = [("\n" if i < lo or i >= hi else ln) for i, ln in enumerate(lines)]
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
                # 百分数判定: 数字之后 (允许空格) 紧跟 '%'
                tail = line[m.end():m.end() + 3]
                pct = tail.lstrip().startswith("%")
                if x in ALLOW:
                    rows.append([name, ln, tok, x, "ALLOW", ALLOW[x], 0.0, ctx])
                    continue
                rid, dev = find_match(x, reg, tok, pct)
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

    # ---- 第三关: tex 交叉验证节的表格与注册表逐位一致 ----
    print()
    print("=" * 100)
    print("第三关: paper/example.tex 交叉验证节的表 11 / 表 12  vs  注册表")
    print("=" * 100)
    t_checked, t_issues, t_note = tex_xval_check()
    if t_note:
        print(f"  [skip] {t_note}")
    else:
        print(f"  比对 {t_checked} 个表格数值（表 11 特征根/系数/衰减率，表 12 偏差）")
        if t_issues:
            print(f"  !! 不一致 {len(t_issues)} 处:")
            for tag, got, exp, extra in t_issues[:20]:
                print(f"     {tag}: tex={got} registry={exp}  {extra}")
        else:
            print("  全部与注册表一致。")
    if t_issues:
        print(f"\n第三关失败: {len(t_issues)} 处 tex 表格值与注册表不一致。")
        raise SystemExit(3)
    print("第三关通过: tex 交叉验证节表格与注册表一致。")


if __name__ == "__main__":
    main()
