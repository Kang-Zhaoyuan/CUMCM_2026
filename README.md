# 2026 CUMCM Problem A: Coupled Heat and Mass Transfer Modeling and Drying Time Prediction for Cylindrical Porous Media

本项目为 2026 年高教社杯全国大学生数学建模竞赛 A 题（中药材热风烘干过程热质耦合传输与控制优化）的完整数值求解、学术可视化与 LaTeX 论文工程。

---

## 成果直达

* **论文终稿 PDF (19 页全篇)**：[`2026_CUMCM_Problem_A_Final_Paper.pdf`](2026_CUMCM_Problem_A_Final_Paper.pdf)
* **LaTeX 源码主入口**：[`paper/main.tex`](paper/main.tex)
* **数值结果工作簿**：[`code/results/`](code/results/) (`result1.xlsx` ~ `result4.xlsx`)
* **总体机理设计蓝图**：[`整体答案思路.md`](整体答案思路.md) / [`整体答案思路.pdf`](整体答案思路.pdf)

---

## 物理机理与数值方法概要

1. **控制方程**：
   柱坐标系二维轴对称非稳态热质耦合偏微分方程组。温度场 $T(r,z,t)$ 与干基含水率场 $C(r,z,t)$ 满足局部能量与组分质量守恒：
   $$\rho(C) c_p(C) \frac{\partial T}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(r k(C) \frac{\partial T}{\partial r}\right) + \frac{\partial}{\partial z}\left(k(C) \frac{\partial T}{\partial z}\right)$$
   $$\frac{\partial C}{\partial t} = \frac{1}{r}\frac{\partial}{\partial r}\left(r D_m(C) \frac{\partial C}{\partial r}\right) + \frac{\partial}{\partial z}\left(D_m(C) \frac{\partial C}{\partial z}\right)$$
   物性参数随局部含水率非线性演变，水分有效扩散系数 $D_m(C)$ 采用分段经验本构。

2. **空间离散 (FVM)**：
   采用微元网格中心有限体积法（Finite Volume Method）。计算域利用对称性取 $r \in [0, R(t)]$ 与半长 $z \in [0, L/2]$。网格规模 $N_r = 120, N_z = 120$，径向设置非均匀拉伸因子 $\text{stretch}=2.0$，外边界加密以精确捕捉对流传质陡峭梯度。

3. **时间积分 (BDF)**：
   变物性非线性离散产生高维刚性常微分方程组（联合自由度 29,282）。使用变阶自适应步长后向差分公式（BDF）结合稀疏 Jacobian 解析装配进行时间推进（相对容差 $10^{-7}$，绝对容差 $10^{-9}$）。

4. **边界条件与几何收缩**：
   * 外表面满足非线性 Robin 传热传质对流边界条件。环境温湿度由附件1实验数据经单调保形三次 Hermite 插值（PCHIP）平滑驱动；4 小时后采用末尾 20 点成对算术平均延拓。
   * 问题四引入移动边界网格（Moving Boundary Mesh），根据附件2实测径向收缩动力学建立坐标微分映射，消除固定边界对干燥终点的低估效应。

5. **核心定量预测结论**：
   * 全域干燥判定准则：$\max_{r,z} C(r,z,t) \le 0.15\ \mathrm{kg/kg}$。
   * 固定几何（问题三）全域干燥达标时间：$t^* \approx 57.44\ \mathrm{h}$。
   * 动态收缩几何（问题四）全域干燥达标时间：$t^* \approx 53.62\ \mathrm{h}$。

---

## 论文章节源码检索

| 章节 | 标题 | LaTeX 源文件 | 内容摘要 |
| :--- | :--- | :--- | :--- |
| 摘要 | 题目、摘要与关键词 | [`paper/sections/00_abstract.tex`](paper/sections/00_abstract.tex) | FVM离散、BDF积分、PCHIP延拓、动网格收缩机制与定量结果 |
| 第 1 节 | 问题重述 | [`paper/sections/01_problem_restatement.tex`](paper/sections/01_problem_restatement.tex) | 热风干燥工艺背景、四项求解任务与物理约束定义 |
| 第 2 节 | 问题分析 | [`paper/sections/02_problem_analysis.tex`](paper/sections/02_problem_analysis.tex) | 传热传质时空多尺度耦合剖析与分步求解策略 |
| 第 3 节 | 模型假设 | [`paper/sections/03_model_assumptions.tex`](paper/sections/03_model_assumptions.tex) | 轴对称性、各向同性、对流边界条件合理性论证 |
| 第 4 节 | 符号说明 | [`paper/sections/04_symbols.tex`](paper/sections/04_symbols.tex) | 核心变量、物性参数、物理单位与几何记号定义 |
| 第 5 节 | 数据分析与基础模型 | [`paper/sections/05_data_processing.tex`](paper/sections/05_data_processing.tex) | 附件1温湿度数据处理、PCHIP单调插值平滑性证明 |
| 第 6 节 | 模型的建立与求解 | [`paper/sections/06_model_establishment_and_solution.tex`](paper/sections/06_model_establishment_and_solution.tex) | FVM微元离散推导、Jacobian装配、四问求解与收敛性验证 |
| 第 7 节 | 模型评价与改进 | [`paper/sections/07_model_evaluation.tex`](paper/sections/07_model_evaluation.tex) | 瞬时通量守恒校验、网格独立性分析（60~160）、参数敏感性 |
| 第 8 节 | 参考文献 | [`paper/sections/08_references.tex`](paper/sections/08_references.tex) | 文献引用列表 |
| 附录 | 支撑材料与程序 | [`paper/appendices/`](paper/appendices/) | 计算代码清单、数据补充表格与 AI 工具合规使用声明 |

---

## 复现运行命令

```bash
# 1. 数值求解与结果导出
cd code
pip install -r requirements.txt
python Problem1.py --nr 120 --nz 120 --stretch 2.0 --output results/result1.xlsx
python Problem2.py --nr 120 --nz 120 --stretch 2.0 --output results/result2.xlsx
python Problem3.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result3.xlsx
python Problem4.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result4.xlsx
python checkConservation.py

# 2. 论文图件与表格生成
cd ../figures && python scripts/run_all.py
cd ../paper && python scripts/extract_paper_tables.py

# 3. 论文编译 (XeLaTeX)
xelatex -interaction=nonstopmode main.tex
bibtex main.aux
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```
