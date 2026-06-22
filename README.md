# final-exam-review

> **规则驱动 AI 行为 + 脚本加速重复劳动** — 大学生期末复习助手 Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 这是什么

`final-exam-review` 是一个专为**期末复习场景**设计的 Claude Code / AI Agent Skill。它合并了 [seevwis43825/final-exam-review-skill](https://github.com/seevwis43825/final-exam-review-skill)（工具链型）和 [lucianwhy/final-review](https://github.com/lucianwhy/final-review)（规则型）的优点，把两套方案整合为一个统一的、更优的解决方案。

### 它适合这样的场景

- 你已经有了课程资料（PPT、课本 PDF、历年真题、平时作业、笔记）
- 你希望 AI 基于这些资料整理知识点、清洗笔记、生成题目、补解析
- 你希望题目贴近真实考试题型和考法，而不是随机题库风格
- 你希望答案解析不止讲"为什么对"，更要讲"考试怎么拿分"
- 你需要生成专业排版的 PDF 复习文档、思维导图或模拟卷

### 与原始两个仓库的关系

| 维度 | [seevwis43825](https://github.com/seevwis43825/final-exam-review-skill) | [lucianwhy](https://github.com/lucianwhy/final-review) | **本仓库（合并版）** |
|------|------|------|------|
| 定位 | 工具链驱动 | 纯规则驱动 | **规则驱动 + 工具增强** |
| 文件数 | 14（脚本+模板） | 3（规则文档） | **16（全整合）** |
| AI 行为约束 | 弱 | 强 | **强** |
| 自动化管线 | 完整 5-Phase | 无 | **完整 5-Phase** |
| 质量审查 | Critic+Reviser | 无 | **Critic+Reviser** |
| PDF 排版 | Pandoc+XeLaTeX | 无 | **Pandoc+XeLaTeX** |
| 思维导图 | Mermaid | 无 | **Mermaid** |
| 模拟卷 | 自动生成 | 无 | **自动生成** |
| 得分导向规则 | 弱 | 极强 | **极强** |
| 规则同步机制 | 无 | 有 | **有（增强版）** |
| 零依赖可用 | 否 | 是 | **是（核心规则层零依赖）** |

## 快速开始

### 方式 1：作为 Skill 使用（推荐）

```bash
# 安装
npx skills add kobe0714/final-exam-review -g

# 然后在对话中直接说：
# "期末复习" / "整理复习资料" / "考试重点" / "出模拟卷" / "考前突击"
```

触发后，AI Agent 会自动按照 Skill 规则工作：确认考试题型 → 清洗资料 → 提炼知识点 → 生成题目和解析。

### 方式 2：作为 Agent 长期规则使用

把 [`AGENT.md`](./AGENT.md) 的内容复制到你的 `CLAUDE.md` 或 `AGENT.md` 中。这样即使不显式触发 Skill，AI 在处理复习任务时也会遵循同一套规则。

### 方式 3：独立运行脚本

```bash
# 安装 Python 依赖
pip install "markitdown[all]" liteparse pymupdf python-docx

# 一键生成复习文档
python3 scripts/scanner.py "./课程资料/"       # Phase 0: 检测考试结构
python3 scripts/extract_all.py "./课程资料/"    # Phase 1: 提取资料
python3 scripts/fuse_knowledge.py "./课程资料/" # Phase 2: 知识融合
python3 scripts/generate_mindmap.py Ch1         # Phase 2: 思维导图
bash scripts/build.sh "./课程资料/" "期末复习"   # Phase 3: PDF+DOCX+HTML
python3 scripts/generate_mock.py "./课程资料/"   # Phase 4: 模拟卷
python3 scripts/check_deps.py                   # 依赖检查
```

## 核心规则（AI 行为）

### 题源优先级

| 优先级 | 题源 | 说明 |
|--------|------|------|
| 1（最高） | 历年真题 | 最贴近真实考试，优先复用 |
| 2 | 老师 PPT | 课堂重点，考试范围的主要依据 |
| 3 | 平时作业 / 阅读作业 | 老师出题偏好的直接体现 |
| 4 | 速成课题目 | 优先级较低，但知识点梳理价值高 |
| 5（最低） | AI 补充题 | 仅在已有材料不足时使用 |

### 材料处理流程

```
转 Markdown → 清洗 → 提知识点 → 出题
（顺序不可颠倒）
```

- 默认使用 `markitdown` 转换 PPT/PDF/Word
- 复杂 PDF 使用 `liteparse` 处理 CMap 编码
- 清洗目标：**清晰、可背、可考**（不是完整存档）

### 出题规则

- 按真实考试题型出题，**不做平均分配**
- 每个知识点通常 `1~6` 题
- 知识点越密、越高频、考法越多 → 题量越多
- 题型要**匹配知识点最可能考法**：
  - 识记辨析型 → 选择/判断/填空
  - 定义比较型 → 简答
  - 推理证明构造型 → 证明题/计算题

### 解析规则（得分导向）

解析**不只解释对错，还要服务考试拿分**：

- **客观题** → 补 `这题核心知识点` + 关键定义/性质/判定依据 + 易混点
- **主观题** → 补 `这题答题核心点` + `必须出现` + `常见失分点` + 标准作答框架
- **通用的** → 先写什么抢步骤分、哪些词必须写、哪些错误最丢分

### 可执行得分技巧

```
看到判断题 → 先看边界条件和反例
看到简答题 → 先写定义，再写性质，再写结论
看到证明题 → 先写已知、求证和入口定理/定义
不会完整作答 → 先写核心定义、关键性质、结论，先抢步骤分
```

## 自动化管线

```
Phase 0: SCAN     → 检测考试结构（题型、章节分布）
Phase 1: EXTRACT  → 多引擎资料提取（PPT+PDF+DOCX→结构化文本）
Phase 2: FUSE     → 知识点融合 + 思维导图 + 内容分类
Phase 2.5: REVIEW → 质量审查（Critic 评分→Reviser 修正，≥80/100 通过）
Phase 3: OUTPUT   → 生成 MD+PDF+DOCX+HTML + 可选模拟卷
```

### 管线命令速查

| 任务 | 命令 |
|------|------|
| 检测考试结构 | `python3 scripts/scanner.py "<dir>"` |
| 提取所有资料 | `python3 scripts/extract_all.py "<dir>"` |
| 融合为复习文档 | `python3 scripts/fuse_knowledge.py "<dir>"` |
| 生成思维导图 | `python3 scripts/generate_mindmap.py "<chapter>"` |
| 构建最终 PDF | `bash scripts/build.sh "<dir>" "<name>"` |
| 生成模拟卷 | `python3 scripts/generate_mock.py "<dir>"` |
| 检查依赖 | `python3 scripts/check_deps.py` |

### 质量审查（Critic + Reviser）

```
融合后的 MD → Critic 逐章评分 → 分数 ≥ 80？→ 是 → Phase 3 输出
                                    → 否 → Reviser 重写 → 回到 Critic
```

Critic 评分维度（每章满分 100）：题纲覆盖 40% + 答案准确 30% + 结构完整 20% + 可读性 10%
最多 2 轮修订。2 轮后仍 < 80 分，标记用户审查。

### 答案可信度三级标记

| 级别 | 标记 | 规则 |
|------|------|------|
| 已确认 | （无标记） | 习题答案与 PPT + 课本内容一致 |
| 单源 | `[*]` | 仅有习题答案，无 PPT/课本直接确认 |
| 存疑 | `[!]` | 习题答案与 PPT 或课本冲突 → 课本为准 |

## 仓库结构

```
final-exam-review/
  SKILL.md              # 完整工作流和规则（AI 行为约束 + 自动化管线）
  AGENT.md              # 长期默认规则（可复制进 CLAUDE.md）
  README.md             # 本文件
  scripts/              # 自动化脚本（8 个）
    scanner.py          # Phase 0: 考试结构检测
    extract_all.py      # Phase 1: 多引擎资料提取
    fuse_knowledge.py   # Phase 2: 知识融合
    generate_mindmap.py # Phase 2: Mermaid 思维导图
    fix_formatting.py   # Phase 3: Markdown 格式修复
    build.sh            # Phase 3: Pandoc+XeLaTeX PDF 构建
    generate_mock.py    # Phase 4: 模拟卷生成
    check_deps.py       # 依赖检查
  templates/            # LaTeX 模板（5 个）
    content-classes.tex     # 内容分类样式（定义/理论/公式/易错/关联）
    enhanced-style.tex      # 增强样式
    table-style.tex         # 专业表格（booktabs + colortbl）
    mermaid-filter.lua      # Mermaid 图表 Pandoc 滤镜
    dywsy21-template.tex    # 完整文档模板
```

## 依赖

### 核心规则层（零依赖）
- 无需安装任何工具即可使用 AI 行为规则

### 自动化管线（可选）

| 工具 | 安装 | 用途 |
|------|------|------|
| markitdown | `pip install "markitdown[all]"` | PPTX/DOCX → Markdown |
| liteparse | `pip install liteparse` | PDF OCR + 文本提取 |
| PyMuPDF | `pip install pymupdf` | PDF 页面渲染 |
| python-docx | `pip install python-docx` | DOCX 后备 |
| Pandoc | `winget install JohnMacFarlane.Pandoc` | MD → PDF/DOCX/HTML |
| MiKTeX | `winget install MiKTeX.MiKTeX` | XeLaTeX 引擎 |
| mermaid-cli | `npm install -g @mermaid-js/mermaid-cli` | 思维导图渲染 |

一键检查：
```bash
python3 scripts/check_deps.py
```

## 常见错误

1. **跳过 Phase 0 确认** → 在花时间提取资料前，始终先和用户确认考试结构
2. **先出题再清洗** → 材料不洗就出题，题目质量低、噪音高。顺序不可颠倒
3. **题源平均分配** → 真题 >> AI 补充题，不可等量齐观
4. **解析只写"为什么对"** → 要讲"考试怎么拿分"，不只是知识讲解
5. **信任单源答案** → 只有习题答案没有 PPT/课本验证的，标记 `[*]`
6. **对 CMap 编码 PDF 用 PyMuPDF** → 用 liteparse 代替
7. **表格在 PDF 中渲染为纯文本** → 表格前缺少空行导致 Pandoc 跳过

## 红线

- "材料不用洗，直接出题吧" → 必须先清洗
- "所有题源平均分配就行" → 违反优先级规则
- "解析解释一下对错就够了" → 必须服务拿分
- "流程顺序可以灵活调整" → 转→洗→提→出 的顺序不可变
- "不用确认考试结构，直接开始提取" → 必须先 Phase 0

## 学科扩展

欢迎为具体学科补充专用内容：

- 高等数学、离散数学、线性代数
- 数据结构、计算机网络、操作系统
- 宏观经济学、微观经济学、国际金融
- 或其他任何有考试的专业课

建议扩展方向：专用题型总结、高频考点、易错点、证明题/计算题/简答题答题套路、专用 Markdown 资料。

## Contributing

欢迎根据真实复习实践更新本 Skill。尤其欢迎：

- 更好的题源优先级策略
- 更稳的 Markdown 清洗规则
- 更贴近考试的出题协议
- 更强的客观题/主观题解析模板
- 更实用的考试得分技巧总结
- 某个具体学科的专用复习规则和资料

贡献流程：

1. Fork 本仓库
2. 从 fork 新建分支
3. 修改相关文件
4. 提交 commit 并推送
5. 向主仓库发起 Pull Request
6. 在 PR 里说明：改了什么、为什么改、适用于什么复习场景

## License

MIT — 详见 [LICENSE](LICENSE)
