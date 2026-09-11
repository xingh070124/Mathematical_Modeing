# 问题二求解：烘干全过程耦合传热传质模型的数值求解、验证与结果

> 本文求解 `problem2.md` 建立的模型，给出问题二要求的表 3、表 4 与 `result2.xlsx`。
>
> 全部数值由下列脚本运行产生，可复现：
>
> | 脚本 | 作用 | 输出 |
> |---|---|---|
> | `python src/q2_latent_heat.py` | 汽化潜热 $H_{\rm evap}(T)$ 的热力学推导与 IAPWS-95 定标 | `outputs/registry_q2_latent_heat.csv` |
> | `python src/q2_energy_algebra.py` | 能量方程正确形式的符号推导与量级核验 | `outputs/registry_q2_energy.csv` |
> | `python src/q2_model_numbers.py` | 模型中全部可复算数字 | `outputs/registry_q2_model.csv` |
> | `python src/q2_solve.py --selftest` | 质量矩阵恒等式、Jacobian 有限差分校核 | 控制台 |
> | `python src/q2_verify.py` | 收敛性、守恒性、极值原理、模型变体对照（V0–V11） | `outputs/q2_verify.log`, `outputs/registry_q2_verify.csv` |
> | `python src/q2_produce.py` | 生产计算 | `outputs/result2.xlsx`, `outputs/q2_production.log`, `outputs/registry_q2_production.csv` |
> | `python src/q2_reconcile.py` | 数字对账（两关） | `outputs/reconciliation_q2.csv` |
>
> 环境：Python 3.12.3，numpy 2.5.1，scipy 1.18.1，openpyxl 3.1.2，iapws 1.5.5。

---

## 1 问题二的求解目标

题面（问题 2）：烘干过程一般持续 2–3 天，预热平衡与恒温干燥阶段的参数有所不同。
要求建立**整个烘干过程**药材温度 $T(r,t)$ 与水分浓度 $C(r,t)$ 的数学模型，
相关经验公式统一采用附录 3，并给出

- **表 3 / 表 4**：3 h 内每隔 $0.5\ \mathrm{h}$、距中心 $0,0.5,1,1.5,2\ \mathrm{cm}$ 处的温度与水分浓度；
- **`result2.xlsx`**：$0\sim10800\ \mathrm{s}$ 内每隔 $1\ \mathrm{s}$、径向每隔 $0.1\ \mathrm{cm}$ 的完整结果。

所有结果保留四位小数。本文按此输出。

---

## 2 问题二与问题一的本质差别

这是本文的重点。问题一与问题二**不是同一个方程换一组参数**，而是模型结构上发生了变化。
下表先给结论，随后逐条给出后果的**定量**证据。

| 项目 | 问题一（预热平衡，0–1800 s） | 问题二（全过程，0–10800 s） | 后果 |
|---|---|---|---|
| 扩散系数 | $D=7\times10^{-9}e^{-0.89/C}$，**只依赖 $C$** | $D=2.4\times10^{-3}e^{-0.45/C}e^{-3850/T}$，**依赖 $C$ 与 $T$** | 两场**双向耦合**，必须联立 |
| 密度 | $\rho=820$ 常数 | $\rho=650+128C$ | 热惯性随干燥进程变化 |
| 比热容 | $c_p=2600$ 常数 | $c_p=1450+\dfrac{2736C}{C+1}$ | —— |
| 导热系数 | $k=0.36$ 常数 | $k=0.21+\dfrac{0.38C}{C+1}$ | —— |
| $\rho c_p$ | 常数 $2.132\times10^6$ | 由 $3.335\times10^6$ 降至 $1.209\times10^6$（**降幅 63.74 %**） | **能量方程形式必须重选**（§2.1） |
| 蒸发吸热 | 无（预热阶段蒸发极弱，题面附录 2 亦未给出潜热） | **有**：$q_{\rm evap}=H_{\rm evap}h_m(C_R-C_\infty)$ | **极值原理下界失效**（§2.2） |
| 非线性 | 只有一个非线性系数 $D(C)$，用**半隐式滞后**即足够 | $D(C,T)$、$\rho c_p(C)$、$k(C)$ 三重非线性 | 必须**牛顿迭代** |
| 求解方式 | 两个独立线性三对角系统（追赶法） | 非线性耦合系统 $\to$ 阻尼 Newton + 带状 LU | 迭代次数 3–6 |

