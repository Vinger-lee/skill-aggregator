# Skill Aggregator 设计文档

## 概述

Skill Aggregator 是一个 AI Agent 元技能系统，通过三段式工作流（意图分析 → 澄清确认 → 技能匹配）自动分析任务并推荐最适合的技能。

## 核心特性

- **三段式工作流**：意图分析 → 澄清确认 → 技能匹配
- **自动索引更新**：检测技能文件变化，自动重建索引
- **多维度匹配**：关键词、领域、技术栈、TF-IDF 相似度
- **优先级加权**：核心技能自动提权
- **CLI + Python API**：命令行工具和编程接口双支持

## 架构设计

### 目录结构

```
skill-aggregator/
├── skill_aggregator/          # 核心包
│   ├── __init__.py           # 包入口 + 自动索引检查
│   ├── __main__.py           # python -m skill_aggregator 入口
│   ├── aggregator.py         # CLI 主入口 + 推荐函数
│   ├── intent.py             # 意图分析引擎
│   ├── matcher.py            # 技能匹配引擎
│   └── indexer.py            # 索引构建器
├── scripts/
│   └── build_index.py        # 手动索引重建工具
├── docs/
│   ├── DESIGN.md             # 本文档
│   └── EXAMPLES.md           # 使用示例
└── tests/
    └── test_matcher.py       # 单元测试
```

### 核心模块

#### 1. 意图分析引擎 (`intent.py`)

**职责**：分析用户任务描述，提取结构化意图

**输出**：
```python
{
    "domain": "coding",           # 领域
    "domain_confidence": 0.85,    # 领域可信度
    "activity": "fix",            # 活动类型
    "activity_confidence": 0.90,  # 活动可信度
    "stack": ["react", "three.js"], # 技术栈
    "project": "my-project",       # 项目名
    "goal": "修复黑夜闪烁问题",    # 目标描述
    "ambiguity": 0.2,             # 模糊度 (0-1)
    "clarifying": [...]           # 澄清问题（如果需要）
}
```

**关键算法**：
- 领域识别：基于关键词字典匹配
- 活动识别：动词提取 + 语义映射
- 技术栈识别：正则匹配 + 常见技术栈库
- 模糊度计算：基于关键词覆盖率和置信度

#### 2. 技能匹配引擎 (`matcher.py`)

**职责**：基于意图和任务特征匹配最相关的技能

**匹配维度**：
1. **关键词匹配** (40%)：任务关键词与技能关键词的交集
2. **领域匹配** (25%)：任务领域与技能领域的匹配度
3. **TF-IDF 相似度** (20%)：基于 TF-IDF 的文本相似度
4. **优先级加权** (15%)：核心技能自动提权

**评分公式**：
```python
score = (
    keyword_score * 0.40
    + domain_score * 0.25
    + similarity_score * 0.20
    + priority_bonus * 0.15
)
```

#### 3. 索引构建器 (`indexer.py`)

**职责**：扫描技能目录，构建索引文件

**索引结构**：
```python
{
    "total_skills": 42,
    "built_at": "2026-05-02T10:30:00",
    "files_hash": "abc123...",
    "skills": [
        {
            "name": "systematic-debugging",
            "path": "/path/to/SKILL.md",
            "domain": ["coding"],
            "keywords": ["debug", "fix", "error"],
            "description": "...",
            "priority": 1
        },
        ...
    ]
}
```

**自动更新机制**：
- 计算所有技能文件的哈希值
- 与上次保存的哈希值对比
- 如果不匹配，自动重建索引
- 在包导入时静默执行检查

## 三段式工作流

### Phase 1: 意图分析

**输入**：用户任务描述（自然语言）

**处理**：
1. 提取关键词和技术栈
2. 识别领域和活动类型
3. 计算模糊度
4. 生成澄清问题（如果需要）

**输出**：结构化意图对象

### Phase 2: 澄清确认（可选）

**触发条件**：
- 模糊度 > 0.3
- 用户使用 `--clarify` 参数
- 意图分析返回澄清问题

**处理**：
- 展示澄清问题
- 等待用户确认
- 更新意图对象

### Phase 3: 技能匹配

**输入**：结构化意图对象

**处理**：
1. 加载索引文件
2. 计算每个技能的匹配得分
3. 排序并返回 Top-N

**输出**：匹配结果列表

## 使用方式

### 1. 命令行工具

```bash
# 通过 console_scripts 入口
skill-aggregator "修复 Three.js 地球的黑夜闪烁"

# 通过 python -m
python3 -m skill_aggregator "修复 Three.js 地球的黑夜闪烁"

# 意图分析模式
skill-aggregator --intent-only "帮我搞一下那个动画"

# 澄清模式
skill-aggregator --clarify "做个水墨动画"
```

### 2. Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# 方式 1：直接推荐（自动处理意图分析）
results = recommend("修复 Three.js 地球的黑夜闪烁", top_n=5)

# 方式 2：分步执行
intent = analyze_intent("修复 Three.js 地球的黑夜闪烁")
results = match_by_intent(intent, top_n=5)
```

## 扩展性设计

### 添加新的技能目录

编辑 `skill_aggregator/indexer.py`：

```python
SKILL_DIRS = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".claude" / "agents",
    Path.home() / ".claude" / "skills",
    # 添加自定义目录
    Path("/path/to/your/custom/skills"),
]
```

### 自定义匹配权重

编辑 `skill_aggregator/matcher.py` 中的评分公式。

### 添加优先级技能

编辑 `skill_aggregator/matcher.py` 中的 `priority_skills` 集合。

## 性能优化

- **索引缓存**：索引文件存储在 `~/.skill-aggregator/index.json`
- **哈希检查**：只在文件变化时重建索引
- **TF-IDF 预计算**：索引构建时预计算 TF-IDF 向量
- **Top-N 优化**：使用堆排序，只保留 Top-N 结果

## 未来规划

- [ ] 支持多语言技能描述
- [ ] 添加技能依赖关系图
- [ ] 实现技能组合推荐
- [ ] 支持用户反馈学习
- [ ] 添加 Web UI 界面
