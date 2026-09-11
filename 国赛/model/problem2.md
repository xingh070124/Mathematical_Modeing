# 问题二建模：整个烘干过程（预热平衡 + 恒温干燥）的耦合传热传质模型

> 本文建立 2026 年高教社杯 A 题问题二（烘干全过程，输出前 3 h）的数学模型。
> 全部物性经验式取自题面**附录 3**，环境激励取自**附件 1**。
>
> **数值方法**：一维有限元（**线性单元**） + **集中质量矩阵** + **后向 Euler** + **Newton 迭代**。
>
> 与问题一的根本区别：问题一的 $D=D(C)$ 仅依赖含水率，温度场与水分场**单向解耦**；
> 问题二的 $D=D(C,T)$ 含 Arrhenius 温度项，且 $\rho,\ c_p,\ k$ 均随 $C$ 变化，
> 故两场**双向耦合、强非线性**，必须联立求解并作非线性迭代。

---

## 1 问题与建模目标

一根圆柱形中药材，长 $L=25\ \mathrm{cm}$、半径 $R=2\ \mathrm{cm}$，初始温度
$T_0=28\ ^\circ\mathrm{C}$、初始干基含水率 $C_0=2.55\ \mathrm{kg/kg}$，置于热风烘房中。

要求建立**整个烘干过程**（预热平衡阶段 + 恒温干燥阶段）药材内部温度场 $T(r,t)$
与水分浓度场 $C(r,t)$ 的数学模型，其中物性经验式**统一采用附录 3**；并给出

- **表 3 / 表 4**：3 h 内每隔 0.5 h（即 $0.5,1.0,1.5,2.0,2.5,3.0\ \mathrm{h}$）、
  到中心距离 $0,0.5,1,1.5,2\ \mathrm{cm}$ 处的温度与水分浓度；
- **`result2.xlsx`**：$0\sim 10800\ \mathrm{s}$ 内每隔 $1\ \mathrm{s}$、径向每隔
  $0.1\ \mathrm{cm}$ 的完整结果（工作表 `温度`、`水分浓度`）。

**待求解的未知场**：$T(r,t)$、$C(r,t)$，$r\in[0,R]$，$t\in[0,10800\ \mathrm{s}]$。

---

## 2 与问题一的区别（建模要点）

| 项目 | 问题一（预热平衡） | 问题二（全过程） |
|---|---|---|
| 扩散系数 | $D=7\times10^{-9}e^{-0.89/C}$，**只依赖 $C$** | $D=2.4\times10^{-3}e^{-0.45/C}e^{-3850/T}$，**依赖 $C$ 与 $T$** |
| 密度 | $\rho=820$ 常数 | $\rho=650+128C$，**随 $C$ 变化** |
| 比热容 | $c_p=2600$ 常数 | $c_p=1450+\dfrac{2736C}{C+1}$，**随 $C$ 变化** |
| 导热系数 | $k=0.36$ 常数 | $k=0.21+\dfrac{0.38C}{C+1}$，**随 $C$ 变化** |
| 蒸发吸热 | 无（预热阶段蒸发极弱，忽略） | **有**：表面相变吸热 $q_{\rm evap}=H_{\rm evap}h_m(C_R-C_\infty)$，见 §4.4 |
| 方程耦合 | 单向解耦，可各自求解 | **双向耦合**（三条通路，见下） |
| 求解方式 | 两个独立线性三对角系统（追赶法） | **非线性耦合系统 → Newton 迭代** |

**三条耦合通路**：

1. $T\to D\to C$：温度经 Arrhenius 项 $\exp(-3850/T)$ 影响水分扩散速率（强，$\partial\ln D/\partial T\approx4.25\%/\mathrm{K}$）；
2. $C\to\rho c_p,k\to T$：含水率经物性影响热惯性与导热能力（强，$\rho c_p$ 全程变化 $63.7\%$）；
3. **$C(R,t)\to q_{\rm evap}\to T(R,t)$**：表面含水率经相变潜热**直接**影响表面热平衡（弱但不可忽略，见 §4.4(c)）。

三条通路构成闭合反馈回路，这是问题二必须联立求解的根本原因。

---

## 3 建模假设

| 编号 | 假设 | 依据与适用范围 |
|---|---|---|
| **B1** | 药材为均质、各向同性的连续介质，形状为正圆柱 | 题面给定"形状大致呈圆柱形" |
| **B2** | 只考虑径向一维传递，忽略轴向与周向 | 中截面 $\partial_z=0$ 为对称性带来的**精确**条件（见问题一 §2.1）；端面换热面积仅占侧面 4 % |
| **B3** | 药材内部满足局部热平衡（LTE），固相与液相温度相同 | Biot 数量级分析见 §7 |
| **B4** | 物性 $\rho,c_p,k$ 随含水率 $C$ 按附录 3 经验式变化，**不显式依赖 $T$** | 题面明确"经验公式统一采用附录 3" |
| **B5** | 水分迁移由 Fick 扩散描述，$D=D(C,T)$ 由附录 3 给定 | 题面给定；忽略毛细压力驱动、重力与对流传质项 |
| **B6** | 表面为第三类（Robin）边界，平衡值取环境值 $T_\infty(t)$、$C_\infty(t)$ | 与附录 2 的 $h$、$h_m$ 配套；适用性边界讨论见问题一 §7.2 |
| **B7** | 前 3 h 内体积不收缩，$R$ 取常数 | 附件 2 显示 3 h 内 $R$ 由 2.000 降至约 1.75 cm（收缩约 12 %），收缩的显式处理属问题 4 |
| **B8** | 预热平衡与恒温干燥两阶段的差异**由环境激励 $T_\infty(t),C_\infty(t)$ 的时间历程体现**，控制方程形式统一 | 题面"相关经验公式统一采用附录 3"即指方程不变、参数统一 |
| **B9** | **计入水分蒸发吸热**：表面相变潜热 $q_{\rm evap}=H_{\rm evap}h_m(C_R-C_\infty)$，其中 $H_{\rm evap}(T)$ 由 **Clapeyron 方程 + Kirchhoff 定律推导**并按 IAPWS-95 定标，量级 $\sim2.43\times10^6\ \mathrm{J/kg}$ | 题面**未给出** $H_{\rm evap}$，但它可由 $T,p_{\rm sat},c_{p,l},c_{p,v}$ 等基础热力学量**推导得到**，无需引入经验拟合参数；推导、定标与闭合检验见 §4.4(c)。若需与"无相变"模型对比，令 $H_{\rm evap}=0$ 即可退化 |

> **对 B8 的说明**：题目指出"预热平衡与恒温干燥阶段的参数有所不同"，但同时要求
> "相关经验公式统一采用附录 3"。本文据此理解为：**控制方程与物性经验式在全程统一**，
> 两阶段的差别体现为环境条件 $T_\infty(t)$、$C_\infty(t)$（附件 1）在不同时段的变化。
> 这一处理使模型在全程连续、无需在阶段切换处引入人为间断。

---

## 4 控制方程

### 4.1 温度场

对半径 $r$ 处厚 $\mathrm{d}r$ 的薄环作能量守恒（净导入热量 = 内能增量）：

$$\rho(C)\,c_p(C)\,\frac{\partial T}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\left(k(C)\,r\frac{\partial T}{\partial r}\right)
+S_h$$

其中 $S_h$ 为**水分蒸发吸热源项**（$\mathrm{W/m^3}$，吸热为负）。本文采用单场 Fick
扩散描述水分迁移（式 2），水分以液相扩散至表面后蒸发，故**相变吸热发生在表面**，
$S_h$ 以表面热流（第二类边界）形式进入模型——详见 §4.4。若需刻画物料内部的分布式
蒸发（多相模型），可改用体源形式 $S_h=-H_{\rm evap}\dot m_v$（$\dot m_v$ 为体积蒸发
速率，$\mathrm{kg/(m^3\cdot s)}$），本文不采用，理由见 §4.4(b)。

**注意**：$\rho c_p$ 随 $C$ 变化，**不能移到时间导数之内或之外**——即写成
$\partial(\rho c_pT)/\partial t$ 与 $\rho c_p\,\partial T/\partial t$ 在本题中不等价。
本文采用式 (1) 的形式（以 $T$ 为状态量、$\rho c_p$ 作为系数），理由是题面附录 3 的
物性经验式以 $C$ 为自变量，属于"以温度 $T$ 为基本未知量、物性为已知场系数"的表述习惯。

### 4.2 水分场

对同一薄环作干基水分质量守恒：