### 2.1 差别的核心：$\rho c_p$ 随 $C$ 变化 ⇒ 能量方程不能写成守恒形式

问题一中 $\rho c_p$ 是常数，于是
$\dfrac{1}{\rho c_p}\dfrac{\partial(\rho c_pT)}{\partial t}$ 与
$\dfrac{\partial T}{\partial t}$ **恒等**（`q2_energy_algebra.py` §D 用 sympy 验证：两者之差恰为 $0$）。
问题二中 $\rho c_p$ 随 $C$ 变化 63.74 %，两者不再恒等，**必须做出选择，且这个选择造成的差别不是小量**。

**推导。** 取半径 $r$ 处厚 $\mathrm{d}r$ 的薄环控制体（单位轴向长度），内含干物质（质量不变）
与水（质量随 $C$ 变化）。附录 3 的两式可以**精确**写成混合物形式：

$$\rho_{\rm bulk}=\rho_s(1+C),\qquad \rho_{\rm bulk}c_p=\rho_s\big(c_s+C\,c_l\big)$$

其中 $c_s$ 为干物质比热、$c_l$ 为液态水比热。`q2_energy_algebra.py` §A 用 sympy 解出

$$c_s=1450\ \mathrm{J/(kg\cdot K)},\qquad c_l=4186\ \mathrm{J/(kg\cdot K)}$$

且数值核验的相对差仅 $1.926\times10^{-16}$。$c_l=4186\ \mathrm{J/(kg\cdot K)}$ 正是液态水的
教科书比热值——这说明**附录 3 的 $\rho(C)$ 与 $c_p(C)$ 并不是两个独立的经验式，
而是同一条混合物关系 $\rho_{\rm bulk}c_p=\rho_s(c_s+Cc_l)$ 的两种写法**。

在此结构下，对控制体写严格能量平衡（水以扩散离开时*带走*显焓 $\bar h_w=c_l(T-T_{\rm ref})$）：

$$\frac{\partial}{\partial t}\big[\rho c_p(T-T_{\rm ref})\big]
=\nabla\!\cdot\!(k\nabla T)-\nabla\!\cdot\!\big(\bar h_w\mathbf J_w\big)$$

配合水量守恒 $\nabla\!\cdot\!\mathbf J_w=-\rho_s\dfrac{\partial C}{\partial t}$，
右端末项展开为 $+c_l(T-T_{\rm ref})\rho_s\partial_tC-c_l\mathbf J_w\!\cdot\!\nabla T$，
而左端展开为 $\rho_s(c_s+c_lC)\partial_tT+c_l(T-T_{\rm ref})\rho_s\partial_tC$
——含 $(T-T_{\rm ref})\partial_tC$ 的两项**精确相消**，得到

$$\boxed{\ \rho(C)c_p(C)\frac{\partial T}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\!\left(k(C)\,r\frac{\partial T}{\partial r}\right)
-c_l\,\mathbf J_w\!\cdot\!\nabla T\ }$$

即**非保守形式**（以 $T$ 为状态量、$\rho c_p$ 为系数）才是正确的；而"守恒形式"
$\partial(\rho c_pT)/\partial t=\nabla\!\cdot\!(k\nabla T)$ 会多出一个**伪源项**

$$S_{\rm false}=+c_l(T-T_{\rm ref})\,\rho_s\,\frac{\partial C}{\partial t}$$

在 $c_l(T-T_{\rm ref})\rho_s\partial_tC$ 中取 $T-T_{\rm ref}\sim7\ \mathrm K$、
$\rho_s=275.0423\ \mathrm{kg/m^3}$、体积平均 $\partial_tC=-8.3\times10^{-5}\ \mathrm{kg/(kg\cdot s)}$，
得 $|S_{\rm false}|=6.56\times10^{2}\ \mathrm{W/m^3}$，与主项
$\rho c_p\partial_tT\sim2.60\times10^{3}\ \mathrm{W/m^3}$ 之比为 **0.252**
（`registry_q2_energy.csv` 的 `EC_ratio`）——**同量级，绝不可忽略**。

