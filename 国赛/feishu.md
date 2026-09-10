回复 星河: 
输出完整方案
# 问题一完整方案：预热平衡阶段热质耦合模型

---

## 一、物理模型

### 1.1 几何简化

药材：圆柱形，L=25cm，R=2cm。L/R=12.5 → 忽略轴向，只考虑径向一维传递。

坐标系：圆柱坐标(r,θ,z)，轴对称 → θ无关，z无关 → 仅r方向。

### 1.2 物理过程

- **热量**：热风通过对流加热药材表面 → 热量通过导热从表面传向中心
- **水分**：药材内部水分通过扩散向表面迁移 → 表面水分被热风带走
- **两个过程单向解耦**：本题参数中温度方程不含C，水分方程不含T → 可独立求解

### 1.3 模型假设

1. 药材为均匀各向同性多孔介质
2. 忽略轴向传递（L/R=12.5足够大）
3. 预热阶段尺寸不变（问题4才考虑收缩）
4. 物性参数(ρ, cp, k)为常数（题目附录2给定）
5. 水分扩散系数D仅依赖含水率C（题目公式给定）
6. 忽略辐射换热（对流为主）
7. 环境温度T∞(t)和含水率C∞(t)由附件1数据插值得到

---

## 二、控制方程

### 2.1 温度场

对圆柱体内半径r处的薄环做能量守恒：

$$\rho c_p \frac{\partial T}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(k \frac{\partial T}{\partial r}\right)$$

本题ρ, cp, k为常数，定义热扩散系数：

$$\alpha = \frac{k}{\rho c_p} = \frac{0.36}{820 \times 2600} = 1.6793 \times 10^{-7} \text{ m}^2/\text{s}$$

方程化简为：

$$\frac{\partial T}{\partial t} = \alpha \cdot \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial T}{\partial r}\right) \tag{1}$$

### 2.2 水分场

水分迁移遵循Fick扩散定律：

$$\frac{\partial C}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(D(C) \cdot r \frac{\partial C}{\partial r}\right) \tag{2}$$

扩散系数（题目附录2）：

$$D(C) = 7 \times 10^{-9} \cdot \exp\left(-\frac{0.89}{C}\right) \quad (\text{m}^2/\text{s}) \tag{3}$$

这是一个**非线性扩散方程**。

### 2.3 两个方程的关键区别

| | 温度方程(1) | 水分方程(2) |
|--|-----------|-----------|
| 线性/非线性 | **线性**（α常数） | **非线性**（D依赖C） |
| 物理含义 | Fourier导热 | Fick扩散 |
| 可解析求解？ | ✅ 可以（Bessel级数） | ❌ 只能数值求解 |

---

## 三、定解条件

### 3.1 初始条件（t=0）

$$T(r, 0) = 28°C = 301.15 \text{ K} \tag{4}$$
$$C(r, 0) = 2.55 \text{ kg/kg} \tag{5}$$

### 3.2 边界条件

**中心 r=0（对称性）**：

$$\frac{\partial T}{\partial r}\bigg|_{r=0} = 0, \quad \frac{\partial C}{\partial r}\bigg|_{r=0} = 0 \tag{6}$$

**表面 r=R（第三类边界条件，Robin条件）**：

热量：

$$-k\frac{\partial T}{\partial r}\bigg|_{r=R} = h\left[T(R,t) - T_\infty(t)\right] \tag{7}$$

水分：

$$-D(C)\frac{\partial C}{\partial r}\bigg|_{r=R} = h_m\left[C(R,t) - C_\infty(t)\right] \tag{8}$$

参数：h=25 W/(m²·K)，hm=8×10⁻⁷ m/s。

### 3.3 环境激励

T∞(t) 和 C∞(t) 由附件1离散数据通过**PCHIP保形插值**得到连续函数。

### 3.4 单位规范

| 物理量 | 单位 | 注意 |
|--------|------|------|
| 距离r | m | 题目给cm，需转换 |
| 时间t | s | — |
| 温度T | K | D(C)公式中T用K |
| 含水率C | kg/kg | 干基，无量纲 |

---

## 四、无量纲化与特征尺度

### 4.1 无量纲变量

$$\xi = \frac{r}{R}, \quad \tau = \frac{\alpha t}{R^2}, \quad \theta = \frac{T - T_\infty}{T_0 - T_\infty}, \quad \phi = \frac{C - C_\infty}{C_0 - C_\infty}$$

### 4.2 关键无量纲数

**热Biot数**（表面热阻/内部热阻）：

$$Bi = \frac{hR}{k} = \frac{25 \times 0.02}{0.36} = 1.389$$

Bi>1 → 内外温差不可忽略，不能用集总参数法。

**热特征时间**：