$$\frac{\partial C}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\left(r\,D(C,T)\frac{\partial C}{\partial r}\right)
\label{eq:C}\tag{2}$$

### 4.3 附录 3 物性经验式

$$\rho(C)=650+128C\quad(\mathrm{kg/m^3}),\qquad
c_p(C)=1450+\frac{2736C}{C+1}\quad(\mathrm{J/(kg\cdot K)}),\qquad
k(C)=0.21+\frac{0.38C}{C+1}\quad(\mathrm{W/(m\cdot K)})$$

$$D(C,T)=2.4\times10^{-3}\exp\!\left(-\frac{0.45}{C}\right)\exp\!\left(-\frac{3850}{T}\right)
\quad(\mathrm{m^2/s}),\qquad T\ \text{取热力学温度}\ \mathrm{K}$$

**非线性来源**（三重）：

1. $D$ 对 $C$ 呈 $\exp(-0.45/C)$ 型强非线性——$C$ 越小时 $D$ 衰减越快；
2. $D$ 对 $T$ 呈 Arrhenius 型 $\exp(-3850/T)$——温度每升高 $10\ \mathrm{K}$（$50\to60\ ^\circ\mathrm{C}$），
   $D$ 约增大 $1.43$ 倍；
3. $(\rho c_p)(C)$ 随 $C$ 单调下降（$C:2.55\to0.15$ 时由 $3.335\times10^6$ 降至
   $1.209\times10^6\ \mathrm{J/(m^3\cdot K)}$，降幅 $63.7\%$），使热惯性在干燥过程中显著改变。

### 4.4 水分蒸发吸热项（相变潜热耦合）

#### (a) 物理机制与数学表述

水分从药材表面蒸发进入热风时需吸收**汽化潜热** $H_{\rm evap}$，该热量取自药材本身，
因而**抑制表面升温、甚至使表面温度低于环境温度**（"蒸发降温"效应）。这是干燥过程
中传热与传质耦合的**第二条通路**（第一条为 $D$ 的 Arrhenius 温度依赖，见 §7.2）。

**表面能量平衡**。设 $q_{\rm cond}=-k\,\partial T/\partial r\big|_R$ 为物料内部向表面
传导的热流（向外为正），$q_{\rm conv}=h\left[T_\infty-T(R)\right]$ 为热风对表面的对流
供热（向物料内为正），$q_{\rm evap}$ 为表面蒸发吸收的热流（取自物料，为耗散项）。
稳态下表面能量守恒：

$$q_{\rm cond}+q_{\rm conv}=q_{\rm evap}$$

整理得**含蒸发吸热的第三类边界条件**：

$$\boxed{\ -k\left.\frac{\partial T}{\partial r}\right|_{r=R}
=h\left[T(R,t)-T_\infty(t)\right]+q_{\rm evap}\ },\qquad
q_{\rm evap}=H_{\rm evap}\,\phi_w\big|_R
\label{eq:bcT_evap}\tag{3'}$$

其中 $\phi_w|_R$ 为表面水分通量。与题面给定的传质边界（式 4）联立，在表面上恒有

$$\phi_w\big|_R=h_m\left[C(R,t)-C_\infty(t)\right]$$

（蒸发质量通量 = 对流带走的量），故最终

$$\boxed{\ q_{\rm evap}=H_{\rm evap}\,h_m\left[C(R,t)-C_\infty(t)\right]\ }
\label{eq:qevap}\tag{3''}$$

**符号约定的一致性**：式 (3'') 采用与题面边界条件（式 3、4）**相同的通量口径**——
传质边界 $-D\,\partial_rC=h_m(C-C_\infty)$ 中两侧同为"以浓度梯度表示的通量"，
不额外乘以密度因子。本文沿用该口径以保证与题面参数（$h_m=8\times10^{-7}\ \mathrm{m/s}$）
自洽；由此带来的量纲说明与敏感性见 (c)。

**方向验证**：$C>C_\infty$ 时 $q_{\rm evap}>0$，式 (3') 右端增大，即**向外传导的热流
增大**，等价于表面温度**降低**——与"蒸发使表面变冷"的物理预期一致。✓

#### (b) 为何用表面热流而非体源

两类建模路线：

| 路线 | 形式 | 适用模型 | 本文取舍 |
|---|---|---|---|
| **表面热流**（式 3'） | 进入 Robin 边界，为边界项 | 单场 Fick 扩散（液相迁移为主，相变在表面发生） | **采用** |
| **体源** | $S_h=-H_{\rm evap}\dot m_v$ 进入控制方程 | 多相/多孔介质模型（含独立气相场、内部蒸发前沿） | 不采用 |

**理由**：本文采用单一含水率场 $C$ 的 Fick 扩散模型（式 2），模型中**不含独立的水
蒸气相场**，无法定义内部的体积蒸发速率 $\dot m_v$；在此框架下，水分的"迁移"与"相变"
在空间上是分离的——液相扩散至表面、在表面蒸发。故相变吸热只能且应当以**表面热流**
形式施加。这与文献做法一致（杨历 2005 的边界含 $r_l\alpha_m(M-M_f)$ 潜热项；
番石榴模型在表面边界扣除 $\lambda_vD_{\rm eff}\partial_xc_w$）。

若要在本模型中加入分布式内部蒸发，需升级为含气相场的多相模型（如胡众欢 2020 的
气/液双场方程 + 源项 $R=K_{\rm evap}(a_wc_{v,\rm sat}-c_v)$），超出本题范围。

#### (c) 汽化潜热 $H_{\rm evap}(T)$ 的热力学推导、定标与量级

题面附录 2/3 **未给出** $H_{\rm evap}$（假设 B9）。本节不作"直接抄文献常数"的处理，
而是由**热力学基本关系推导其函数形式与温度系数**，再用国际水物性标准 IAPWS-95 定标，
并在第 (v) 小节作闭合检验。

##### (i) 相平衡条件 → Clapeyron 方程

液、气两相在饱和线上共存时，两相的比 Gibbs 自由能（化学势）相等：

$$g_l(T,p_{\rm sat})=g_v(T,p_{\rm sat})$$

沿饱和线微分，并利用 $\mathrm{d}g=-s\,\mathrm{d}T+v\,\mathrm{d}p$：

$$-s_l\,\mathrm{d}T+v_l\,\mathrm{d}p_{\rm sat}=-s_v\,\mathrm{d}T+v_v\,\mathrm{d}p_{\rm sat}$$

整理后代入可逆相变关系 $s_v-s_l=H_{\rm evap}/T$：

$$\boxed{\ \frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}
=\frac{s_v-s_l}{v_v-v_l}=\frac{H_{\rm evap}}{T\,(v_v-v_l)}\ }
\qquad\Longleftrightarrow\qquad
H_{\rm evap}=T\,(v_v-v_l)\,\frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}
\label{eq:clapeyron}\tag{3a}$$

式 (3a) 即**精确的 Clapeyron 方程**（$v_l,v_v$ 为液、气两相的比容），它把潜热这一
"能量量"与可测的饱和蒸气压曲线联系起来，是本节推导的出发点。

##### (ii) Clausius–Clapeyron 近似及其误差的定量解释

对式 (3a) 引入两项近似：

1. **$v_l\ll v_v$**：$20\ ^\circ\mathrm{C}$ 时 $v_v=57.76\ \mathrm{m^3/kg}$、
   $v_l=1.002\times10^{-3}\ \mathrm{m^3/kg}$，$v_l/v_v=1.7\times10^{-5}$，
   忽略 $v_l$ 的相对误差为 $O(10^{-5})$；
2. **气相为理想气体**：$v_v=R_vT/p_{\rm sat}$，其中
   $R_v=\dfrac{R_u}{M_w}=\dfrac{8.314462618}{0.0180153}=461.5\ \mathrm{J/(kg\cdot K)}$。

代入式 (3a) 即得 **Clausius–Clapeyron（CC）方程**：

$$\boxed{\ \frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}
=\frac{H_{\rm evap}\,p_{\rm sat}}{R_vT^2}
\qquad\Longleftrightarrow\qquad
H_{\rm evap}(T)=R_vT^2\,\frac{\mathrm{d}\ln p_{\rm sat}}{\mathrm{d}T}\ }
\label{eq:cc}\tag{3b}$$

**CC 近似的误差可精确量化**。保留真实气体则 $v_v=ZR_vT/p_{\rm sat}$（$Z$ 为压缩因子），
代回式 (3a) 得 $H_{\rm evap}=R_vT^2(\mathrm{d}\ln p_{\rm sat}/\mathrm{d}T)/Z$，故

