# 评审报告：药材的烘干问题（CUMCM A 题）

- **评审日期**：2026-09-12
- **评审对象**：`paper/example.tex` / `paper/example.pdf`（40 页，2026-09-12 修复后版本）
- **评审模式**：scientific（数学建模专家视角），附呈现与格式检查
- **评审依据**：全文通读（tex 2100+ 行）+ 全部推导独立复算（sympy/解析/数值）+ 四道数字对账门实跑 + 图件三道渲染门 + judge 全页视觉检查 + 官方格式规范核对
- **评审时使用的证据标准**：每一分数点必须有可定位的稿件/注册表/复算证据

---

## Mode

scientific（建模专家视角），venue = 全国大学生数学建模竞赛（CUMCM）本科组 A 题。
评分维度按官方评审标准（假设合理性 / 建模创造性 / 结果正确性 / 表述清晰性）映射到
通用 rubric 的八个维度；格式合规按《论文格式规范（2026 年修订稿）》核对。

## Venue and assumptions

- CUMCM 本科组，国奖评审语境（国一 ≈ 前 0.6–1.5%，国二 ≈ 前 3–5%）。
- 假设：评审人按"摘要—假设—建模—求解—验证—论文格式"流程阅读；无官方标准答案，
  结果正确性只能以内部一致性 + 物理合理性评估（本评审恰好具备全部复算证据）。
- 格式规范依据官网 2026 年修订稿：正文（第 4 页起）不超过 30 页，附录页数不限，
  第一页承诺书、第二页编号专用页、第三页摘要专用页。

## Paper summary

四问共用一条"物理主线、四次升级"的建模链：问题一以常物性、两场解耦的有限体积 +
全隐式 Euler 求解 30 分钟温度/水分场（表 1、2）；问题二引入附录 3 变物性与蒸发吸热
（L_v(T) 由 Clapeyron + IAPWS-95 定标），论证能量方程取非保守形式，线性元 + 集中质量
+ 阻尼 Newton 求解 3 h 场；问题三以终止事件（max C 穿越阈值）把"积分到时刻"变为
"积分到状态"，线方法 + 自适应 BDF 得 t_dry = 57.42 h（Richardson 外推 57.49 h）；
问题四以物质坐标 ξ=r/R(t) 把收缩动边界化为固定域（水分方程无 Ṙ 残留项），得
t_dry = 51.09 h，并证明"以附件 2 实测幅度的径向收缩是落入 2–3 天时间窗的必要条件"。
验证体系含：退化一致性（问题四关闭收缩与问题三逐位一致）、两套独立离散收敛到同一
极限（差 0.0016 h）、Bessel 半解析交叉验证（7.5e-6 K）、二维轴对称对照（≤0.0032 h）、
Jacobian 谱（全部左半平面）、误差预算（数值 ±0.011 h vs 物理 MC 95% [32.4, 87.5] h）、
排湿可达性前提（C̄∞ ≤ 0.12）与收缩模式影响区间 [24.3, 129.8] h。

## Likely stance and calibrated score

**9 / 10，clear accept**（CUMCM 语境：具备国一等奖竞争力的第一梯队论文）。
Scholarly Confidence：5/5（全文、附录、代码、注册表、全部验证门与视觉检查均可用）。

## Quantitative Scorecard

