# 核心数值求解器与计算结果 (Numerical Solvers & Results)

本目录包含 2026 年高教社杯全国大学生数学建模竞赛 A 题的全部核心数值求解代码、空间离散网格模块、离散守恒验证程序以及最终导出的提交结果数据表。

---

## 代码结构与功能划分

| 脚本文件 | 求解问题 / 模块功能 | 核心数学与物理模型 |
| :--- | :--- | :--- |
| [`grid.py`](grid.py) | 二维轴对称有限体积网格与通量装配 | 柱坐标系有限体积法（FVM），内部界面通量差分、外表面 Robin 对流换热/传质边界装配、刚性系统稀疏 Jacobian 解析计算 |
| [`Problem1.py`](Problem1.py) | **问题一**：预热平衡阶段非稳态扩散 | 固定热物性（密度、比热容、导热系数恒定）、经验水分扩散系数 $D_m(C)$、固定圆柱边界下温度场与湿度场联合演变 |
| [`Problem2.py`](Problem2.py) | **问题二**：全过程温湿双向耦合干燥 | 温度与含水率双向耦合变物性模型，前 3 小时高精度瞬态场求解（每隔 1 秒高频采样输出） |
| [`Problem3.py`](Problem3.py) | **问题三**：全域干燥判据定位与烘干时长 | 固定几何尺寸下，积分至全域含水率最大值不超过 $0.15\ \mathrm{kg/kg}$，通过 Scipy Event 机制精准截获干燥终点时刻 |
| [`Problem4.py`](Problem4.py) | **问题四**：移动边界径向动态收缩模型 | 引入附件2径向收缩本构，构建随时间移动的自适应 FVM 控制体网格，精确预测形变工况下的烘干终止时刻 |
| [`checkConservation.py`](checkConservation.py) | 空间离散格式全局守恒性严格校验 | 在非均匀构造场上对有限体积积分格式进行瞬时全局能量守恒与质量守恒数值验证 |
| [`requirements.txt`](requirements.txt) | Python 环境依赖声明 | `numpy`, `scipy`, `openpyxl`, `matplotlib` |

---

## 运行与复现指南

### 1. 环境依赖配置
推荐使用 Python 3.10+。在命令行执行：

```bash
pip install -r requirements.txt
```

### 2. 执行求解脚本
所有求解脚本均支持命令行参数调用，默认网格规模与参数已统一同步为正式论文提交方案（`nr=120, nz=120, stretch=2.0`）：

```bash
# 问题一求解 (预热平衡阶段，0~1800s，每100s采样)
python Problem1.py --nr 120 --nz 120 --stretch 2.0 --output results/result1.xlsx

# 问题二求解 (前3小时瞬态场，0~10800s，每1s采样)
python Problem2.py --nr 120 --nz 120 --stretch 2.0 --output results/result2.xlsx

# 问题三求解 (固定几何全域干燥，PCHIP环境延拓N=20)
python Problem3.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result3.xlsx

# 问题四求解 (径向收缩移动网格全域干燥，PCHIP环境延拓N=20)
python Problem4.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result4.xlsx

# 空间离散全局守恒性校验
python checkConservation.py
```

---

## 算法参数规范与正式设定

* **网格离散**：
  * 径向微元数 $N_r = 120$
  * 轴向微元数 $N_z = 120$
  * 径向节点非均匀拉伸比率 $\mathrm{stretch} = 2.0$（外边界处网格加密以精确捕捉边界层陡峭梯度）
  * 单个物理量自由度：$121 \times 121 = 14641$ 个节点；温度场与湿度场联合状态向量自由度为 $29282$。
* **时间积分**：
  * 积分算法：变阶自适应步长后向差分公式（BDF，解决传热与扩散时间尺度差异引起的强刚性问题）。
  * 相对容差：$\mathrm{rtol} = 10^{-7}$
  * 绝对容差：$\mathrm{atol} = 10^{-9}$
* **环境延拓**：
  * 问题三与问题四在 $t > 4\ \mathrm{h}$ 后，采用附件1最后 $N=20$ 个真实采样时刻的温度与含水率成对算术平均值平滑延拓：
    $$T_\infty = 50.01765\ ^\circ\mathrm{C},\quad C_\infty = 0.0499795\ \mathrm{kg/kg}$$

---

## 输出结果数据说明 (`results/`)

各问正式计算结果已输出至 [`results/`](results/) 目录：

1. [`results/result1.xlsx`](results/result1.xlsx)：预热阶段 $100\sim 1800\ \mathrm{s}$ 药材中部截面各径向测点的温度与干基含水率。
2. [`results/result2.xlsx`](results/result2.xlsx)：前 3 小时（$0 \sim 10800\ \mathrm{s}$）药材中部截面各径向测点的高精度秒级时序场。
3. [`results/result3.xlsx`](results/result3.xlsx)：固定几何尺寸下药材干燥至全域含水率 $\le 0.15\ \mathrm{kg/kg}$ 的全时序过程（精准预测烘干总时间约为 $57.44\ \mathrm{h}$）。
4. [`results/result4.xlsx`](results/result4.xlsx)：考虑径向动态收缩下药材干燥全时序数据及外径收缩时序。
