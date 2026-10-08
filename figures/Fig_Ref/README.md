# 极坐标切片披萨图与截面场快照工程 (Polar Pizza Plots & Field Snapshots)

本目录包含问题一与问题四极坐标时空联合披萨图（Pizza Plot）的生成流水线，以及问题二、三截面场快照脚本。

---

## 核心可视化算法

### 1. 极坐标时钟披萨展开图 (Clockwise Radial Pizza Plot)
* **坐标映射**：
  * 极角 $\theta \in [0, 2\pi)$：映射干燥推进时间轴 $t \in [0, t_{\text{end}}]$（顺时针展开）。
  * 极径 $r \in [0, R]$：映射圆柱药材物理空间半径 $r$（圆心为药材轴线 $r=0$，外沿为药材表面 $r=R$）。
* **收缩螺旋扩展 (Archimedean Shrinkage Spiral)**：
  在问题四中，外径随时间物理收缩：$R(t) = R_0 - \Delta R(t)$。披萨图外轮廓自动适配为阿基米德收缩螺旋线，直观呈现脱水导致的几何边界内缩。

---

## 核心文件索引

| 脚本 / 数据 | 对应图件 | 技术实现说明 |
| :--- | :--- | :--- |
| [`plot_q1_combined_pizza.py`](plot_q1_combined_pizza.py) | `q1_combined_pizza.png` | 问题一预热阶段（0~1800 s）1×2 双子图：左侧水分扩散场（Coolwarm 色标）、右侧温度场（Inferno 色标） |
| [`plot_q4_combined_pizza.py`](plot_q4_combined_pizza.py) | `q4_combined_pizza.png` | 问题四考虑动态收缩工况下的 1×2 联合螺旋披萨图（读取 `q4_solution_data.npz`） |
| [`field_snapshot_code/`](field_snapshot_code/) | `q3_moisture_field.png` | 柱扇区场与子午面长方形截面流线/等值线快照脚本 |
| [`q4_solution_data.npz`](q4_solution_data.npz) | - | 问题四数值积分生成的时空场矩阵缓存（含时间、半径、温度与含水率阵列） |
