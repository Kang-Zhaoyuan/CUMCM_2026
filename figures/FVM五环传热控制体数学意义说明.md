# 有限体积法 (FVM) 宏微观多尺度传热控制体数学意义与建模解析

> **对应正式图件**：[`eda_figures/fvm_multiscale_macro_micro.png`](./fvm_multiscale_macro_micro.png) （300 DPI 印刷级）  
> **专属复现脚本**：[`eda_figures/scripts/plot_fvm_multiscale_macro_micro.py`](./scripts/plot_fvm_multiscale_macro_micro.py)  
> **建议论文章节**：论文第 4 节《传热与水分迁移机理建模 —— 偏微分方程的有限体积法 (FVM) 空间离散与微元拓扑》

---

## 1. 宏微观多尺度耦合架构与几何拓扑概述

本图针对圆柱体物料（中药材）在变温变湿烘房环境下的非稳态热湿耦合传递过程，构建了一套**宏观圆柱全域网格化 $\leftrightarrow$ 微观有限体积局部控制体拓扑**的跨尺度关联图景。整图采用国际顶刊（Nature / Science / ASME）通行的局部放大范式，直观揭示了连续介质力学偏微分方程如何转化为代数守恒系统的全过程。

```text
┌─────────────────────────────────┐           ┌──────────────────────────────────────────────┐
│  宏观尺度 (Macro Scale)         │           │  微观尺度 (Micro Scale)                      │
│  - 柱坐标系 (r, theta, z)       │  虚线透射 │  - 有限体积法 (FVM) 5 环控制体拓扑           │
│  - 几何全域 3D 透视圆柱         │ ────────> │  - 中心单元 (i,j) 及其 4 邻域 (E, W, N, S)   │
│  - 径向/轴向结构化网格线        │ (局域微元)│  - 四向热通量 Q 矢量流动 (守恒界面面积分)    │
│  - 红色细环: 目标计算物料环     │           │  - 特征物理几何尺度: Delta r, Delta z        │
└─────────────────────────────────┘           └──────────────────────────────────────────────┘
```

### 1.1 左侧宏观尺度：柱坐标全域几何与空间网格
1. **坐标系基准**：
   - 轴向基准 $+z$：沿物料中心轴垂直向上，范围 $z \in [0, L]$（或取中心对称面为 $z=0$）；
   - 径向基准 $+r$：自中心轴水平指向外圆柱面，范围 $r \in [0, R(t)]$；
   - 坐标轴均采用 LaTeX 规范数学斜体 $z$ 与 $r$，箭头具备立体光影倒角。
2. **三维透视网格系统**：
   - 柱面经纬线直观展示了三维空间的结构化网格剖分；
   - 顶面由连续闭合实线椭圆勾勒，底面配合空间遮挡采用虚实交替线，严格遵循三维投影透视几何学规范。
3. **目标计算薄环（红色环元）**：
   - 在物料内部 $z = z_j$ 高度处，高亮标出一个厚度微薄的红色物料环；
   - 红色圆环在宏观上代表空间离散后的一个圆环层，其中心半径为 $r_i$、径向厚度为 $\Delta r$、轴向高度为 $\Delta z$。
4. **局部微元取景框 (Viewfinder Overlay)**：
   - 采用棱角分明、黑色实线的纯二维矩形框，精准框选红色圆环右侧边缘的一小段微元；
   - **几何物理意义**：该微元对应于沿周向角展开的 $\Delta \theta$ 柱坐标扇形微元（$\mathrm{d}V = r \, \mathrm{d}r \, \mathrm{d}\theta \, \mathrm{d}z$）。

### 1.2 中间过渡层：经典对角虚线透射
- 严格遵循火山图 (Volcano Plot) 与经典工程图学的局部放大规范；
- 彻底摒弃遮挡视线的色块或半透明光锥，仅使用两条纯黑细虚线将取景框的右上角、右下角对角投射至右图卡片的左上角、左下角；
- 透视开角约为 $45^\circ \sim 50^\circ$，形成舒展大气的几何放大对应关系。

### 1.3 右侧微观尺度：五环有限体积控制体拓扑
- **棱角分明的黑色矩形外框**：白底学术卡片，增强独立聚焦感；
- **中心母环单元 $(i, j)$**：加粗纯黑闭合多边形框，代表求解的核心控制体 $P$；
- **四邻域拓扑单元**：
  1. **内环 (West 面)**：单元 $(i-1, j)$，朝向对称中心轴 $r=0$；
  2. **外环 (East 面)**：单元 $(i+1, j)$，朝向外圆柱受热面 $r=R$；
  3. **远环 (North 面)**：单元 $(i, j+1)$，朝向端面换热面 $z=L/2$；
  4. **近环 (South 面)**：单元 $(i, j-1)$，朝向轴向对称中截面 $z=0$；
