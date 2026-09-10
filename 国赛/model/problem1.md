# 问题一建模：预热平衡阶段药材温度与水分浓度变化的数学模型

> 本文建立 2026 年高教社杯 A 题问题一（预热平衡阶段，0 ~ 1800 s）的数学模型。
> 全部参数取自题面附录 2 与附件 1；全部数值结论均由 `src/q1_solve.py`、
> `src/q1_produce.py` 运行得到，数字注册表见 `outputs/registry_q1.csv` 与
> `outputs/registry_q1_production.csv`。
>
> **本文相对于原始建模思路作了修正，修正项在 §9.3、§9.5、§9.6 与 §11 中逐条说明，
> 并在 `problem_slove1.md` 中给出数值验证。**

---

## 1 问题与建模目标

一根圆柱形中药材，长 $L=25\ \mathrm{cm}$、半径 $R=2\ \mathrm{cm}$，初始温度
$T_0=28\ ^\circ\mathrm{C}$、初始干基含水率 $C_0=2.55\ \mathrm{kg/kg}$，置于热风烘房
中。烘房温度 $T_\infty(t)$ 与烘房水分浓度 $C_\infty(t)$ 随时间变化，由附件 1 给出
（采样间隔 60 s，覆盖 0 ~ 14400 s）。

要求建立预热平衡阶段（前 1800 s）药材内部温度场 $T(r,t)$ 与水分浓度场 $C(r,t)$
的数学模型，并给出 100、300、600、900、1200、1500、1800 s 时刻，到药材中心距离
$0,\ 0.5,\ 1,\ 1.5,\ 2\ \mathrm{cm}$ 处的结果（表 1、表 2），以及 1800 s 内
每隔 1 s、径向每隔 0.1 cm 的完整结果（`result1.xlsx`）。

**待求解的未知场**：$T(r,t)$、$C(r,t)$，$r\in[0,R]$，$t\in[0,1800\ \mathrm{s}]$。

---

## 2 建模假设

| 编号 | 假设 | 依据与适用范围 |
|---|---|---|
| **A1** | 药材为均质、各向同性的连续介质，形状为正圆柱 | 题面给定"形状大致呈圆柱形" |
| **A2** | 只考虑径向一维传递，忽略轴向与周向 | 周向由轴对称性严格成立；轴向见 §2.1 |
| **A3** | 药材内部满足局部热平衡（LTE），固相与液相温度相同 | 含湿多孔介质尺度远小于试样尺度，$R=2\ \mathrm{cm}$ 下成立 |
| **A4** | 预热平衡阶段物性为常数（$\rho,c_p,k$ 取自附录 2） | 附录 2 对问题 1 只给常数；问题 2 起才给随 $C$ 变化的经验式 |
| **A5** | 水分迁移由 Fick 扩散描述，扩散系数 $D=D(C)$ 由附录 2 给定 | 题面明确要求；忽略毛细压力驱动、重力与对流项 |
| **A6** | 表面水分浓度对应的平衡值为热风水分浓度 $C_\infty(t)$（第三类边界） | 与附录 2 给出的对流传质系数 $h_m$ 配套，见 §7.2 的适用性讨论 |
| **A7** | 预热平衡阶段（1800 s）体积不收缩，$R$ 视为常数 | 附件 2 显示 $t=1800\ \mathrm{s}$ 时 $R$ 降至 1.873 cm（相对 $R_0$ 变化，见 §7.3），问题 4 才显式考虑收缩 |

### 2.1 轴向维度的处理（对假设 A2 的严格论证）

常见的一维化理由是"长径比 $L/R=12.5$ 足够大"（题面参数给出 $L/R=12.5$）。
但更严格的论证来自对称性：**在圆柱的中截面 $z=0$ 上，$\partial T/\partial z=0$、
$\partial C/\partial z=0$ 是上下两半对称性导致的精确条件**，与 $L/R$ 无关。因此对
$z=0$ 所在的径线，纯径向导热/扩散方程在该线上**精确成立**，并非近似。

$L/R=12.5$ 真正的作用是论证**远离中截面的截面**受端面影响的深度有限。端面面积与
侧面面积之比为

$$\frac{\pi R^2}{2\pi R L}=\frac{R}{2L}=\frac{2}{2\times 25}=0.04,$$

即端面换热面积仅占侧面的 4 %，同时轴向导热会把端面扰动限制在 $\sim\sqrt{\alpha t}$
深度内：1800 s 时 $\sqrt{\alpha t}=\sqrt{1.6886\times10^{-7}\times1800}\approx 1.74\ \mathrm{cm}$，
与 $R=2\ \mathrm{cm}$ 同量级，说明 30 min 以内轴向影响尚局限于端部附近。题面要求的
输出位置（距中心 0 ~ 2 cm）位于中截面径线上，故一维径向导热模型是恰当的。

> 说明：本文未对完整二维轴对称模型作数值对比，因此 A2 的"远端截面"部分属于
> **有依据的推断**而非已验证结论；同一条径线（中截面）上的结果是精确的。

