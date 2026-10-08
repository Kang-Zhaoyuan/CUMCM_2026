# 数值求解器与计算结果 (Numerical Solvers & Results)

本目录包含柱坐标系有限体积法（FVM）离散、稀疏 Jacobian 解析装配、变阶后向差分公式（BDF）时间推进的全部实现代码及最终导出的结果工作簿。

---

## 核心源码构成

| 文件 | 模块功能与核心算法 | 关键实现细节 |
| :--- | :--- | :--- |
| [`grid.py`](grid.py) | 二维轴对称有限体积网格与通量装配 | 柱坐标系 $(r,z)$ 控制体面通量积分；外表面 Robin 传热传质边界处理；刚性方程组解析稀疏 Jacobian 构建 |
| [`Problem1.py`](Problem1.py) | 问题一求解器（预热平衡阶段） | 恒定热物性，经验水分扩散系数 $D_m(C)$，固定几何边界；输出 $0\sim 1800\ \mathrm{s}$ 截面场 |
| [`Problem2.py`](Problem2.py) | 问题二求解器（变物性耦合干燥） | 温度与水分双向耦合变物性模型；前 3 小时（$0\sim 10800\ \mathrm{s}$）秒级瞬态场积分 |
| [`Problem3.py`](Problem3.py) | 问题三求解器（全域干燥与终点截获） | 固定几何尺寸长时程推进；SciPy `solve_ivp` Event 事件精确截获 $\max C(r,z,t) \le 0.15\ \mathrm{kg/kg}$ 干燥终点 |
| [`Problem4.py`](Problem4.py) | 问题四求解器（径向收缩移动网格） | 动态移动边界 FVM 格式，根据附件2收缩本构动态重构控制体网格，积分至全域达标终点 |
| [`checkConservation.py`](checkConservation.py) | 全局守恒性严格数值校验 | 在非均匀构造场上对离散积分通量进行全局能量与水分质量瞬时守恒性校验 |
| [`requirements.txt`](requirements.txt) | 依赖声明 | `numpy`, `scipy`, `openpyxl`, `matplotlib` |

---

## 正式求解参数配置

* **空间网格**：$N_r = 120,\ N_z = 120$，径向网格拉伸比 $\text{stretch} = 2.0$（外边界加密），单变量自由度 14,641，状态向量总自由度 29,282。
* **时间推进**：SciPy BDF（变阶后向差分公式），$\text{rtol} = 10^{-7},\ \text{atol} = 10^{-9}$。
* **环境延拓**：$t > 14400\ \mathrm{s}$ 后，环境参数取附件1末尾 $N=20$ 点成对算术平均：$T_\infty = 50.01765\ ^\circ\mathrm{C},\ C_\infty = 0.0499795\ \mathrm{kg/kg}$。

---

## 求解指令与结果输出 (`results/`)

```bash
python Problem1.py --nr 120 --nz 120 --stretch 2.0 --output results/result1.xlsx
python Problem2.py --nr 120 --nz 120 --stretch 2.0 --output results/result2.xlsx
python Problem3.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result3.xlsx
python Problem4.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result4.xlsx
python checkConservation.py
```

* [`results/result1.xlsx`](results/result1.xlsx)：预热阶段 $100\sim 1800\ \mathrm{s}$（间隔 $100\ \mathrm{s}$）截面温度与含水率分布。
* [`results/result2.xlsx`](results/result2.xlsx)：前 3 小时（$0 \sim 10800\ \mathrm{s}$，间隔 $1\ \mathrm{s}$）高频时序场。
* [`results/result3.xlsx`](results/result3.xlsx)：固定几何全域干燥达标历程（预测总干燥时间：$57.44\ \mathrm{h}$）。
* [`results/result4.xlsx`](results/result4.xlsx)：动态收缩几何全域干燥达标历程与外径演变（预测总干燥时间：$53.62\ \mathrm{h}$）。
