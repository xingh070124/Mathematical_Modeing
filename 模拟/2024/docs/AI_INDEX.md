---
doc_type: ai_index
repo: Mathematical_Modeing
subject: 2024 CUMCM A 题 "板凳龙"
indexed_at: 2026-08-27
indexer: opencode
related: [LITERATURE_REVIEW.md, AGENT_MEMORY.md, index.json]
extraction_toolchain: pdfplumber 0.11.7 / pypdf 6.14.2 / pymupdf
---

# AI 索引 —— docs/ 参考文献浏览索引

本文件是 AI（或人）在 `docs/` 目录中**自主翻阅文献的入口**。它回答三个问题：
1. **有哪些文件、能否读取？**（§1 清单 + §2 完整性诊断）
2. **每篇讲什么、在哪几页能找到关键内容？**（§3 逐篇索引）
3. **怎么取全文、怎么复现抽取？**（§4 操作指南 + §5 提取命令）

配套机器可读 JSON：`./index.json`（本文件的程序化版本，供脚本/Agent 直接解析）。

---

## 1. 目录清单与可读性总表

| # | 文件名 | 真实类型 | 文本可抽取 | 页数 | 主题类别 |
|---|---|---|---|---|---|
| C1 | `C1_Michalek_N-trailer.pdf` | ❌ HTML 错误页（ScienceDirect Cloudflare） | 否 | 0 | N-trailer 运动学 |
| C3 | `C3_Multiobjective_control_of_a_ve.pdf` | ✅ PDF | 是（38 页全） | 38 | 三节拖车控制 / 铰接链运动学 |
| E1 | `E1_Continuous-Curvature_Path_Gene.pdf` | ✅ PDF | 是（16 页全） | 16 | 费马螺线连续曲率路径 |
| E3 | `E3_Optimal_paths_for_a_car_that_g.pdf` | ⚠️ 截断 PDF | 否（0 页） | 0 | 含倒车汽车最短路径 |
| F1 | `F1_Verscheure.pdf` | ✅ PDF | 是（10 页全） | 10 | 路径约束时间最优轨迹 |
| F2 | `F2_Jerk-Limited_Time-Optimal_Spee.pdf` | ✅ PDF | 是（13 页全） | 13 | jerk 受限时间最优速度 |

> 注意：**文件扩展名不可信**。C1 是 HTML，E3 是损坏 PDF。判断"能否读取"请用 §5 的探测命令，不要依赖文件名。

---

## 2. 文件完整性诊断记录

| 文件 | 文件头（前 8 字节） | 诊断 | 处置建议 |
|---|---|---|---|
| C1_Michalek_N-trailer.pdf | `<!DOCTYPE` | 下载失败：ScienceDirect Cloudflare 错误页（CPE00001 ::CLOUDFLARE_ERROR_1000S_BOX::），参考号 a31afd122df6c4f0 | 重新下载原文；占位介绍见 LITERATURE_REVIEW §3.2 |
| C3_Multiobjective_control_of_a_ve.pdf | `%PDF-1.4` | 正常 | 无 |
| E1_Continuous-Curvature_Path_Gene.pdf | `%PDF-1.4` | 正常 | 无 |
| E3_Optimal_paths_for_a_car_that_g.pdf | `%PDF-1.4` | 截断：`EOF marker not found`；根 Pages 树无 /Kids；pypdf/pikepdf/pymupdf 均打不开页 | 重新下载（Reeds-Shepp 1990 扫描版约 40 页） |
| F1_Verscheure.pdf | `%PDF-1.4` | 正常 | 无 |
| F2_Jerk-Limited_Time-Optimal_Spee.pdf | `%PDF-1.4` | 正常 | 无 |

---

## 3. 逐篇索引（含"去哪页找什么"）

### C1_Michalek_N-trailer.pdf（损坏，无法分页）
- **状态**：占位。真实内容 = ScienceDirect 错误页，无正文。
- **意图主题**：广义 N-trailer 运动学建模与跟踪控制（off-axle 铰接、奇异构型、VFO 控制）。
- **替代来源建议**：搜索关键词 `Michalek generalized N-trailer kinematics` / `Michalek N-trailer tracking control`（IEEE/IFAC）。
- **与赛题关系**：Q1 运动学建模、Q2 碰撞/奇异构型。