$$\frac{H_{\rm evap}^{\rm CC}}{H_{\rm evap}^{\rm true}}=\frac{1}{Z}$$

数值验证（IAPWS-95）：

| $T$ (°C) | 20 | 30 | 40 | 50 |
|---|---|---|---|---|
| 压缩因子 $Z$ | 0.998649 | 0.998027 | 0.997189 | 0.996086 |
| $1/Z-1$（理论预测） | $0.1352\%$ | $0.1977\%$ | $0.2819\%$ | $0.3930\%$ |
| 式 (3b) 实测偏差 | $0.1370\%$ | $0.2008\%$ | $0.2871\%$ | $0.4014\%$ |

理论与实测吻合到 $0.002\%\sim0.009\%$——**证实 CC 近似的偏差确实全部来自气相非理想性**，
且其量级（$<0.5\%$）在本题精度要求下可忽略。

##### (iii) Kirchhoff 定律 → 潜热的温度依赖

由 $H_{\rm evap}(T)=h_v(T)-h_l(T)$，沿饱和线对 $T$ 求导：

$$\boxed{\ \frac{\mathrm{d}H_{\rm evap}}{\mathrm{d}T}=c_{p,v}(T)-c_{p,l}(T)
\equiv\Delta c_p(T)\ }$$

即 **Kirchhoff 定律**：潜热的温度系数等于气、液两相定压比热之差。若 $\Delta c_p$ 在
区间内近似为常数，积分即得潜热的**线性温度依赖**：

$$H_{\rm evap}(T)=H_{\rm evap}(T_0)+\Delta c_p\,(T-T_0)$$

数值（IAPWS-95，$20\sim50\ ^\circ\mathrm{C}$）：

| $T$ (°C) | 20 | 25 | 30 | 35 | 40 | 45 | 50 |
|---|---|---|---|---|---|---|---|
| $c_{p,l}$ (J/(kg·K)) | 4184.4 | 4181.6 | 4180.1 | 4179.5 | 4179.6 | 4180.4 | 4181.5 |
| $c^0_{p,v}$（理想气体） | 1863.2 | 1864.4 | 1865.6 | 1867.0 | 1868.4 | 1869.8 | 1871.3 |
| $\Delta c_p^0=c^0_{p,v}-c_{p,l}$ | $-2321.2$ | $-2317.2$ | $-2314.4$ | $-2312.5$ | $-2311.3$ | $-2310.5$ | $-2310.2$ |
| $\mathrm{d}H_{\rm evap}/\mathrm{d}T$（数值） | $-2367.2$ | $-2370.5$ | $-2375.9$ | $-2383.1$ | $-2392.1$ | $-2402.8$ | $-2415.0$ |

**两项的差别及其解释**：理想气体项平均为 $\Delta c_p^0=-2.314\times10^3\ \mathrm{J/(kg\cdot K)}$，
而数值斜率平均为 $-2.387\times10^3\ \mathrm{J/(kg\cdot K)}$，相差 $-73\ \mathrm{J/(kg\cdot K)}$
（$3.0\%$）。差异来源正是 (ii) 中被略去的**饱和蒸气非理想性**：真实蒸气的焓沿饱和线
还含压力项

$$\left(\frac{\partial h_v}{\partial p}\right)_T\frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}
=v_v\,(1-T\alpha_v)\,\frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}$$

该项随 $T$ 升高而增大（$p_{\rm sat}$ 由 $2.34$ 升至 $12.35\ \mathrm{kPa}$，$v_v$ 由
$57.8$ 降至 $12.0\ \mathrm{m^3/kg}$），正是表中数值斜率由 $-2367$ 单调变到 $-2415$ 的
原因。**因此工作区间内应取实测斜率，而非理想气体值。**

##### (iv) 数值定标

以物料初温 $28\ ^\circ\mathrm{C}$ 为物理锚点，取 IAPWS-95 的精确值
$H_{\rm evap}(28\ ^\circ\mathrm{C})=2.43456\times10^6\ \mathrm{J/kg}$；斜率由
$28\sim50\ ^\circ\mathrm{C}$（实际工况区间）上的最小二乘定出
$\Delta c_p=-2.391\times10^3\ \mathrm{J/(kg\cdot K)}$：

$$\boxed{\ H_{\rm evap}(T)=2.4346\times10^6-2.391\times10^3\,(T-28\ ^\circ\mathrm{C})
\quad(\mathrm{J/kg})\ }$$

等价地以摄氏温度直接展开：

$$H_{\rm evap}(T)\approx2.5015\times10^6-2.391\times10^3\,T_{^\circ\mathrm{C}}
\quad(\mathrm{J/kg})$$

| $T$ | $20\ ^\circ\mathrm{C}$ | $28\ ^\circ\mathrm{C}$ | $40\ ^\circ\mathrm{C}$ | $50\ ^\circ\mathrm{C}$ |
|---|---|---|---|---|
| 定标式 (J/kg) | $2.4537\times10^6$ | $2.4346\times10^6$ | $2.4059\times10^6$ | $2.3820\times10^6$ |
| IAPWS-95 参考 | $2.4535\times10^6$ | $2.4346\times10^6$ | $2.4060\times10^6$ | $2.3819\times10^6$ |
| 相对偏差 | $+0.007\%$ | $0$ | $-0.005\%$ | $+0.001\%$ |

在 $28\sim50\ ^\circ\mathrm{C}$ 上最大残差 $80\ \mathrm{J/kg}$（$0.0033\%$），
外推至 $20\ ^\circ\mathrm{C}$ 时偏差仍 $<0.01\%$。

> **说明**：上式由热力学第一性关系推导、国际水物性标准定标，**不引入额外可调参数**；
> 题面未给 $H_{\rm evap}$ 的问题至此闭合。若需退化到"无相变"模型，令 $H_{\rm evap}=0$
> 即可（见 §14 的 V8）。

##### (v) 一致性验证（闭合检验）

将定标式反代回 CC 方程 (3b) 积分，自三相点 $(273.16\ \mathrm{K},\ 0.6117\ \mathrm{kPa})$
出发反演饱和蒸气压，与 IAPWS-95 独立对比：

| $T$ (°C) | 10 | 20 | 30 | 40 | 50 |
|---|---|---|---|---|---|
| $p_{\rm sat}$ IAPWS (kPa) | 1.22820 | 2.33932 | 4.24697 | 7.38494 | 12.35195 |
| 由定标式反演 (kPa) | 1.22753 | 2.33620 | 4.23666 | 7.35633 | 12.28144 |
| 相对偏差 | $-0.05\%$ | $-0.13\%$ | $-0.24\%$ | $-0.39\%$ | $-0.57\%$ |

偏差为负且随 $T$ 单调增大，其数值与 (ii) 中已定量的 $1/Z-1$（$0.135\%@20\ ^\circ\mathrm{C}
\to0.393\%@50\ ^\circ\mathrm{C}$）同向、同量级——说明偏差**完全来源于 CC 近似本身**，
而非定标式的拟合误差。在 $28\sim50\ ^\circ\mathrm{C}$ 内该偏差 $<0.6\%$，可接受。

##### (vi) 蒸发吸热热流与量级

**蒸发吸热热流**：由式 (3'') 与 (iv) 的定标式，

$$q_{\rm evap}=H_{\rm evap}h_m\left(C_R-C_\infty\right)
\approx2.4059\times10^6\times8\times10^{-7}\times\left(C_R-C_\infty\right)
\approx1.925\left(C_R-C_\infty\right)\ \mathrm{J/(m^2\cdot s)}$$

（$H_{\rm evap}$ 取工作区间中部的 $40\ ^\circ\mathrm{C}$ 值。）

| 时刻 | $C_\infty$（附件 1） | 取 $C_R\approx2.5$ 时 $q_{\rm evap}$ | 对流热流 $h(T_\infty-T_R)$ | 比值 |
|---|---|---|---|---|
| $t=0$ | 0.0196 | $4.77\ \mathrm{J/(m^2s)}$ | $0$（$T_\infty=T_0$） | — |
| $t=1800\ \mathrm{s}$ | 0.0331 | $4.75$ | $25\times(41.5-28)=338$ | $1.4\%$ |
| $t=3600\ \mathrm{s}$ | 0.0427 | $4.73$ | $25\times(47.5-28)=488$ | $1.0\%$ |

**表面温降估计**：若忽略由内部补充的热量，则蒸发造成的表面温降约为

$$\Delta T_R\sim\frac{q_{\rm evap}}{h}=\frac{4.73}{25}\approx0.19\ \mathrm{K}$$

