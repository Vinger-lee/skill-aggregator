# Skill Aggregator

> 🧠 **智能化技能聚合器** — AI Agent 的"元技能"。自动分析用户意图 → 推荐最优技能组合 → 开始工作

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub Stars](https://img.shields.io/github/stars/vinger-lee/skill-aggregator?style=social)](https://github.com/vinger-lee/skill-aggregator)

---

## 🌟 为什么需要？

你的 AI Agent（Hermes / Claude Code / Cursor）可能拥有 **数百个技能**！面对这么多选择：

- ❌ 每次手动翻找合适技能 → 浪费 API Token
- ❌ 模糊的自然语言任务 → 很难精准匹配
- ❌ 技能分散在不同平台 → 找不到

**Skill Aggregator 一招解决：三段式工作流**

---

## 🔄 三段式工作流

```
用户说: "帮我搞一下那个动画"
     │
     ▼
┌─────────────────────────────────────┐
│ Phase 1: 🎯 意图分析                  │
│  提取: 领域/活动/技术栈/目标/模糊度      │
│  → creative / create / canvas        │
│  → 模糊度: 80% ⬅️ 需要确认            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 2: 💬 需求确认                  │
│  用 clarify 跟用户确认意图              │
│  "A) 水墨动效  B) 3D地球  C) 页面过渡?"│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Phase 3: 🔄 加载技能                  │
│  自动加载 Top-5 匹配 skill             │
│  → Creative Ideation + Pixel Art...  │
│  → 开干！🚀                          │
└─────────────────────────────────────┘
```

---

## ⚡ 快速开始

### 安装

```bash
pip install skill-aggregator
# 或从源码安装
git clone https://github.com/vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e .
```

### 命令行使用

```bash
# 🟡 模糊任务 → 输出意图分析 + 澄清建议
python3 -m skill_aggregator --intent-only "帮我搞一下那个动画"

# 🟢 明确任务 → 直接推荐技能
python3 -m skill_aggregator "量化回测策略有bug，交易次数一直显示0"

# 🔄 重建技能索引（添加新skill后运行）
python3 scripts/build_index.py --force
```

### Python API

```python
from skill_aggregator import analyze_intent, recommend

# Phase 1: 分析意图
intent = analyze_intent("给feiyi-web的3D地球加上点击动画")
print(f"领域: {intent['domain']}, 模糊度: {intent['ambiguity']:.0%}")
# → 领域: creative, 模糊度: 30%

# Phase 3: 推荐技能
skills = recommend("feiyi-web 3D 地球动画", top_n=5)
for s in skills:
    print(f"  {s['score']:.0%}  {s['skill']}")
# → 25%  Creative Ideation
# → 25%  Pixel Art
```

---

## 🏗️ 架构

```
skill-aggregator/
├── skill_aggregator/          # 核心包
│   ├── __init__.py            # 自动检测变更 + 增量重建索引
│   ├── intent.py              # 🆕 纯规则意图分析引擎 (322行)
│   ├── indexer.py             # 扫描技能文件 → JSON 索引
│   ├── matcher.py             # TF-IDF + 多维评分匹配 (477行)
│   └── aggregator.py          # CLI + API 主入口
├── scripts/
│   ├── build_index.py         # 手动/强制重建索引
│   └── install.sh             # 一键安装到 Hermes + Claude Code
├── tests/
│   └── test_matcher.py        # 单元测试
└── docs/
    ├── DESIGN.md              # 架构设计文档
    ├── EXAMPLES.md            # 使用示例
    └── IMPLEMENTATION_SUMMARY.md  # 实现总结
```

### 核心模块

| 模块 | 行数 | 功能 |
|:---|:---:|:---|
| `intent.py` | 322 | 纯规则意图分析 — 8领域×11活动，模糊度计算，自动生成澄清问题 |
| `matcher.py` | 477 | TF-IDF + 余弦相似度 + 关键词 + 分类加权，四路评分引擎 |
| `indexer.py` | 239 | 扫描 Hermes/Claude 技能目录，构建索引 (623个) |
| `aggregator.py` | 298 | 三段式 CLI，emoji 彩色输出，Python API |

---

## ✨ 核心特性

### 🎯 智能意图分析（纯规则，零 AI 成本）
- **8 大领域**: coding / creative / finance / devops / research / data / design / social
- **11 种活动**: create / fix / analyze / review / deploy / test / optimize / debug / learn / design / configure
- **技术栈识别**: React, Python, Three.js, Docker, akshare, backtrader, Gradio...
- **模糊度计算**: 0-100%，基于技术名词、项目名、句子长度、模糊词综合判定
- **自动澄清**: 模糊时生成 2-4 个确认选项

### 🧩 智能匹配（四路评分）

| 维度 | 权重 | 说明 |
|:---|:---:|:---|
| 关键词精确匹配 | 40% | 任务关键词命中技能描述 |
| 领域分类匹配 | 25% | 相同 domain 的 skill 加分 |
| TF-IDF 余弦相似度 | 20% | 纯 Python 实现（零外部依赖） |
| 优先级加权 | 15% | 核心工作流技能(debugging等)额外加分 |

### 📦 零外部依赖
- 纯 Python 标准库实现
- 自实现 TF-IDF、余弦相似度、中文分词判定
- 无需 sklearn、numpy、jieba 等

---

## 🔄 自动更新索引

**按需重建，不浪费 API Token：**

```bash
# 添加了新 skill 后，手动重建一次：
python3 scripts/build_index.py --force

# 或者 Python 会自动检测变更（import 时检查文件 hash）
```

### 自动检测原理
```
添加 skill → skill_manage(action='create')
         → python3 scripts/build_index.py --force
         → 索引从 622 → 623 ✅
```

---

## 🧪 兼容性

| AI Agent | 集成方式 | 状态 |
|:---|:---|---:|
| Hermes Agent | `skill_view('skill-aggregator')` | ✅ |
| Claude Code | `.claude/skills/skill-aggregator/SKILL.md` | ✅ |
| Cursor / Windsurf | 复制 SKILL.md 到项目 | ✅ |
| 任意 Python 3.10+ | `pip install skill-aggregator` | ✅ |

---

## 🤝 贡献

欢迎 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

### 短期 TODO
- [ ] 增加中文分词支持（jieba 可选依赖）
- [ ] GitHub Actions CI
- [ ] PyPI 发布
- [ ] VS Code 扩展

---

## 📜 开源协议

MIT License — 详见 [LICENSE](LICENSE)

---

**Made with ❤️ by Vinger**
