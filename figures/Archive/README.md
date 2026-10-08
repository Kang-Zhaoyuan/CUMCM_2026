# 图件设计、迭代与淘汰过程归档库 (Archive)

本文件夹归档了 2026 数模 A 题在探索性数据分析 (EDA) 与几何/物理机理建模过程中产生的所有**中间探索性图件、已淘汰/已融合的早期图件及其对应绘图脚本**。

正式用于论文与正文论述的高清图件及独立绘图脚本已在上一级目录（`../` 与 `../scripts/`）中冻结保留。

---

## 1. 归档目录组织架构

```text
Archive/
├── README.md                      # 本归档库说明文档 (本文件)
│
├── pdf/                           # 矢量中间件与历史 PDF 归档库 (论文全线统一为 300 DPI 高清 PNG)
│   ├── fig_q3_tail_sensitivity.pdf          # 问题 3 延拓敏感性分析矢量 PDF 备份
│   └── fig_q3_tail_sensitivity_cupt.pdf     # CUPT 风格演进中间版本 PDF 备份
│
├── images/                        # 过程与淘汰图件归档库 (共 65+ 张)
│   ├── 【EDA 淘汰/融合图件】
│   │   ├── fig2_chamber_change_rates.png        # [原Fig 2] 烘房温湿度一阶差分与滑动平均变化率 (信息密度低淘汰)
│   │   ├── fig3_boundary_interpolation_inset.png# [原Fig 3] 烘房温湿度局部插值放大图 (已融合进正式 Fig 1)
│   │   ├── fig4_chamber_phase_portrait.png      # [原Fig 4] 烘房温湿度状态空间相轨迹 (控制量非自治动力系统物理牵强淘汰)
│   │   ├── fig6_volume_shrinkage_geometry.png   # [原Fig 6] 早期相对体积与横截面收缩模型 (已融合进正式 Fig 5)
│   │   └── fig7_problem_timescale_timeline.png  # [原Fig 7] 问题求解时间尺度条形图 (与DYC最终精确时间冲突淘汰)
│   │
│   ├── 【FVM 传热矢量与多尺度构图演化图件 (37张)】
│   │   ├── fvm_flux_flared_c2_refined.png       # 3D 渲染五环线稿无标注底图
│   │   ├── fvm_5rings_lineart.png               # 早期 5 环纯线稿定稿图
│   │   ├── flared_c1 ~ flared_c5.png            # 热通量立体喇叭口 (Flared) 5 种造型方案对比
│   │   ├── fvm_flux_v1 ~ v3.png                 # 矢量箭头权重与渐变色过渡探索
│   │   ├── variant_1 ~ variant_4.png            # 画布构图与留白 4 种方案对比
│   │   ├── fvm_macro_cylinder*.png              # 宏观空间网格化圆柱各类透视与构图子图
│   │   ├── fvm_multiscale_style1_arrow_*.png    # XRD 箭头引导方案对比变体
│   │   ├── fvm_multiscale_style2_dashed_*.png   # 双虚线透射方案对比变体
│   │   └── fvm_flux_final_grid.png              # 最终定稿版像素网格图（用于精确核验 Q 坐标）
│   │
│   ├── 【Task 3 动边界与网格划分探索候选图库 (task3_candidates/ 共 22 张)】
│   │   ├── macro_cylinder_shrinkage_candidates_comparison.png # Task 3.2.1 宏观收缩圆柱 Style A~D 四大方案横评图
│   │   ├── macro_cylinder_shrinkage_style_a ~ d.png          # Style A (虚实同轴)、Style B (轮廓脱胎)、Style C (双实线高对比-入选)、Style D (空间重叠)
│   │   ├── task3_2_2_candidates_comparison.png               # Task 3.2.2 微观 3D 厚圆环几何体 4 大透视候选横评图
│   │   ├── task3_2_2_candidate_a ~ d.png                    # 微观候选 A~D (最终选中方案 D 作为演化基准)
│   │   ├── task3_2_2_1_final ~ task3_2_2_4_final.png         # 微观厚圆环网格 3 刀划分、厚度恒定保持、时间文本标注演进图
│   │   ├── task3_2_3_composite_v1 ~ v3.png                   # Task 3.2.3 宏微观放大镜多尺度合成各轮演化图
│   │   └── task3_2_3_2_box_crop.png / box_detail.png        # Task 3.2.3.2 取景框边缘与母线净空微米级核验截图
│   │
│   ├── moving_boundary_landau_fvm_early_draft.png # Task 3.0 早期文本密集型草稿图 (含大量公式与文字堆砌，淘汰废弃)
│   ├── q1_combined_pizza.svg                # 问题 1 披萨图矢量中间件（正式论文统一嵌入超清 PNG，SVG 归档）
│   └── q4_combined_pizza.svg                # 问题 4 螺旋图矢量中间件（正式论文统一嵌入超清 PNG，SVG 归档）
│
└── scripts/                       # 过程与淘汰脚本及建模文件归档库
    ├── 【EDA 淘汰/融合脚本】
    │   ├── plot_fig2_chamber_change_rates.py    # 绘制原 Fig 2 的历史脚本
    │   ├── plot_fig3_boundary_interpolation_inset.py # 绘制原 Fig 3 的历史脚本
    │   ├── plot_fig4_chamber_phase_portrait.py  # 绘制原 Fig 4 的历史脚本
    │   ├── plot_fig6_volume_shrinkage_geometry.py # 绘制原 Fig 6 的历史脚本
    │   └── plot_fig7_problem_timescale_timeline.py # 绘制原 Fig 7 的历史脚本
    │
    ├── 【3D 建模与辅助渲染脚本】
    │   ├── three.min.js                         # WebGL 3D 渲染核心库
    │   ├── OrbitControls.js                     # 3D 交互视角控制器
    │   ├── cylinder_view_picker.html            # 圆柱最佳观察仰角/偏航角交互选择器
    │   ├── fvm_5rings_interactive.html          # 五环控制体 3D 网页可交互调试观察器
    │   ├── render_fvm_lineart.html              # 无头浏览器截图渲染页
    │   ├── plot_fvm_5rings_lineart.py           # 早期纯线稿渲染脚本
    │   ├── render_fvm_annotated_v2.py           # 早期标注草稿脚本
    │   └── scratch_tools/                       # 临时参数探索工具目录
    │
    └── 【Task 3 动边界过程脚本 (task3_drafts/)】
        ├── plot_moving_boundary_landau_fvm_early_draft.py # Task 3.0 早期草稿脚本
        ├── plot_task3_2_1_candidates.py         # 宏观收缩圆柱 4 大方案对比生成脚本
        ├── plot_task3_2_2_candidates.py         # 微观厚圆环 4 大透视对比生成脚本
        ├── plot_task3_2_2_1.py ~ plot_task3_2_2_4.py # 微观厚圆环网格划分与时序演变过程脚本
        ├── plot_task3_2_3.py                    # 宏微观初版合成脚本
        └── plot_task3_2_3_composite.py          # 宏微观合成与取景框净空微调迭代脚本
```

