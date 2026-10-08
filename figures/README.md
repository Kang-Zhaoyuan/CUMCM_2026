# 出版级学术可视化工程 (Scientific Visualization Engineering)

本目录为 2026 年高教社杯全国大学生数学建模竞赛 A 题论文提供全套出版级高清插图与自动化绘图工作流。图件风格严格遵循 CUPT（中国大学生物理学术竞赛）与国际顶级期刊（Nature/Science/Elsevier）标准，具备四边内向刻度、矢量字体隔离、极简几何标注与自适应高对比色彩映射。

---

## 论文正式录用核心插图

| 插图文件 | 分辨率 / 格式 | 论文章节 | 对应生成脚本 | 物理/数学内涵说明 |
| :--- | :---: | :---: | :--- | :--- |
| `cylinder_geometry_symbols_dot_only.png` | 300 DPI / PNG | 第 4 节 | `scripts/plot_cylinder_geometry_symbols.py` | 圆柱坐标系几何边界、轴对称切片、控制方程主导符号与端面/侧面空间关系剖析 |
| `fig1_chamber_temp_humidity.png` | 300 DPI / PNG | 第 5 节 | `scripts/plot_fig1_chamber_temp_humidity.py` | 附件1烘房温湿度离散测量数据点与 PCHIP（单调保形三次 Hermite 插值）连续演变曲线 |
| `fig5_radius_shrinkage_dynamics.png` | 300 DPI / PNG | 第 6 节 | `scripts/plot_fig5_radius_shrinkage_dynamics.py` | 附件2药材脱水径向收缩动力学特征与体积相对形变率拟合对比 |
| `fig_q3_tail_sensitivity.png` | 300 DPI / PNG | 第 6 节 | `scripts/plot_fig_q3_tail_sensitivity.py` | 环境外推延拓点数 $N$ 敏感性分析，验证基准方案（$N=20$）对烘干预测时长的稳定性 |
| `fvm_multiscale_macro_micro.png` | 300 DPI / PNG | 第 6 节 | `scripts/plot_fvm_multiscale_macro_micro.py` | 宏观柱体网格到微观五环传热/传质控制体通量守恒格式的多尺度分解图 |
| `moving_boundary_mesh_shrinkage.png` | 300 DPI / PNG | 第 6 节 | `scripts/plot_moving_boundary_mesh_shrinkage.py` | 径向几何动态收缩过程中的移动边界有限体积网格坐标映射与体积变化原理 |
| `q1_combined_pizza.png` | 300 DPI / PNG | 第 6 节 | `Fig_Ref/plot_q1_combined_pizza.py` | 问题一预热阶段极坐标时空联合披萨图（Pizza Plot）：左侧湿度场、右侧温度场空间扩散 |
| `q3_moisture_field.png` | 300 DPI / PNG | 第 6 节 | `Fig_Ref/field_snapshot_code/...` | 问题三烘干临界时刻中截面二维含水率场快照等值线分布（直观定位最难干的核心盲区） |
| `q4_combined_pizza.png` | 300 DPI / PNG | 第 6 节 | `Fig_Ref/plot_q4_combined_pizza.py` | 问题四考虑动态收缩工况下的温湿场联合螺旋披萨图（直观展示外径随时间物理收缩） |
| `result2_moisture_lines_0p3cm.png` | 300 DPI / PNG | 第 6 节 | `scripts/plot_result2_lines.py` | 问题二前 3 小时各径向观测测点干基含水率随时间演变的高精度秒级时序折线图 |

---

## 子目录与理论文档指南

* [`scripts/`](scripts/)：论文全部主图的自动化绘制脚本库。
  * 运行 `python run_all.py` 可一键全量重新生成论文所需图件并同步输出至 `paper/figures/`。
* [`Fig_Ref/`](Fig_Ref/)：前沿极坐标披萨图（Pizza Plot）与三维截面场快照专题工程。
  * 包含各问解阵缓存（`q4_solution_data.npz`、`field_snapshot_code/01_圆柱扇区场可视化/q2_solution.npz`）。
  * 采用扇形坐标系展开时间轴，以圆盘径向对应物理空间半径，突破传统二维热力图的时空表达局限。
* [`Archive/`](Archive/)：探索与打磨期间的过程性图件（50+ 张）及试验性脚本归档，完整留存学术探索路径。
* [`FVM五环传热控制体数学意义说明.md`](FVM五环传热控制体数学意义说明.md)：详细推导有限体积法中母环、近环、远环、上环、下环五界面传热通量离散格式的数学与物理基础。
* [`绘图注意事项与规范指引.md`](绘图注意事项与规范指引.md)：规定了统一的字体族（SimSun/STSong + STIX）、四边内朝向刻度、图例无外边框白底等高水准规范。
