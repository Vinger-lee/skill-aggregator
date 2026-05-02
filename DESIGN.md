# Skill Aggregator — 设计文档

## 概述

Skill Aggregator 是一个元技能（meta-skill），用于在 AI Agent 启动时自动分析当前任务，并从数百个可用技能中智能推荐最相关的技能组合，以提升工作质量和效率。

## 核心机制

```
用户输入任务 → 任务分析器 → 技能匹配引擎 → 推荐结果 → 自动加载技能
```

### 1. 任务分析器 (Task Analyzer)
- 从用户输入中提取：**领域**（coding/design/marketing...）、**活动类型**（create/fix/analyze/deploy...）、**关键技术**（React/Python/A股...）、**上下文**（quant/feiyi-web/...）
- 使用 NLP 关键词提取 + 语义匹配

### 2. 技能索引 (Skill Index)
- 扫描所有可用 skill（Hermes: `~/.hermes/skills/`, Claude Code: `~/.claude/agents/`）
- 从 SKILL.md / CLAUDE.md 中提取：名称、描述、类别、关键词、触发条件、适用场景
- 构建可搜索的 JSON 索引

### 3. 匹配引擎 (Matching Engine)
- **精确匹配**: 关键词命中（如 "debug" → debugging skills）
- **模糊匹配**: TF-IDF + 余弦相似度
- **分类匹配**: 按类别筛选 + 排重
- **优先级排序**: 按相关性、历史使用频率、任务类型

### 4. 推荐输出 (Recommendation)
- Top-N 推荐（默认 Top-5）
- 加载指令（Hermes 自动 `skill_view()`，Claude Code 自动引用）
- 组合建议（多个技能的联合使用推荐）

## 评分算法

```
score = keyword_match * 0.4 + category_match * 0.3 + description_similarity * 0.2 + priority_bonus * 0.1
```

## 技术栈
- Python 3.10+
- 纯标准库（无外部依赖）
- JSON 索引文件

## 项目结构
```
skill-aggregator/
├── SKILL.md                    # Hermes Agent skill
├── .claude/skills/
│   └── skill-aggregator/
│       └── SKILL.md           # Claude Code skill
├── src/
│   ├── __init__.py
│   ├── indexer.py             # 构建技能索引
│   ├── matcher.py             # 任务-技能匹配引擎
│   └── aggregator.py          # 聚合推荐主逻辑
├── scripts/
│   ├── build_index.sh         # 重建索引脚本
│   └── install.sh             # 安装到 Hermes + Claude Code
├── tests/
│   └── test_matcher.py
├── DESIGN.md                  # 本文档
├── README.md                  # 开源 README
├── CONTRIBUTING.md
├── LICENSE                    # MIT
└── .gitignore
```
