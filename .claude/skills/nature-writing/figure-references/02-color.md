# 02 · 配色（含 Wong / Okabe-Ito 8 色板）

（FIGURE-SKILL Part II §2；总索引见 `../FIGURE-SKILL.md`）

## 2. 配色：先选语义，再选 hue

**Patron sentence** — Wong 2011 (Nature Methods 8:441):
> "About 8% of men and 0.5% of women have some form of color vision deficiency."

读者里十几分之一看不到你 jet colormap 里的红绿差。这一条 alone 就够把 jet 踢出去。
但更深的理由是：好图先决定**语义**——这些颜色是 categorical / sequential / diverging？
然后才挑 hue。

### 2.1 三种 colormap 类型

| 类型 | 数据语义 | 推荐 colormap | 不推荐 |
|---|---|---|---|
| **Categorical** | 离散类别，无内在顺序（method A vs B vs C；细胞类型；模型变体） | Wong 8 色板（§2.2）；个别期刊接受 ColorBrewer "Set2" / "Dark2" | tab10 默认；自创鲜艳色 |
| **Sequential** | 有方向的连续值（density、count、score、概率） | viridis / cividis / magma / Blues 单色阶 | jet / rainbow / hsv |
| **Diverging** | 有中心点的双向值（log fold-change、residual、correlation around 0） | RdBu_r / PiYG / coolwarm | spectral |

强约定：**永远不要用 jet / rainbow / hsv / spectral 表示 sequential 数据**。Wong 2011
之后这是 Nature 系常见审稿意见。

### 2.2 Wong / Okabe-Ito 8 色板

来源：Wong 2011 Nature Methods 8:441；Okabe & Ito 2008 Color Universal Design 同一谱系。
hex 值与 Okabe-Ito 公开的版本对齐（验证 via clauswilke.com/dataviz；如期刊有自家变体
请以官网为准）：

```text
Black           #000000   全图轴线 / 文字 / 中性引用
Orange          #E69F00   强调，警示
Sky Blue        #56B4E9   常作为"我方"或"主类"
Bluish Green    #009E73   常作为对照 / 实验组
Yellow          #F0E442   慎用，最难在白底辨识；只用于 fill 不用于 line
Blue            #0072B2   "我方深色"或主轴
Vermilion       #D55E00   error / negative / 红绿色盲下仍可与绿区分
Reddish Purple  #CC79A7   第二实验组 / 第二方法
```

实战分配建议：

```text
你的方法 / 主结果   → Blue #0072B2  或  Vermilion #D55E00（任选一种作为"品牌色"）
最强 baseline       → Sky Blue #56B4E9  或  Reddish Purple #CC79A7
其他 baseline       → 灰阶 #888888 / #BBBBBB
human / expert      → Black #000000
ablation 变体       → 同主色但降饱和 / 改 line style
```

corpus 内多见：方法 1 个饱和品牌色；baseline 用灰；human anchor 用黑。reviewer 一眼
看到"哪条线是你"。

### 2.3 何时分组高亮

如果你想强调一个事实（"在所有 N 个数据集上我们都赢"），不要把所有方法都同等饱和。
做法：

- 你的方法：饱和 + line width 1.5–2x；
- 直接竞争 baseline：饱和但配色不同；
- 历史 baseline：灰阶 #888 / #BBB / #DDD，按时间深浅；
- 其他参考：极淡灰，只在 legend 出现。

corpus 例：Virchow (extracts/05-medical.md) "AUC of 0.950 with Virchow embeddings, 0.940
with UNI, 0.932 with Phikon and 0.907 with CTransPath" — 4 个方法在 bar plot 中，Virchow 高亮，
其余按时间灰阶递进。

### 2.4 不要做的事

- **jet / rainbow heatmap**：corpus 内零次。生信旧文献偶见，现代 Nature 系审稿会要求改。
- **matplotlib 默认 tab10 直接用**：identifiable 但 saturation 太一致，"我方"和 baseline 一样响。
  必须手动重 assign。
- **黄色 line**：白底几乎不可见。Wong 黄 #F0E442 只用于 fill / region，不用于 line。
- **半透明叠图**：scatter 大量点叠时 alpha=0.3 是好的；line plot 半透明会让读者怀疑是
  "草稿截图"。
- **每张 figure 一套配色**：一篇论文应有一致 color identity，跨 figure 同一类对象同色。

### 2.5 Caveat

- Diverging colormap 的中点必须是 0 或某个有意义的中心；中点不对会反误导。
- Sequential colormap 在 print 灰阶下要单调——viridis / cividis 满足，jet 不满足。
- 红 / 绿配对（"上调 vs 下调"）经典但红绿色盲读不出。把"上下调"改成 vermilion vs sky blue
  是 Wong 2011 主推方案。
- Nature 系一般要求最终 RGB 提交，部分子刊或印刷版可能要 CMYK——以官网为准。RGB → CMYK
  转换会让饱和荧光绿 / 荧光蓝大幅暗化，提交前预览。

---