---

## 3 几何、坐标与守恒关系

采用柱坐标系 $(r,\theta,z)$，$z$ 轴与药材轴线重合，原点取在中截面圆心。取单位轴向
长度 $1\ \mathrm{m}$ 分析。

径向位置 $r$ 处的两个特征面积（单位轴向长度）：

- 侧面积（半径 $r$ 的侧面）：$A(r)=2\pi r$
- 控制体体积（$r_{i-1/2}$ 到 $r_{i+1/2}$ 的环）：$V_i=\pi\left(r_{i+1/2}^2-r_{i-1/2}^2\right)$

由 $\nabla\cdot$ 在柱坐标下的形式，对只依赖 $r$ 的函数 $\phi(r)$：

$$\frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial \phi}{\partial r}\right)
=\nabla^2_{r}\phi ,$$

这是**守恒型**（即先对控制体积分、再用通量差表示）的写法，后文离散化直接以此为基础，
从而自动保证离散守恒性。

---

## 4 控制方程

### 4.1 温度场：径向导热方程

对半径 $r_i$ 处厚 $\Delta r$ 的薄环作能量守恒：单位时间净导入的热量 = 内能增量。

$$\rho c_p\,\frac{\partial T}{\partial t}
= \frac{1}{r}\frac{\partial}{\partial r}\left(k\,r\frac{\partial T}{\partial r}\right)$$

$k$ 为常数（假设 A4），可移至微分号外；两边除以 $\rho c_p$：

$$\boxed{\ \frac{\partial T}{\partial t}
=\frac{\alpha}{r}\frac{\partial}{\partial r}\left(r\frac{\partial T}{\partial r}\right),\qquad
\alpha=\frac{k}{\rho c_p}\ }$$

### 4.2 水分场：非线性扩散方程

对同一薄环作干基水分的质量守恒（忽略对流携带项，假设 A5）：

$$\boxed{\ \frac{\partial C}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\left(r\,D(C)\frac{\partial C}{\partial r}\right)\ }$$

其中（附录 2）

$$D(C)=7\times10^{-9}\exp\!\left(-\frac{0.89}{C}\right)\quad (\mathrm{m^2/s}).$$

**非线性来源**：$D$ 随 $C$ 呈指数变化。在 $C_0=2.55$ 处 $D=4.9377\times10^{-9}\ \mathrm{m^2/s}$；
在问题 3 的干燥目标 $C=0.15$ 处 $D=1.8547\times10^{-11}\ \mathrm{m^2/s}$；
在 1800 s 时的环境湿度 $C_\infty=0.0331$ 处 $D=1.4713\times10^{-20}\ \mathrm{m^2/s}$。
即在整个可能的浓度范围内 $D$ 跨越 $3.36\times10^{11}$ 个数量级。后文 §9.6 说明这一
强非线性对离散格式的要求。

---

## 5 参数确定

| 符号 | 含义 | 数值 | 来源 |
|---|---|---|---|
| $\rho$ | 药材密度 | $820\ \mathrm{kg/m^3}$ | 附录 2 |
| $c_p$ | 比热容 | $2600\ \mathrm{J/(kg\cdot K)}$ | 附录 2 |
| $k$ | 热传导系数 | $0.36\ \mathrm{W/(m\cdot K)}$ | 附录 2 |
| $h$ | 对流换热系数 | $25\ \mathrm{W/(m^2\cdot K)}$ | 附录 2 |
| $h_m$ | 对流传质系数 | $8\times10^{-7}\ \mathrm{m/s}$ | 附录 2 |
| $D_0$ | 扩散系数系数 | $7\times10^{-9}\ \mathrm{m^2/s}$ | 附录 2 |
| $D$ 指数常数 | — | $0.89$ | 附录 2 |
| $R$ | 半径 | $2\ \mathrm{cm}=0.02\ \mathrm{m}$ | 题面 |
| $L$ | 长度 | $25\ \mathrm{cm}$ | 题面 |
| $T_0$ | 初始温度 | $28\ ^\circ\mathrm{C}=301.15\ \mathrm{K}$ | 题面 |
| $C_0$ | 初始含水率 | $2.55\ \mathrm{kg/kg}$ | 题面 |

**热扩散系数**

$$\alpha=\frac{k}{\rho c_p}=\frac{0.36}{820\times2600}=1.6885553\times10^{-7}\ \mathrm{m^2/s}.$$

> **修正说明 ①**：原始建模思路中写作 $\alpha=1.679\times10^{-7}\ \mathrm{m^2/s}$。
> 按附录 2 的参数重算应为 $1.6885553\times10^{-7}\ \mathrm{m^2/s}$，原值偏低
> $0.569\ \%$。本文采用重算值。