被保留后又被略去的对流项 $-c_l\mathbf J_w\!\cdot\!\nabla T$ 的量级为
$8.64\times10^{-1}\ \mathrm{W/m^3}$，与主项之比 $3.32\times10^{-4}$，可安全略去。

**数值验证。** `q2_verify.py` 的 V11 用同一求解器分别实现两种形式（`energy="T"` 与 `energy="conserv"`），
在 $M=200$、$\Delta t=0.25\ \mathrm{s}$ 下比较：中心温度在 $t=10800\ \mathrm{s}$ 相差 **9.87 K**（见 §7.6）。
两个 M 下的数字一致，说明这不是网格误差，而是**模型选择**的差别。

> **结论**：问题二的能量方程取式 (1)（非保守形式）。这一选择在问题一中不存在
> （两种形式恒等），是问题二特有的、且量级最大的建模决定。

### 2.2 第二个差别：蒸发吸热使极值原理的**下界**失效

问题一中温度必落在
$\big[\min(T_0,\min_tT_\infty),\ \max(T_0,\max_tT_\infty)\big]$ 内。问题二含蒸发吸热后，
表面可以**低于初温与环境温度**，下界不再成立。

数值证据（`q2_verify.py` V4）：$M=400$、$\Delta t=1/16\ \mathrm{s}$ 下计算温度下界为
**27.9905 °C**，低于包络下界 28.0000 °C 达 0.0095 K；而关闭蒸发项后
（$M=200$、$\Delta t=0.25\ \mathrm{s}$）下界回到 **28.0000 °C**，越界 **0.000000 K**。
两者对照说明穿透**完全由蒸发项造成**（见 §7.4）。

因此问题二的"极值原理"检验必须改写为：

$$T(r,t)\le\max\big(T_0,\ \max_tT_\infty\big),\qquad
\text{（下界改为）}\ T(R,t)\ge T_0-\frac{q_{\rm evap}^{\max}}{h}$$

### 2.3 第三个差别：水分方程的口径需要交代

附录 3 的 $\rho(C)=650+128C$ 反推出的干基骨架密度
$\rho_s=\rho_{\rm bulk}/(1+C)$ 由 $C=2.55$ 时的 $275.0423\ \mathrm{kg/m^3}$
单调升到 $C=0.15$ 时的 $581.9130\ \mathrm{kg/m^3}$（**变化 $+111.57\%$**，
`registry_q2_energy.csv` 的 `EB_rhos_drift`）。若严格要求"体积不变 $+$ 干物质守恒"，
$\rho_s$ 应为常数，故**附录 3 的 $\rho(C)$ 与无收缩假设并不严格自洽**。

但题面式 (4) 把 $D$ 直接定义在 $C$ 上：

$$-D\frac{\partial C}{\partial r}\bigg|_R=h_m\big[C(R,t)-C_\infty(t)\big]$$

因此本题的水分方程按题面口径取

$$\frac{\partial C}{\partial t}=\frac{1}{r}\frac{\partial}{\partial r}\!\left(rD(C,T)\frac{\partial C}{\partial r}\right)$$

这是题面给定的**唯一**自洽读法：$C$ 是被守恒的场，$D$ 作用在 $C$ 上，
$\rho(C)$ 只进入能量方程的热惯性。该不自洽不影响本模型的求解，但应在论文中作为假设
（`problem2.md` B7：3 h 内体积不收缩）与局限如实说明。

---

## 3 控制方程与定解条件

由 §2.1 的结论，问题二的控制方程为

$$\rho(C)c_p(C)\frac{\partial T}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\!\left(k(C)\,r\frac{\partial T}{\partial r}\right)
\qquad 0<r<R,\ 0<t\le10800\ \mathrm{s} \tag{1}$$

$$\frac{\partial C}{\partial t}
=\frac{1}{r}\frac{\partial}{\partial r}\!\left(r\,D(C,T)\frac{\partial C}{\partial r}\right) \tag{2}$$

物性经验式（附录 3）：

