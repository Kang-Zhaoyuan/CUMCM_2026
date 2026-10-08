# 竞赛论文 LaTeX 排版工程 (LaTeX Paper Project)

本目录为 2026 年高教社杯全国大学生数学建模竞赛 A 题的 LaTeX 排版源码与工程资产。论文严格遵循全国组委会格式规范，最终编译生成 **19 页**完整学术论文。

---

## 论文成果入口

* **终稿 PDF**：[`main.pdf`](main.pdf)（根目录镜像：[`../2026_CUMCM_Problem_A_Final_Paper.pdf`](../2026_CUMCM_Problem_A_Final_Paper.pdf)）
* **排版主入口**：[`main.tex`](main.tex)
* **样式与宏包**：[`cumcmthesis.cls`](cumcmthesis.cls)（国赛论文文档类）、[`cumcm2026.sty`](cumcm2026.sty)（格式控制宏包）
* **参考文献库**：[`references.bib`](references.bib)

---

## 论文模块索引

| 目录 / 文件 | 作用说明 |
| :--- | :--- |
| [`sections/`](sections/) | 论文正文分章节源码（`00_abstract.tex` 至 `08_references.tex`） |
| [`tables/`](tables/) | 各问输出数据 LaTeX 格式表格（由 `scripts/extract_paper_tables.py` 自动从 Excel 计算结果中提取） |
| [`figures/`](figures/) | 论文排版嵌入的 10 张出版级图件 |
| [`appendices/`](appendices/) | 支撑材料清单（附录A）、补充结果（附录B）、主要 Python 计算程序（附录C）及 AI 工具规范使用声明（附录D） |
| [`scripts/`](scripts/) | 表格自动化生成辅助工具（`extract_paper_tables.py`） |
| [`历史文档打磨记录/`](历史文档打磨记录/) | 论文写作全流程打磨历史（39 份 Markdown，含同行审阅批注） |

---

## 自动化表格提取与编译指令

```bash
# 从计算结果中重新提取 LaTeX 表格
python scripts/extract_paper_tables.py

# XeLaTeX 标准编译流程
xelatex -synctex=1 -interaction=nonstopmode main.tex
bibtex main.aux
xelatex -synctex=1 -interaction=nonstopmode main.tex
xelatex -synctex=1 -interaction=nonstopmode main.tex
```
