# AGENTS.md —— 2024 A 题"板凳龙" 自动加载入口

> 本文件由 opencode 在每次进入本目录时**自动读取**，是 AI 理解本项目、定位文献与代码的**唯一必需入口**。
> 其余文档均为按需加载（读入口 → 索引 → 深挖）。

## 这是什么项目

2024 年全国大学生数学建模竞赛 **A 题《"板凳龙"闹元宵》** 模拟赛目录。
223 节板凳首尾相连构成"板凳龙" = **广义 N 拖车（N-trailer）铰接链**，沿阿基米德螺线盘入盘出，龙头前把手恒速 1 m/s。
关键几何：板宽 30 cm、孔径 5.5 cm、孔距板端 27.5 cm；龙头板长 3.41 m（两孔中心距 2.86 m），龙身/尾板长 2.20 m（两孔中心距 1.65 m）；螺线 `r = b·θ`，`b = 0.55/(2π)`。

五问（Q1/Q2 **已解**，Q3–Q5 待做）：
- **Q1** 0–300 s 每秒整条龙 224 把手位置/速度 → 已解，结果见 `附件/result1.xlsx`
- **Q2** 盘入终止时刻（板凳不碰撞）→ 已解，`t*=412.47 s`，首次碰撞龙头(1)↔第9节，结果见 `附件/result2.xlsx`
- Q3 最小螺距；Q4 S 形调头可否缩短；Q5 龙头最大速度（各把手≤2 m/s）→ 待做

## 自动加载顺序（每次进目录执行）

1. 读本文件（AGENTS.md）→ 恢复上下文；
2. 文献相关 → 先读 `docs/AI_INDEX.md`（定位）→ 细节再读 `docs/LITERATURE_REVIEW.md`；
3. 模型/求解相关 → 读 `model/problem1.md`、`model/problem1_solve.md`、`model/problem2.md`、`model/problem2_solve.md`；
4. 代码/脚本 → 读 `src/` 下脚本（自包含，可直接运行）；
5. 脚本化读取文献元数据 → 解析 `docs/index.json`；
6. 涉及回忆/继续/迁移 → 按 ChatMem 流程（见 `C:\Users\极光\.config\opencode\AGENTS.md`）。

## 文献可用性（重要，避免误读/幻觉引用）

`docs/` 共 6 篇，**仅 4 篇可读**：

| 可用 | 不可用（损坏，待重下） |
|---|---|
| C3 Tanaka 三节拖车（38页，铰接链相对角递推 `θ̇ᵢ=(ν/L)sinθᵢ`）| C1 Michalek N-trailer（实为 ScienceDirect 错误页 HTML）|
| E1 Lekkas 费马螺线（16页，`r=k√θ`，曲率连续，Q4 调头设计）| E3 Reeds-Shepp（截断 PDF，0 页）|
| F1 Verscheure 凸规划（10页，SOCP 时间最优，Q5）||
| F2 Artuñedo jerk-limited（13页，`v_SLC=min{v_max,√(a_lat/κ)}`，Q5）||

**规则**：引用 C1/E3 时必须标注"原文待核实，基于文件名/领域知识"，不得当作已核实原文；不要浪费时间修复 E3（已试过 pypdf/pikepdf/pymupdf 均失败）。

## 目录结构速查

