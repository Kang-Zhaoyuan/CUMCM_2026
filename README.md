# 2026年全国大学生数学建模竞赛（CUMCM）A题解决方案

本项目为 2026 年高教社杯全国大学生数学建模竞赛 A 题（中药材热风烘干过程热质耦合传输与控制优化）的完整工程与学术资料归档。工程涵盖原始赛题与实验数据、有限体积数值求解器、出版级学术图件工程、19 页最终提交论文及全生命周期打磨演进记录。

---

## 论文终稿与章节导航

最终提交论文（完整 19 页，包含完整理论推导、高精度图件、数据表格及代码附录）已编译完毕并直接置于项目根目录：

* **论文 PDF 终稿文件**：[`2026_CUMCM_Problem_A_Final_Paper.pdf`](2026_CUMCM_Problem_A_Final_Paper.pdf)
* **LaTeX 源码入口**：[`paper/main.tex`](paper/main.tex)
* **排版输出镜像**：[`paper/main.pdf`](paper/main.pdf)

### 论文章节源码检索
| 章节 | 标题 | 源文件 | 核心内容摘要 |
| :--- | :--- | :--- | :--- |
| 摘要 | 题目、摘要与关键词 | [`paper/sections/00_abstract.tex`](paper/sections/00_abstract.tex) | FVM空间离散、BDF时间积分、PCHIP气象延拓及移动网格方法与定量预测值 |
| 第 1 节 | 问题重述 | [`paper/sections/01_problem_restatement.tex`](paper/sections/01_problem_restatement.tex) | 中药材热风烘干工艺背景、四项核心求解任务说明 |
| 第 2 节 | 问题分析 | [`paper/sections/02_problem_analysis.tex`](paper/sections/02_problem_analysis.tex) | 热质双向耦合机理剖析与求解策略设计 |
| 第 3 节 | 模型假设 | [`paper/sections/03_model_assumptions.tex`](paper/sections/03_model_assumptions.tex) | 轴对称几何、均匀各向同性及 Robin 边界合理性论证 |
| 第 4 节 | 符号说明 | [`paper/sections/04_symbols.tex`](paper/sections/04_symbols.tex) | 全局物理量、单位与几何参量定义表 |
| 第 5 节 | 数据分析与基础模型 | [`paper/sections/05_data_processing.tex`](paper/sections/05_data_processing.tex) | 附件1温湿度实验数据清洗与平滑插值处理 |
| 第 6 节 | 模型的建立与求解 | [`paper/sections/06_model_establishment_and_solution.tex`](paper/sections/06_model_establishment_and_solution.tex) | FVM有限体积空间微元离散、四问求解展开与结果论述 |
| 第 7 节 | 模型评价与改进 | [`paper/sections/07_model_evaluation.tex`](paper/sections/07_model_evaluation.tex) | 格式自洽性检验、网格收敛性验证、优缺点评估与推广 |
| 第 8 节 | 参考文献 | [`paper/sections/08_references.tex`](paper/sections/08_references.tex) | 参考文献引用列表 |
| 附录 | 支撑材料与程序 | [`paper/appendices/`](paper/appendices/) | 包含计算代码清单与 AI 工具规范使用说明声明 |

### 最终计算结果数据检索
各问生成的标准化填报表格存储于 [`code/results/`](code/results/)：
* **问题一计算结果**：[`code/results/result1.xlsx`](code/results/result1.xlsx)（预热阶段 0~1800 s 截面场）
* **问题二计算结果**：[`code/results/result2.xlsx`](code/results/result2.xlsx)（前 3 小时秒级瞬态场）
* **问题三计算结果**：[`code/results/result3.xlsx`](code/results/result3.xlsx)（固定几何全域干燥达标历程，预测干燥时间 57.44 h）
* **问题四计算结果**：[`code/results/result4.xlsx`](code/results/result4.xlsx)（考虑径向动态收缩全域干燥历程与外径演变）

---

## 仓库目录结构