$$\rho(C)=650+128C,\qquad c_p(C)=1450+\frac{2736C}{C+1},\qquad
k(C)=0.21+\frac{0.38C}{C+1}$$

$$D(C,T)=2.4\times10^{-3}\exp\!\left(-\frac{0.45}{C}\right)\exp\!\left(-\frac{3850}{T}\right),
\qquad T\ \text{取 K}$$

定解条件：

$$T(r,0)=T_0=301.15\ \mathrm{K},\qquad C(r,0)=C_0=2.55\ \mathrm{kg/kg}$$

$$\left.\frac{\partial T}{\partial r}\right|_{r=0}=0,\qquad
\left.\frac{\partial C}{\partial r}\right|_{r=0}=0$$

$$-k(C)\left.\frac{\partial T}{\partial r}\right|_{r=R}
=h\big[T(R,t)-T_\infty(t)\big]+\underbrace{H_{\rm evap}h_m\big[C(R,t)-C_\infty(t)\big]}_{\text{蒸发吸热}} \tag{3}$$

$$-D(C,T)\left.\frac{\partial C}{\partial r}\right|_{r=R}
=h_m\big[C(R,t)-C_\infty(t)\big] \tag{4}$$

$T_\infty(t)$、$C_\infty(t)$ 由附件 1 的 241 个点（$\Delta t=60\ \mathrm{s}$）经**保形分段三次
插值（PCHIP）**连续化。纯前 3 h 落在附件 1 的覆盖区间 $[0,14400]\ \mathrm{s}$ 内，无需外推。

### 3.1 附录 3 的耦合结构

三个非线性系数 $D(C,T)$、$\rho c_p(C)$、$k(C)$ 同时进入两个方程，形成三条耦合通路：

| 通路 | 机制 | 强度 |
|---|---|---|
| $T\to D\to C$ | Arrhenius 因子 $\exp(-3850/T)$ | $\partial\ln D/\partial T=3850/T^2=4.245\times10^{-2}\ \mathrm{K^{-1}}$（$T=301.15\ \mathrm K$），即 **4.2 %/K** |
| $C\to\rho c_p,k\to T$ | 热惯性与导热能力随含水率变化 | $\rho c_p$ 全程降 63.74 % |
| $C(R)\to q_{\rm evap}\to T(R)$ | 表面相变潜热直接进入表面热平衡 | 表面温降 $\sim0.19\ \mathrm K$（§4） |

特征数（以 $C_0$、$T_0$ 为基准）：

| 特征数 | 值 | 含义 |
|---|---|---|
| $\mathrm{Bi}=hR/k(C_0)$ | 1.0353 | $>0.1$，内部温度梯度不可忽略 |
| $\mathrm{Bi}_m=h_mR/D(C_0,T_0)$ | 2.8360 | 表面传质与内部扩散阻力同量级 |
| $R^2/\alpha(C_0)$ | 2761.9 s | 温度 3 h 内趋于准稳态 |
| $R^2/D(C_0,T_0)$ | $7.090\times10^4$ s | 水分远未平衡（比 3 h 大 6.6 倍） |
| $\alpha/D$ | 25.67 | 温度过程比水分过程快约 26 倍 ⇒ 刚性 |

**刚性是问题二求解的核心困难**：温度方程的特征时间约 $2.8\times10^3\ \mathrm s$，
水分方程约 $7.1\times10^4\ \mathrm s$，两者相差 26 倍；且 $\rho c_p$ 在求解过程中变化 63.74 %。
因此时间积分格式必须**无条件稳定**，本文取后向 Euler。

---

## 4 蒸发吸热项

### 4.1 题面未给出 $H_{\rm evap}$，本文自行推导

附录 2/3 只给出 $h$、$h_m$，**没有给出汽化潜热**。本文不采用"抄一个文献常数"的做法，
而由基础热力学关系推导其函数形式，再用国际水物性标准 IAPWS-95 定标
（`src/q2_latent_heat.py`、`src/q2_verify.py` 的 V10）。

**(i) Clapeyron 方程。** 液气两相在饱和线上化学势相等，沿饱和线微分并用
$s_v-s_l=H_{\rm evap}/T$：