```
模拟/2024/
├── AGENTS.md              # 本文件（自动加载）
├── A题.pdf                # 赛题原文（3 页）
├── docs/                  # 参考文献库
│   ├── LITERATURE_REVIEW.md   # 三大主题综述 + 对比 + Q1–Q5 映射
│   ├── AI_INDEX.md            # 可读索引：逐篇页码定位、提取命令
│   ├── index.json             # 机器可读索引（公式/元数据/Q1–Q5 映射）
│   ├── AGENT_MEMORY.md        # 持久记忆：术语表、进展、导航协议
│   └── AGENTS.md
├── model/                 # 模型与求解文档
│   ├── problem1.md            # Q1 模型建立（螺线运动学 + 逆推法 + 速度）
│   ├── problem1_solve.md      # Q1 求解（细步长 + 实体碰撞检测 + 结果表）
│   ├── problem2.md            # Q2 碰撞检测完善（缺陷分析 + 修正 + CCD）
│   └── problem2_solve.md      # Q2 求解（终止时刻 + 结果表 + 验证）
├── src/                   # 自包含可运行脚本（python 直接运行）
│   ├── problem1_solve.py      # Q1：细步长求解 + SAT 碰撞检测（写 result1.xlsx）
│   ├── problem2_collision.py  # Q2：SAT/顶点包含/CCD + 二分（写 result2.xlsx）
│   └── anim_dragon.py         # ≈盘入动态仿真 GIF
├── paper/figures/         # 全部示意图与动画
│   ├── anim_盘入仿真.gif         # 动态仿真（150帧）
│   ├── fig_算法流程图.png          # Q1 求解算法流程图
│   ├── fig_整龙盘入轨迹.png / fig_龙头* / fig_把手速度* / fig_龙尾*  # Q1 数据图
│   ├── fig_问题一碰撞间隙.png      # Q1 实体碰撞最小间隙 vs 时间
│   ├── fig_板凳几何尺寸示意.png / fig_盘入整体示意.png / fig_逆推法几何示意.png
│   ├── fig_矩形碰撞示意.png       # 三种碰撞情形（含缺陷1完全包含）
│   ├── fig_问题二算法流程.png      # 宽相+精相+二分
│   ├── fig_问题二数据结构.png      # 数据结构/函数组织
│   ├── fig_CCD连续碰撞示意.png    # CCD 隧道效应 + 黄金分割
│   └── fig_碰撞临界时刻.png        # Q2 t*=412.47s 形态
└── 附件/                  # 结果文件（题目要求 6 位小数）
    ├── result1.xlsx            # Q1 每秒全龙位置/速度（位置+速度两 sheet）
    ├── result2.xlsx            # Q2 终止时刻 224 把手的 x/y/速度
    └── result4.xlsx            # Q4（待做）
```

## 当前完成度与关键结果

**已解决：**
- **Q1**：`b=0.55/(2π)`；弧长积分二分求龙头极角 + 逆推法（作圆取极角最近者）求 224 把手；细步长 dt=0.1s 中心差分求速（龙头 v≈0.999995≈1 m/s）；**实体碰撞检测**（板宽 0.30 m，SAT）0–300 s 最小间隙 1.95e-7 m，无碰撞；已写 `附件/result1.xlsx`。
- **Q2**：碰撞检测 = 宽相 AABB 预筛 + 精相（顶点包含 ∪ SAT）+ CCD（连续碰撞检测黄金分割）；二分求 `t*=412.47 s`，首次碰撞龙头(1)↔第9节；已写 `附件/result2.xlsx`。

**关键数值（用于论文/校验）：**
- 龙头 t=0 位置：`(8.8, 0)`（第 16 圈）
- Q1 龙头速度：0.999995~0.999983 m/s（细步长）
- Q1 0–300 s 最小间隙：`1.95e-7 m`（无碰撞）
- Q2 终止时刻：`t* = 412.47 s`，精确值 `412.47009 s`（CCD）
- Q2 碰撞对：`(1, 9)`（龙头 ↔ 第 9 节）

**待办：**
- 重下 C1/E3 原文并更新综述/索引；
- Q3 最小螺距、Q4 S 形调头、Q5 龙头最大速度；
- 论文正文按 `problem1_solve.md`/`problem2*.md` 的表与图组织。

## 环境与运行

- Windows / PowerShell；Python 3.12.3（conda）
- 依赖：`numpy`、`scipy`（brentq）、`openpyxl`（读写 xlsx）、`matplotlib`、`pillow`
- 运行：`python src/problem1_solve.py`、`python src/problem2_collision.py`、`python src/anim_dragon.py`
- 中文字体：matplotlib 需注册 `C:\Windows\Fonts\msyh.ttc`（脚本内已处理）
- 抽取工具 pdfplumber 0.11.7 / pypdf 6.14.2 / pymupdf；抽取命令见 `docs/AI_INDEX.md` §5

## 重要约定

- **Q1/Q2 数据一致**：`附件/result1.xlsx`、`result2.xlsx` 与 `model/*.md` 表、`src/*.py` 输出三者对齐（全量校验偏差仅 6 位小数舍入 ≤5e-7）。
- **碰撞判定**：SAT 天然覆盖"矩形完全包含"（缺陷1）；显式顶点包含作双保险；相邻板凳（编号差=1）经把手铰接，跳过不判碰撞；终止时刻用二分 + CCD 逼近。
- **码表注释风格**：代码是自包含数值脚本，含中文 docstring；图为 200 dpi。
