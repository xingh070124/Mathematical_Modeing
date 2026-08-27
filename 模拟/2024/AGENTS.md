# AGENTS.md —— 2024 A 题"板凳龙"文献库自动加载入口

> 本文件由 opencode 在每次进入本目录时**自动读取**，是 AI 自主翻阅 `docs/` 文献的唯一必需入口。
> 其余文档均为按需加载（读到索引后再深挖）。

## 这是什么项目

2024 年全国大学生数学建模竞赛 **A 题《"板凳龙"闹元宵》** 模拟赛目录。
223 节板凳首尾相连构成"板凳龙" = **广义 N 拖车（N-trailer）铰接链**，沿阿基米德螺线盘入盘出，龙头前把手恒速 1 m/s。
五问：Q1 螺旋位置/速度；Q2 碰撞终止时刻；Q3 最小螺距；Q4 S 形调头可否缩短；Q5 龙头最大速度(各把手≤2 m/s)。

## 自动加载顺序（每次进目录执行）

1. 读本文件（AGENTS.md）→ 恢复上下文；
2. 需要翻阅文献时，先读 `docs/AI_INDEX.md`（定位）→ 需要细节再读 `docs/LITERATURE_REVIEW.md`（综述全文）；
3. 需要脚本化读取/元数据 → 解析 `docs/index.json`；
4. 需要延续上轮工作/了解进展 → 读 `docs/AGENT_MEMORY.md`；
5. 涉及回忆/继续/迁移 → 按 ChatMem 流程（见 `C:\Users\极光\.config\opencode\AGENTS.md`）。

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
├── A题.pdf            # 赛题原文（3 页）
├── docs/              # 参考文献库（本次工作的核心）
│   ├── LITERATURE_REVIEW.md   # 三大主题综述（C3/E1/F1/F2 细节 + 对比 + Q1–Q5 映射）
│   ├── AI_INDEX.md            # 可读索引：逐篇页码定位、提取命令
│   ├── index.json             # 机器可读索引（公式/元数据/Q1–Q5 映射）
│   ├── AGENT_MEMORY.md        # 持久记忆：术语表、进展、导航协议
│   └── AGENTS.md              # 本文件（自动加载）
└── 论文/              # result1/2/4.xlsx（结果模板，解题后校验用）
```

## 当前进展（截至上次会话）

已完成：6 篇 PDF 全文抽取与完整性诊断；综述/索引/记忆三件套已写入 `docs/`；ChatMem 检查点 `cb97b914`。
待办：重下 C1/E3 原文；按综述 §8 映射实现 Q1–Q5 求解代码，并用 `论文/result*.xlsx` 校验。

## 环境

- 使用环境名称为`math_model`如果没有利用conda创建

Windows / PowerShell；Python 3.12.3；抽取工具 pdfplumber 0.11.7 / pypdf 6.14.2 / pymupdf。
文本抽取命令见 `docs/AI_INDEX.md` §5。