即**约 $0.2\ \mathrm{K}$ 量级的表面降温**——在四位小数的报告精度（$5\times10^{-5}$）下
**必须计入**，但不会改变温度场的整体形态。

**参数敏感性（重要提醒）**：$q_{\rm evap}$ 与 $h_m$ 成正比。题面给定的
$h_m=8\times10^{-7}\ \mathrm{m/s}$ 比"热质传递类比"估计值（$\sim0.02\ \mathrm{m/s}$，
见问题一 §7.2）低约 **4 个数量级**；若改用类比值，$q_{\rm evap}$ 将放大**约 25000 倍**，
远超对流供热而成为表面热平衡的主导项（此时表面将被强烈冷却）。因此：

- **本文按题面给定 $h_m$ 计算**，$q_{\rm evap}$ 为 $O(1\ \mathrm{W/m^2})$ 的小修正；
- 该结论**强依赖于 $h_m$ 的口径**，论文中应显式说明；建议在数值验证中给出
  $h_m$ 的敏感性分析（见 §14 的 V9）。

#### (d) 对模型结构的影响

引入式 (3'') 后，温度方程在**表面节点**上出现对 $C_M$ 的显式依赖，形成第三条耦合通路：

$$\text{（新）}\quad C(R,t)\ \xrightarrow{\ q_{\rm evap}=H_{\rm evap}h_m(C-C_\infty)\ }\ T(R,t)$$

此前只有 $C\to\rho c_p,k\to T$ 的**间接**通路（通过物性），现在是**直接的表面耦合**。
该通路的 Jacobian 贡献为常数（§11.2 块 (1,2) 的 $(M,M)$ 元），实现简单、不增加带宽。

---

## 5 参数确定与量级分析

| 符号 | 含义 | 数值 | 来源 |
|---|---|---|---|
| $h$ | 对流换热系数 | $25\ \mathrm{W/(m^2\cdot K)}$ | 附录 2 |
| $h_m$ | 对流传质系数 | $8\times10^{-7}\ \mathrm{m/s}$ | 附录 2 |
| $H_{\rm evap}$ | 水的汽化潜热 | $2.4346\times10^6-2.391\times10^3\,(T-28\ ^\circ\mathrm{C})\ \mathrm{J/kg}$ | **题面未给**，由 Clapeyron 方程 + Kirchhoff 定律推导、按 IAPWS-95 定标（假设 B9，§4.4c）；$28\sim50\ ^\circ\mathrm{C}$ 内为 $2.4346\sim2.3820\times10^6$ |
| $R$ | 半径 | $2\ \mathrm{cm}=0.02\ \mathrm{m}$ | 题面 |
| $T_0$ | 初始温度 | $28\ ^\circ\mathrm{C}=301.15\ \mathrm{K}$ | 题面 |
| $C_0$ | 初始含水率 | $2.55\ \mathrm{kg/kg}$ | 题面 |

**物性随 $C$ 的变化**（由附录 3 直接算出）：

| $C$ (kg/kg) | $\rho$ (kg/m³) | $c_p$ (J/(kg·K)) | $k$ (W/(m·K)) | $\alpha=k/(\rho c_p)$ (m²/s) |
|---|---|---|---|---|
| $2.55$（初始） | 976.40 | 3415.30 | 0.48296 | $1.4483\times10^{-7}$ |
| $2.00$ | 906.00 | 3274.00 | 0.46333 | $1.5620\times10^{-7}$ |
| $1.00$ | 778.00 | 2818.00 | 0.40000 | $1.8245\times10^{-7}$ |
| $0.50$ | 714.00 | 2362.00 | 0.33667 | $1.9963\times10^{-7}$ |
| $0.15$（问题 3 目标） | 669.20 | 1806.87 | 0.25957 | $2.1467\times10^{-7}$ |

**扩散系数**（由附录 3 算出）：

| $C$ | $T$ | $D$ (m²/s) |
|---|---|---|
| $2.55$ | $28\ ^\circ\mathrm{C}$（$301.15\ \mathrm{K}$） | $5.6417\times10^{-9}$ |
| $2.55$ | $50\ ^\circ\mathrm{C}$ | $1.3471\times10^{-8}$ |
| $1.00$ | $50\ ^\circ\mathrm{C}$ | $1.0247\times10^{-8}$ |
| $0.15$ | $50\ ^\circ\mathrm{C}$ | $8.0012\times10^{-10}$ |
| $0.05$ | $50\ ^\circ\mathrm{C}$ | $1.9833\times10^{-12}$ |

> 可见 $D$ 在可能的 $(C,T)$ 范围内跨越约 **7 个数量级**（$5.6\times10^{-9}$ 至
> $2.0\times10^{-12}$），且 $T$ 由 $28\to50\ ^\circ\mathrm{C}$ 使 $D$ 增大 $2.4$ 倍——
> 温度对水分迁移的**加速作用不可忽略**，这正是两场耦合的物理体现。

---

## 6 定解条件

### 6.1 初始条件（$t=0$，$0\le r\le R$）

$$T(r,0)=T_0=28\ ^\circ\mathrm{C}=301.15\ \mathrm{K},\qquad C(r,0)=C_0=2.55\ \mathrm{kg/kg}$$

### 6.2 中心对称条件（$r=0$）

由轴对称与可微性：

$$\left.\frac{\partial T}{\partial r}\right|_{r=0}=0,\qquad\left.\frac{\partial C}{\partial r}\right|_{r=0}=0$$

### 6.3 表面第三类边界（$r=R$）

$$-k(C)\left.\frac{\partial T}{\partial r}\right|_{r=R}
=h\left[T(R,t)-T_\infty(t)\right]+H_{\rm evap}\,h_m\left[C(R,t)-C_\infty(t)\right]
\label{eq:bcT}\tag{3}$$

$$-D(C,T)\left.\frac{\partial C}{\partial r}\right|_{r=R}=h_m\left[C(R,t)-C_\infty(t)\right]
\label{eq:bcC}\tag{4}$$

式 (3) 右端第二项即**蒸发吸热热流** $q_{\rm evap}$（式 (3'')），其推导与量级见 §4.4；
若取 $H_{\rm evap}=0$ 则退化为无相变耦合的纯对流边界。

### 6.4 环境激励的连续化

附件 1 给出 $T_\infty(t)$、$C_\infty(t)$ 的离散值（$\Delta t=60\ \mathrm{s}$，覆盖
$0\sim14400\ \mathrm{s}$），采用**保形分段三次插值（PCHIP）**连续化，理由见问题一 §6.4
（水分浓度序列含测量噪声，PCHIP 单调不过冲）。

**时间范围**：题面要求输出前 3 h（$10800\ \mathrm{s}$），落在附件 1 的覆盖区间内，
无需外推。若需外推至 2 ~ 3 天的全过程，本文建议对 $t>14400\ \mathrm{s}$ 采用
**末值保持**（$T_\infty=T_\infty(14400)$、$C_\infty=C_\infty(14400)$），并在论文中注明。

---

## 7 模型特性分析

### 7.1 特征数与量纲分析

以 $R$ 为特征长度、$R^2/\alpha(C_0)$ 为特征时间：

| 特征数 | 定义 | 数值 | 含义 |
|---|---|---|---|
| 热 Biot 数 | $\mathrm{Bi}=hR/k(C_0)$ | $1.0353$ | $>0.1$，内部温度梯度不可忽略，必须用分布参数模型 |
| 传质 Biot 数 | $\mathrm{Bi}_m=h_mR/D(C_0,T_0)$ | $2.8360$ | 表面传质与内部扩散阻力同量级 |
| 导热特征时间 | $R^2/\alpha(C_0)$ | $2761.9\ \mathrm{s}$ | 与 3 h 同量级，说明 3 h 内温度接近平衡 |
| 湿分特征时间 | $R^2/D(C_0,T_0)$ | $70900.9\ \mathrm{s}$ | 比 3 h 大 6.6 倍，说明水分远未平衡 |
| 热/湿时间尺度比 | $D/\alpha$ | $0.0390$ | 水分过程比温度过程慢约 26 倍 |

**关键结论**：3 h 内温度已趋于准稳态（$t\gg R^2/\alpha$），而含水率仅发生部分下降。
这意味着在 3 h 的时间窗内，**温度方程起"快速跟随"作用、水分方程起"慢变主导"作用**，
两者的时间尺度分离（约 26 倍）是刚性的主要来源，要求时间积分格式**无条件稳定**
（后向 Euler 满足）。

### 7.2 耦合的强度分析

由附录 3 可直接估计两条耦合路径的强度：

