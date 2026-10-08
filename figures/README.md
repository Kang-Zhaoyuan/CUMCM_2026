# 学术可视化工程 (Visualization Pipeline)

本目录包含论文全套插图、极坐标展开切片图（Pizza Plot）及主图生成脚本。图件设计遵循 CUPT 与期刊印刷规范（四边向内刻度、SimSun/STSong + STIX 数学字体、矢量与 300 DPI 无损导出）。

---

## 论文核心插图索引

| 插图文件 | 论文位置 | 生成脚本 | 物理/数学内涵 |
| :--- | :---: | :--- | :--- |
| [`cylinder_geometry_symbols_dot_only.png`](cylinder_geometry_symbols_dot_only.png) | 第 4 节 | `scripts/plot_cylinder_geometry_symbols.py` | 柱坐标系轴对称切片、控制体微元与主导边界传质符号定义 |
| [`fig1_chamber_temp_humidity.png`](fig1_chamber_temp_humidity.png) | 第 5 节 | `scripts/plot_fig1_chamber_temp_humidity.py` | 附件1离散实验温湿度与 PCHIP 单调保形三次插值驱动曲线 |
| [`fig5_radius_shrinkage_dynamics.png`](fig5_radius_shrinkage_dynamics.png) | 第 6 节 | `scripts/plot_fig5_radius_shrinkage_dynamics.py` | 附件2实测径向收缩动力学与相对体积收缩本构关系拟合对比 |
| [`fig_q3_tail_sensitivity.png`](fig_q3_tail_sensitivity.png) | 第 6 节 | `scripts/plot_fig_q3_tail_sensitivity.py` | 环境外推点数 $N$ 敏感性分析（$N=1\sim 60$），验证 $N=20$ 基准方案鲁棒性 |
| [`fvm_multiscale_macro_micro.png`](fvm_multiscale_macro_micro.png) | 第 6 节 | `scripts/plot_fvm_multiscale_macro_micro.py` | 宏观柱体网格到微观五环（母环、近环、远环、上环、下环）通量守恒格式多尺度剖析 |
| [`moving_boundary_mesh_shrinkage.png`](moving_boundary_mesh_shrinkage.png) | 第 6 节 | `scripts/plot_moving_boundary_mesh_shrinkage.py` | 径向几何动态收缩过程中的移动边界有限体积微元坐标映射与网格自适应演变 |
| [`q1_combined_pizza.png`](q1_combined_pizza.png) | 第 6 节 | `Fig_Ref/plot_q1_combined_pizza.py` | 问题一极坐标时空联合披萨图：左侧含水率扩散场、右侧温度场空间演变 |
| [`q3_moisture_field.png`](q3_moisture_field.png) | 第 6 节 | `Fig_Ref/field_snapshot_code/...` | 问题三烘干临界时刻中截面二维等值线场快照，定位干燥盲区 |
| [`q4_combined_pizza.png`](q4_combined_pizza.png) | 第 6 节 | `Fig_Ref/plot_q4_combined_pizza.py` | 问题四动态收缩工况下的螺旋披萨图，直观展现物理外径随时间连续收缩 |
| [`result2_moisture_lines_0p3cm.png`](result2_moisture_lines_0p3cm.png) | 第 6 节 | `scripts/plot_result2_lines.py` | 问题二前 3 小时各径向观测测点（$r=0, 0.5, 1.0, 1.5, 2.0\ \mathrm{cm}$）含水率秒级演变曲线 |

---

## 模块结构与执行

* **批处理生成**：进入 `scripts/` 执行 `python run_all.py` 可全量更新论文主图。
* **极坐标切片工程 (`Fig_Ref/`)**：包含极坐标披萨图展开算法（以圆盘角向代表时间轴、径向代表物理半径）及二维流线/等值线快照脚本。
* **微元推导理论 (`FVM五环传热控制体数学意义说明.md`)**：有限体积法控制体内外界面面通量守恒差分推导。
* **历史探索草稿 (`Archive/`)**：算法研发过程中的 50 余张阶段性草图与调试脚本。