### C3_Multiobjective_control_of_a_ve.pdf（38 页，全可读）
- **论文**：Tanaka, Hori, Wang, *Multi-objective Control of a Vehicle with Triple Trailers*（Univ. of Electro-Communications + Duke）。
- **关键内容定位**：
  - 第 5 页：铰接链离散运动学模型（**最重要**）——θ₀、θ₁、θ₂、θ₃ 与相对角 θ01/θ12/θ23 的递推（`θᵢ(t+1)=θᵢ(t)+(νΔt/L)sinθᵢ₋₁,ᵢ`）；
  - 第 7–9 页：T-S 模糊模型（两规则 A₁/B₁、A₂/B₂）、PDC 控制器、隶属函数；
  - 第 10–16 页：LMI 稳定性（Thm 1）、衰减率 GEVP（Thm 2）、输入/输出约束（Thm 3–4）、初值无关化（Thm 5）、干扰抑制 L₂ 增益（Thm 6）；
  - 第 6 页：折刀（jack-knife）现象描述与八个折刀位置定义（相对角 ±90°）。
- **核心公式**：
  - `θ₀(t+1)=θ₀(t)+(νΔt/ℓ)tan(u(t))`
  - `θᵢ(t+1)=θᵢ(t)+(νΔt/L)sin(θᵢ₋₁,ᵢ)`，i=1,2,3
  - 状态 `x=[θ01 θ12 θ23 θ3 y]ᵀ`
- **关键词**：Takagi-Sugeno fuzzy, PDC, LMI, jack-knife, backing control, triple trailer。

### E1_Continuous-Curvature_Path_Gene.pdf（16 页，全可读）
- **论文**：Lekkas, Dahl, Breivik, Fossen, *Continuous-Curvature Path Generation Using Fermat's Spiral*, Modeling Identification and Control 34(4):183–198, 2013。
- **关键内容定位**：
  - 第 2 页：引言、路径生成两大类别（直线+圆弧 / 样条）；
  - 第 3–4 页：Dubins 路径与曲率不连续问题、回旋线（clothoid）及 Fresnel 积分缺陷；
  - 第 6 页：**费马螺线定义** `r=k√θ`、曲率 `κ(θ)=12√θ(3+4θ²)/(k(1+4θ²)^{3/2})`、κ(0)=0；
  - 第 7 页：笛卡尔参数化 `p_FS(θ)=[x0+k√θcos(ρθ+χ0); y0+k√θsin(ρθ+χ0)]`、镜像曲线、放缩因子 k 与初始切角 χ0；
  - 第 7–8 页：**正则化换元 u=√θ** 消除 θ=0 参数速度奇异、正则性条件 `|dp/du|=k√2√(1+4ρ²u⁴)≠0`；
  - 第 8 页后：弧长（Gaussian 超几何函数）、路径构造（FS smoothing 与 circular smoothing with FS transition）。
- **核心公式**：`r=k√θ`；`κ(0)=0`；`u:=√θ` 换元；`v_SLC` 类曲率—速度关联见 F2。
- **关键词**：Fermat's spiral, continuous curvature, clothoid, path planning, path tracking, curvature continuity, G²。

### E3_Optimal_paths_for_a_car_that_g.pdf（损坏，无法分页）
- **状态**：占位。截断 PDF，0 页可读。
- **意图主题（公认经典）**：Reeds & Shepp, *Optimal paths for a car that goes both forwards and backwards*, Pacific J. Math. 145(2):367–393, 1990。前进+倒车的最短路径由至多 6 段（直线/圆弧）组成。
- **与赛题关系**：Q4 调头曲线最短性下界。
- **替代来源**：arXiv/Google Scholar 检索 `Reeds Shepp optimal paths car forwards backwards 1990`。

### F1_Verscheure.pdf（10 页，全可读）
- **论文**：Verscheure, Demeulenaere, Swevers, De Schutter, Diehl, *Practical Time-Optimal Trajectory Planning for Robots: a Convex Optimization Approach*, IEEE TAC 2008（K.U.Leuven OPTEC）。
- **关键内容定位**：
  - 第 2 页：问题设定——沿路径的动力学 `τ(s)=m(s)s̈+c(s)ṡ²+g(s)`、时间最优 min T；
  - 第 2–3 页：**换元 a(s)=s̈, b(s)=ṡ²，约束 b'(s)=2a(s)**，目标 `T=∫₀¹ 1/√b(s) ds`；
  - 第 3 页：凸性论证、DAE 形式（单微分状态 b）；
  - 第 3–4 页：扩展目标（时间—能量 `x²/√y`、力矩变化率 `|τ'(s)|`）与扩展约束（速度限制 `(qᵢ'(s))²b(s)≤q̇̄ᵢ²`）；
  - 第 4 页：直接转录 + **SOCP** 求解。