$$\frac{\partial \ln D}{\partial T}=\frac{3850}{T^2}\approx4.25\times10^{-2}\ \mathrm{K^{-1}}
\quad(\text{在 }T=301\ \mathrm{K})$$

即温度每升高 $1\ \mathrm{K}$，$D$ 增大约 $4.25\%$——**温度对水分迁移的灵敏系数约 4 %/K**，
在 $28\to50\ ^\circ\mathrm{C}$ 的升温区间内 $D$ 累计增大 $2.4$ 倍，属**强耦合**。

反向路径：$C$ 由 $2.55$ 降至 $0.15$ 时 $\rho c_p$ 下降 $63.7\%$，等价于**热惯性减小**，
使物料升温更快——这是"干燥后期升温加速"的机理来源，同样不可忽略。

**第三条通路（蒸发吸热，新增）**：表面含水率经相变潜热直接影响表面热平衡，
其强度可由"表面温降"衡量（§4.4c）：

$$\Delta T_R\sim\frac{q_{\rm evap}}{h}\approx0.2\ \mathrm{K}$$

与温升总幅度（$28\to50\ ^\circ\mathrm{C}$，约 $22\ \mathrm{K}$）相比为 **$0.9\%$**，
属**弱耦合**；但因其**直接作用于表面节点**（不经物性缓冲），在四位小数精度下必须保留。

---

## 8 弱形式（Galerkin）

### 8.1 函数空间与试探/检验函数

取试探函数 $T(\cdot,t),C(\cdot,t)\in V$，检验函数 $v\in V$，其中

$$V=\left\{v\in H^1(0,R)\ :\ v\ \text{满足 }r\to0\ \text{处的对称性（自然满足）}\right\}$$

即中心对称条件在弱形式中**自然满足**（无需强加），这是柱坐标加权 $r\,\mathrm{d}r$ 的
直接结果。

### 8.2 温度方程

式 (1) 两端乘以权函数 $v$ 并以 $r\,\mathrm{d}r$ 为体积权积分：

$$\int_0^R \rho c_p\,\frac{\partial T}{\partial t}\,v\,r\,\mathrm{d}r
=\int_0^R \frac{1}{r}\frac{\partial}{\partial r}\left(k\,r\frac{\partial T}{\partial r}\right)v\,r\,\mathrm{d}r
=\int_0^R \frac{\partial}{\partial r}\left(k\,r\frac{\partial T}{\partial r}\right)v\,\mathrm{d}r$$

右端分部积分：

$$\int_0^R\! \frac{\partial}{\partial r}\!\left(k r\frac{\partial T}{\partial r}\right)v\,\mathrm{d}r
=\Big[k\,r\frac{\partial T}{\partial r}v\Big]_0^R-\int_0^R k\,r\frac{\partial T}{\partial r}\frac{\partial v}{\partial r}\,\mathrm{d}r$$

边界项：$r=0$ 处因 $r=0$ 而自动为零；$r=R$ 处代入式 (3)（**含蒸发吸热项**），得

$$\left.k\,r\frac{\partial T}{\partial r}v\right|_{R}
=-hR\left[T(R)-T_\infty\right]v(R)-H_{\rm evap}h_mR\left[C(R)-C_\infty\right]v(R)$$

故

$$\boxed{\ \int_0^R\! \rho c_p\,\frac{\partial T}{\partial t}\,v\,r\,\mathrm{d}r
+\int_0^R\! k\,r\,\frac{\partial T}{\partial r}\frac{\partial v}{\partial r}\,\mathrm{d}r
+hR\left[T(R,t)-T_\infty(t)\right]v(R)
+\underbrace{H_{\rm evap}h_mR\left[C(R,t)-C_\infty(t)\right]v(R)}_{\text{蒸发吸热}}=0\ }
\label{eq:weakT}\tag{5}$$

其中末项是**唯一使温度方程显式依赖 $C$ 的项**（其余 $C$ 依赖均通过物性 $\rho c_p,k$
间接进入），它把温度与水分在**表面节点 $M$** 上直接耦合起来。

### 8.3 水分方程

同理，式 (2) 乘 $v$ 并以 $r\,\mathrm{d}r$ 积分、分部积分、代入式 (4)：

$$\boxed{\ \int_0^R\! \frac{\partial C}{\partial t}\,v\,r\,\mathrm{d}r
+\int_0^R\! D\,r\,\frac{\partial C}{\partial r}\frac{\partial v}{\partial r}\,\mathrm{d}r
+h_mR\left[C(R,t)-C_\infty(t)\right]v(R)=0\ }
\label{eq:weakC}\tag{6}$$

**注**：第三类边界以**自然边界条件**方式进入弱形式，无需在试探空间中强加，
这是有限元方法相对有限差分的一个结构性优点。

---

## 9 有限元离散（线性单元）

### 9.1 网格

取节点 $r_i=i\,\Delta r$，$\Delta r=R/M$，$i=0,1,\dots,M$（与问题一同一套节点式网格，
便于两问结果对照）。$r_0=0$ 为中心、$r_M=R$ 为表面。

单元 $e_i=[r_{i-1},r_i]$，长度 $h_e\equiv\Delta r$。线性（$P_1$）基函数：

$$\varphi_i(r)=\begin{cases}
\dfrac{r-r_{i-1}}{\Delta r}, & r\in[r_{i-1},r_i]\\[6pt]
\dfrac{r_{i+1}-r}{\Delta r}, & r\in[r_i,r_{i+1}]\\[6pt]
0, & \text{其他}
\end{cases}$$

满足 $\sum_j\varphi_j(r)\equiv1$（单位分解）与 $\varphi_i(r_j)=\delta_{ij}$。

有限元近似：$T(r,t)\approx\sum_{j=0}^{M}T_j(t)\varphi_j(r)$，
$C(r,t)\approx\sum_{j=0}^{M}C_j(t)\varphi_j(r)$。

### 9.2 质量矩阵与刚度矩阵

**质量矩阵（温度）**

$$M_{ij}=\int_0^R\rho c_p\,\varphi_i\varphi_j\,r\,\mathrm{d}r$$

**刚度矩阵（温度）**

$$K_{ij}=\int_0^R k\,r\,\varphi_i'\varphi_j'\,\mathrm{d}r$$

单元 $e=[r_{i-1},r_i]=[a,b]$（记 $h\equiv\Delta r$，$\rho c_p$、$k$ 在单元内取节点平均值）
上的解析积分：

**一致质量矩阵**（含轴对称权 $r$）

$$M^{e}=\frac{\rho c_p\,h}{12}
\begin{bmatrix}3a+b & a+b\\ a+b & a+3b\end{bmatrix}$$

> **推导**：$M^e_{11}=\int_a^b\rho c_p r\varphi_1^2\,\mathrm{d}r$，令 $r=a+s$（$s\in[0,h]$）、
> $\varphi_1=1-s/h$，则
> $\int_0^h(a+s)(1-s/h)^2\mathrm{d}s=\dfrac{a h}{3}+\dfrac{h^2}{12}=\dfrac{h(3a+b)}{12}$；
> 同理 $M^e_{12}=\dfrac{h(a+b)}{12}$、$M^e_{22}=\dfrac{h(a+3b)}{12}$。
> **退化检验**：当权函数退化为常数（$a=h/2$ 的中置单元）时三项分别为
> $h/3,\ h/6,\ h/3$，回到标准一维线性单元质量矩阵，验证公式正确。

**刚度矩阵**

$$K^{e}=\frac{k\,(a+b)}{2h}
\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$$

