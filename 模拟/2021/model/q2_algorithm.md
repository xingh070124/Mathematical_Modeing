# 问题二算法实现：生成调整方案与 `result.xlsx`

## 1. 数据接口

输入目录为 `data/`，文件编码采用严格 `GBK/GB18030`。建立三个映射：

```text
node[id] = (x, y, z)                 # 附件1
actuator[id] = (lower, upper_base)   # 附件2
panel[k] = (id1, id2, id3)           # 附件3
```

程序首先校验 2226 个节点、2226 个促动器行、4300 个面板，检查 ID 唯一性、面板引用完整性和所有坐标有限。附件 4 复制到新的输出路径后再写入，原模板绝不覆盖。

## 2. 坐标与目标面计算

```python
alpha = radians(36.795)
beta = radians(78.169)
s = array([cos(beta)*cos(alpha), cos(beta)*sin(alpha), sin(beta)])
s /= norm(s)
```

根据题面焦面与焦比求 `P`、`f`，再计算 `V=P-f*s`。为避免符号错误，执行以下几何断言：焦点到顶点距离为 `f`；焦点位于轴线；顶点横向坐标为零；工作口径在局部 `(e1,e2)` 平面中的半径为 150 m。

对每个节点计算横向半径 `rho`，只保留 `rho<=150` 的节点及与其相关的输出记录。若附件 3 的某个面跨过口径边界，面板积分时按三角形与口径圆的裁剪区域处理，节点调整表则按题目要求的节点筛选规则处理。

## 3. 机构方向与决策变量

对附件 2 每个 ID：

\[
a_i=(u_i^{\rm base}-b_i)/\|u_i^{\rm base}-b_i\|.
\]

标准态上端点与下端点距离约为 `1.98 m`，该值只作为数据一致性诊断；不能将其误当成允许伸缩范围。用
\[
p_i(\delta_i)=p_i+\delta_i a_i
\]
构造节点位置，按题目符号写入 `δ_i`。若附件 2 上端点被认定为节点的真实基准位置，应以 `u_i^{base}` 与 `p_i` 的差异做一致性报告，并选择一种基准定义贯穿计算。

## 4. 数值求解伪代码

```text
load and validate data
construct direction s, orthonormal e1/e2, focus P, vertex V, focal length f
select working-aperture nodes I and adjacency edges E
for each i in I:
    compute actuator direction ai
    compute initial target residual and linear Jacobian
solve a bounded linearized least-squares subproblem
repeat until step/residual tolerance:
    rebuild exact node positions p_i + delta_i*ai
    evaluate surface residuals and edge-length constraint residuals
    solve trust-region/SQP correction with box bounds and inequalities
    accept step only if merit function decreases
check all constraints on the exact, unrounded solution
write vertex, node coordinates, and actuator strokes to a copy of 附件4.xlsx
read the written workbook back and recompute every metric
```

面残差可用节点到隐式抛物面的有符号距离，也可用
\[
\Phi_i=\|q_i\|^2-(q_i\cdot s)^2-4f(q_i\cdot s)
\]
进行无量纲化。相邻边约束按
\[
|l'_{ij}-l_{ij}|/l_{ij}\le0.0007
\]
实现，除非核对题面后确认其定义是另一种相邻促动器约束。

## 5. 写入与格式验证

保持模板的三个工作表：

1. `X坐标, Y坐标, Z坐标`：只写入一行顶点；
2. `节点编号, X坐标, Y坐标, Z坐标`：按附件 1 原始顺序写入工作口径节点；
3. `对应主索节点编号, 伸缩量(米)`：按同一节点顺序写入带符号位移。

写入时保留数值型单元格，设置显示格式为 `0.000`；不要把数字整体转换为字符串。完成后用 `openpyxl.load_workbook(data_only=False)` 重新读取，验证表头、工作表顺序、行数、ID 集合和有限数值。

## 6. 停止与失败状态

建议容差：步长 `1e-8 m`，相对目标变化 `1e-10`，最大迭代次数由求解器配置记录。输出状态至少包括：`converged`、`infeasible`、`max_iter`、`data_error`。不可行时保留诊断文件（最大边长违约、越界行程、节点残差），不生成伪装成最终答案的工作簿。

## 7. 复算指标

对未四舍五入解和导出后（三位小数）解分别计算：

- 目标面残差的最大值、RMS、95% 和 99% 分位数；
- `max(abs(delta_i))` 及越界数；
- 所有相邻边的最大相对长度变化、均值和违反数；
- 调整前后节点半径及面板边长变化。

三位小数后的约束若不再满足，应以导出文件为提交方案重新优化或报告舍入造成的违约，不能只报告内部高精度解。