# -*- coding: utf-8 -*-
import os

EDA_DIR = r"D:\HIT\数模2026\eda_figures"

README_MD = """# 2026 全国大学生数学建模竞赛 A 题 - 探索性数据分析 (EDA) 绘图工程

本目录存放 2026 数模 A 题初期数据探索与机理分析的所有可视化脚本及对应高清图件。为了便于在论文写作过程中针对单张图件进行细粒度微调，所有绘图脚本均已完成**彻底的模块化拆分**，实现**一个脚本独立对应一张图件**的严格双射关系。

---

## 1. 脚本与图件双射对应表 (Bijective Mapping)

| 序号 | 绘图脚本 (`.py`) | 输出图件 (`.png`) | 数据源 | 核心物理/数学内容 | 建议论文放置位置 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **Fig 1** | [`plot_fig1_chamber_temp_humidity.py`](./plot_fig1_chamber_temp_humidity.py) | `fig1_chamber_temp_humidity.png` | 附件 1 | 烘房 4 小时预热阶段温度与水蒸气质量浓度时序双轴曲线，标注 0.5h, 3.0h, 4.0h 关键转折点 | 第 3 节：烘房外环境建模 / 边界条件确定 |
| **Fig 2** | [`plot_fig2_chamber_change_rates.py`](./plot_fig2_chamber_change_rates.py) | `fig2_chamber_change_rates.png` | 附件 1 | 温度升温速率与水分浓度变化率时序波动分析（差分离散点 + 7 分钟滑动平均滤波拟合趋势线） | 数据预处理 / 边界变化率平滑性分析 |
| **Fig 3** | [`plot_fig3_boundary_interpolation_inset.py`](./plot_fig3_boundary_interpolation_inset.py) | `fig3_boundary_interpolation_inset.png` | 附件 1 | 烘房离散实测点与连续三次样条 (Cubic Spline) 插值拟合曲线对比（含 $t \\in [1800, 3600]\\ \\mathrm{s}$ 局部放大子图） | PDE 数值求解边界条件离散化与平滑性检验 |
| **Fig 4** | [`plot_fig4_chamber_phase_portrait.py`](./plot_fig4_chamber_phase_portrait.py) | `fig4_chamber_phase_portrait.png` | 附件 1 | 烘房温度-水蒸气质量浓度 $(T_{\\mathrm{env}}, C_{\\mathrm{env}})$ 相平面状态演化轨迹，时间映射色彩及转移箭头 | 烘房环境热湿强耦合动力学机理分析 |
| **Fig 5** | [`plot_fig5_radius_shrinkage_dynamics.py`](./plot_fig5_radius_shrinkage_dynamics.py) | `fig5_radius_shrinkage_dynamics.png` | 附件 2 | 药材 72 小时截面外径实测衰减曲线及收缩速率演变（双子图：$R(t)$ 与 $|\\mathrm{d}R/\\mathrm{d}t|$，标出 43.33% 收缩率） | 第 5 节：问题 3 动边界尺寸收缩规律与几何模型 |
| **Fig 6** | [`plot_fig6_volume_shrinkage_geometry.py`](./plot_fig6_volume_shrinkage_geometry.py) | `fig6_volume_shrinkage_geometry.png` | 附件 2 + 几何模型 | 药材圆柱体体积相对保留率 $V(t)/V_0$ 动态与截面各向同性收缩几何相图（$V/V_0 = (R/R_0)^2$ 机理推导） | 模型假设与几何推导 / 轴向长度不变性论证 |
| **Fig 7** | [`plot_fig7_problem_timescale_timeline.py`](./plot_fig7_problem_timescale_timeline.py) | `fig7_problem_timescale_timeline.png` | 赛题文本 | 题目四问求解时间尺度与附件数据跨度对比甘特图（0.5h, 3h, 4h, 48h, 72h 秒级/小时级分级解析） | 第 1 节：问题重述 / 模型总体框架技术路线图 |

---

## 2. 运行环境与依赖库

- **Python 版本**: Python 3.11+
- **核心依赖**:
  ```bash
  pip install numpy scipy pandas openpyxl matplotlib
  ```
- **操作系统与字体**:
  - Windows 系统下已配置微软雅黑 (`Microsoft YaHei`) 与黑体 (`SimHei`) 字体回退机制；
  - 数学公式采用 Matplotlib 内置 STIX 引擎渲染，无需依赖本地外部 TeXLive 环境，完全开箱即用。

---

## 3. 执行指南

### 3.1 单脚本执行（论文调图推荐）
当您在论文排版时，需要微调某张图的坐标轴范围、文字大小、图例位置或线条粗细时，可直接针对对应脚本操作：
```powershell
# 例如仅重新生成图 1
py -3.11 plot_fig1_chamber_temp_humidity.py

# 例如仅重新生成图 5
py -3.11 plot_fig5_radius_shrinkage_dynamics.py
```

### 3.2 一键批量重新生成所有图件
运行批处理调度脚本 [`run_all.py`](./run_all.py)：
```powershell
py -3.11 run_all.py
```
终端将依次调用并输出 7 个图件的渲染进度与保存成功提示。

---

## 4. 图件详细参数与代码微调指引

### 4.1 Fig 1 (`plot_fig1_chamber_temp_humidity.py`)
- **调整双轴范围**: 修改 `ax1.set_ylim(...)`（温度范围，默认 `[15, 55]`）或 `ax2.set_ylim(...)`（水分浓度范围，默认 `[0.005, 0.055]`）。
- **调整关键点标注**: 搜索 `ax1.axvline(x=..., ...)` 与 `ax1.annotate(...)`，可自由增删时间竖虚线或修改注释文字坐标 `xytext`。

### 4.2 Fig 2 (`plot_fig2_chamber_change_rates.py`)
- **调整滤波窗口**: 位于 `df['dT_smooth'] = df['dT_dt'].rolling(window=7, min_periods=1, center=True).mean()`。如需更平滑的曲线，可增大 `window` 参数（例如改为 11 或 15）。
- **调整纵坐标网格与刻度**: 调整 `ax1.set_ylim(-0.005, 0.035)`。

### 4.3 Fig 3 (`plot_fig3_boundary_interpolation_inset.py`)
- **调整局部放大子图位置与尺寸**:
  ```python
  ax_ins = inset_axes(ax, width="42%", height="40%", loc='lower right',
                      bbox_to_anchor=(0, 0.08, 0.95, 0.95), bbox_transform=ax.transAxes)
  ```
- **调整放大时间区间**: 修改 `sub_mask = (t_fit >= 1800) & (t_fit <= 3600)` 中的时间端点。

### 4.4 Fig 4 (`plot_fig4_chamber_phase_portrait.py`)
- **调整色阶映射 (Colormap)**: 脚本中 `cmap='viridis'`，可根据论文配色需求替换为 `'plasma'`, `'coolwarm'`, `'Spectral'` 等。
- **调整相轨迹箭头密度**: 修改 `arrow_indices = np.linspace(5, len(df)-15, 6, dtype=int)` 中的采样个数。

### 4.5 Fig 5 (`plot_fig5_radius_shrinkage_dynamics.py`)
- **调整收缩动力学关键标注**: 搜索 `ax1.annotate(r'$R(72\\ \\mathrm{h}) = 8.50\\ \\mathrm{mm}$' ...)`，可修改箭头指向位置与文字位移。
- **调整差分求导窗口**: `dr_dt = -np.gradient(r_mm, t_h)`，若需更平滑速率可用样条导数替换。

### 4.6 Fig 6 (`plot_fig6_volume_shrinkage_geometry.py`)
- **调整右侧机理说明文本框**:
  ```python
  desc_box = (
      r"$\\mathbf{Geometric\\ Shrinkage\\ Mechanism:}$" + "\\n"
      r"$\\bullet\\ V(t) = \\pi [R(t)]^2 L$" + "\\n"
      r"$\\bullet\\ L \\gg R_0 \\Rightarrow L \\approx \\mathrm{const}$" + "\\n"
      r"$\\bullet\\ \\frac{V(t)}{V_0} = \\left(\\frac{R(t)}{R_0}\\right)^2$" + "\\n"
      r"$\\bullet\\ \\mathrm{Total\\ Volume\\ Loss} \\approx 67.9\\%$"
  )
  ```
  文本框锚定在 `xytext=(34, 15)`，与右上方图例完美避让无重叠。

### 4.7 Fig 7 (`plot_fig7_problem_timescale_timeline.py`)
- **调整各条目起止时间与颜色**: 修改 `bars` 列表中的元组定义 `(名称, 起始小时, 结束小时, 颜色HEX, 描述字符串)` 即可立即反映在时间轴上。

---

## 5. 输出文件双重备份说明

所有脚本均内置双输出路径机制：
1. **本地工程目录**：`D:\\HIT\\数模2026\\eda_figures\\figX_xxx.png`（供建模本地代码与文档使用）；
2. **Artifact 目录**：`C:\\Users\\kqdx\\.gemini\\antigravity\\brain\\...\\figX_xxx.png`（供对话系统与外部预览器实时展示）。

如果需要将图件嵌入 LaTeX 论文，推荐直接从本工程目录下引用，或在脚本中通过修改 `fig.savefig(..., format='pdf')` 导出矢量 PDF 图件。
"""