$$\frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T}=\frac{H_{\rm evap}}{T(v_v-v_l)}
\quad\Longleftrightarrow\quad H_{\rm evap}=T(v_v-v_l)\frac{\mathrm{d}p_{\rm sat}}{\mathrm{d}T} \tag{5}$$

**(ii) Clausius–Clapeyron 近似及其误差。** 引入 $v_l\ll v_v$ 与理想气体
$v_v=R_vT/p_{\rm sat}$（$R_v=R_u/M_w=461.518\ \mathrm{J/(kg\cdot K)}$），得

$$H_{\rm evap}(T)=R_vT^2\frac{\mathrm{d}\ln p_{\rm sat}}{\mathrm{d}T} \tag{6}$$

保留真实气体 $v_v=ZR_vT/p_{\rm sat}$ 时 $H^{\rm CC}_{\rm evap}/H^{\rm true}_{\rm evap}=1/Z$。
数值核验（V10）：$1/Z-1$ 与 CC 偏差的最大不一致为 **0.0102 个百分点**，
印证 CC 的偏差**全部来自气相非理想性**且量级 $<0.41\%$。精确 Clapeyron 式 (5)
复现 IAPWS-95 的 $h_{fg}$ 最大偏差 **0.1016 J/kg**（相对 $4\times10^{-8}$）。

**(iii) Kirchhoff 定律。** $\mathrm{d}H_{\rm evap}/\mathrm{d}T=c_{p,v}-c_{p,l}$，
故在窄温区内 $H_{\rm evap}$ 近似线性。

**(iv) 定标。** 以物料初温 $28\ ^\circ\mathrm C$ 为物理锚点，由 IAPWS-95 取
$H_{\rm evap}(28\ ^\circ\mathrm C)=2434560.5\ \mathrm{J/kg}$，在 $28\sim50\ ^\circ\mathrm C$ 上
最小二乘得斜率 $-2391.0094\ \mathrm{J/(kg\cdot K)}$：

$$\boxed{\ H_{\rm evap}(T)=2.4346\times10^{6}-2.391\times10^{3}\,(T-28\ ^\circ\mathrm C)
\quad \mathrm{J/kg}\ } \tag{7}$$

在 $28\sim50\ ^\circ\mathrm C$ 上的最大残差为 **109.2 J/kg（0.00449 %）**，
远低于本题精度要求。该定标式与热力学第一性关系一致，**不引入任何可调参数**。

**注意**：$H_{\rm evap}$ 的**量级**（$2.4\times10^6$）决定了蒸发项的权重；
其温度依赖（28→50 °C 变化 2.2 %）影响很小——用常数 $H_{\rm evap}(40\ ^\circ\mathrm C)$
替代式 (7) 只改变表面温度 $7.6\times10^{-4}\ \mathrm K$（§7.5 的 V8 变体）。

### 4.2 量级：蒸发项是"小修正"但必须保留

由式 (3) 的末项与式 (4)：

$$q_{\rm evap}=H_{\rm evap}h_m\big[C_R-C_\infty\big]
\approx2.4059\times10^{6}\times8\times10^{-7}\times\Delta C
\approx1.925\,\Delta C\ \ \mathrm{J/(m^2\cdot s)}$$

| 时刻 | $C_\infty$ | $q_{\rm evap}$（取 $C_R\approx2.5$） | $h(T_\infty-T_R)$ | 比值 |
|---|---|---|---|---|
| $t=0$ | 0.0196 | 4.774 | 0 | — |
| $t=1800\ \mathrm s$ | 0.0331 | 4.748 | 337.5 | 1.41 % |
| $t=3600\ \mathrm s$ | 0.0427 | 4.730 | 487.5 | 0.97 % |

**表面温降估计**：$\Delta T_R\sim q_{\rm evap}/h=4.73/25\approx0.19\ \mathrm K$，
仅为总温升（28→50 °C，22 K）的 **0.86 %**——属**弱耦合**，但直接作用于表面节点，
在四位小数精度下必须保留。数值结果（V8）与这一解析估计同量级，见 §7.5。

### 4.3 通量口径的交代（重要）

