# -*- coding: utf-8 -*-
import os

EDA_DIR = r"D:\HIT\数模2026\eda_figures"

README_MD = """# 2026 全国大学生数学建模竞赛 A 题 - 探索性数据分析 (EDA) 绘图工程

本工程存放 2026 数模 A 题初期数据探索与机理分析的所有可视化脚本及对应高清图件。为了便于在论文写作过程中针对单张图件进行细粒度微调与归档管理，所有绘图代码已**统一归档至 `scripts/` 子文件夹**中，并实现**一个脚本独立对应一张图件**的严格双射关系。

---

## 1. 目录组织架构 (Directory Layout)

```text
eda_figures/
│
├── fig1_chamber_temp_humidity.png          # [图1] 预热温湿度时序演化
├── fig2_chamber_change_rates.png           # [图2] 升温速率与水分变化率
├── fig3_boundary_interpolation_inset.png   # [图3] 边界样条插值与局部放大
├── fig4_chamber_phase_portrait.png         # [图4] 温-湿状态相平面轨迹
├── fig5_radius_shrinkage_dynamics.png      # [图5] 药材外径实测收缩动力学
├── fig6_volume_shrinkage_geometry.png      # [图6] 圆柱体体积收缩几何机理
├── fig7_problem_timescale_timeline.png     # [图7] 四问求解时间跨度甘特图
│
├── run_all.py                              # 根目录一键调度批处理脚本
├── README.md                               # 本工程双射文档与调图指引
├── 绘图注意事项与规范指引.md               # 论文级可视化规范、配色与避坑红线
│
└── scripts/                                # 【归档】所有绘图脚本代码库
    ├── plot_fig1_chamber_temp_humidity.py
    ├── plot_fig2_chamber_change_rates.py
    ├── plot_fig3_boundary_interpolation_inset.py
    ├── plot_fig4_chamber_phase_portrait.py
    ├── plot_fig5_radius_shrinkage_dynamics.py
    ├── plot_fig6_volume_shrinkage_geometry.py
    ├── plot_fig7_problem_timescale_timeline.py
    ├── plot_eda_figures.py                 # 早期集成式绘图脚本归档备份
    └── run_all.py                          # 脚本目录内批量运行器
```

---

## 2. 脚本与图件双射对应表 (Bijective Mapping)

| 序号 | 独立绘图脚本 (`scripts/`) | 输出图件 (`.png`) | 数据源 | 核心物理/数学内容 | 建议论文放置位置 |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **Fig 1** | [`plot_fig1_chamber_temp_humidity.py`](./scripts/plot_fig1_chamber_temp_humidity.py) | `fig1_chamber_temp_humidity.png` | 附件 1 | 烘房 4 小时预热阶段温度与水蒸气质量浓度时序双轴曲线，标注 0.5h, 3.0h, 4.0h 关键转折点 | 第 3 节：烘房外环境建模 / 边界条件确定 |
| **Fig 2** | [`plot_fig2_chamber_change_rates.py`](./scripts/plot_fig2_chamber_change_rates.py) | `fig2_chamber_change_rates.png` | 附件 1 | 温度升温速率与水分浓度变化率时序波动分析（差分离散点 + 7 分钟滑动平均滤波拟合趋势线） | 数据预处理 / 边界变化率平滑性分析 |
| **Fig 3** | [`plot_fig3_boundary_interpolation_inset.py`](./scripts/plot_fig3_boundary_interpolation_inset.py) | `fig3_boundary_interpolation_inset.png` | 附件 1 | 烘房离散实测点与连续三次样条 (Cubic Spline) 插值拟合曲线对比（含 $t \\in [1800, 3600]\\ \\mathrm{s}$ 局部放大子图） | PDE 数值求解边界条件离散化与平滑性检验 |
| **Fig 4** | [`plot_fig4_chamber_phase_portrait.py`](./scripts/plot_fig4_chamber_phase_portrait.py) | `fig4_chamber_phase_portrait.png` | 附件 1 | 烘房温度-水蒸气质量浓度 $(T_{\\mathrm{env}}, C_{\\mathrm{env}})$ 相平面状态演化轨迹，时间映射色彩及转移箭头 | 烘房环境热湿强耦合动力学机理分析 |
| **Fig 5** | [`plot_fig5_radius_shrinkage_dynamics.py`](./scripts/plot_fig5_radius_shrinkage_dynamics.py) | `fig5_radius_shrinkage_dynamics.png` | 附件 2 | 药材 72 小时截面外径实测衰减曲线及收缩速率演变（双子图：$R(t)$ 与 $|\\mathrm{d}R/\\mathrm{d}t|$，标出 43.33% 收缩率） | 第 5 节：问题 3 动边界尺寸收缩规律与几何模型 |
| **Fig 6** | [`plot_fig6_volume_shrinkage_geometry.py`](./scripts/plot_fig6_volume_shrinkage_geometry.py) | `fig6_volume_shrinkage_geometry.png` | 附件 2 + 几何模型 | 药材圆柱体体积相对保留率 $V(t)/V_0$ 动态与截面各向同性收缩几何相图（$V/V_0 = (R/R_0)^2$ 机理推导） | 模型假设与几何推导 / 轴向长度不变性论证 |
| **Fig 7** | [`plot_fig7_problem_timescale_timeline.py`](./scripts/plot_fig7_problem_timescale_timeline.py) | `fig7_problem_timescale_timeline.png` | 赛题文本 | 题目四问求解时间尺度与附件数据跨度对比甘特图（0.5h, 3h, 4h, 48h, 72h 秒级/小时级分级解析） | 第 1 节：问题重述 / 模型总体框架技术路线图 |

---

## 3. 运行指南

### 3.1 单脚本调图（针对单张图微调）
在论文排版需要微调单张图件的参数时，可直接在终端中运行对应的归档脚本：
```powershell
# 在 eda_figures 目录下运行
py -3.11 scripts/plot_fig1_chamber_temp_humidity.py
py -3.11 scripts/plot_fig5_radius_shrinkage_dynamics.py

# 或进入 scripts 目录运行
cd scripts
py -3.11 plot_fig1_chamber_temp_humidity.py
```
> 所有脚本内部均已配置好路径解析，无论在根目录还是在 `scripts/` 目录运行，生成的 `.png` 均会自动统一输出并保存在 `eda_figures/` 根目录。

### 3.2 一键批量重新生成全部图件
在 `eda_figures` 目录下执行调度脚本：
```powershell
py -3.11 run_all.py
```

---

## 4. 各脚本核心微调参数速查

- **Fig 1 (`scripts/plot_fig1_chamber_temp_humidity.py`)**:
  - `ax1.set_ylim(...)`（温度左轴范围，默认 `[15, 55]`）
  - `ax2.set_ylim(...)`（水分浓度右轴范围，默认 `[0.005, 0.055]`）
  - `ax1.axvline(...)`、`ax1.annotate(...)`（分段临界点竖线与标注文本）
- **Fig 2 (`scripts/plot_fig2_chamber_change_rates.py`)**:
  - `window=7`（滑动平均窗口大小，调大更平滑，调小更敏锐）
- **Fig 3 (`scripts/plot_fig3_boundary_interpolation_inset.py`)**:
  - `inset_axes(..., width="42%", height="40%", loc='lower right', ...)`（局部放大图位置与尺寸）
- **Fig 4 (`scripts/plot_fig4_chamber_phase_portrait.py`)**:
  - `cmap='viridis'`（相图时间演变色系，可选 `'plasma'`, `'coolwarm'`）
- **Fig 5 (`scripts/plot_fig5_radius_shrinkage_dynamics.py`)**:
  - `ax1.annotate(...)`（72h 结束点及收缩率文字位置与箭头）
- **Fig 6 (`scripts/plot_fig6_volume_shrinkage_geometry.py`)**:
  - `xytext=(34, 15)`（右图几何不变性机理解析框位置，与图例完美避让）
- **Fig 7 (`scripts/plot_fig7_problem_timescale_timeline.py`)**:
  - `bars` 列表（定义问题阶段起止时间、色卡与文字描述）
"""

with open(os.path.join(EDA_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(README_MD.strip() + "\n")

print("[SUCCESS] README.md updated with scripts/ layout!")