$$\tau_T = \frac{R^2}{\alpha} = \frac{0.02^2}{1.6793 \times 10^{-7}} = 2382 \text{ s} \approx 39.7 \text{ min}$$

1800s < τ_T → 预热阶段温度尚未完全平衡。

**水分特征时间**（初始）：

$$\tau_C = \frac{R^2}{D_0} = \frac{0.02^2}{5.593 \times 10^{-10}} = 7.15 \times 10^5 \text{ s} \approx 8.3 \text{ 天}$$

τ_C >> τ_T → 水分扩散比热传导慢约300倍。

**Lewis数**（热扩散/质扩散）：

$$Le = \frac{\alpha}{D_0} = \frac{1.6793 \times 10^{-7}}{5.593 \times 10^{-10}} \approx 300$$

Le >> 1 → **热先走、水后走**，这是问题一的核心物理结论。

---

## 五、数值方案

### 5.1 离散化网格

```
径向：M个内部节点 + 1个表面节点，Δr = R/M
时间：N个步长，Δt = t_total/N

r_i = i·Δr,  i = 0,1,...,M
t_n = n·Δt,  n = 0,1,...,N

T_i^n ≈ T(r_i, t_n)
C_i^n ≈ C(r_i, t_n)
```

推荐参数：M=200, Δr=0.0001m=0.01cm, Δt=0.25s。

### 5.2 r=0 奇点处理（L'Hôpital法则）

圆柱坐标 $\frac{1}{r}\frac{\partial}{\partial r}$ 在r=0处为0/0型：

$$\lim_{r\to 0} \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial T}{\partial r}\right) = 2\frac{\partial^2 T}{\partial r^2}\bigg|_{r=0}$$

所以r=0处控制方程变为：

$$\frac{\partial T}{\partial t}\bigg|_{r=0} = 2\alpha \frac{\partial^2 T}{\partial r^2}\bigg|_{r=0} \tag{9}$$

### 5.3 温度方程：Crank-Nicolson格式

对控制方程(1)在(t_n, t_{n+1})时间中点做C-N离散：

$$\frac{T_i^{n+1} - T_i^n}{\Delta t} = \frac{\alpha}{2}\left[\mathcal{L}(T^{n+1}) + \mathcal{L}(T^n)\right]$$

其中 $\mathcal{L}$ 是空间差分算子。

#### 内部节点 i=1,...,M-1

守恒型有限体积差分：

$$\mathcal{L}(T)_i = \frac{1}{r_i \Delta r}\left[r_{i+1/2}\frac{T_{i+1}-T_i}{\Delta r} - r_{i-1/2}\frac{T_i-T_{i-1}}{\Delta r}\right]$$

其中 $r_{i\pm1/2} = (i\pm0.5)\Delta r$。

组装为三对角系统：

$$a_i T_{i-1}^{n+1} + b_i T_i^{n+1} + c_i T_{i+1}^{n+1} = d_i \tag{10}$$

系数：

$$a_i = -\frac{\alpha \Delta t}{2} \cdot \frac{(i-0.5)}{i \cdot \Delta r^2}$$
$$b_i = 1 + \frac{\alpha \Delta t}{2} \cdot \frac{2i+1}{2i \cdot \Delta r^2} + \frac{\alpha \Delta t}{2} \cdot \frac{(i-0.5)}{i \cdot \Delta r^2} = 1 + \frac{\alpha \Delta t}{2} \cdot \frac{(i+0.5)+(i-0.5)}{i \cdot \Delta r^2}$$

实际上更简洁的形式：

$$a_i = -\frac{\alpha \Delta t}{2\Delta r^2} \cdot \frac{i-0.5}{i}$$
$$b_i = 1 + \frac{\alpha \Delta t}{2\Delta r^2} \cdot \frac{(i+0.5)+(i-0.5)}{i} = 1 + \frac{\alpha \Delta t}{\Delta r^2}$$
$$c_i = -\frac{\alpha \Delta t}{2\Delta r^2} \cdot \frac{i+0.5}{i}$$

右端（已知项）：

$$d_i = a_i T_{i-1}^n + (2-b_i) T_i^n + c_i T_{i+1}^n$$

#### r=0 节点（i=0）

由式(9)和对称性 T_{-1}=T_1：

$$b_0 T_0^{n+1} + c_0 T_1^{n+1} = d_0$$
$$b_0 = 1 + \frac{2\alpha \Delta t}{\Delta r^2}, \quad c_0 = -\frac{2\alpha \Delta t}{\Delta r^2}, \quad d_0 = (2-b_0)T_0^n - c_0 T_1^n$$

#### r=R 表面节点（i=M）

对流边界 $-k\frac{\partial T}{\partial r}\big|_{r=R} = h(T_M - T_\infty)$：

$$\frac{\partial T}{\partial r}\bigg|_{r=R} \approx \frac{T_M - T_{M-1}}{\Delta r} = -\frac{h}{k}(T_M - T_\infty^{n+1})$$

