# 竞赛论文 LaTeX 完整工程 (LaTeX Paper Project)

本目录为 2026 年高教社杯全国大学生数学建模竞赛 A 题的完整 LaTeX 排版工程。论文最终编译生成共计 **19 页**的高水平学术论文终稿，严格遵循全国组委会格式规范与视觉呈现标准。

---

## 最终论文成果

* **论文题目**：《中药材热风烘干过程的传热传质建模与烘干时长预测》
* **论文终稿 PDF**：
  * 本目录入口：[`main.pdf`](main.pdf)（8.42 MB）
  * 仓库根目录直达：[`../2026_CUMCM_Problem_A_Final_Paper.pdf`](../2026_CUMCM_Problem_A_Final_Paper.pdf)
* **核心内容概览**：
  * **摘要**：精炼提炼 FVM 二维轴对称微元离散、变阶自适应 BDF 积分、PCHIP 气象延拓及移动网格四大机理创新，给出各问高精度定量预测值。
  * **正文六大节**：问题重述、问题分析、模型假设、符号系统、数据分析与基础模型、模型建立与逐问求解。
  * **验证体系**：网格收敛性验证（$60\times 60 \to 160\times 160$）、时间离散瞬时守恒性校验、环境外推参数敏感性分析。
  * **附录**：支撑材料清单、数据补充表格、主要 Python 计算源程序、AI 工具规范使用说明。

---

## 论文目录架构

```text
paper/
├── main.tex                    # 论文排版总主控文件（引入宏包、各分章源码与附录）
├── main.pdf                    # 编译成型的 19 页最终提交论文 PDF
├── cumcm2026.sty               # 2026 年国赛排版样式定制宏包
├── cumcmthesis.cls             # 国赛论文专业文档类（版心、字号、标题定制）
├── references.bib              # BibTeX 格式参考文献元数据库
│
├── sections/                   # 论文正文各章节模块源码
│   ├── 00_abstract.tex         # 标题、摘要与关键词
│   ├── 01_problem_restatement.tex # 问题重述（背景、意义、四个核心求解任务）
│   ├── 02_problem_analysis.tex # 逐问机理与数学难点深入剖析
│   ├── 03_model_assumptions.tex # 基础假设与简化合理性论证
│   ├── 04_symbols.tex          # 全局核心物理与数学符号定义表
│   ├── 05_data_processing.tex  # 实验数据清洗与平滑插值处理
│   ├── 06_model_establishment_and_solution.tex # 核心建模与四问求解（400+ 行推导与论述）
│   ├── 07_model_evaluation.tex # 模型优缺点评价、灵敏度分析与推广价值
│   └── 08_references.tex       # 参考文献引用导入
│
├── tables/                     # 自动化生成的各问数据 LaTeX 表格代码
│   ├── q1-grid.tex             # 问题一网格独立性验证误差收敛表
│   ├── q1-temperature.tex      # 问题一特定时刻中部截面温度分布表
│   ├── q1-moisture.tex         # 问题一特定时刻中部截面干基含水率分布表
│   ├── q2-temperature.tex      # 问题二前 3 小时中部截面温度分布表
│   ├── q2-moisture.tex         # 问题二前 3 小时中部截面含水率分布表
│   ├── q3-moisture.tex         # 问题三全域干燥达标长时程演变表
│   └── q4-moisture.tex         # 问题四径向收缩工况下含水率与外径演化表
│
├── figures/                    # 论文排版嵌入的高清图件（自动与 figures/ 保持同步）
├── appendices/                 # 附录 A~D（支撑材料、补充数据、程序清单、AI使用声明）
├── scripts/                    # 表格自动化生成辅助工具
│   └── extract_paper_tables.py # 从计算生成的 Excel 中自动化提取 tables/*.tex 的工具脚本
│
└── 历史文档打磨记录/             # 论文写作全生命周期版本迭代库（全部 39 份 Markdown，含审阅批注）
```

---

## 编译与自动化构建

### 1. 自动化提取数据表格
若更新了数值模拟结果，可首先执行提取脚本：
```bash
python scripts/extract_paper_tables.py
```

### 2. XeLaTeX 标准三步编译
进入 `paper/` 目录，依次调用 XeLaTeX 与 BibTeX：
```bash
xelatex -synctex=1 -interaction=nonstopmode main.tex
bibtex main.aux
xelatex -synctex=1 -interaction=nonstopmode main.tex
xelatex -synctex=1 -interaction=nonstopmode main.tex
```
编译成功后即可更新生成高质量 `main.pdf`。