---

## 2. 设计、迭代与淘汰决策备忘录

| 归档项 / 迭代阶段 | 原始定位 | 淘汰/融合理由与处置记录 |
| :--- | :--- | :--- |
| **Fig 2** (`plot_fig2_chamber_change_rates.py`) | 烘房温湿度一阶差分变化率 | 一阶差分主要反映传感器高频数值微扰与滑动平均窗口选取，在正文中无法提供额外的烘干机理，论文篇幅宝贵，果断剔除。 |
| **Fig 3** (`plot_fig3_boundary_interpolation_inset.py`) | 实测散点与 PCHIP 局部放大插值对比 | 插值算法在数学建模中属标准前置工程，无须耗费单独图幅展开证明。其“散点真实记录+连续保形光滑曲线”的精髓已在 Task 1 中完美合入 **Fig 1**。 |
| **Fig 4** (`plot_fig4_chamber_phase_portrait.py`) | 温度-水分浓度相轨迹 | 烘房温湿度为由 PLC 人工设定的时间程序控制量（非内部物理状态自发自治演化），相图在物理动力学上缺乏自治系统的相流管流意义，容易误导评委，果断剔除。 |
| **Fig 6** (`plot_fig6_volume_shrinkage_geometry.py`) | 相对体积留存率与横截面收缩几何模型 | 原图与 Fig 5 存在严重信息重叠。在 Task 2 中，将轴向长度不变几何下的相对体积 $V(t)/V_0$ 直接融合进 **Fig 5(a)** 作为双轴曲线，右侧 **Fig 5(b)** 呈现同心圆截面收缩，原独立图件归档废弃。 |
| **Fig 7** (`plot_fig7_problem_timescale_timeline.py`) | 赛题四问求解时间尺度甘特图 | 早期按赛题直觉绘制，与后续 DYC 全流程高保真数值模拟程序的时间尺度（如72h连续求解、特定烘干目标停止判据）存在口径冲突，避免概念混淆，果断剔除。 |
| **Task 3.0 早期草稿** (`moving_boundary_landau_fvm_early_draft.png`) | 动边界 Landau 变换公式与网格图件 | 画面充斥大量 LaTeX 推导公式、文字说明与四种杂乱配色，视觉重心失焦且与论文正文推导高度重叠，破坏了自明性原则，被用户全盘否决并重启 Task 3.2 流程。 |
| **Task 3.2.1 宏观左图探索** (`macro_cylinder_shrinkage_style_a~d`) | 宏观收缩圆柱与环形微元表征 | 横向对比四大方案：方案 A (虚实同轴混淆)、方案 B (虚线轮廓脱胎过于稀疏)、方案 D (空间交叠杂乱)。最终选定**方案 C (双实线高对比：经典正红初始物料环 + 深酒红收缩物料环)**，并依用户反馈彻底移除环内冗余微箭头。 |
| **Task 3.2.2 微观右图探索** (`task3_2_2_1~4_final`) | 微观厚圆环网格保持与时序示意 | 1. 废除蓝色轮廓与柱面 $\theta$ 面，回归纯净黑红两色与 $(+z, +r)$ 轴；<br>2. 径向切一刀改为切两刀，形成 $3\times 3\times 3=27$ 均匀网格；<br>3. 修正坐标轴 Chevron 箭头端点微米级重叠；<br>4. 坚决落实“药材厚度恒定 ($h_s = h_0$)，仅直径收缩”的模型假设；<br>5. 移除粗重中央箭头，采用截面正下方 $t$ 与 $t+\Delta t$ 纯数学标注，并加入共线纤细微型演化箭头。 |
| **Task 3.2.3 宏微观合成与净空微调** (`task3_2_3_1~2_final`) | 多尺度放大镜透射与取景框定位 | 针对左侧正方形取景框重叠内母线问题，经过 $x_2=758\to 766\to 764$ 精密测算微调：在 $x_2=764.0$ 处完全包裹物料环最右端点 ($x=753$)，同时与较小圆柱内母线 ($x \in [774, 781]$) 留出 $10\,\mathrm{px}$ 黄金呼吸净空，消除了线条粘连；右侧卡片适度放大并维持扁平构图，形成完美的 Task 3 终版定稿。 |
| **矢量 PDF 与 SVG 归档** (`Archive/pdf/`, `scripts/*.svg`) | 敏感性分析与径向动力学矢量源文件 | 论文及排版全线统一为 300 DPI 超清 PNG 格式，杜绝多格式混编与编译歧义。矢量 PDF 与早期版本移入 `Archive/pdf/` 归档封存，矢量 SVG 源码保留于 `scripts/`，根目录与 `figures/` 仅保留纯正超清定稿 PNG。 |
| **敏感性早期脚本** (`plot_sensitivity_tail.py`) | 早期单轴双轴探索脚本 | 早期版本包含过多文字修饰与散点绝对数值堆叠，现已由 CUPT 极简学术风正式脚本 `plot_fig_q3_tail_sensitivity.py` 全面替代，早期草稿移至 `task3_drafts/`。 |