```text
.
├── 2026_CUMCM_Problem_A_Final_Paper.pdf  # 论文 PDF 终稿（根目录直达）
├── 整体答案思路.md                        # A 题全局解题思路、理论推导与技术路线
├── 整体答案思路.pdf                        # 总体思路文档 PDF 版
├── README.md                              # 仓库主索引文档
├── .gitignore                             # Git 忽略配置
│
├── problem/                               # 赛题题干与原始实验数据
│   ├── A题.pdf                            # 官方赛题文档
│   ├── problem_A_text.txt                 # A 题题干纯文本
│   ├── 附件/                              # 原始附件（附件1温湿度时序、附件2尺寸测量、附件3提交模板）
│   └── README.md                          # 赛题背景与数据字典说明
│
├── code/                                  # 核心数值求解器与计算结果
│   ├── Problem1.py                        # 问题一求解脚本
│   ├── Problem2.py                        # 问题二求解脚本
│   ├── Problem3.py                        # 问题三求解脚本
│   ├── Problem4.py                        # 问题四求解脚本
│   ├── grid.py                            # 二维轴对称 FVM 空间网格剖分与通量装配
│   ├── checkConservation.py               # 离散格式全局能量与质量瞬时守恒性验证
│   ├── requirements.txt                   # 计算环境依赖 (numpy, scipy, openpyxl, matplotlib)
│   ├── results/                           # 各问最终输出结果表格 (result1.xlsx ~ result4.xlsx)
│   └── README.md                          # 求解器算法理论、离散格式与复现指南
│
├── figures/                               # 出版级学术可视化工程
│   ├── *.png                              # 论文录用的全套高清主图
│   ├── scripts/                           # 论文插图自动化生成脚本库
│   ├── Fig_Ref/                           # 披萨图与截面快照求解脚本及数据
│   ├── Archive/                           # 过程性草稿图件（50+ 张）与调试脚本
│   ├── FVM五环传热控制体数学意义说明.md     # 控制体推导数学与物理说明
│   ├── 绘图注意事项与规范指引.md            # 学术图件设计规范
│   └── README.md                          # 图表索引与可视化说明
│
├── paper/                                 # 竞赛论文 LaTeX 完整工程
│   ├── main.tex                           # 论文主排版源码
│   ├── main.pdf                           # 编译完成的 19 页最终提交论文
│   ├── cumcm2026.sty / cumcmthesis.cls    # 竞赛论文样式文件
│   ├── references.bib                     # BibTeX 引用数据库
│   ├── sections/                          # 论文正文分章节源码
│   ├── tables/                            # 论文各问数据 LaTeX 格式表格
│   ├── figures/                           # 论文排版引用的高清图件
│   ├── appendices/                        # 附录源码（支撑材料、补充数据、程序清单、AI使用声明）
│   ├── scripts/                           # 结果数据自动转 LaTeX 表格工具
│   ├── 历史文档打磨记录/                    # 论文打磨全周期版本历史（39 份 Markdown，含审阅批注）
│   └── README.md                          # 论文架构、编译指南与各章节介绍
│
└── references/                            # 核心学术参考文献库
    ├── *.pdf                              # 11 篇支撑学术文献（传热传质、收缩动力学、PCHIP、ODE）
    ├── _Filelist_Of_Reference.txt         # 文献清单
    ├── 可能会用到的论文引用.json            # 结构化引用元数据
    └── README.md                          # 参考文献解读与引用关联说明
```

---

## 运行与复现指南

### 1. 数值求解复现

```bash
cd code
pip install -r requirements.txt

# 执行各问求解并输出至 results/ 目录
python Problem1.py --nr 120 --nz 120 --stretch 2.0 --output results/result1.xlsx
python Problem2.py --nr 120 --nz 120 --stretch 2.0 --output results/result2.xlsx
python Problem3.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result3.xlsx
python Problem4.py --nr 120 --nz 120 --stretch 2.0 --tail-points 20 --output results/result4.xlsx

# 离散格式全局守恒性校验
python checkConservation.py
```

### 2. 论文插图重新生成

```bash
cd figures
python scripts/run_all.py
```

### 3. LaTeX 论文编译

```bash
# 从计算结果提取 LaTeX 表格
python paper/scripts/extract_paper_tables.py

# 编译 LaTeX 论文 (XeLaTeX + BibTeX)
cd paper
xelatex -synctex=1 -interaction=nonstopmode main.tex
bibtex main.aux
xelatex -synctex=1 -interaction=nonstopmode main.tex
xelatex -synctex=1 -interaction=nonstopmode main.tex
```

---

## 提交规范

项目开发过程严格遵循 Conventional Commits 规范：

```regex
^(feat|fix|docs|refactor|test|chore)\((q[1-5]|data|model|latex|env|all)\): .{1,50}$
```

* **类型**：`feat`（新模型/功能）、`fix`（修正）、`docs`（文档/论文）、`refactor`（重构）、`test`（验证/检验）、`chore`（环境/构建）
* **范围**：`q1`~`q4`（具体问题）、`data`（数据处理）、`model`（机理模型）、`latex`（排版系统）、`all`（全局）

---

## 许可与声明

本仓库代码、数据及论文为 2026 年全国大学生数学建模竞赛参赛成果开源归档，供学术研究与交流参考。