| Dimension | Score (1-5) | Confidence (1-5) | Evidence basis | Deduction / score-change condition |
|:---|:---:|:---:|:---|:---|
| Novelty / 建模创造性 | 4 | 5 | §5.2.2 能量形式基准无关论证；§5.4.2 物质坐标消 Ṙ 项；附录 C.4 相容性反解（ρ_d≤700.8 判据）；§5.3.5 排湿可达性 | 组合与严谨层面的创新，非方法论创新；要达 5 需与 adrover2019 等动边界文献做定量方法对比（正文仅引用接轨） |
| Soundness / 假设与正确性 | 5 | 5 | 12 项符号推导全 PASS；退化一致性 206720.4135 s 逐位复现；谱全左半平面；守恒残差 2.8e-7 | 无实质扣分；收缩模式不可约束属题面数据限制且已量化（计入 Limitations） |
| Evidence / 结果与验证 | 5 | 5 | 表 7/8/9/13 偏差与灵敏度；表 14 二维对照；MC N=100 + bootstrap 上端 ±3.6 h 声明；问题二/三重叠段双实现互差 3.98e-5 | MC N=100 偏小（已如实声明抽样噪声）；无实验数据外部对照（题面未提供，非论文过错） |
| Significance | 4 | 4 | 排湿前提、51.09 h 工期结论、误差三档口径可直接用于工艺 | 题面限定场景；推广段（§7.3）为定性论述 |
| Clarity / 表述清晰性 | 4 | 5 | 摘要单页四问"首先-然后-得"结构；图为主；三线表规范；judge 视觉验收 40 页无溢出 | 四处小项：fig11(c)"表面积"应为"表面半径"（tex:1183）；表号非单调（表13 先于表10–12/14）；α/D=25.671 未注明温度基准（tex:502，附录 D 同题得 10.75）；"四个数量级"实为 3.7 个量级（tex:1319/1334） |
| Reproducibility | 5 | 5 | 附录 G 表 21 源程序清单；outputs/registry_*.csv 逐字面量对账门（本轮实跑四门全过、全部数值可重算） | 无 |
| Ethics / Limitations | 5 | 5 | §7.2 收缩模式缺内部数据、h_m 口径、平台外推均已量化；FV 对照"效力边界"显式声明 | 无 |
| Venue fit / 格式合规 | 4 | 4 | 2026 修订稿：正文≤30 页（实际约 28 页，余量 2 页）；附录不限；摘要单页；无目录；隐名通过 | 页数余量仅 2 页；2026 参赛规则另引"AI 工具使用规定"，提交前确认是否需附 AI 使用说明页 |

**Overall:** 9/10 | **Scholarly Confidence:** 5/5
**Recommendation:** accept（CUMCM 语境：国一竞争力）
**Verdict:** 若当年格式执行回到 25 页上限或正文再增 3 页，降 2 分（格式红线）；
补充与动边界文献的定量方法对照可 +0.5；修复 Clarity 四处小项不改变总分（属 4 分内整改）。

## Top strengths

1. **可追溯的验证体系（竞赛论文罕见的强度）**：每个数值字面量可追到注册表；问题四关闭
   收缩后与问题三逐位一致（206720.4135 s）是"结果可信"的硬证据（§5.4.4(1)）。
2. **模型边界的诚实量化**：收缩模式影响区间 [24.3, 129.8] h、数值 ±0.011 h 与物理
   [32.4, 87.5] h 分层报告（表 13），不把数值精度冒充物理精度。
3. **附录 C.4 相容性反解**：证明"无孔隙体积可加"与附件 2 收缩数据矛盾（临界半径判据
   ρ_d≤700.8），据此把 R(t) 定位为独立几何输入——这是评委欣赏的"为什么不加某个约束"的
   正面论证。
4. **终止判据的物理机制落地**：末期"越干越难干"的负反馈（D 塌缩 17 倍 × 推动力缩小 →
   139 h 渐近线）与排湿前提（C̄∞ 需 ≲0.12）把数学结果翻译成工程结论（§5.3.4(4)、§5.3.5）。
5. **物性处理超出惯例**：L_v(T) 不取文献常数而由 Clapeyron 推导 + IAPWS-95 定标
   （残差 0.00449%）；能量方程形式之争用基准无关比 10.81 裁决而非相对量级（§5.2.2–5.2.3）。

## Major/fatal concerns

无 fatal 级问题。以下为最高权重的非 fatal 关注点：