GUIDELINES_MD = """# 数学建模论文级可视化规范与后续绘图注意事项指引

> **适用场景**：全国大学生数学建模竞赛 (CUMCM) / 美国大学生数学建模竞赛 (MCM/ICM) 及后续热质传递偏微分方程 (PDE) 仿真模拟与优化控制可视化。  
> **编写目的**：统一全队后续绘图的审美标准、工程复用规范、LaTeX 渲染稳定性与排版防踩坑机制，确保所有图件具备“顶级期刊级”的自明性与观赏性。

---

## 一、 图件设计的核心哲学：自明性与信息层级

### 1.1 何谓“自明性 (Self-Explanatory)”？
- **评委阅卷习惯**：评委在初筛论文时，往往优先浏览**摘要、模型框架图、核心结果曲线与对比图**。
- **合格标准**：评委**完全不读正文上下文**，仅凭“图名 + 坐标轴标签 + 图例 + 关键标注框 (Callout Box)”，就能在 **5~10 秒内**完全读懂：
  1. 这张图测的是什么物理量？
  2. 横纵坐标的尺度与物理单位是什么？
  3. 哪条曲线代表哪个工况/模型？
  4. 图中最关键的结论点（峰值、拐点、收敛点、达标阈值）在哪里？

### 1.2 信息分层三部曲
1. **第一层（骨架）**：清晰平直的坐标轴、向内刻度线 (`direction='in'`)、轻量网格线 (`linestyle='--', alpha=0.5~0.6`)；
2. **第二层（主体）**：主曲线与数据点，线宽充足 (`linewidth=2.0~2.5`)，标记大小适中 (`markersize=5~7`)，颜色具备鲜明区分度；
3. **第三层（灵魂）**：辅助参考线（临界阈值竖虚线、稳态水平渐近线）、关键状态转移箭头、微型公式推导/机理标注框。

---

## 二、 字体与排版规范

### 2.1 中英文字体协调配置
在 Windows 环境下，最稳定的方案是中文采用微软雅黑或黑体，英文字符与数学公式采用 `STIX` 字体集（STIX 与经典学术字体 Times New Roman 风格高度一致）：

```python
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 确保负号正常显示，绝不出现方块或乱码
plt.rcParams['mathtext.fontset'] = 'stix'   # 数学公式使用 STIX 字体，完美契合科技论文
plt.rcParams['xtick.direction'] = 'in'      # 刻度线朝内，符合国际期刊惯例
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['xtick.major.size'] = 4.5      # 主刻度长度
plt.rcParams['ytick.major.size'] = 4.5
plt.rcParams['lines.linewidth'] = 2.0       # 默认加粗曲线，避免打印发虚
```

### 2.2 字号分级规范 (Font Hierarchy)
为保证图件在论文双栏（约 8cm 宽）或单栏（约 14~16cm 宽）排版缩小后依然清晰可辨，字号必须形成严格梯度：

| 元素类型 | 建议字号 (`pt`) | 加粗属性 | 说明 |
| :--- | :---: | :---: | :--- |
| **主标题 (Title)** | 13.0 ~ 14.5 | `fontweight='bold'` | 居中，概括图件核心结论，`pad=12` |
| **坐标轴标签 (Axis Labels)** | 11.5 ~ 12.5 | `fontweight='bold'` | 必须带物理量符号与标准括号单位 |
| **刻度数字 (Tick Labels)** | 9.5 ~ 10.5 | 正常 | 保证 0, 10, 20 等数字清晰 |
| **图例项 (Legend)** | 9.5 ~ 10.5 | 正常 / 粗体 | 带半透明背景 `framealpha=0.9` |
| **标注框/注释 (Annotations)** | 9.0 ~ 10.0 | 粗体或重点加粗 | 指示拐点、稳态值、几何机理 |

---

## 三、 LaTeX 公式渲染与高危“踩坑”红线

### 3.1 字符串转义陷阱：必须全量使用原生字符串 (`r'...'`)
在 Python 解释器中，反斜杠 `\\` 会被优先解析为转义字符：
- `\\r` 会被解析成 **ASCII 回车符 (0x0D)**，导致 `\\rightarrow` 变成 `\\r` + `ightarrow`，破坏整段字符串；
- `\\f` 会被解析成 **换页符 (0x0C)**，导致 `\\frac` 被吞；
- `\\a` 会被解析成 **响铃符 (0x07)**，导致 `\\approx` 报错。

> 🔴 **死命令**：任何包含 LaTeX 符号的字符串，必须且只能写作 `r'$...$'`！即使后面要换行拼接，每一段也必须带 `r` 前缀：
> ```python
> # 正确示范
> label = r'$T_{\\mathrm{env}}(t)\\ (^\circ\\mathrm{C})$'
> # 绝对禁止
> label = '$T_{\\mathrm{env}}(t)\\ (^\circ\\mathrm{C})$'  # 极易隐蔽报错
> ```

### 3.2 Matplotlib MathText 语法限制陷阱
Matplotlib 内置的 mathtext 解析器**并不等同于完整的 LaTeX 编译器**：
- ❌ **不支持** `\\le` 和 `\\ge`（运行必报 `ValueError: Unknown symbol: \\le`）；
- ✅ **必须使用** `\\leq` 和 `\\geq`；
- ❌ **不支持** `\\begin{equation}`、`\\boldsymbol` 等复杂宏包环境；
- ✅ **粗体公式请用** `\\mathbf{...}`。

### 3.3 国际标准单位 (SI Units) 规范排版
- **物理量符号**（变量）：使用斜体数学字母，如 $t$, $T$, $r$, $R$, $C$, $V$；
- **物理单位**：根据国际计量标准，单位**必须使用正体**排版，严禁使用斜体！
  - 错误：`$t (h)$` （$h$ 变成了普朗克常数或高度变量）
  - 正确：`$t\\ (\\mathrm{h})$`、`$\\tau\\ (\\mathrm{s})$`
  - 正确：`$C\\ (\\mathrm{kg/m^3})$`、`$C_{\\mathrm{dry}}\\ (\\mathrm{kg/kg})$`
  - 正确：摄氏度写作 `$T\\ (^\circ\\mathrm{C})$`
- **变量与单位之间留出空格**：使用 `\\ ` 或 `~` 隔开，如 `r'$t\\ (\\mathrm{h})$'`。

---

## 四、 配色哲学与视觉对比度

### 4.1 严禁使用默认纯饱和色
严禁在学术图件中直接使用 Python 默认的 `red`, `blue`, `green`, `yellow`, `cyan`，这类纯色饱和度过高，打印刺眼且缺乏专业质感。

### 4.2 顶级学术与数模推荐色板 (Hex Palette)

| 语义色彩 | HEX 编码 | RGB 视觉感 | 适用场景 |
| :--- | :---: | :---: | :--- |
| **热力红 (Crimson)** | `#C0392B` / `#E74C3C` | 深暖红 / 活力红 | 温度曲线、升温阶段、高温警戒线、问题 1 区间 |
| **海洋蓝 (Ocean Blue)** | `#2980B9` / `#3498DB` | 沉稳纯蓝 | 湿度/水分浓度、冷流体、基准拟合曲线、附件 1 实测 |
| **森林绿 (Emerald)** | `#27AE60` / `#16A085` | 护眼墨绿 | 稳态达成、达标阈值 ($C \\leq 0.15$)、烘干完成时刻 |
| **琥珀橙 (Amber)** | `#D35400` / `#E67E22` | 暖橙 | 变物性阶段、问题 2 区间、温度-水分耦合项 |
| **皇家紫 (Amethyst)** | `#8E44AD` / `#6C3483` | 优雅深紫 | 药材几何尺寸、半径收缩动态、附件 2 长期演变 |
| **高级灰 (Slate Gray)** | `#2C3E50` / `#7F8C8D` | 石板黑灰 | 坐标轴基准、网格虚线、几何辅助推导说明框 |

### 4.3 渐变色系 (Colormap) 选择
- **单调递增/时间演变**：推荐 `'viridis'`（感知均匀，黑白打印仍具备区分度）、`'cividis'`（色盲友好）；
- **发散对比（正负偏差/温差）**：推荐 `'coolwarm'`、`'RdBu_r'`；
- **极端高温/热场云图**：推荐 `'inferno'`、`'magma'`、`'hot'`。

---

## 五、 画面布局与防重叠避让设计

### 5.1 图例与标注避让黄金法则
1. **避让数据密集区**：
   - 曲线大多从左下到右上时，图例置于 `loc='upper left'` 或 `loc='lower right'`；
   - 曲线大多从左上到右下衰减时，图例置于 `loc='upper right'`。
2. **文本框坐标系分离**：
   - 数据标记点采用数据坐标 `xy=(t_val, y_val)`；
   - 文本内容使用偏移坐标 `xytext=(+30, -20)`，搭配 `textcoords='offset points'`，确保无论坐标轴范围如何微调，文字永不遮挡数据点：
   ```python
   ax.annotate(r'$R(72\ \mathrm{h}) = 8.50\ \mathrm{mm}$',
               xy=(72, 8.5), xytext=(-80, 25), textcoords='offset points',
               arrowprops=dict(arrowstyle='->', color='#8E44AD', lw=1.5),
               fontsize=10, fontweight='bold', color='#8E44AD')
   ```

### 5.2 双轴图 (Twinx) 图例合并机制
使用 `ax2 = ax1.twinx()` 时，两个轴各自调用 `ax.legend()` 会在图面左右两端各生成一个图例框，极其丑陋。**必须合并为一个图例**：
```python
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', framealpha=0.9)
```

### 5.3 局部放大图 (Inset Axes) 布局警示
当使用 `mpl_toolkits.axes_grid1.inset_locator.inset_axes` 插入子图时：
- ❌ **严禁调用** `fig.tight_layout()`，这会导致 Matplotlib 抛出 `UserWarning: This figure includes Axes that are not compatible with tight_layout` 并引起子图尺寸畸变；
- ✅ **正确做法**：直接在 `fig.savefig(..., bbox_inches='tight')` 中依靠保存引擎完成边界紧凑裁剪。

---

## 六、 导出分辨率与矢量图件规范

### 6.1 分辨率底线 (DPI)
- **正式论文用图**：必须设置 `dpi=300` 以上；
- **裁剪参数**：必须带 `bbox_inches='tight'`，消除四周多余留白：
  ```python
  fig.savefig('figure.png', dpi=300, bbox_inches='tight')
  ```

### 6.2 矢量图 (PDF / EPS) 导出建议
若建模论文采用 LaTeX 排版（如 CTeX / Overleaf 模板），**位图 (PNG) 缩放后必然出现锯齿，矢量图才是顶级视觉质量的保证**。只需在保存函数中追加一行：
```python
# 同时生成高分辨率位图 (供预览与 Word) 与 矢量图 (供 LaTeX)
fig.savefig('figure.png', dpi=300, bbox_inches='tight')
fig.savefig('figure.pdf', bbox_inches='tight')  # 无限放大无锯齿
```

---

## 七、 面向后续建模任务（问题 1 ~ 4）的专业绘图指引

在完成初期数据探索 (EDA) 后，后续求解偏微分方程与参数反演时，需遵循以下专门建议：

### 7.1 问题 1 & 2：径向分布场 $T(r, t)$ 与 $C(r, t)$
- **切片曲线对比图**：选取典型时刻（如 $t = 5, 10, 20, 30\\,\\mathrm{min}$），横轴为无量纲半径 $r/R$，纵轴为温度或含水率，展示从外表向圆心的内传波形；
- **时空二维等高线热力图 (Contourf / pcolormesh)**：横轴时间 $t$，纵轴半径 $r$，颜色表示物理场强，直观展示热渗透层与干燥锋面的推进。

### 7.2 问题 3：动边界收缩与移动网格 (ALE / Landau 变换)
- **物理网格示意图**：绘制一维柱坐标网格随时间逐渐向内挤压收缩的动态网格示意图；
- **动边界与固定边界误差对比**：将“考虑收缩”与“忽略收缩”的含水率衰减曲线画在同一图中，用阴影区域标出收缩效应带来的脱水速率加速增益。

### 7.3 问题 4：烘干策略优化与能耗帕累托前沿 (Pareto Front)
- **多阶段烘干曲线阶梯图**：展示分段阶梯升温控湿曲线；
- **目标权衡散点图**：横轴为烘干总耗时 $t_{\\mathrm{final}}$，纵轴为能耗 $E$，绘制多目标遗传算法 (NSGA-II) 或强化学习的 Pareto 前沿解集，标出最优折中点。
"""

with open(os.path.join(EDA_DIR, "README.md"), "w", encoding="utf-8") as f:
    f.write(README_MD.strip() + "\n")

with open(os.path.join(EDA_DIR, "绘图注意事项与规范指引.md"), "w", encoding="utf-8") as f:
    f.write(GUIDELINES_MD.strip() + "\n")

print("[SUCCESS] README.md and 绘图注意事项与规范指引.md created cleanly!")