- **核心公式**：`a(s)=s̈`；`b(s)=ṡ²`；`b'(s)=2a(s)`；`T=∫₀¹ ds/√b(s)`。
- **关键词**：time-optimal, convex optimization, second-order cone program (SOCP), path coordinate, trajectory planning。

### F2_Jerk-Limited_Time-Optimal_Spee.pdf（13 页，全可读）
- **论文**：Artuñedo, Villagra, Godoy, *Jerk-limited time-optimal speed planning for arbitrary paths*, J. Intelligent & Robotic Systems（CSIC-UPM，西班牙）。
- **关键内容定位**：
  - 第 2 页：相关工作综述（MPC 局限、既有 jerk-limited 方法局限）；
  - 第 2–3 页：**速度限制曲线** `v_SLC,i = min{v_max, √(a_lat_max/|κ_i|)}`（向心加速度公式）；
  - 第 3–4 页：**Algorithm 1** 加速度受限规划（速度限制曲线 → 正向限最大加速度 → 逆向限最大减速度 → fallback）；
  - 第 3 页表 I：参数定义（v_ini, v_end, v_max, a_lat_max, a_long_max/min）；
  - 第 4 页后：jerk 受限阶段（Pontryagin bang-bang on jerk）。
- **核心公式**：`v_SLC=min{v_max, √(a_lat_max/|κ|)}`。
- **关键词**：jerk-limited, time-optimal speed, speed limit curve, lateral acceleration, arbitrary paths, autonomous driving。

---

## 4. Agent 翻阅指南（工作流）

**Step 0 读取**：先读本文件确定目标文献编号 → 需要详细内容再读 `LITERATURE_REVIEW.md` 对应章节 → 要逐段引用时按 §5 抽取全文。

**Step 1 定位**：用 §3 的"关键内容定位"直接跳到目标页码（对可读 PDF 有效）。

**Step 2 取全文**：对可读 PDF 执行 §5 命令抽取纯文本（已抽取的缓存副本曾位于临时目录，但**工作区外不保证持久**，建议按命令复现）。

**Step 3 交叉验证**：同一概念在 C3（运动学）、E1/F1/F2（路径/速度）之间的衔接关系见 `LITERATURE_REVIEW.md` §7–§8。

**Step 4 遇到损坏文件**：C1、E3 直接引用"意图主题 + 领域知识"，并在结论中标注"待重新下载"，不得当作已核实原文引用。

---

## 5. 提取 / 探测命令（Windows PowerShell + Python）

```powershell
# 探测文件真实类型（看文件头，别信扩展名）
python -c "import sys; d=open(r'<file>','rb').read(16); print(d)"
# 期望：PDF 开头 b'%PDF-1.4...'；HTML 开头 b'<!DOCTYPE html>'（=下载失败）

# 全文本抽取（pdfplumber，适用正常 PDF）
python -c "
import pdfplumber, sys
with pdfplumber.open(r'<file>') as pdf:
    for i,p in enumerate(pdf.pages):
        print(f'===== PAGE {i+1} =====')
        print(p.extract_text() or '')
"

# 健壮性探测（pypdf / pymupdf，判断是否损坏）
python -c "from pypdf import PdfReader; r=PdfReader(r'<file>'); print('pages', len(r.pages))"
python -c "import fitz; print('pages', fitz.open(r'<file>').page_count)"
```

**已确认结论**（可直接引用，无需重跑）：
- 可读：C3(38 页)、E1(16 页)、F1(10 页)、F2(13 页)；
- 不可读：C1（HTML 错误页）、E3（截断 PDF，0 页）。

---

## 6. 主题 → 文献反向索引

| 主题关键词 | 文献 | 所在章节（LITERATURE_REVIEW） |
|---|---|---|
| 铰接链运动学、相对角、sin 递推 | C3（+C1 待补） | §3 |
| 折刀 / jack-knife / 碰撞 | C3 | §3.1、§9 |
| N-trailer、off-axle、奇异构型 | C1（待补） | §3.2 |
| 连续曲率、费马螺线、clothoid、过渡曲线 | E1 | §4.2 |
| 最短路径、含倒车、调头下界 | E3（待补） | §4.1 |
| 时间最优、凸优化、SOCP、路径坐标 | F1 | §5.1 |
| 速度限制曲线、曲率—速度、jerk、bang-bang | F2 | §5.2 |
| 螺线（阿基米德/费马）参数化 | 赛题本身 + E1 | §1、§4.2 |