| # | 关注点 | 严重度 | 证据 | 影响 | 修复类别 |
|:--|:---|:---|:---|:---|:---|
| M1 | 收缩模式（均匀/仿射）是最大结构性不确定源 [24.3, 129.8] h，题面数据（仅表面半径）不可进一步约束 | 中（已如实量化） | §7.2、§5.4.4(3)、附录 C | t_dry 的物理解读必须连同该区间；论文已如此报告 | 无需修稿（数据限制）；已到该假设的边界 |
| M2 | 正文约 28 页，距 30 页上限余量仅 2 页 | 中（流程风险） | _pages.py 实测：模型评价止于 p28、参考文献 p28–29 | 任何内容增补可能触线；若当年执行旧 25 页规范则超页 | 流程：冻结正文长度，扩写只进附录 |
| M3 | 无外部实验/文献数值对照（如与 adrover2019 的同类工况对比） | 低-中 | 全文验证均为内部一致性 | "结果正确"依赖自洽而非外部锚点；题面未给实测数据属客观限制 | 增强（可选）：与任一文献模型在同化参数下对算一例 |

## Writing and presentation concerns

| # | 位置 | 问题 | 建议 |
|:--|:---|:---|:---|
| W1 | tex:1183（图 11(c) 图注） | "可见**表面积**在 36 h 后基本冻结在 1.20 cm"——1.20 cm 是长度，主语应为"表面半径 R(t)" | 改"表面半径" |
| W2 | tex:502（§5.2.1） | "α/D=25.671"未注明温度基准；附录 D 表 15 同一量在 50°C 下为 10.75，两处口径不同易被追问 | 注明"按初温 28°C 计"或统一引用附录 D 口径 |
| W3 | tex:1319/1334（§5.4.4、§7.1） | "数值误差比物理不确定度小四个数量级"：55.1/0.011≈5.0×10³≈3.7 个量级 | 改"约三个半数量级"或"三个数量级以上" |
| W4 | 表 13（p27）先于附录表 10–12/14 出现 | 表号非单调（题面固定表 1–6 的设计折衷） | 在表 13 或附录 G 加一句编号约定说明即可，不必重编号 |
| W5 | §5.2.3（tex:611） | "保留但略去的对流项"措辞自相矛盾（式 (5) 中该项保留、量级可略） | 改"保留在方程中、量级可略" |

## Format/venue concerns

- **页数**：按 2026 年修订稿合规（正文约 28 ≤ 30；附录 11 页不限）。余量仅 2 页。
- **摘要**：第 1 页单页含关键词 ✓（2026 规范摘要为第 3 页专用页，提交时由承诺书/编号页
  前置，模板处理一致）。
- **目录**：无 ✓（规范明令不要目录）。
- **隐名**：无身份信息 ✓（仅题注与文献条目含机构名词）。
- **AI 工具**：2026 参赛规则引用《AI 工具使用规定》；本项目为 AI 深度辅助产出，
  提交前按当年规定确认是否需附使用说明页（附录页数不限，不挤占正文）。

## Multi-reviewer panel

```text
Reviewer: 最有利评审（Best-Justified）
Expertise: 计算传热传质 / 数值方法
Likely score: 9
Confidence: 5
Main positive signal: 验证密度与可追溯性达到工程仿真报告水准，竞赛论文中罕见；
  退化一致性 + 双离散 + 解析对照构成完整可信度链（§5.4.4(1)）
Main negative signal: 无
Evidence basis: 四道对账门实跑归零、12 项推导复算 PASS、图件三道门 PASS
Fatal concern if any: 无
Score-change condition: 无需变化
```

```text
Reviewer: 批判评审（Critical）
Expertise: 应用数学 / 竞赛评委
Likely score: 8（倾向 accept）
Confidence: 4
Main positive signal: 即便只读摘要与表 13，结论的适用边界（三档口径）清晰可查
Main negative signal: 全部验证为内部一致性，无任何外部数值锚点；模型主体
  （Fick 扩散 + 第三类边界 + 动边界）均为成熟组件，"创造性"依赖组合与严谨
Evidence basis: §5.3–5.5 验证清单；文献 [9][10] 仅引用接轨未对比
Fatal concern if any: 无（题面未给实测数据，外部对照客观不可得）
Score-change condition: 若评委把"无外部对照"权重调高，可降至 7
```