**单位约定**：$D(C)$ 中不含温度，故温度一律换算为绝对温度参与计算时不影响 $D$；
但为与问题 2 ~ 4（附录 3、4 的 $D$ 含 Arrhenius 温度项）保持一致，本文统一使用
热力学温度 $\mathrm{K}$ 作为 $T$ 的状态量，输出结果再折算为 $^\circ\mathrm{C}$。

---

## 6 定解条件

### 6.1 初始条件（$t=0$，$0\le r\le R$）

$$T(r,0)=T_0=28\ ^\circ\mathrm{C}=301.15\ \mathrm{K},\qquad C(r,0)=C_0=2.55\ \mathrm{kg/kg}$$

### 6.2 中心对称条件（$r=0$）

由轴对称与可微性，

$$\left.\frac{\partial T}{\partial r}\right|_{r=0}=0,\qquad
\left.\frac{\partial C}{\partial r}\right|_{r=0}=0.$$

### 6.3 表面第三类边界（$r=R$）

**换热**（牛顿冷却，热流向环境为正）：

$$-k\left.\frac{\partial T}{\partial r}\right|_{r=R}=h\left[T(R,t)-T_\infty(t)\right]$$

**传质**（对流干燥，水流出药材为正）：

$$-D(C)\left.\frac{\partial C}{\partial r}\right|_{r=R}=h_m\left[C(R,t)-C_\infty(t)\right]$$

注意传质边界左端含 $D(C)$，需用表面含水率计算，这一点在 §9.5 中直接决定表面节点的
系数形式。

### 6.4 环境激励 $T_\infty(t)$、$C_\infty(t)$ 的连续化

附件 1 给出离散值（$\Delta t=60\ \mathrm{s}$），需插值为连续函数。本文采用**保形分段三
次插值（PCHIP）**，理由：附件 1 的水分浓度序列含明显测量噪声——240 个时间步中有
**80 步出现下降**，单步降幅最大达 $4.4\times10^{-4}\ \mathrm{kg/kg}$，而该序列的
平均趋势仅约 $1.3\times10^{-4}\ \mathrm{kg/kg}$ 每步，即噪声标准差约为趋势增量的
2 倍。PCHIP 单调分段，不会因过冲产生负浓度或虚假极值；普通三次样条在
$0\sim1800\ \mathrm{s}$ 区间虽未过冲，但在全区间会产生超出数据范围的外推值。

在问题一实际用到的 $0\sim1800\ \mathrm{s}$（附件 1 前 31 个点）内，该序列是单调递增的，
因此插值方法的选择对本问结果影响极小（见 `problem_slove1.md` §6 的敏感性验证）。

---

## 7 模型特性分析

### 7.1 特征数与量纲分析

以 $R$ 为特征长度、$R^2/\alpha$ 为特征时间：

| 特征数 | 定义 | 数值 | 含义 |
|---|---|---|---|
| 热 Biot 数 | $\mathrm{Bi}=hR/k$ | $1.3889$ | $>0.1$，内部温度梯度不可忽略，必须求解分布参数模型而非集中参数模型 |
| 传质 Biot 数 | $\mathrm{Bi}_m=h_mR/D(C_0)$ | $3.2404$ | 表面传质与内部扩散阻力同量级 |
| 导热特征时间 | $R^2/\alpha$ | $2368.9\ \mathrm{s}$ | 与 1800 s 同量级，说明 30 min 内温度尚未充分平衡 |
| 湿分特征时间 | $R^2/D(C_0)$ | $81010\ \mathrm{s}$ | 比 1800 s 大 45 倍，说明水分松弛远慢于温度 |
| 长径比 | $L/R$ | $12.5$ | 见 §2.1 |

**关键结论**：$\mathrm{Bi}=1.39$ 意味着不能把药材当作等温体处理；$R^2/\alpha=2368.9\ \mathrm{s}$
与 $R^2/D(C_0)=81010\ \mathrm{s}$ 相差 34 倍，说明**温度与水分的时间尺度显著分离**，
这是预热平衡阶段的物理本质：温度在 30 min 内快速响应，而水分几乎不动。

### 7.2 关于表面传质边界的适用性（存疑项，未作修改）

附录 2 给定 $h_m=8\times10^{-7}\ \mathrm{m/s}$。若按热质传递类比（Chilton–Colburn
类比）由 $h=25\ \mathrm{W/(m^2\cdot K)}$ 估算，对空气取
$\rho_a c_{p,a}\approx1.2\times1005\approx1.2\times10^{3}\ \mathrm{J/(m^3\cdot K)}$，
则等效传质系数约为

$$h_m^{\rm eq}\sim\frac{h}{\rho_a c_{p,a}}\approx 0.02\ \mathrm{m/s},$$

比附录 2 给定的 $8\times10^{-7}$ 大**约 4 个数量级**。