- **四向热通量矢量 $Q$**：鲜艳红色渐变喇叭口矢量箭头，表征界面传热强度与流动方向；
- **尺寸标注与局部坐标基准**：
  - $\Delta r$ 与 $\Delta z$：工程制图级共线引出线与双向尺度箭头；
  - 左下角立体坐标轴：$+z$ 轴与扇形底面 $+r$ 轴。

---

## 2. 连续传热偏微分方程与二维轴对称简化

圆柱物料内部的非稳态变物性热传导控制方程为：
$$\rho(C) c_p(C) \frac{\partial T}{\partial t} = \nabla \cdot \big( k(C) \nabla T \big) + \dot{q}_v$$

式中：
- $\rho(C)$ 为含水物料的表观干湿密度 $(\mathrm{kg/m^3})$；
- $c_p(C)$ 为等效定压比热容 $(\mathrm{J/(kg\cdot K)})$；
- $k(C)$ 为物料等效热导率 $(\mathrm{W/(m\cdot K)})$；
- $\dot{q}_v$ 为水分汽化潜热相变内热源项 $(\mathrm{W/m^3})$，$\dot{q}_v = -h_{fg} \dot{m}'''_{vap}$。

### 2.1 二维轴对称假设的物理合理性
由于烘房内的气流在宏观上包覆整个圆柱物料，周向温湿度分布具备高度均匀性，可合理引入**周向均一性假设**：
$$\frac{\partial (\cdot)}{\partial \theta} \equiv 0$$
在柱坐标系 $(r, \theta, z)$ 下，拉普拉斯算子展开为二维形式：
$$\rho(C) c_p(C) \frac{\partial T}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left( r k(C) \frac{\partial T}{\partial r} \right) + \frac{\partial}{\partial z}\left( k(C) \frac{\partial T}{\partial z} \right) + \dot{q}_v$$

物理求解域简化为纵向对称半截面：
$$\Omega = \left\{ (r, z) \mid 0 \le r \le R(t), \; 0 \le z \le \frac{L}{2} \right\}$$

### 2.2 耦合边界条件体系
1. **外圆柱面对流与辐射换热面 ($r = R(t)$)**：
   $$-k(C) \left. \frac{\partial T}{\partial r} \right|_{r=R} = h_r \big( T_s - T_{\mathrm{env}}(t) \big) + \varepsilon \sigma \big( T_s^4 - T_{\mathrm{env}}^4(t) \big) + \dot{m}''_s h_{fg}$$
2. **中心对称轴 ($r = 0$)**：
   $$\left. \frac{\partial T}{\partial r} \right|_{r=0} = 0 \quad (\text{自然对称绝热条件})$$
3. **端部换热面 ($z = L/2$)**：
   $$-k(C) \left. \frac{\partial T}{\partial z} \right|_{z=L/2} = h_z \big( T_{\text{end}} - T_{\mathrm{env}}(t) \big)$$
4. **中心对称中截面 ($z = 0$)**：
   $$\left. \frac{\partial T}{\partial z} \right|_{z=0} = 0 \quad (\text{几何对称边界})$$

---

## 3. 高斯散度定理与有限体积法 (FVM) 空间积分转化

### 3.1 积分形式转化
在有限体积法中，直接对控制体单元 $V_{i,j}$ 两端施加三维空间体积分：
$$\int_{V_{i,j}} \rho c_p \frac{\partial T}{\partial t} \, \mathrm{d}V = \int_{V_{i,j}} \nabla \cdot \big( k \nabla T \big) \, \mathrm{d}V + \int_{V_{i,j}} \dot{q}_v \, \mathrm{d}V$$

应用**高斯散度定理 (Gauss Divergence Theorem)**，将二阶空间偏导项的体积分严格转化为闭合控制体外表面 $\partial V_{i,j}$ 的通量面积分：
$$\int_{V_{i,j}} \nabla \cdot \big( k \nabla T \big) \, \mathrm{d}V = \oint_{\partial V_{i,j}} \big( k \nabla T \big) \cdot \boldsymbol{n} \, \mathrm{d}S = \sum_{f \in \{E, W, N, S\}} \int_{A_f} \boldsymbol{q}_f \cdot (-\boldsymbol{n}_f) \, \mathrm{d}S$$

式中：
- $\boldsymbol{n}_f$ 为边界面 $f$ 的外法向单位向量；
- $\boldsymbol{q}_f = -k \nabla T$ 为傅里叶导热热通量密度矢量 $(\mathrm{W/m^2})$。

假定单元内物理量为网格中心平均值，即得常微分方程系统：
$$V_{i,j} \rho_{i,j} c_{p,\, i,j} \frac{\mathrm{d}T_{i,j}}{\mathrm{d}t} = Q_{i+1/2,\, j} - Q_{i-1/2,\, j} + Q_{i,\, j+1/2} - Q_{i,\, j-1/2} + \dot{q}_{v,\, i,j} V_{i,j}$$

> **FVM 相对 FDM/FEM 的核心学术优势**：
> 1. **局部与全局绝对守恒性**：在相邻控制体（例如母环与外环）交界面上，外环流出的热量在代数表达式上与母环流入的热量符号相反、绝对值恒等（$Q_{E \to P} \equiv - Q_{P \to E}$）。因此，对全域所有控制体求和时，所有内部界面的通量严格对消，不会因截断误差产生任何虚假数值热源或能量漂移；
> 2. **天然适应变物性与强间断**：物料干湿界面、相变前沿处物性发生突变时，FVM 无需连续性光滑假设即可维持稳定求解。

---

## 4. 几何度量体系与尺寸标注的数学解析

### 4.1 几何尺寸标注：$\Delta r$ 与 $\Delta z$
- **径向控制体厚度 $\Delta r$**（标注于近环底部边界）：
  $$\Delta r_i = r_{i+1/2} - r_{i-1/2}$$
- **轴向控制体高度 $\Delta z$**（标注于外环外侧边界）：
  $$\Delta z_j = z_{j+1/2} - z_{j-1/2}$$

为了精准捕捉边界处极高温度梯度并优化内部计算效率，网格采用非均匀二次多项式加密：
$$r_i = R(t) \left[ 1 - \left( 1 - \frac{i}{N_r} \right)^2 \right], \quad z_j = \frac{L}{2} \left[ 1 - \left( 1 - \frac{j}{N_z} \right)^2 \right]$$

### 4.2 柱坐标控制体几何度量公式
对于旋转对称的圆环形控制体，其物理体积为：
$$V_{i,j} = \int_{z_{j-1/2}}^{z_{j+1/2}} \mathrm{d}z \int_{0}^{2\pi} \mathrm{d}\theta \int_{r_{i-1/2}}^{r_{i+1/2}} r \, \mathrm{d}r = \pi \left( r_{i+1/2}^2 - r_{i-1/2}^2 \right) \Delta z_j = 2\pi \, r_i \, \Delta r_i \, \Delta z_j$$
*(注：若按周向切片 $\Delta \theta$ 计算，则两端同时乘以 $\frac{\Delta \theta}{2\pi}$，代数关系完全保形)*

各界面的有效换热面积为：
- **径向外界面 ($A_{i+1/2,\, j}$, East 面)**：$A_{i+1/2,\, j} = 2\pi \, r_{i+1/2} \, \Delta z_j$ （面积随半径增大而扩大）
- **径向内界面 ($A_{i-1/2,\, j}$, West 面)**：$A_{i-1/2,\, j} = 2\pi \, r_{i-1/2} \, \Delta z_j$
- **轴向高位面 ($A_{i,\, j+1/2}$, North 面)**：$A_{i,\, j+1/2} = \pi \left( r_{i+1/2}^2 - r_{i-1/2}^2 \right)$
- **轴向低位面 ($A_{i,\, j-1/2}$, South 面)**：$A_{i,\, j-1/2} = \pi \left( r_{i+1/2}^2 - r_{i-1/2}^2 \right)$

---

## 5. 四向热通量 $Q$ 的物理内涵与界面重构

图中四个红色的空间立体喇叭口渐变矢量分别定量表征穿过四个控制体边界面流向中心母环的总热导率通量 $(\mathrm{W})$：

### 5.1 界面物性的调和平均重构 (Harmonic Mean)
在界面处，热导率采用**调和平均 (Harmonic Mean)** 方式重构（与电学中电阻串联法则等价），确保在非均质界面的热流密度连续性：
$$k_{i+1/2,\, j} = \frac{2 \, k_{i,j} \, k_{i+1,j}}{k_{i,j} + k_{i+1,j}}$$

### 5.2 各向热通量的严谨数学离散表达式

1. **径向外侧流入通量 $Q_{i+1/2,\, j}$ (East 面)**：
   - **物理方向**：外环向中心母环传热；
   - **离散公式**：
     $$Q_{i+1/2,\, j} = k_{i+1/2,\, j} \cdot A_{i+1/2,\, j} \cdot \left( \frac{T_{i+1,\, j} - T_{i,\, j}}{r_{i+1} - r_i} \right)$$
   - **柱坐标几何效应**：$A_{i+1/2,\, j} > A_{i-1/2,\, j}$，体现了圆柱几何中“外侧受热面积大、向内聚拢热流汇聚”的柱几何收缩效应。

2. **径向内侧流出通量 $Q_{i-1/2,\, j}$ (West 面)**：
   - **物理方向**：中心母环向更内侧内环传热；
   - **离散公式**：
     $$Q_{i-1/2,\, j} = k_{i-1/2,\, j} \cdot A_{i-1/2,\, j} \cdot \left( \frac{T_{i,\, j} - T_{i-1,\, j}}{r_i - r_{i-1}} \right)$$

3. **轴向高位流入通量 $Q_{i,\, j+1/2}$ (North 面)**：
   - **物理方向**：远端高温端面沿轴向向下向母环传热；
   - **离散公式**：
     $$Q_{i,\, j+1/2} = k_{i,\, j+1/2} \cdot A_{i,\, j+1/2} \cdot \left( \frac{T_{i,\, j+1} - T_{i,\, j}}{z_{j+1} - z_j} \right)$$

4. **轴向低位流出通量 $Q_{i,\, j-1/2}$ (South 面)**：
   - **物理方向**：母环向中心中截面方向传热；
   - **离散公式**：
     $$Q_{i,\, j-1/2} = k_{i,\, j-1/2} \cdot A_{i,\, j-1/2} \cdot \left( \frac{T_{i,\, j} - T_{i,\, j-1}}{z_j - z_{j-1}} \right)$$

---

## 6. 控制方程的常微分动力学系统与数值算法

将各界面的热通量综合代入，得到中心母环 $(i, j)$ 的温度演化方程：
$$\frac{\mathrm{d}T_{i,j}}{\mathrm{d}t} = \frac{1}{\rho_{i,j} c_{p,\, i,j} V_{i,j}} \left[ Q_{i+1/2,\, j} - Q_{i-1/2,\, j} + Q_{i,\, j+1/2} - Q_{i,\, j-1/2} + \dot{q}_{v,\, i,j} V_{i,j} \right]$$

在全空间维度堆叠为向量 $\boldsymbol{T} \in \mathbb{R}^{N_r \times N_z}$，方程化为大型非线性刚性常微分方程组：
$$\mathbf{M}(\boldsymbol{C}) \frac{\mathrm{d}\boldsymbol{T}}{\mathrm{d}t} = \mathbf{K}(\boldsymbol{C}, \boldsymbol{T})\boldsymbol{T} + \boldsymbol{F}_{\mathrm{bc}}(t)$$

式中：
- $\mathbf{M}$ 为非线性质量对角矩阵；
- $\mathbf{K}$ 为具备五对角（五环稀疏）结构的导热刚度矩阵；
- $\boldsymbol{F}_{\mathrm{bc}}(t)$ 为引入外界烘房温湿度时变边界的激励向量。

时域推进算法采用具备 A-稳定性的**高阶隐式后向差分公式 (BDF-2 / BDF-3)** 或 **Radau IIA 算法**，配合动网格坐标变换，实现动边界收缩条件下的高精度自适应时间步进求解。

---

## 7. 竞赛论文级图题与正文嵌入规范 (Publication-Ready)

### 7.1 论文图题推荐 (Figure Caption)

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=\textwidth]{eda_figures/fvm_multiscale_macro_micro.png}
  \caption{有限体积法 (FVM) 宏微观跨尺度传热机理与空间控制体热通量拓扑图
  \newline \small (左侧展示柱坐标系 $(r,\theta,z)$ 下圆柱物料全域三维透视网格剖分与计算微元取景定位；中间经双虚线投射局部放大；右侧直角卡片详细展示五环控制体单元 $(i,j)$ 拓扑结构、四向热传导通量 $Q$ 矢量流动与局部特征尺寸 $\Delta r,\Delta z$。)}
  \label{fig:fvm_multiscale}
\end{figure}
```

### 7.2 论文正文嵌入叙述范例 (可直接植入第 4 节)

> 为了兼顾宏观圆柱几何边界与局部非线性相变导热的高精度求解，本文基于有限体积法 (Finite Volume Method, FVM) 建立了二维轴对称跨尺度传热模型（如图 \ref{fig:fvm_multiscale} 所示）。
> 宏观上，物料求解域在柱坐标系 $(r, \theta, z)$ 下被离散为结构化空间网格，高亮红色圆环表示位于高度 $z_j$、半径 $r_i$ 处的局部物料层。利用局部取景视窗提取其右侧微元，投射展开为局域五环控制体拓扑。
> 在微观尺度下，以加粗黑色矩形标识的中心母环单元 $(i,j)$ 为守恒积分基元，外界对流传入的热量通过外表面通量 $Q_{i+1/2,\, j}$ 向内汇聚，同时沿径向向内芯传递 ($Q_{i-1/2,\, j}$)，并在轴向上与相邻两层单元进行纵向导热交互 ($Q_{i,\, j\pm 1/2}$)。得益于 FVM 的闭合边界面通量连续性，相邻单元间的热量交换在离散代数方程中天然满足守恒定律，为后续求解动边界、强非线性热湿迁移方程组提供了无虚假数值振荡的坚实数学物理基础。