题面式 (4) 写作 $-D\,\partial C/\partial r|_{R}=h_m(C_R-C_\infty)$，
其中 $h_m$ 的单位是 $\mathrm{m/s}$，$C$ 的单位是 $\mathrm{kg/kg}$。
两侧量纲为 $\mathrm{kg/(m\cdot s)}$，即题面采用的是"通量以单位密度表示"的口径。
本文的 $q_{\rm evap}$ 沿用**同一口径**，保证与题面给定的 $h_m=8\times10^{-7}\ \mathrm{m/s}$
自洽。

**该口径需要显式声明**：若按"热质传递类比"估计，$h$ 与 $h_m$ 应满足
$h_m\sim h/(\rho_{\rm air}c_{p,\rm air})\approx0.02\ \mathrm{m/s}$，比题面值高约 4 个数量级。
此时 $q_{\rm evap}$ 放大 $\sim2.5\times10^{4}$ 倍，将远超对流供热而成为表面热平衡的主导项。
因此"蒸发吸热是弱耦合"的结论**强依赖于 $h_m$ 的口径**，本文在 §7.5 给出 $h_m$ 的
敏感性（V9），并在 §9 的局限中如实说明。

---

## 5 离散格式

### 5.1 弱形式与线性单元

取权函数 $v$，分别以 $r\,\mathrm{d}r$ 加权积分并分部积分，第三类边界作为**自然边界条件**
自动进入弱形式（这一结构性优点是有限元相对有限差分的主要收益）：

$$\int_0^R\!\rho c_p\frac{\partial T}{\partial t}v\,r\,\mathrm{d}r
+\int_0^R\!kr\frac{\partial T}{\partial r}\frac{\partial v}{\partial r}\,\mathrm{d}r
+\Big\{hR\big[T(R)-T_\infty\big]+H_{\rm evap}h_mR\big[C(R)-C_\infty\big]\Big\}v(R)=0 \tag{8}$$

$$\int_0^R\!\frac{\partial C}{\partial t}v\,r\,\mathrm{d}r
+\int_0^R\!Dr\frac{\partial C}{\partial r}\frac{\partial v}{\partial r}\,\mathrm{d}r
+h_mR\big[C(R)-C_\infty\big]v(R)=0 \tag{9}$$

网格 $r_i=i\Delta r$，$\Delta r=R/M$，线性（$P_1$）基函数 $\varphi_i$。
单元 $[a,b]=[r_{i-1},r_i]$ 上的解析积分（含轴对称权 $r$）：

$$\mathbf M^e=\frac{\rho c_p\Delta r}{12}
\begin{bmatrix}3a+b & a+b\\ a+b & a+3b\end{bmatrix},\qquad
\mathbf K^e=\frac{k(a+b)}{2\Delta r}
\begin{bmatrix}1&-1\\-1&1\end{bmatrix}$$

退化检验：中置单元（$a=\Delta r/2$）给出 $M_{11}=M_{22}=\Delta r/3$、$M_{12}=\Delta r/6$，
回到标准一维线性单元质量矩阵。✓

### 5.2 行和集中质量矩阵

对一致质量矩阵按**行和集中**，利用单位分解 $\sum_j\varphi_j\equiv1$：

$$M^L_{ii}=\int_0^R\!\rho c_p\varphi_i\,r\,\mathrm{d}r$$

内部节点由左右两个单元贡献相加得（`q2_solve.py` 已用恒等式核验，相对误差 $2.1\times10^{-16}$）

$$\boxed{\ M^L_{ii}=\rho(C_i)c_p(C_i)\,\Delta r\,r_i\qquad(1\le i\le M-1)\ } \tag{10}$$

边界节点只有单侧单元：

$$M^L_{00}=\frac{\rho c_p\Delta r^2}{6},\qquad
M^L_{MM}=\frac{\rho c_p\Delta r^2(3M-1)}{6}$$

水分方程的质量矩阵不含 $\rho c_p$，内部与边界分别为 $\Delta r\,r_i$、
$\Delta r^2/6$、$\Delta r^2(3M-1)/6$。