> **推导**：$\int_{a}^{b} k\,r\,(\varphi')^2\mathrm{d}r
> =k\int_a^b r\,\frac{1}{h^2}\mathrm{d}r=\frac{k}{2h^2}(b^2-a^2)
> =\frac{k(a+b)}{2h}$；非对角元取负号。

**边界项**：$hR\,v(R)$ 对应的贡献只在 $i=j=M$ 处，即
$K_{MM}\mathrel{+}=hR$；右端 $hR\,T_\infty(t)$ 作用在第 $M$ 个方程。

### 9.3 集中质量矩阵（lumped mass matrix）

将一致质量矩阵按**行和集中**（row-sum lumping）：

$$M^{L}_{ii}=\sum_{j}M_{ij}=\int_0^R\rho c_p\,\varphi_i\Big(\sum_j\varphi_j\Big)r\,\mathrm{d}r
=\int_0^R\rho c_p\,\varphi_i\,r\,\mathrm{d}r
\quad(\text{用单位分解}\ \textstyle\sum_j\varphi_j\equiv1)$$

单元 $e=[a,b]$ 的行和为：左节点 $\rho c_p h\dfrac{2a+b}{6}$、右节点 $\rho c_p h\dfrac{a+2b}{6}$
（由 §9.2 的一致质量矩阵行求和得到）。

对内部节点 $i$（$1\le i\le M-1$），由左右两个单元贡献——在左单元 $[r_{i-1},r_i]$ 中
它是**右节点**，在右单元 $[r_i,r_{i+1}]$ 中它是**左节点**：

$$M^{L}_{ii}=\rho c_p\left[\frac{\Delta r\,(r_{i-1}+2r_i)}{6}+\frac{\Delta r\,(2r_i+r_{i+1})}{6}\right]
=\frac{\rho c_p\Delta r}{6}\Big[(i-1+2i)+(2i+i+1)\Big]\Delta r=\rho c_p\,\Delta r\,r_i$$

（末步用到 $r_i=i\Delta r$ 及 $(3i-1)+(3i+1)=6i$）。即

$$\boxed{\ M^{L}_{ii}=\rho(C_i)\,c_p(C_i)\,\Delta r\,r_i\ }$$

> **数值核验**：按上式与直接对一致质量矩阵作行求和，在 $i=1,\dots,M-1$ 上相对误差
> 为机器精度（$\sim10^{-16}$），已验证。

边界节点只有单侧单元贡献：

$$M^{L}_{00}=\rho c_p\frac{\Delta r\,(2r_0+r_1)}{6}=\frac{\rho c_p\,\Delta r^2}{6},\qquad
M^{L}_{MM}=\rho c_p\frac{\Delta r\,(r_{M-1}+2r_M)}{6}=\frac{\rho c_p\,\Delta r^2(3M-1)}{6}$$

水分方程的质量矩阵不含 $\rho c_p$，同理得

$$M^{L,C}_{ii}=\Delta r\,r_i\quad(\text{内部}),\qquad
M^{L,C}_{00}=\frac{\Delta r^2}{6},\qquad M^{L,C}_{MM}=\frac{\Delta r^2(3M-1)}{6}$$

**采用集中质量矩阵的理由**：

1. **物理意义明确**：$M^L_{ii}=\rho c_p\Delta r\,r_i$ 恰是"节点 $i$ 所在环形控制体"
   （体积 $\Delta r\cdot r_i$，单位轴向长度）的热容，与有限体积法的控制体离散一致；
2. **保持极值原理**：质量矩阵对角化后，离散格式的最大值原理与正性条件更易满足
   （一致质量矩阵在粗网格下可能产生小的负系数，破坏极值原理）；
3. **计算效率**：时间推进无需解质量矩阵（$\dot{\mathbf T}$ 显式），且与后向 Euler
   配合时对角矩阵使 Newton 的 Jacobian 结构更简单；
4. **与守恒性相容**：行和集中保持 $\sum_i M^L_{ii}=\int\rho c_p\,r\,\mathrm{d}r$，
   总热容精确守恒。

> **代价**：集中质量使空间精度由 $O(\Delta r^2)$ 降至 $O(\Delta r)$（超收敛点消失）。
> 对本题四位小数的报告精度，需通过网格收敛性验证确认（见 §12）。

---

## 10 时间离散（后向 Euler）

### 10.1 半离散系统

将 §9 代入弱形式 (5)(6)，取 $v=\varphi_i$，得半离散常微分方程组：

$$\mathbf M(C)\,\dot{\mathbf T}+\mathbf K(C)\,\mathbf T+hR\left(T_M-T_\infty\right)\mathbf e_M=\mathbf 0$$

$$\mathbf M^{C}\,\dot{\mathbf C}+\mathbf K^{C}(C,T)\,\mathbf C+h_mR\left(C_M-C_\infty\right)\mathbf e_M=\mathbf 0$$

其中 $\mathbf e_M=(0,\dots,0,1)^{\mathsf T}$，$\mathbf M,\mathbf M^C$ 取集中形式（对角）。

### 10.2 后向 Euler 离散

在 $t^{n+1}=t^n+\Delta t$ 处取隐式：

$$\boxed{\ \mathbf M(\mathbf C^{n+1})\,\frac{\mathbf T^{n+1}-\mathbf T^{n}}{\Delta t}
+\mathbf K(\mathbf C^{n+1})\,\mathbf T^{n+1}
+hR\left(T^{n+1}_M-T_\infty^{n+1}\right)\mathbf e_M
+H_{\rm evap}h_mR\left(C^{n+1}_M-C_\infty^{n+1}\right)\mathbf e_M=\mathbf 0\ }
\label{eq:BE_T}\tag{7}$$

$$\boxed{\ \mathbf M^{C}\,\frac{\mathbf C^{n+1}-\mathbf C^{n}}{\Delta t}
+\mathbf K^{C}(\mathbf C^{n+1},\mathbf T^{n+1})\,\mathbf C^{n+1}
+h_mR\left(C^{n+1}_M-C_\infty^{n+1}\right)\mathbf e_M=\mathbf 0\ }
\label{eq:BE_C}\tag{8}$$

**后向 Euler 的选择理由**：

- **无条件稳定（A-稳定且 L-稳定）**：本题时间尺度比达 26（§7.1），且 $\rho c_p$
  在干燥过程中变化近 64 %，显式格式的稳定步长约束（$\Delta t\lesssim\Delta r^2/(2\alpha)$）
  在细网格下极苛刻；后向 Euler 无此限制；
- **L-稳定性对刚性衰减友好**：水分方程在低含水率段的特征时间可达 $10^5\ \mathrm{s}$ 以上，
  而温度方程特征时间为 $10^3\ \mathrm{s}$ 量级，L-稳定格式能有效抑制快模态的虚假振荡；
- **与 Newton 迭代天然配合**：后向 Euler 的每步是非线性代数方程组，正是 Newton 法的应用对象；
- **代价**：时间精度仅 $O(\Delta t)$（一阶），需通过时间步收敛性验证保证四位小数精度。

---

## 11 非线性求解（Newton 迭代）

### 11.1 残差方程

记未知向量 $\mathbf U=(\mathbf T,\mathbf C)^{\mathsf T}\in\mathbb R^{2(M+1)}$，式 (7)(8)
构成非线性代数方程组 $\mathbf R(\mathbf U^{n+1})=\mathbf 0$，分块写出：

$$\mathbf R_T(\mathbf T,\mathbf C)=\mathbf M(\mathbf C)\frac{\mathbf T-\mathbf T^n}{\Delta t}
+\mathbf K(\mathbf C)\mathbf T+hR\left(T_M-T_\infty^{n+1}\right)\mathbf e_M
+H_{\rm evap}h_mR\left(C_M-C_\infty^{n+1}\right)\mathbf e_M=\mathbf 0$$

$$\mathbf R_C(\mathbf T,\mathbf C)=\mathbf M^{C}\frac{\mathbf C-\mathbf C^n}{\Delta t}
+\mathbf K^{C}(\mathbf C,\mathbf T)\mathbf C+h_mR\left(C_M-C_\infty^{n+1}\right)\mathbf e_M=\mathbf 0$$

### 11.2 Jacobian（$2\times2$ 分块）

$$\mathbf J=\begin{bmatrix}
\dfrac{\partial\mathbf R_T}{\partial\mathbf T} & \dfrac{\partial\mathbf R_T}{\partial\mathbf C}\\[10pt]
\dfrac{\partial\mathbf R_C}{\partial\mathbf T} & \dfrac{\partial\mathbf R_C}{\partial\mathbf C}
\end{bmatrix}$$

**块 (1,1)**（温度-温度）：$\mathbf M$、$hR$ 项与 $T$ 无关，故

$$\frac{\partial\mathbf R_T}{\partial\mathbf T}=\frac{\mathbf M(\mathbf C)}{\Delta t}+\mathbf K(\mathbf C)+hR\,\mathbf e_M\mathbf e_M^{\mathsf T}$$

**块 (1,2)**（温度对含水率的导数）：来自 $\mathbf M(\mathbf C)$ 与 $\mathbf K(\mathbf C)$ 的
隐式依赖。因 $\mathbf M$ 为对角，其元素 $M_{ii}=\rho(C_i)c_p(C_i)\Delta r\,r_i$，故

$$\left[\frac{\partial}{\partial C_j}\left(\mathbf M(\mathbf C)\frac{\mathbf T-\mathbf T^n}{\Delta t}\right)\right]_i
=\delta_{ij}\,\frac{(\rho c_p)'(C_i)\,\Delta r\,r_i}{\Delta t}\left(T_i-T_i^n\right)$$

$\mathbf K(\mathbf C)$ 依赖 $k(C)$。界面导热系数取相邻节点算术平均后，**单元局部形式**最便于
求导：对单元 $e_k=[r_k,r_{k+1}]$，记 $k_e=\tfrac12\big[k(C_k)+k(C_{k+1})\big]$，
其刚度矩阵为
$K^{e_k}=\dfrac{k_e(r_k+r_{k+1})}{2\Delta r}\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$，
对 $(\mathbf K\mathbf T)$ 的局部贡献为

$$\big(K^{e_k}T^{e_k}\big)=\frac{k_e(r_k+r_{k+1})}{2\Delta r}
\begin{bmatrix}T_{k+1}-T_k\\ -(T_{k+1}-T_k)\end{bmatrix}$$

于是（节点 $j$ 只出现在含它的两个单元中）：

$$\left[\frac{\partial(\mathbf K\mathbf T)}{\partial C_j}\right]_i
=\sum_{e_k\ni j}\frac{k'(C_j)}{2}\cdot\frac{r_k+r_{k+1}}{2\Delta r}\cdot
\big(\pm(T_{k+1}-T_k)\big)\Big|_{\text{作用于节点 }i}$$

其中 $k'(C_j)=\dfrac{0.38}{(C_j+1)^2}$，$(\pm)$ 按该单元对第 $i$ 个方程的贡献符号取
（左节点取 $-(T_{k+1}-T_k)$、右节点取 $+(T_{k+1}-T_k)$）。可见 $\partial\mathbf R_T/\partial\mathbf C$
为**稀疏带状**（带宽与 $\mathbf K$ 相同），不破坏整体稀疏性。

**另需叠加蒸发吸热项的直接贡献**（式 (7) 末项对 $C$ 求导）：该项只作用于表面节点，
且对 $C$ 是**线性**的，故只贡献一个常数对角元：

$$\boxed{\ \left[\frac{\partial\mathbf R_T}{\partial\mathbf C}\right]_{MM}
\mathrel{+}=H_{\rm evap}\,h_m\,R\ }$$

这是三条耦合通路中**唯一显式出现于 Jacobian 的非物性项**；若取 $H_{\rm evap}=0$
（无相变），该元消失，块 (1,2) 退化为纯物性耦合。注意其量级（$H_{\rm evap}$ 取
$40\ ^\circ\mathrm{C}$ 值，见 §4.4(c)）：
$H_{\rm evap}h_mR=2.4059\times10^6\times8\times10^{-7}\times0.02\approx0.0385\
\mathrm{J/(kg\cdot K\cdot s)}$，与对角元 $1/\Delta t=4\ \mathrm{s^{-1}}$ 相比仅为其
$0.96\%$，属**弱耦合**（与 §4.4(c) 的结论一致）。

**块 (2,1)**（水分对温度的导数）：仅由 $D(C,T)$ 的 Arrhenius 项产生。界面扩散系数同样取
算术平均：$D_{i-1/2}=\tfrac12\big[D(C_{i-1},T_{i-1})+D(C_i,T_i)\big]$。完全平行于块 (1,2)：

$$\left[\frac{\partial(\mathbf K^{C}\mathbf C)}{\partial T_j}\right]_i
=\sum_{e_k\ni j}\frac{1}{2}\frac{\partial D}{\partial T}\Big|_{(C_j,T_j)}\cdot
\frac{r_k+r_{k+1}}{2\Delta r}\cdot\big(\pm(C_{k+1}-C_k)\big)\Big|_{\text{作用于节点 }i}$$

其中 $\dfrac{\partial D}{\partial T}\Big|_{(C_j,T_j)}=D(C_j,T_j)\cdot\dfrac{3850}{T_j^2}$。

**块 (2,2)**（水分-水分）：

$$\frac{\partial\mathbf R_C}{\partial\mathbf C}=\frac{\mathbf M^{C}}{\Delta t}
+\mathbf K^{C}+\frac{\partial\mathbf K^{C}}{\partial\mathbf C}\mathbf C
+h_mR\,\mathbf e_M\mathbf e_M^{\mathsf T}$$

### 11.3 导数公式（由附录 3 解析给出）

$$\frac{\partial \rho}{\partial C}=128,\qquad
\frac{\partial c_p}{\partial C}=\frac{2736}{(C+1)^2},\qquad
\frac{\partial k}{\partial C}=\frac{0.38}{(C+1)^2}$$

$$\frac{\partial(\rho c_p)}{\partial C}=c_p\frac{\partial\rho}{\partial C}+\rho\frac{\partial c_p}{\partial C}
=128\,c_p(C)+\frac{2736\,\rho(C)}{(C+1)^2}$$

$$\boxed{\ \frac{\partial D}{\partial C}=D(C,T)\cdot\frac{0.45}{C^2}\ },\qquad
\boxed{\ \frac{\partial D}{\partial T}=D(C,T)\cdot\frac{3850}{T^2}\ }$$

（由 $D=D_0e^{-0.45/C}e^{-3850/T}$ 直接求导，$D_0=2.4\times10^{-3}$。所有导数在
$C>0$、$T>0$ 上解析、有界，Newton 法适用。）

### 11.4 Newton 迭代格式

第 $k$ 次迭代（当前时间步 $n+1$）：

$$\mathbf J(\mathbf U^{(k)})\,\delta\mathbf U^{(k)}=-\mathbf R(\mathbf U^{(k)}),\qquad
\mathbf U^{(k+1)}=\mathbf U^{(k)}+\theta\,\delta\mathbf U^{(k)}$$

初值取上一时间步解 $\mathbf U^{(0)}=\mathbf U^{n}$（时间步长较小时收敛快）。

**收敛准则**（同时满足）：

$$\left\|\mathbf R(\mathbf U^{(k)})\right\|_\infty\le\varepsilon_R,\qquad
\left\|\delta\mathbf U^{(k)}\right\|_\infty\le\varepsilon_U$$

取 $\varepsilon_R=10^{-10}$（残差，量纲混合时按分块归一）、$\varepsilon_U=10^{-10}$；
最大迭代数 $k_{\max}=30$，超限则减小 $\Delta t$ 重试。

**阻尼策略**：由于 $C$ 极小时 $\partial D/\partial C=D\cdot0.45/C^2$ 增长很快
（$C=0.05$ 时 $\partial D/\partial C\approx1.8\times10^{-11}$，但相对灵敏
$0.45/C^2=180$），在迭代初期可能出现步长过大。采用**回溯线搜索**：若
$\|\mathbf R(\mathbf U^{(k)}+\theta\delta\mathbf U)\|>\|\mathbf R(\mathbf U^{(k)})\|$，
则 $\theta\leftarrow\theta/2$，直至残差下降或 $\theta<10^{-4}$。

### 11.5 简化方案（准 Newton，可选）

若严格 Jacobian 的实现成本过高，可采用**冻结系数的准 Newton**：
在 Jacobian 中把 $\mathbf M(\mathbf C)$、$\mathbf K(\mathbf C)$、$\mathbf K^C(\mathbf C,\mathbf T)$
取为当前迭代值（不显式求其对 $C,T$ 的导数），即只保留线性部分。此时
$\partial\mathbf R_T/\partial\mathbf C\approx\mathbf 0$、$\partial\mathbf R_C/\partial\mathbf T\approx\mathbf 0$，
Jacobian 近似分块对角，每个 Newton 步退化为两个独立线性系统。

该简化把收敛阶由二次降为**线性（Picard 迭代）**，但对本题（时间步长小、初值好）
通常 3 ~ 6 次迭代即可收敛。**本文以严格 Newton 为推荐方案，准 Newton 作为备用**，
并在数值验证中比较两者的迭代次数与最终解一致性。

---

## 12 求解流程与数值参数

### 12.1 网格与时间步

| 参数 | 取值 | 理由 |
|---|---|---|
| 空间节点数 $M$ | $200$（$\Delta r=0.01\ \mathrm{cm}$） | 题面输出间隔 $0.1\ \mathrm{cm}$ 恰为 $\Delta r$ 的 10 倍，输出节点直接落在网格上；同时通过 $M=100,200,400$ 的收敛性验证 |
| 时间步长 $\Delta t$ | $0.25\ \mathrm{s}$ | 后向 Euler 为一阶，需足够小；$0.25$ 整除 $1\ \mathrm{s}$，输出时刻恰好落在网格上；通过 $\Delta t=1,0.5,0.25,0.125\ \mathrm{s}$ 收敛性验证 |
| 总时长 | $10800\ \mathrm{s}$（3 h） | 题面要求 |

### 12.2 求解流程

```
输入: U^0 = (T^0, C^0); 网格 {r_i}; 时间步 dt; 环境 T_inf(t), C_inf(t)
for n = 0, 1, 2, ... (直到 t = 10800 s):
    t_{n+1} = t_n + dt
    由 PCHIP 插值得到 T_inf^{n+1}, C_inf^{n+1}
    # ---- Newton 迭代 ----
    U = U^n                              # 初值
    for k = 0, 1, ..., k_max:
        由 U 计算节点物性 rho(C), cp(C), k(C), D(C,T)   # 附录3
        组装集中质量矩阵 M(C), M^C
        组装刚度矩阵 K(C), K^C(C,T)（界面系数取算术平均）
        加入边界项 hR, h_m R
        计算残差 R(U) = (R_T, R_C)                        # 式(7)(8)
        if ||R||_inf <= eps_R: break
        计算 Jacobian J(U)                                # §11.2-11.3
        解 J dU = -R                                      # 稀疏 LU（分块）
        回溯线搜索确定 theta
        U = U + theta * dU
        if ||theta*dU||_inf <= eps_U: break
    U^{n+1} = U
    if n*dt 是 1 s 的整数倍: 记录输出（21 个径向位置）
```

**线性代数**：Jacobian 为 $2(M+1)\times2(M+1)$ 的**稀疏带状矩阵**（每行至多 7 个非零元），
用稀疏 LU（如 SuperLU / UMFPACK）或分块追赶法求解，复杂度 $O(M)$。

### 12.3 数值性质

1. **守恒性**：有限元弱形式配合集中质量矩阵，保证离散总热容与总水量的收支精确
   （在机器精度内），不受网格粗细影响；
2. **稳定性**：后向 Euler 无条件稳定；集中质量矩阵使离散算子的正性更易保持；
3. **极值原理**：温度应始终位于 $\left[\min(T_0,\min_tT_\infty),\ \max(T_0,\max_tT_\infty)\right]$
   包络内，含水率单调不增（在 $C_\infty<C$ 时）——作为**硬性检验标准**；
4. **收敛性**：空间 $O(\Delta r)$（线性单元 + 集中质量）、时间 $O(\Delta t)$
   （后向 Euler），需通过收敛性验证确认四位小数精度。

---

## 13 待求量与输出约定

**表 3（温度，$^\circ\mathrm{C}$）与表 4（水分浓度，$\mathrm{kg/kg}$）**：
时间 $0.5,1.0,1.5,2.0,2.5,3.0\ \mathrm{h}$（$1800,3600,\dots,10800\ \mathrm{s}$）
$\times$ 距离 $0,0.5,1,1.5,2\ \mathrm{cm}$。

**`result2.xlsx`**：两个工作表

- 工作表 `温度`：$A$ 列为时间（$1,2,\dots,10800\ \mathrm{s}$），第 1 行为到中心距离
  $0,0.1,0.2,\dots,2.0\ \mathrm{cm}$，共 $10800\times21$ 个温度值；
- 工作表 `水分浓度`：同结构的水分浓度值。

所有数值**保留 4 位小数**。

---

## 14 数值验证计划

| 编号 | 验证项 | 方法 | 通过标准 |
|---|---|---|---|
| V1 | 空间收敛性 | $M=100,200,400,800$（$\Delta t$ 固定） | 相邻网格结果差 $<5\times10^{-5}$（四位小数阈值） |
| V2 | 时间收敛性 | $\Delta t=1,0.5,0.25,0.125\ \mathrm{s}$ | 相邻步长结果差 $<5\times10^{-5}$ |
| V3 | Newton 收敛 | 记录每步迭代次数 | 平均 3 ~ 6 次，$\|\mathbf R\|_\infty<10^{-10}$ |
| V4 | 极值原理 | 检查 $T$ 包络与 $C$ 单调性 | 无越界、无振荡 |
| V5 | 离散守恒 | 总热量/总水量收支残差 | 相对残差 $<10^{-12}$ |
| V6 | 与问题一衔接 | $t\le1800\ \mathrm{s}$ 内与问题一解对比 | 差异可由**物性差异（附录 2 vs 附录 3）**定量解释 |
| V7 | 与简化模型对比 | 冻结系数准 Newton vs 严格 Newton | 最终解一致（差 $<10^{-8}$） |
| V8 | **蒸发吸热项影响** | 令 $H_{\rm evap}=0$ 与 $H_{\rm evap}=H_{\rm evap}(T)$（§4.4c 的定标式，$40\ ^\circ\mathrm{C}$ 时 $2.4059\times10^6$）各算一次，比较 $T(R,t)$ | 表面温差 $\approx0.19\ \mathrm{K}$（与 §4.4c 的解析估计一致），且差值随 $C_R\to C_\infty$ 单调减小 |
| V10 | **$H_{\rm evap}(T)$ 推导链检验** | `src/q2_latent_heat.py`：三条路线互检（精确 Clapeyron / CC / Kirchhoff 定标），并反演 $p_{\rm sat}$ | 精确 Clapeyron 复现 IAPWS-95 的 $h_{fg}$ 至 $<0.1\ \mathrm{J/kg}$；CC 偏差与 $1/Z-1$ 吻合到 $0.01\%$；定标式在 $28\sim50\ ^\circ\mathrm{C}$ 残差 $<0.0033\%$；反演 $p_{\rm sat}$ 偏差 $<0.6\%$ |
| V9 | **$H_{\rm evap}$、$h_m$ 敏感性** | 对 $H_{\rm evap}$ 取 $\pm20\%$、$h_m$ 取 $1\times,10\times,100\times$ 重算 | 量化蒸发项对 $h_m$ 口径的依赖（§4.4c 的量纲敏感性提醒）；结果用于论文的局限性讨论 |

**V6 说明**：问题一与问题二在 $0\sim1800\ \mathrm{s}$ 用**不同物性经验式**（附录 2 常数
vs 附录 3 随 $C$ 变化），因此两问结果**本就不应完全相同**；验证的目的是确认差异
方向与量级符合物性差异的预期（例如附录 3 的 $\rho c_p$ 更大、$k$ 更大），而非数值 bug。

---

## 15 产出文件

| 文件 | 内容 |
|---|---|
| `model/problem2.md` | 本文（模型建立） |
| `src/q2_latent_heat.py` | $H_{\rm evap}(T)$ 的热力学推导、IAPWS-95 定标与闭合检验（§4.4c） |
| `outputs/registry_q2_latent_heat.csv` | 潜热定标数字注册表（$p_{\rm sat},v_l,v_g,h_{fg},c_{p,l},c_{p,v},Z$） |
| `src/q2_solve.py` | FEM（线性单元 + 集中质量 + 后向 Euler + Newton）求解器 |
| `src/q2_verify.py` | 收敛性、守恒性、极值原理验证（V1 ~ V7） |
| `src/q2_produce.py` | 生产计算，生成 `outputs/result2.xlsx` 与表 3/表 4 |
| `outputs/result2.xlsx` | 问题二完整结果（温度 / 水分浓度，$10800\times21$） |
| `outputs/registry_q2.csv` | 数字注册表（论文对账用） |

---

## 16 与问题一数值方案的对照

| 项目 | 问题一 | 问题二 |
|---|---|---|
| 空间离散 | 守恒型**有限体积**（控制体 + 界面通量） | **有限元**（Galerkin 弱形式 + 线性单元） |
| 质量矩阵 | 无（控制体法直接给出节点热容） | **集中质量矩阵** $M^L_{ii}=\rho c_p\Delta r\,r_i$ |
| 时间离散 | 后向 Euler（半隐式，界面 $D$ 滞后一步） | **后向 Euler（全隐式）** |
| 非线性处理 | 滞后系数 → 线性三对角（追赶法） | **Newton 迭代**（严格 Jacobian） |
| 物性 | 常数 | 随 $C$ 变化（附录 3） |
| 耦合 | 单向解耦 | **双向耦合** |
| 求解复杂度 | $O(M)$ 追赶法 | $O(M)$ 稀疏 LU × Newton 迭代 |

> **一致性说明**：两问的集中质量矩阵元素 $M^L_{ii}=\rho c_p\Delta r\,r_i$ 与问题一
> 控制体体积 $V_i\propto r_i\Delta r$ 在物理上完全等价（均为"节点所在环形控制体的热容"），
> 因此**两问在空间离散上具有相同的一阶守恒结构**，便于结果对照与交叉验证。