```text
Reviewer: 方法/正确性评审（Method & Soundness）
Expertise: 偏微分方程数值解 / 刚性常微分方程
Likely score: 9
Confidence: 5
Main positive signal: 非保守形式的裁决论证（基准无关比 10.81）与"无 Ṙ 残留项"的
  均匀场检验在方法论上示范级；事件定位 + Richardson 外推处理隐式终止时刻正确
Main negative signal: R0"自洽读法归零"的认识论论证微妙（附录 3 的 ρ(C) 与
  恒定 ρ_s 不能同时成立），论文已显式承认（§5.2.2"同一个不自洽"）
Evidence basis: verify_derivation 12 项、q2_energy_verify_sympy、q45_stiffness 全部复算
Fatal concern if any: 无
Score-change condition: 无
```

```text
Reviewer: 证据/实验评审（Evidence）
Expertise: 科学计算 / 不确定度量化
Likely score: 8
Confidence: 5
Main positive signal: 误差预算分"数值/工艺/物理"三档（表 13），MC 与 bootstrap
  抽样噪声声明（±3.6 h）符合 UQ 规范
Main negative signal: MC N=100 偏小；单因素灵敏度与 MC 均为 ±5%/±10% 均匀扰动，
  未讨论扰动分布形状的影响
Evidence basis: registry_q3_mc / registry_q4_sens
Fatal concern if any: 无
Score-change condition: N≥1000 重跑 MC 可 +0.5（本轮注册表口径下非必需）
```

```text
Reviewer: 创新/定位评审（Novelty & Positioning）
Expertise: 食品/药材干燥建模
Likely score: 7
Confidence: 4
Main positive signal: 与 adrover2019（等温动边界）、feyissa2009（COMSOL 动边界）
  接轨恰当；相容性反解（附录 C.4）是对文献"shrinkage 与 drying 分开测量"局限的
  直接回应
Main negative signal: 未与任何文献模型做定量对比；Luikov 类双场耦合模型为成熟框架
Evidence basis: §1.1、§4.4、文献列表 17 条
Fatal concern if any: 无（竞赛语境下创新性要求低于期刊）
Score-change condition: 增加一段与 adrover2019 模型的逐项差异表可 +0.5
```

```text
Reviewer: 写作/清晰评审（Writing & Clarity）
Expertise: 科技写作
Likely score: 8
Confidence: 5
Main positive signal: 摘要单页四问结构完整；图表叙述先行后数；术语全文稳定
  （L_v 符号规范化后无 H_evap 残留）
Main negative signal: W1–W5 五处小项（表面积笔误、双口径比值、表号非单调等）
Evidence basis: tex:502/1183/1319/1334；表 13 与附录表顺序
Fatal concern if any: 无
Score-change condition: 修复 W1–W5 不改变总分（4 分内整改）
```

```text
Reviewer: 领域应用评审（Domain Application）
Expertise: 中药材干燥工艺
Likely score: 8
Confidence: 4
Main positive signal: 排湿是目标可达性前提（C̄∞≤0.12 裕度）、临界半径判据、
  表面传质阻力不可忽略（0.0527 高于平台值 5.3%）等结论可直接指导工艺
Main negative signal: 恒温段 h、h_m 沿用预热段取值（题面未给），工程上干燥阶段
  对流系数通常更高；论文以 ±20% 扰动界定（§5.2.6），可接受
Evidence basis: §5.3.5 排湿讨论、表 8/9
Fatal concern if any: 无
Score-change condition: 无
```

### Panel synthesis

```text
Agreement: 全员 accept 方向；对"验证与诚实度突出、创造性属组合层面"判断一致
Disagreement: 批判/创新评审（7–8）与正确性/可复现评审（9）对"外部对照缺失"
  的权重分歧——竞赛语境下前者让位
Decisive positive axis: 结果正确性的内部证据链（退化一致 + 双离散 + 解析对照）
Decisive negative axis: 无外部数值锚点 + 收缩模式不可约束（题面数据限制）
Unresolved evidence: 当年格式执行版本（25 vs 30 页）与 AI 说明页要求
Final calibrated stance: 9/10，clear accept（国一竞争力）；格式合规须在提交前复核
```

## Claim-to-evidence audit