**集中质量的物理意义**：$M^L_{ii}=\rho c_p\Delta r\,r_i$ 恰是"节点 $i$ 所在环形控制体"
（体积 $\Delta r\cdot r_i$，单位轴向长度）的热容，与问题一的有限体积控制体
$V_i$ 在内部节点**逐项完全相同**。因此问题一与问题二在空间离散上具有相同的守恒结构，
这是两问结果可以互相校验的基础。

### 5.3 $r=0$ 节点：集中质量的一个已知弱点（本文的诚实交代）

在**内部**节点两种口径完全一致，但在 $r=0$ 处不同：

| 口径 | $r=0$ 的热容 | $r=0$ 的刚度系数 | 等效 $T_0$ 方程 |
|---|---|---|---|
| 行和集中 FEM | $\rho c_p\,\Delta r^2/6$ | $k\Delta r/2/\Delta r=k/2$ | $\dot T_0=3\alpha(T_1-T_0)/\Delta r^2$ |
| 精确半控制体 FV | $\rho c_p\,\Delta r^2/8$ | $k/2$ | $\dot T_0=4\alpha(T_1-T_0)/\Delta r^2$ |

而柱坐标算子在 $r\to0$ 的精确值为
$\frac1r\partial_r(r\partial_rT)\to2\partial_r^2T\to4\alpha(T_1-T_0)/\Delta r^2$。
**即集中质量在 $r=0$ 的等效系数恰为精确值的 $3/4$**，与 $M$ 无关，属**局部不一致**。

这是集中质量（行和集中）在柱坐标下的固有代价。本文的处理是：

1. **如实指出**该不一致只影响 $r=0$ 附近的一层网格，内部节点与守恒型有限体积逐项相同；
2. **定量测量**其影响：`src/q2_center_node.py` 用常数系数 Robin 圆柱问题与 Bessel 解析解
   对比两种口径的误差随 $M$ 的下降（§7.2）；
3. **在 §7.3 的生产不确定度中用"两种口径之差"作为该项的误差上界**，确认其低于
   四位小数阈值 $5\times10^{-5}$。

> 若要求 $r=0$ 也严格一致，只需把 $M^L_{00}$ 换成 $\rho c_p\Delta r^2/8$
> （即 `Par(boundary="halfcv")`，问题一的精确半控制体口径）。本文以
> `boundary="lumped"`（严格按 `problem2.md` §9.3 的行和集中）为生产口径，
> 因为它是标准 FEM 做法且内部守恒结构与问题一一致；`halfcv` 作为对照。

### 5.4 时间离散与残差

后向 Euler（A-稳定且 L-稳定）给出非线性代数方程组 $\mathbf R(\mathbf U^{n+1})=\mathbf 0$，
$\mathbf U=(\mathbf T,\mathbf C)^{\mathsf T}\in\mathbb R^{2(M+1)}$：

$$\mathbf R_T=\mathbf M(\mathbf C)\frac{\mathbf T-\mathbf T^n}{\Delta t}+\mathbf K(\mathbf C)\mathbf T
+hR(T_M-T_\infty^{n+1})\mathbf e_M+H_{\rm evap}h_mR(C_M-C_\infty^{n+1})\mathbf e_M$$

$$\mathbf R_C=\mathbf M^C\frac{\mathbf C-\mathbf C^n}{\Delta t}+\mathbf K^C(\mathbf C,\mathbf T)\mathbf C
+h_mR(C_M-C_\infty^{n+1})\mathbf e_M$$

界面系数取相邻节点**算术平均**：$k_{i+1/2}=\tfrac12(k_i+k_{i+1})$，
$D_{i+1/2}=\tfrac12(D_i+D_{i+1})$。

### 5.5 Jacobian

解析 Jacobian 为 $2\times2$ 分块、带宽 $(3,3)$ 的稀疏带矩阵（交错排序 $[T_0,C_0,T_1,C_1,\dots]$）：

$$\mathbf J=\begin{bmatrix}
\dfrac{\partial\mathbf R_T}{\partial\mathbf T} & \dfrac{\partial\mathbf R_T}{\partial\mathbf C}\\[8pt]
\dfrac{\partial\mathbf R_C}{\partial\mathbf T} & \dfrac{\partial\mathbf R_C}{\partial\mathbf C}
\end{bmatrix}$$

由附录 3 的解析导数：