同时需要指出：模型把 $C_\infty$（烘房空气的含水量）直接当作**药材表面平衡含水率**。
物理上，与热风平衡的是药材表层的**平衡含水率**，它是空气温度与相对湿度的函数
（吸附等温线），通常远高于同温度下空气本身的含湿量。附件 1 给出的 $C_\infty$ 在
$0.0196\sim0.0503\ \mathrm{kg/kg}$ 量级，而药材初始含水率 $C_0=2.55\ \mathrm{kg/kg}$，
两者相差约 50 ~ 130 倍。

**处理方式**：$h_m$ 与 $C_\infty$ 均由题面附录 2 与附件 1 直接规定，本文**按题目给定值
建模，不作改动**，以保证结果与题目要求的可比性。上述量级差异作为**模型的适用性边界**
记录在此：由该边界条件算出的表面水分浓度会显著高于"与热风真正平衡"时的值，因而
**水分浓度的绝对值应以相对趋势而非绝对平衡值来解读**。这一判断影响问题 3 的目标
判定，故在此显式标记为存疑项。

### 7.3 关于体积收缩

附件 2 给出 $R$ 从 $2.000\ \mathrm{cm}$（$t=0$）降至 $1.873\ \mathrm{cm}$
（$t=1800\ \mathrm{s}$），即 30 min 内相对收缩 $6.35\ \%$。问题一只要求建立
**预热平衡阶段**的模型，且附录 2 的物性为常数，故本文按 A7 取 $R$ 为常数。
收缩的显式处理属问题 4（附录 4），本文不做。

### 7.4 参数解耦性（对原始思路的重要限定）

原始建模思路称"两个过程同时发生、相互独立"。这一说法**只在问题一成立**，原因是：

- 问题一的 $D$ 只依赖 $C$（见 §4.2），**不依赖 $T$**，故温度场不影响水分场；
- 水分场也不进入温度控制方程（无蒸发潜热项，$c_p$ 为常数）。

因此问题一中两个方程确实**单向解耦**，可独立求解。

但问题 2 ~ 4 的附录 3、4 给出的扩散系数为

$$D=2.4\times10^{-3}\exp\!\left(-\frac{0.45}{C}\right)\exp\!\left(-\frac{3850}{T}\right)
\quad(\text{附录 3}),\qquad
D=4.2\times10^{-4}\exp\!\left(-\frac{0.30}{C}\right)\exp\!\left(-\frac{3850}{T}\right)
\quad(\text{附录 4}),$$

**含温度**。因此从问题 2 起温度场与水分场是**双向耦合**的，不能再当作独立过程处理。
本文在问题一的范围内按解耦求解，并将这一区别明确标记，以免在后续问题中沿用错误的
解耦假设。

---

## 8 模型的数学性质

1. **适定性**：$\alpha>0$ 常数、$D(C)>0$，两个方程均为一致抛物型；初值有界且
   $C_\infty>0$，满足极值原理，解有界且唯一。
2. **极值原理**：温度不会超过初始值与边界值包络，即
   $\min(T_0,\min_t T_\infty)\le T(r,t)\le\max(T_0,\max_t T_\infty)$。
   该性质是数值格式的**硬性检验标准**（见 `problem_slove1.md` §4）。
3. **强非线性**：$D$ 随 $C$ 指数变化（§4.2），且在干燥前沿附近变化剧烈，要求空间离散
   具备守恒性，否则守恒误差不随网格加密消失（§9.6）。

---

## 9 守恒型有限体积离散

### 9.1 网格

取**节点式**网格：$r_i=i\,\Delta r$，$\Delta r=R/M$，$i=0,1,\dots,M$。
即 $r_0=0$（中心）与 $r_M=R$（表面）都是节点。这一选择的理由是题面要求的输出位置
（$0,0.1,\dots,2\ \mathrm{cm}$）在 $M$ 为 10 的整数倍时恰好落在节点上，可直接取值而
无需插值。

节点 $i$ 的控制体为 $[r_{i-1/2},\,r_{i+1/2}]$，其中

$$r_{i\pm1/2}=\left(i\pm\tfrac12\right)\Delta r,\qquad
r_{-1/2}=0,\quad r_{M+1/2}=R .$$

控制体体积（单位轴向长度已约去 $2\pi$）：$V_i=\pi\left(r_{i+1/2}^2-r_{i-1/2}^2\right)$；
界面面积：$A_{i\pm1/2}=2\pi r_{i\pm1/2}$。

两个关键的几何比（后文反复使用）：

$$\frac{A_{i+1/2}}{V_i}=\frac{2\pi(i+\frac12)\Delta r}{\pi\Delta r^2\left[(i+\frac12)^2-(i-\frac12)^2\right]}
=\frac{2i+1}{2i\,\Delta r}=:f_i^{+},\qquad
\frac{A_{i-1/2}}{V_i}=\frac{2i-1}{2i\,\Delta r}=:f_i^{-}.$$

### 9.2 控制体能量平衡（以温度为例）

$$\rho c_p V_i\frac{dT_i}{dt}=k\,A_{i+1/2}\frac{T_{i+1}-T_i}{\Delta r}
-k\,A_{i-1/2}\frac{T_i-T_{i-1}}{\Delta r}$$

