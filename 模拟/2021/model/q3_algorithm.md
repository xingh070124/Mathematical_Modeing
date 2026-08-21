# 问题三算法实现：三角面板接收比计算

## 1. 输入与状态构造

读取附件 1、附件 3 和问题二输出的 `result.xlsx`。构造两套节点坐标：

- `base[id]`：附件 1 的基准态坐标；
- `work[id]`：从问题二工作表 2 读取的调整后坐标。

读取问题二工作表 1 的顶点和题面方向参数，构造馈源中心 `P`、入射方向 `d_in` 和接收平面。检查两套坐标的 ID 集合相同、三角面引用完整；任何缺失或重复 ID 都终止计算。

## 2. 面板方向和权重

对每个状态分别执行：

```text
for each triangle (i,j,k):
    obtain p_i, p_j, p_k
    area = 0.5 * norm(cross(p_j-p_i, p_k-p_i))
    normal = cross(...) / (2*area)
    if normal orientation disagrees with global convention:
        normal = -normal
    keep the portion inside the 300 m aperture
    compute projected weight area * max(0, abs(dot(d_in, normal)))
```

退化三角形（面积小于 `1e-10 m²`）记录并跳过，同时在报告中给出数量。工作口径裁剪可采用三角形内重心采样近似；若所有节点均在口径内，可将裁剪误差作为诊断而非默认忽略。

## 3. 反射线命中判断

对三角形内采样点 `x`：

1. 计算 `d_out=d_in-2*dot(d_in,n)*n`；
2. 求反射线与馈源接收平面 `P + {y:y·n_feed=0}` 的交点；
3. 若射线参数 `t>=0` 且交点到 `P` 的距离不超过 `0.5 m`，则命中；
4. 以投影权重乘命中指标累加。

若反射线与接收平面平行，判为不命中，除非其所在面恰好与接收平面重合，此类退化情况单独记录。为避免符号约定错误，对一组人工构造的正入射平面执行反射方向单元测试。

## 4. 确定性三角积分伪代码

```text
for state in [base, work]:
    total = 0; received = 0; skipped = 0
    for triangle in panels:
        clip triangle to aperture (or use aperture mask at samples)
        compute area and normal
        for M-point deterministic barycentric quadrature:
            x = barycentric_sample(triangle, m)
            g = illumination_weight(x, normal, optional_distance_model)
            total += area * weight_m * g
            if ray_hits_feed(x, normal):
                received += area * weight_m * g
    eta[state] = received / total
increase M until both eta values change below tolerance
report eta_work, eta_base, absolute and relative changes
```

采样点必须使用固定的重心点集；不使用随机蒙特卡洛，或使用固定种子并记录种子。推荐从 1、4、16、64 点/三角形逐级加密，要求相邻等级接收比相对变化小于 `1e-3`（阈值可按运行成本调整），同时报告最终 `M`。

## 5. 数值稳定性与复杂度

- 平面求交分母绝对值小于 `1e-12` 时视为平行；
- 归一化法向前检查面积；
- 所有功率权重先截断为非负并检查有限性；
- 复杂度为 `O(KM)`，`K=4300`、`M` 为每面板采样点数；内存可保持 `O(K)` 或流式累加。

## 6. 验证与输出

至少输出：

- 两状态有效面板数、总面积、总投影权重；
- `η_work`、`η_base`、绝对差和相对变化；
- 积分加密表及收敛状态；
- 退化面板、口径裁剪和反射线平行异常数；
- 以附件 4 三位小数坐标与内部高精度坐标分别计算的结果差异。

独立复算时不复用第一次计算中保存的法向和交点，而是重新从导出的节点坐标展开三角面；若两次结果在容差内一致，才把接收比写入最终报告。若 `η_base=0`，不报告相对提升率，只报告绝对接收比差。

## 7. 模型边界

程序计算的是题面几何光学模型的接收比估计。没有实测馈源方向图、面板反射系数、遮挡和波动光学参数时，不应把输出称为真实射电望远镜系统效率，也不能仅凭一次网格采样结果声称工程最优。