代入控制方程在i=M的离散形式：

$$a_M T_{M-1}^{n+1} + b_M T_M^{n+1} = d_M$$
$$a_M = -\frac{2\alpha \Delta t}{\Delta r^2}$$
$$b_M = 1 + \frac{2\alpha \Delta t}{\Delta r^2} + \frac{2\alpha h \Delta t}{k \Delta r}$$
$$d_M = (2-b_M)T_M^n - a_M T_{M-1}^n + \frac{2\alpha h \Delta t}{k \Delta r} T_\infty^{n+1}$$

### 5.4 水分方程：BDF2 + Newton-Raphson

水分方程(2)是非线性的（D依赖C），采用**二阶BDF2 + Newton迭代**。

#### BDF2时间离散

$$\frac{3C^{n+1} - 4C^n + C^{n-1}}{2\Delta t} = \mathcal{L}_D(C^{n+1})$$

其中 $\mathcal{L}_D$ 是含变系数D(C)的空间差分算子。

#### Newton迭代

设 $C^{n+1,(k)}$ 为第k次迭代值，定义残差：

$$F(C) = \frac{3C - 4C^n + C^{n-1}}{2\Delta t} - \mathcal{L}_D(C) = 0$$

Newton迭代：

$$C^{n+1,(k+1)} = C^{n+1,(k)} - J^{-1} F(C^{n+1,(k)})$$

其中J是Jacobian矩阵。由于 $\mathcal{L}_D$ 对C的依赖只在D(C)上，Jacobian是三对角矩阵。

#### 空间离散（变系数处理）

扩散项用调和平均处理界面扩散系数：

$$D_{i+1/2} = \frac{2 D_i D_{i+1}}{D_i + D_{i+1}}$$

则 $\mathcal{L}_D(C)_i = \frac{1}{r_i \Delta r}\left[D_{i+1/2} r_{i+1/2} \frac{C_{i+1}-C_i}{\Delta r} - D_{i-1/2} r_{i-1/2} \frac{C_i-C_{i-1}}{\Delta r}\right]$

### 5.5 环境数据插值：PCHIP

PCHIP（分段三次Hermite插值）比线性插值光滑，比三次样条更安全（保单调性，不产生振荡）。

```python
from scipy.interpolate import PchipInterpolator

T_inf_func = PchipInterpolator(t_env, T_env_data)
C_inf_func = PchipInterpolator(t_env, C_env_data)
```

---

## 六、半解析验证（加分大项）

### 6.1 Bessel本征展开

温度方程(1)是线性常系数问题，对Robin边界条件可以构造解析解。

边界条件：$\frac{\partial T}{\partial r}\big|_{r=0}=0$（中心对称），$-k\frac{\partial T}{\partial r}\big|_{r=R}=h(T-T_\infty)$（表面对流）。

分离变量法：

$$T(r,t) = T_\infty + \sum_{k=1}^{\infty} A_k e^{-\lambda_k^2 \alpha t} J_0(\lambda_k r)$$

其中 λ_k 是超越方程的正根：

$$\lambda_k J_1(\lambda_k R) = \frac{h}{k} J_0(\lambda_k R) \tag{11}$$

即：

$$\lambda_k R \cdot J_1(\lambda_k R) = Bi \cdot J_0(\lambda_k R)$$

前4个本征值（Bi=1.389时）：

| k | λ_k R | J_0(λ_k R) | J_1(λ_k R) |
|---|-------|------------|------------|
| 1 | ~2.0 | ... | ... |
| 2 | ~5.0 | ... | ... |
| 3 | ~8.0 | ... | ... |
| 4 | ~11.0 | ... | ... |

（具体值需用数值方法求解超越方程）

展开系数：

$$A_k = \frac{2}{R^2 J_0^2(\lambda_k R)} \int_0^R r \cdot [T_0 - T_\infty] \cdot J_0(\lambda_k r) dr = \frac{2(T_0 - T_\infty)}{\lambda_k R J_1(\lambda_k R)}$$

### 6.2 Duhamel原理（时变环境）

对于时变边界 $T_\infty(t)$，用Duhamel原理：

$$T(r,t) = T_0 + \int_0^t \frac{\partial}{\partial t'} \left[\sum_{k=1}^{\infty} B_k e^{-\lambda_k^2 \alpha (t-t')} J_0(\lambda_k r)\right] T_\infty(t') dt'$$

离散化后与数值解对比，验证数值格式的正确性。

### 6.3 验证判据

| 检验项 | 标准 |
|--------|------|
| 最大绝对误差 | < 10⁻⁵ K |
| 收敛阶 | ≈ 2.00（C-N理论值） |
| 相邻网格误差比 | ≈ 4（二阶格式特征） |