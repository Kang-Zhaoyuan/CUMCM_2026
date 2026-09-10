# CUMCM 2026

2026 年全国大学生数学建模竞赛团队协作仓库。

---

## 1. Commit Message 规范

### 正则约束
```regex
^(feat|fix|docs|refactor|test|chore)\((q[1-5]|data|model|latex|env|all)\): .{1,50}$
```

### 字段定义
| 字段 | 匹配正则 | 说明 |
| :--- | :--- | :--- |
| **type** | `feat|fix|docs|refactor|test|chore` | 操作类型：新功能、修复、文档/论文、重构、验证、构建配置 |
| **scope** | `q[1-5]|data|model|latex|env|all` | 作用域：指定题号、数据层、模型算法、论文排版、环境依赖、全局 |
| **subject** | `.{1,50}` | 简要描述（末尾不加标点，≤50 字符） |

### 范例 (Valid)
* `feat(q1): 建立灰色预测 GM(1,1) 模型`
* `fix(q2): 修正遗传算法交叉概率越界问题`
* `docs(latex): 完成第 6 节模型求解排版与图表引用`
* `refactor(data): 向量化清洗附件1异常值`
* `chore(env): 更新 requirements.txt 增加 pulp 依赖`

---

## 2. 分支命名规范

### 正则约束
```regex
^(feat|fix|docs)/(q[1-5]|latex|data)-[a-z0-9_]+$
```

### 范例 (Valid)
* `feat/q1-gray_model`
* `fix/q2-ga_bounds`
* `docs/latex-sec6`
* `feat/data-clean`

---

## 3. 核心准则
1. **主分支约束**：`main` 仅合并可运行、可成功编译的代码与论文，严禁直接 `push -f`。
2. **论文防冲突**：各队员仅编辑 `sections/` 下各自章节文件，严禁多人并发修改 `main.tex`。
3. **可复现约束**：随机算法代码必须显式固定随机种子（如 `seed=42`）。