$$\frac{\partial(\rho c_p)}{\partial C}=128\,c_p(C)+\frac{2736\,\rho(C)}{(C+1)^2},\qquad
\frac{\partial k}{\partial C}=\frac{0.38}{(C+1)^2}$$

$$\frac{\partial D}{\partial C}=D\cdot\frac{0.45}{C^2},\qquad
\frac{\partial D}{\partial T}=D\cdot\frac{3850}{T^2}$$

块 $(1,1)$、$(2,2)$ 的线性部分为 $\mathbf M/\Delta t+\mathbf K$（加边界对角元）；
块 $(1,2)$ 由 $\mathbf M(\mathbf C)$、$\mathbf K(\mathbf C)$ 的隐式依赖与**蒸发项**
$H_{\rm evap}h_mR$ 构成；块 $(2,1)$ 由 $D$ 的 Arrhenius 温度依赖构成。
块 $(1,2)$ 的蒸发项是**唯一显式出现于 Jacobian 的非物性项**，其值
$H_{\rm evap}h_mR=0.0389536$（取 $H_{\rm evap}(28\ ^\circ\mathrm C)$），
与对角元 $1/\Delta t=32\ \mathrm{s^{-1}}$（$\Delta t=1/32\ \mathrm{s}$）相比仅占
$0.122\%$。若取 $H_{\rm evap}=0$，块 $(1,2)$ 退化为纯物性耦合。

**Jacobian 已被逐元核验**：`q2_solve.py --selftest` 对 $M=12$ 的密矩阵与中心差分
逐元比较，六种配置（默认、$H_{\rm evap}=0$、常数 $H_{\rm evap}$、守恒形式、
`halfcv` 边界、附录 2 物性）的最大相对偏差均为 $2.25\times10^{-7}$ 量级（有限差分自身的
截断误差），即**解析 Jacobian 正确**。

### 5.6 Newton 迭代

$$\mathbf J(\mathbf U^{(k)})\delta\mathbf U^{(k)}=-\mathbf R(\mathbf U^{(k)}),\qquad
\mathbf U^{(k+1)}=\mathbf U^{(k)}+\theta\,\delta\mathbf U^{(k)}$$

初值取上一时间步解。收敛判据同时要求
$\|\mathbf R\|_\infty\le10^{-11}\|\mathbf R(\mathbf U^n)\|_\infty$ 与
$\|\theta\delta\mathbf U\|_\infty\le10^{-13}$；最大迭代 25 次，并带回溯线搜索
（残差上升则 $\theta\leftarrow\theta/2$，至多 12 次）。

---

## 6 求解流程与参数

```
输入: U^0 = (T^0, C^0); 网格 {r_i}; dt; 环境 T_inf(t), C_inf(t)
for n = 0, 1, ... (到 t = 10800 s):
    T_inf, C_inf <- PCHIP(附件1) 在 t_{n+1}
    U = U^n
    repeat k = 1..25:
        组装 R(U) 与 J(U)          # 一次组装同时给出残差与 Jacobian
        if ||R||_inf <= 1e-11*||R(U^n)||_inf: break
        解 J dU = -R               # 带状 LU, 带宽 (3,3)
        U <- U + theta*dU;  必要时回溯 theta /= 2
    U^{n+1} = U
    if t_{n+1} 是 1 s 的整数倍: 记录 21 个输出半径的结果
```

| 参数 | 取值 | 理由 |
|---|---|---|
| 空间节点数 $M$ | **800**（$\Delta r=0.0025\ \mathrm{cm}$） | $M$ 为 20 的倍数，输出半径 $0,0.1,\dots,2.0\ \mathrm{cm}$ 恰落在节点上；由 §7.2 的空间收敛性确认 |
| 时间步长 $\Delta t$ | **1/32 s = 0.03125 s** | 整除 1 s；由 §7.2 的时间收敛性确认 |
| 总时长 | 10800 s | 题面要求 |

**线性代数**：Jacobian 每行至多 7 个非零元（带宽 $(3,3)$），用 LAPACK 带状求解器，
复杂度 $O(M)$；每步 Newton 平均 3 次迭代。

---

（§7 数值验证与 §8 结果在计算完成后补齐。）
