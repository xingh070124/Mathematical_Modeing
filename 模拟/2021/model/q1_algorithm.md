# 问题一算法实现：计算正上方目标的理想抛物面

## 1. 输入、输出与依赖

**输入**

- `data/附件1.csv`：节点编号及三维坐标；
- `data/附件2.csv`：促动器下端点与基准态上端点；
- `data/附件3.csv`：三角面板的三个节点编号；
- 题面常数：`R`、`F/R`、工作口径 `D=300 m`、行程范围和 `0.07%` 约束。

CSV 必须以严格 `GBK`（必要时 `GB18030`）解码，禁止静默替换字符。节点编号始终按字符串处理。输出是解析参数、节点调整诊断和约束检查报告；问题二再将同一接口写入 `result.xlsx`。

建议依赖：Python 3.10+、NumPy、Pandas、SciPy、openpyxl。算法不使用随机数。

## 2. 数据校验

1. 检查附件 1、2 均为 2226 行，附件 3 为 4300 行；
2. 检查节点编号唯一、坐标有限；
3. 检查附件 2 的每个节点均在附件 1 中；
4. 检查附件 3 的所有三个节点均存在且同一面无重复节点；
5. 由附件 3 展开无向边集合 `E`；
6. 计算附件 1 节点半径作为诊断，报告均值、最大偏差，不强行将约 `300.4 m` 数据改成 `300 m`。

## 3. 几何计算

正上方情形设
\[
e_3=(0,0,1),\qquad s=e_3.
\]
根据题面焦面定义求焦点 `P`，再求
\[
V=P-fe_3.
\]
对任一点 `x` 计算
\[
q=x-V,\quad w=q\cdot e_3,\quad
\Phi(x)=\|q\|^2-w^2-4fw.
\]
在工作口径内的筛选条件为
\[
\rho(x)=\sqrt{\|q\|^2-w^2}\le150\text{ m}.
\]

促动器方向由附件 2 的基准态上端点 `t_i` 与下端点 `b_i` 给出：
\[
a_i=(t_i-b_i)/\|t_i-b_i\|.
\]
若题目把附件 1 节点视作主索位置，则用 `a_i` 计算沿促动器方向的节点更新；若机构几何要求从基准上端点而非节点坐标开始，则在报告中明确这一区别并保持全流程一致。

## 4. 求解伪代码

```text
read three GBK CSV files
validate row counts, IDs, finite values, and triangle references
build node map ID -> index and edge set E
build e3, focal point P, vertex V from the stated geometry
select nodes I with rho <= 150 m
for each i in I:
    compute actuator direction ai
    define Phi_i(delta) = Phi(pi + delta*ai)
solve bounded least squares:
    minimize sum_i w_i*Phi_i(delta_i)^2 + lambda*sum_(i,j) in E (delta_i-delta_j)^2
    subject to -0.6 <= delta_i <= 0.6
    and each edge-length relative change <= 0.0007
reconstruct p'_i and evaluate Phi, distance residuals, edge changes
report parameters and feasibility; if infeasible, report violation and stop
```

推荐先用 `scipy.optimize.least_squares` 的有界版本处理节点面残差，再用 `scipy.optimize.minimize(method='SLSQP' 或 'trust-constr')` 加入边长不等式；节点数较多时采用解析/有限差分 Jacobian 和稀疏约束。若仅求解析理想面而不执行离散拟合，应明确输出“连续解”，不要把它称为已满足全部机构约束的解。

## 5. 精度、失败处理和复杂度

- 角度转弧度使用双精度；几何残差计算使用 `float64`；
- 停止条件建议为目标函数相对变化 `<1e-10`、步长 `<1e-8 m` 或达到最大迭代次数；
- 任何非有限坐标、重复 ID、缺失面节点直接报错；
- 若约束不可行，输出 `status=infeasible`、最大行程违约、最大边长违约和未满足节点数，不生成具有误导性的“最优”结果；
- 预处理为 `O(N+M)`，其中 `N=2226`、`M=4300`；每次目标函数评估为 `O(N+M)`，稀疏实现可降低内存。

## 6. 独立验证

- 回代 `V`：应满足 `q= P-V` 与焦距关系；
- 回代任意采样点：`|Phi|` 应接近零；
- 调整后报告节点到目标面的最大、RMS、95%/99%分位距离；
- 重新计算所有 `E` 上的 `|l'ij/lij-1|`，检查最大值和违反条数；
- 重新读取导出的坐标，独立于优化器计算同一指标；
- 对 `F/R` 和角度施加小扰动，报告结果变化，不据此直接声称鲁棒。

## 7. 可复现记录

运行日志应记录输入文件路径、文件哈希、解码方式、题面参数、优化器、容差、初值、终止状态和全部约束指标。文档中的 `Given/Derived/Assumed` 分类必须与日志一致。