除以 $\rho c_p V_i$，并用 $f_i^{\pm}$ 表示：

$$\frac{dT_i}{dt}=\frac{\alpha}{\Delta r}
\left[f_i^{+}\left(T_{i+1}-T_i\right)-f_i^{-}\left(T_i-T_{i-1}\right)\right]$$

展开得三对角形式：

$$\frac{dT_i}{dt}=a_iT_{i-1}+b_iT_i+c_iT_{i+1},\qquad
a_i=\frac{\alpha f_i^{-}}{\Delta r},\quad
b_i=-\frac{\alpha\left(f_i^{+}+f_i^{-}\right)}{\Delta r},\quad
c_i=\frac{\alpha f_i^{+}}{\Delta r}.$$

### 9.3 内部节点的三对角系数（含修正 ②）

代入 $f_i^{\pm}$：

$$f_i^{+}+f_i^{-}=\frac{(2i+1)+(2i-1)}{2i\,\Delta r}=\frac{4i}{2i\,\Delta r}=\frac{2}{\Delta r},$$

因此

$$a_i=\frac{\alpha(2i-1)}{2i\,\Delta r^2}=\frac{\alpha(i-\frac12)}{i\,\Delta r^2},\qquad
\boxed{\,b_i=-\frac{2\alpha}{\Delta r^2}\,},\qquad
c_i=\frac{\alpha(2i+1)}{2i\,\Delta r^2}=\frac{\alpha(i+\frac12)}{i\,\Delta r^2}.$$

采用全隐式（后向 Euler）离散时间导数，
$\dfrac{dT_i}{dt}\approx\dfrac{T_i^{n+1}-T_i^{n}}{\Delta t}$，并要求右端在 $n+1$ 时刻取值：

$$\left(-\frac{\alpha(i-\frac12)}{i\Delta r^2}\right)T_{i-1}^{n+1}
+\left(\frac{2\alpha}{\Delta r^2}+\frac{1}{\Delta t}\right)T_i^{n+1}
+\left(-\frac{\alpha(i+\frac12)}{i\Delta r^2}\right)T_{i+1}^{n+1}
=\frac{T_i^{n}}{\Delta t}$$

即 $a_iT_{i-1}^{n+1}+b_iT_i^{n+1}+c_iT_{i+1}^{n+1}=d_i$，其中

$$\boxed{\ a_i=-\frac{\alpha(i-\frac12)}{i\,\Delta r^2},\quad
b_i=\frac{1}{\Delta t}+\frac{2\alpha}{\Delta r^2},\quad
c_i=-\frac{\alpha(i+\frac12)}{i\,\Delta r^2},\quad
d_i=\frac{T_i^{n}}{\Delta t}\ }$$

> **修正说明 ②（关键）**：原始建模思路给出的内部对角元为
> $$b_i^{\text{(原)}}=\frac{1}{\Delta t}+\frac{\alpha(2i+1)}{2i\,\Delta r^2}
> =\frac{1}{\Delta t}-c_i,$$
> 即把 $T_{i+1}$ 的系数 $c_i$ 误当成了对角元。按 §9.2—9.3 的守恒型推导，对角元应为
> $1/\Delta t+2\alpha/\Delta r^2$。两式之差恰为
> $$b_i^{(\text{原})}-b_i=\frac{\alpha(2i+1)}{2i\Delta r^2}-\frac{2\alpha}{\Delta r^2}
> =-\frac{\alpha(2i-1)}{2i\Delta r^2}=-a_i\neq0 .$$
>
> 等价地，原方案的三系数行和不再为零：
> $a_i+b_i^{(\text{原})}+c_i=-\dfrac{\alpha(2i-1)}{2i\Delta r^2}\neq0$，
> 而守恒型格式恒有 $a_i+b_i+c_i=0$（离散算子湮灭常数，是守恒性的必要条件）。
>
> 该差异**不是精度问题而是稳定性问题**：行和不为零意味着离散空间算子的最大特征值
> 实部为**正值**（反耗散），全隐式格式会以 $(1+\lambda\Delta t)^n$ 的因子放大扰动。
> 数值验证见 `problem_slove1.md` §4。**本文采用修正后的系数。**

### 9.4 中心节点 $i=0$

控制体为 $[0,\Delta r/2]$，内侧界面 $r_{-1/2}=0$，面积为零，无热流：

$$\rho c_p V_0\frac{dT_0}{dt}=k\,A_{1/2}\frac{T_1-T_0}{\Delta r},\qquad
V_0=\pi\left(\frac{\Delta r}{2}\right)^2,\quad A_{1/2}=2\pi\frac{\Delta r}{2}=\pi\Delta r .$$

$$\frac{A_{1/2}}{V_0}=\frac{\pi\Delta r}{\pi\Delta r^2/4}=\frac{4}{\Delta r}$$

故