| Claim | Where stated | Evidence provided | Strength | Deduction |
|:---|:---|:---|:---|:---|
| t_dry(问题三) = 57.42 h，外推 57.49 h，数值 ±0.028 h | §5.3.4、表 9 | M=100/200/400 链 + 容限/积分器互检（≤0.17 s）+ 双实现互差 3.98e-5 | strong | 无 |
| t_dry(问题四) = 51.09 h；径向收缩（附件 2 幅度）是 2–3 天窗内达标的必要条件 | §5.4.3、图 11(d) | 四算例效应分解 + 冻结收缩 +78.7 h + 模式区间 [24.3,129.8] h + 措辞已限定"以附件 2 实测幅度" | strong | 无 |
| 数值误差 ±0.011 h ≪ 物理不确定度 [32.4, 87.5] h（"四个数量级"） | §5.4.4 表 13、§7.1 | 实测渐近阶 1.95 的 M 链 + MC 95% | adequate | 55.1/0.011≈3.7 个量级，"四个数量级"略夸大（W3，措辞级） |
| 径向一维简化损失 ≤0.0032 h | §5.3.5(4)、附录 B | 二维轴对称对照（Nz=25/50、最不利算例）+ 比较原理上解论证 | strong | 无 |
| 排湿是达标前提（C̄∞≲0.12 时延长 ≤10 h） | §5.3.5 | 五情景实测 + C̄∞=C* 渐近停滞 | strong | 无 |

## Concern-to-action table

| Concern | Action | Owner skill | Severity | Score impact |
|:---|:---|:---|:---:|:---|
| W1 "表面积"笔误（tex:1183） | 改"表面半径" | ccf-paper-writer | low | 无（表述分内） |
| W2 α/D=25.671 温度基准（tex:502） | 注明"按初温 28°C"或统一引附录 D | ccf-paper-writer | low | 无 |
| W3 "四个数量级"（tex:1319/1334） | 改"三个数量级以上" | ccf-paper-writer | low | 无 |
| W4 表号非单调说明 | 表 13 处加一句编号约定 | ccf-paper-writer | low | 无 |
| W5 "保留但略去"措辞（tex:611） | 改"保留在方程中、量级可略" | ccf-paper-writer | low | 无 |
| M2 页数余量 2 页 | 冻结正文长度；增补只进附录 | 流程约定 | medium | 触线则 −2 |
| M3 无外部对照 | （可选）与 adrover2019 同化参数对算一例 | ccf-experiment-designer | low-medium | +0.5 |
| AI 说明页 | 按 2026《AI 工具使用规定》确认并附页（附录不计页） | 提交流程 | medium | 合规风险 |

## Recommended next CCFA owner

`ccf-paper-writer`（W1–W5 五处定点小修，均不改数字、不触对账门的新字面量；
W2/W3 若补充数字需同步注册表）。

## Checks run

- 全文通读（tex 2100+ 行）；全部解析推导独立复算（12 项 sympy + 能量恒等式 + 潜热定标）
- 四道数字对账门、q2/q3/q4 数值验证链、q3 二维对照 pilot（全部 exit 0，2026-09-12 实跑）
- 附录 C.4 手工逐格验算（表 10 全表、临界半径、κ 序列）；附录 D/E/F 数值复算
- 编译健康（0 error/overfull/undefined/missing char）、40 页 judge 视觉验收、
  typo/留白/篇幅扫描
- 格式规范核对（官网 2026 年修订稿）与隐名检查

## Unresolved or unverified

- 当年（提交年度）格式规范的执行版本与《AI 工具使用规定》的申报形式——需以
  www.mcm.edu.cn 当年文件为准。
- MC 抽样分布形状（均匀 ±5%）的合理性未做对照（uniform 为竞赛惯例，风险低）。
- 与文献模型的定量对比不存在（M3），无法评估本文解与文献解的绝对偏差。

## Output self-check

- 段落顺序符合 standard report 契约；表格列数一致；分数均有证据定位；
- 总分 9 与最强未决弱点（无外部对照 + 页数余量）相容（9 而非 10 的理由即在此）；
- 无占位符、无泛化措辞；中文标点统一。
