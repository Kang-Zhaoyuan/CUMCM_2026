# CUMCM 2026 Problem A / 2026年全国大学生数学建模竞赛 A题

Coupled Heat and Mass Transfer Modeling for Porous Media Drying / 中药材热风烘干过程热质耦合传输建模与仿真

---

## 核心成果 / Primary Deliverables

* **论文终稿 / Final Manuscript**：[`2026_CUMCM_Problem_A_Final_Paper.pdf`](2026_CUMCM_Problem_A_Final_Paper.pdf) (19 Pages / 完整 19 页)
* **总体技术路线 / Methodology Blueprint**：[`整体答案思路.md`](整体答案思路.md) | [`整体答案思路.pdf`](整体答案思路.pdf)
* **计算结果工作簿 / Numerical Solution Workbooks**：[`code/results/`](code/results/) (`result1.xlsx` ~ `result4.xlsx`)

---

## 模块导航 / Repository Navigation

| 目录 / Directory | 说明 / Description (CN) | Description (EN) |
| :--- | :--- | :--- |
| [`paper/`](paper/) | LaTeX 排版工程（主源码 `main.tex`、各分章源码、数据表格及 39 份历史 Markdown 打磨版本） | LaTeX manuscript source (`main.tex`), section files, tables, and 39 historical markdown drafts with peer review notes. |
| [`code/`](code/) | 有限体积法（FVM）数值求解器（`Problem1~4.py`、`grid.py`、守恒性校验 `checkConservation.py` 及输出表格） | Finite Volume Method (FVM) solvers (`Problem1~4.py`, `grid.py`, `checkConservation.py`) and numerical output workbooks. |
| [`figures/`](figures/) | 论文正式图件、自动化绘图脚本库（`scripts/`）、极坐标展开披萨图（`Fig_Ref/`）及草稿归档（`Archive/`） | Publication-grade figures, automated plotting scripts (`scripts/`), polar pizza plots (`Fig_Ref/`), and draft archives (`Archive/`). |
| [`problem/`](problem/) | 官方赛题文档（`A题.pdf`、纯文本提取）及原始实验数据集（烘房温湿度、尺寸收缩测量、提交模板） | Official problem description (`A题.pdf`, text extract) and raw experimental datasets (chamber conditions, shrinkage measurements, templates). |
| [`references/`](references/) | 11 篇支撑学术文献（干燥动力学、收缩本构、PCHIP 单调插值、刚性 ODE 求解）与引用元数据 | 11 reference papers covering drying kinetics, shrinkage mechanics, PCHIP interpolation, and stiff ODE integration. |

---

## 复现指令 / Quickstart

```bash
# 1. 数值求解 / Run numerical simulations
cd code
pip install -r requirements.txt
python Problem1.py --output results/result1.xlsx
python Problem2.py --output results/result2.xlsx
python Problem3.py --output results/result3.xlsx
python Problem4.py --output results/result4.xlsx

# 2. 编译论文 / Compile LaTeX manuscript (XeLaTeX + BibTeX)
cd ../paper
xelatex -interaction=nonstopmode main.tex
bibtex main.aux
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```