$$\boxed{\ b_0=\frac{1}{\Delta t}+\frac{4\alpha}{\Delta r^2},\qquad
c_0=-\frac{4\alpha}{\Delta r^2},\qquad d_0=\frac{T_0^{n}}{\Delta t}\ }$$

> 该式与原始思路一致（原始思路由 L'Hôpital 法则得到 $\partial_tT|_0=2\alpha\,\partial_{rr}T|_0$
> 并离散化，结果相同）。**此处原方案正确，未作修改。**

### 9.5 表面节点 $i=M$

表面节点控制体为半控制体 $[R-\Delta r/2,\ R]$，内侧面 $A_{M-1/2}=2\pi(R-\Delta r/2)$，
外表面即 $r=R$，$A_s=2\pi R$。能量平衡中，外侧界面**不再用差分近似**，而是直接代入
第三类边界所给出的实际热流：

$$\rho c_p V_M\frac{dT_M}{dt}
=-k\,A_{M-1/2}\frac{T_M-T_{M-1}}{\Delta r}+h\,A_s\left[T_\infty(t)-T_M\right]$$

记 $\displaystyle f_M^{-}=\frac{A_{M-1/2}}{V_M}$，$\displaystyle g_h=\frac{A_s\,h}{\rho c_p V_M}=\frac{A_s\,h\,\alpha}{k\,V_M}$，
全隐式离散后

$$\boxed{\ a_M=-\frac{\alpha f_M^{-}}{\Delta r},\qquad
b_M=\frac{1}{\Delta t}+\frac{\alpha f_M^{-}}{\Delta r}+g_h,\qquad
d_M=\frac{T_M^{n}}{\Delta t}+g_h\,T_\infty^{n+1}\ }$$

**渐近形式**：当 $M\to\infty$（$\Delta r\to0$）时，
$V_M=\pi\!\left(R^2-(R-\tfrac{\Delta r}{2})^2\right)=\pi\Delta r\left(R-\tfrac{\Delta r}{4}\right)\to\pi R\,\Delta r$
（**半环**体积，不是整环 $2\pi R\Delta r$）、$A_{M-1/2}=2\pi(R-\tfrac{\Delta r}{2})\to2\pi R$，故

$$f_M^{-}=\frac{A_{M-1/2}}{V_M}\to\frac{2\pi R}{\pi R\,\Delta r}=\frac{2}{\Delta r},$$

于是

$$a_M\to-\frac{2\alpha}{\Delta r^2},\qquad
b_M\to\frac{1}{\Delta t}+\frac{2\alpha}{\Delta r^2}+\frac{2h\alpha}{k\,\Delta r},\qquad
d_M\to\frac{T_M^{n}}{\Delta t}+\frac{2h\alpha}{k\,\Delta r}T_\infty^{n+1}.$$

> **说明**：上式表明，**原始思路给出的表面系数在渐近意义上是正确的**——它就是节点式半控制体
> 系数的首项。这一点值得强调，因为中间曾出现过相反的判断，事后证明是推导时把 $V_M$ 的极限
> 误取为整环 $2\pi R\Delta r$（正确为半环 $\pi R\Delta r$）所致。取错后 $f_M^-\to1/\Delta r$，
> 便会错误地得出"原方案扩散项偏大 2 倍"的结论。
>
> 两者的差别只在 **$O(\Delta r)$ 的几何因子是否保留**。精确半控制体系数
> $$a_M^{\text{exact}}=-\frac{2\alpha}{\Delta r^2}\cdot\frac{R-\Delta r/2}{R-\Delta r/4},
> \qquad
> g_h^{\text{exact}}=\frac{2\alpha h}{k\,\Delta r}\cdot\frac{R}{R-\Delta r/4}$$
> 与用户写法相差相对量 $1/(4M)$：$M=200$ 时 $1.25\times10^{-3}$，$M=3200$ 时 $7.81\times10^{-5}$
> （均已核验，见 `outputs/registry_q1_energy.csv` 的 E4 组）。
>
> **保留这些几何因子与否，改变的是边界离散的收敛阶**（见 `problem_slove1.md` §5）：
> 用户写法为**一阶**，精确半控制体为**二阶**。在 $M=800$ 时前者误差
> $4.0\times10^{-2}\ \mathrm{K}$、后者 $4.5\times10^{-6}\ \mathrm{K}$。
> 由于题面要求四位小数（阈值 $5\times10^{-5}$），即便取 $M=3200$，用户写法仍残留约
> $0.01\ \mathrm{K}$ 的误差，故**本文保留精确几何因子**。这是一处**精度改进**，
> 不是"原方案算错"。

> **附注（水分表面节点同理）**：水分表面节点的对流项 $g_m=A_sh_m/V_M$ 在
> $M\to\infty$ 时趋于 $2h_m/\Delta r$，与原始思路写法一致；同样保留几何因子。

### 9.6 水分方程与非线性的守恒处理（含修正 ③）

水分方程的空间离散结构与温度完全平行，只需 $\alpha\to D$、$h/k\to h_m$。
但有一个**必须改正**的关键细节。

**（a）界面扩散系数的取法**

守恒型格式要求**同一条界面上的通量在所有控制体中取同一数值**。对界面
$r_{i+1/2}$，温度方程中 $k$ 为常数，两侧取值相同；但水分方程中 $D$ 随 $C$ 变化，
若各控制体都用"自己的节点值 $D(C_i)$"去计算通量，则界面 $r_{i+1/2}$ 从节点 $i$
看是 $D(C_i)$、从节点 $i+1$ 看是 $D(C_{i+1})$，**两者不等，离散水量不再守恒**。

正确做法是取**界面上的单一扩散系数**（本文用相邻节点算术平均）：

$$D_{i+1/2}=\frac{D(C_i)+D(C_{i+1})}{2}$$

于是离散方程为

$$a_i^{C}=-\frac{D_{i-1/2}f_i^{-}}{\Delta r},\qquad
b_i^{C}=\frac{1}{\Delta t}+\frac{D_{i-1/2}f_i^{-}+D_{i+1/2}f_i^{+}}{\Delta r},\qquad
c_i^{C}=-\frac{D_{i+1/2}f_i^{+}}{\Delta r},\qquad
d_i^{C}=\frac{C_i^{n}}{\Delta t}$$

> **修正说明 ③**：原始建模思路用"上一时刻的 $D_i^n=D(C_i^n)$"代入，且四个系数
> （含左右两个界面）都携带同一个 $D_i^n$，属于上述**非守恒取法**。
> 数值上其离散水量收支残差达**表面总通量的 10.1 %**，且**不随网格加密减小**
> （$M=100/200/400$ 时分别为 10.10 %/10.12 %/10.12 %）——即这是一个
> **相容性量级的错误**而非精度问题。改用界面平均值后残差降至 $10^{-14}$ 量级
> （机器精度）。对问题一结果的实际影响为最大 $|\Delta C|\approx6.35\times10^{-2}\ \mathrm{kg/kg}$
> （出现在表面附近，网格无关），约为 $C_0$ 的 2.5 %；但该误差在后续问题
> （含水率更低、$D$ 变化更大）中会迅速增大（3 h 时达 $0.68\ \mathrm{kg/kg}$），
> 因此**必须改正**。

**（b）时间离散**

$D(C)$ 依赖 $C$，方程非线性。本文采用**全隐式时间离散 + 滞后一个时间步的界面扩散系数**
（半隐式）。即用 $C^n$ 计算 $D_{i\pm1/2}$，但未知量 $C^{n+1}$ 出现在三对角线性和右端，
每步只需解一个线性三对角系统，无需 Newton 迭代。该处理引入的误差为 $O(\Delta t)$，
与全隐式 Euler 本身同阶；数值验证表明其相对于完全非线性求解的偏差为
$\max|\Delta T|=5.9\times10^{-5}\ \mathrm{K}$、$\max|\Delta C|=5.3\times10^{-6}\ \mathrm{kg/kg}$
（见 `problem_slove1.md` §6），远低于四位小数的报告精度。

**（c）表面节点**

将第三类边界 $-D\partial_rC=h_m(C_M-C_\infty)$ 代入表面半控制体的外侧界面：

$$\rho V_M\frac{dC_M}{dt}=-D_{M-1/2}A_{M-1/2}\frac{C_M-C_{M-1}}{\Delta r}
+h_mA_s\left[C_\infty(t)-C_M\right]$$

$$\boxed{\ a_M^{C}=-\frac{D_{M-1/2}f_M^{-}}{\Delta r},\qquad
b_M^{C}=\frac{1}{\Delta t}+\frac{D_{M-1/2}f_M^{-}}{\Delta r}+g_m,\qquad
d_M^{C}=\frac{C_M^{n}}{\Delta t}+g_mC_\infty^{n+1},\qquad
g_m=\frac{A_s h_m}{V_M}\ }$$

注意 **$D$ 只出现在扩散项中**，对流项 $g_m$ 不含 $D$——这与原始思路的写法一致，
原始思路在此处的处理是正确的。

### 9.7 离散系统的完备性与求解

未知量为 $T_i^{n+1}$、$C_i^{n+1}$（$i=0,\dots,M$），各 $M+1$ 个；方程为：

| 节点 | 温度方程 | 水分方程 |
|---|---|---|
| $i=0$ | 对称（二对角） | 对称（二对角） |
| $i=1,\dots,M-1$ | 三对角（§9.3） | 三对角（§9.6a） |
| $i=M$ | 第三类边界（§9.5） | 第三类边界（§9.6c） |

两个系统均为**严格对角占优**的三对角方程组（$b_i>|a_i|+|c_i|$，因含 $1/\Delta t$），
可用追赶法（Thomas 算法）以 $O(M)$ 复杂度直接求解，无需迭代。

**解耦求解流程**（每时间步）：

```
输入: T^n, C^n, t_{n+1}
1. 由附件 1 插值得到 T_inf^{n+1}, C_inf^{n+1}
2. 组装温度三对角系数 (§9.3, §9.4, §9.5)  -> 追赶法 -> T^{n+1}
3. 由 C^n 计算界面扩散系数 D_{i+1/2}      (§9.6a)
4. 组装水分三对角系数 (§9.6)              -> 追赶法 -> C^{n+1}
5. n <- n+1, 重复
```

由于问题一中两方程解耦（§7.4），步骤 2、3–4 相互独立，不存在迭代收敛问题。

---

## 10 待求量与输出约定

**论文表 1（温度，单位 $^\circ\mathrm{C}$）与表 2（水分浓度，单位 $\mathrm{kg/kg}$）**：
时间 $100,300,600,900,1200,1500,1800\ \mathrm{s}$ $\times$ 距离 $0,0.5,1,1.5,2\ \mathrm{cm}$。

**`result1.xlsx`**：两个工作表

- 工作表 `温度`：$A$ 列为时间（$1,2,\dots,1800\ \mathrm{s}$），第 1 行为到中心距离
  $0,0.1,0.2,\dots,2.0\ \mathrm{cm}$，共 $1800\times21$ 个温度值；
- 工作表 `水分浓度`：同结构的水分浓度值。

所有数值**保留 4 位小数**（$^\circ\mathrm{C}$ 与 $\mathrm{kg/kg}$ 均按此精度报告）。

---

## 11 相对原始建模思路的修正汇总

| 序号 | 位置 | 原方案 | 本文修正 | 性质 |
|---|---|---|---|---|
| ① | $\alpha$ 数值 | $1.679\times10^{-7}$ | $1.6885553\times10^{-7}\ \mathrm{m^2/s}$ | 数值误差（$-0.569\%$） |
| ② | 内部对角元 $b_i$ | $\dfrac{1}{\Delta t}+\dfrac{\alpha(2i+1)}{2i\Delta r^2}$ | $\dfrac{1}{\Delta t}+\dfrac{2\alpha}{\Delta r^2}$ | **算子反耗散，格式失效**（严重） |
| ③ | 水分界面扩散系数 | 节点值 $D_i^n$ 用于两侧界面 | 界面平均值 $D_{i\pm1/2}$ | **非守恒，残差 10.1 % 且不收敛** |
| ④ | 表面扩散/对流项 | $a_M=-\dfrac{2\alpha}{\Delta r^2}$，$g_h=\dfrac{2\alpha h}{k\Delta r}$ | 保留几何因子：$a_M=-\dfrac{\alpha f_M^-}{\Delta r}$，$g_h=\dfrac{A_s h}{\rho c_p V_M}$ | 用户写法为**一阶**边界（$M=800$ 时误差 $0.040\ \mathrm{K}$）；保留几何因子为**二阶**（$4.5\times10^{-6}\ \mathrm{K}$）。**精度改进，非纠错** |
| ⑤ | 轴向简化理由 | 以 $L/R=12.5$ 为唯一依据 | 补充中截面 $\partial_z=0$ 的**精确**论证 | 论证加强 |
| ⑥ | "两过程相互独立" | 作为普遍结论 | 仅问题一成立；问题 2–4 因 $D=f(C,T)$ 而**双向耦合** | 适用范围限定 |
| ⑦ | 时间步取值 | $\Delta t=0.1\ \mathrm{s}$（$M=200$） | $\Delta t=2^{-8}\ \mathrm{s}$（$M=3200$） | 原取值已随修正 ② 失效；新取值经收敛验证 |

**保持不变（原方案正确）的部分**：控制方程形式、中心节点的 $b_0,c_0$、
**表面节点系数的渐近形式**（$a_M\to-2\alpha/\Delta r^2$、$g_h\to2\alpha h/(k\Delta r)$，
即用户写法在首项上正确，本文只是保留几何因子以提高边界阶数）、
水分表面节点不含 $D$ 的对流项、温度与水分在问题一中的解耦求解流程。

---

## 12 产出文件

| 文件 | 内容 |
|---|---|
| `model/problem1.md` | 本文（模型建立） |
| `model/problem_slove1.md` | 数值求解、验证、表 1/表 2 与结果说明 |
| `src/q1_solve.py` | 求解器 + 符号验证 + 收敛性 + 解析/MOL 独立验证 |
| `src/q1_diagnostics.py` | 方案诊断（稳定性阈值、守恒性、面值取法） |
| `src/q1_energy_check.py` | 算子特征值、离散水量收支、$\Delta t\to0$ 极限 |
| `src/q1_produce.py` | 生产计算，生成 `outputs/result1.xlsx` |
| `outputs/result1.xlsx` | 问题一完整结果（温度 / 水分浓度） |
| `outputs/registry_q1.csv`, `outputs/registry_q1_production.csv` | 数字注册表 |
