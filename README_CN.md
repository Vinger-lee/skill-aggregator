# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-jieba%20%7C%20stdlib-green" alt="Dependencies">
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code Style">
  <br>
  <b>🧠 你的 AI 助手会 600+ 个技能，但你只知道 10 个。Skill Aggregator 帮你找出该用哪个。</b>
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README_CN.md">中文</a> ·
  <a href="docs/i18n/README.ja.md">日本語</a> ·
  <a href="docs/i18n/README.ko.md">한국어</a> ·
  <a href="docs/i18n/README.fr.md">Français</a> ·
  <a href="docs/i18n/README.es.md">Español</a> ·
  <a href="docs/i18n/README.ru.md">Русский</a> ·
  <a href="docs/i18n/README.ar.md">العربية</a>
</p>

---

## 🤔 你遇到过这个问题吗？

你装了 Superpowers、Karpathy 的 Planning with Files、一堆 Plugin……你的 AI 助手**已经有 400+ 个技能**了。

但你每次还是自己写 prompt？手动翻文件夹找技能名？

```
❌ 用户：帮我写个 Canvas 动画
❌ AI：好的，我自己写……（用基础能力硬写，不知道有 p5.js skill）
✅ 用了 Skill Aggregator：自动匹配到 p5js、pixel-art、creative-ideation 三个 skill
```

**Skill Aggregator 是 AI 技能的"搜索引擎"**——你描述任务，它告诉你该用哪个 skill。

---

## ⚡ 快速开始

```bash
pip install skill-aggregator

# 描述你的任务，自动推荐技能
skill-aggregator "用 React 写一个登录页面的表单验证"
```

输出：
```
🎯 意图分析结果
  ├─ 领域: coding (可信度: 80%)
  ├─ 活动: create (可信度: 66%)
  └─ 模糊度: 10% ✓ 足够明确

📋 Top-8 推荐技能
  ├─ 65%  react-component-extraction
  ├─ 45%  systematic-debugging
  ├─ 40%  test-driven-development
  ├─ 30%  node-inspect-debugger
  ├─ 25%  planning-with-files
  ├─ 20%  github-code-review
  ├─ 15%  react-best-practices
  └─ 15%  chinese-code-review

💡 组合建议: react-component-extraction + test-driven-development 联动
```

---

## ✨ 为什么牛逼

| 功能 | 说明 |
|------|------|
| 🧠 **意图理解** | 不只看关键词，理解你的真实意图（在写 bug 还是在做设计？） |
| 🈯 **中英双语** | jieba 中文分词 + 英文正则，中英混合任务随便写 |
| 🔄 **环境感知** | 自动读取 `~/.hermes/config.yaml`，发现你装的所有 skill 目录 |
| 🎯 **四路评分** | 关键词匹配(40%) + 领域匹配(25%) + TF-IDF相似度(20%) + 优先级(15%) |
| 🧹 **技能清洗** | 扫描 400+ 个 skill，检测损坏/缺描述/重复等问题 |
| 📦 **轻量零依赖*** | 纯 Python 标准库（jieba 可选，没装也能跑） |
| 🔌 **Python API** | `from skill_aggregator import recommend` 一行搞定 |

> \* jieba 是唯一外部依赖，用于中文分词。未安装时自动降级。

---

## 🆚 跟其他方案比

| 方案 | 智能匹配 | 中文分词 | 环境感知 | 技能清洗 | 零配置 |
|------|:--:|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ TF-IDF | ✅ jieba | ✅ auto | ✅ | ✅ |
| 手动查文件夹 | ❌ | ❌ | ❌ | ❌ | — |
| 直接问 AI | ⚠️ 部分 | ⚠️ 部分 | ❌ | ❌ | ✅ |
| grep 搜索 | ⚠️ 关键词 | ❌ | ❌ | ❌ | ✅ |

---

## 📖 更多用法

### 意图分析模式

```bash
skill-aggregator --intent-only "帮我搞一下那个接口"
# 输出:
# 🎯 领域: coding (可信度: 50%)
# ⚠️  模糊度: 80% — 需要澄清
# 💬 建议确认以下问题:
#   1. 你指的是哪个接口？REST API 还是 GraphQL？
#   2. 是想修复 bug、添加功能、还是重构？
```

### 技能健康检查

```bash
# 扫描所有技能，检测问题
skill-aggregator --clean

# 🧹 技能清洗报告
#   ├─ 总技能数: 390
#   ├─ 有效技能: 350
#   └─ 问题数量: 40
#
# 错误 (8)
#   💥 my-broken-skill — frontmatter 解析失败
#
# 警告 (10)
#   ⚠️  my-skill — 缺少描述
#   ⚠️  other-skill — 目录为空

# JSON 输出（适合 CI 集成）
skill-aggregator --clean --json | jq '.issues[] | select(.severity == "error")'
```

### Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# 一行推荐
results = recommend("给 API 加 JWT 认证", top_n=5)
for r in results:
    print(f"{r['skill']}: {r['score']:.0%}")

# 三段式：意图 → 澄清 → 匹配
intent = analyze_intent("优化数据库查询性能")
if intent['ambiguity'] > 0.3:
    for q in intent['clarifying']:
        print(f"❓ {q}")
else:
    results = match_by_intent(intent, top_n=5)
```

---

## 🔧 工作原理

```
你的任务描述
      ↓
┌─────────────────┐
│  意图分析引擎    │ → 领域 (coding/design/...)
│  (intent.py)    │ → 活动类型 (create/fix/...)
│                 │ → 技术栈检测 (React/Docker/...)
│                 │ → 模糊度评估
└────────┬────────┘
         ↓ 如果模糊 → 输出澄清问题
         ↓ 如果清晰 →
┌─────────────────┐
│  技能匹配引擎    │ → TF-IDF 余弦相似度
│  (matcher.py)   │ → 关键词精确匹配
│  + jieba 分词   │ → 领域 + 优先级加权
│                 │ → Top-N 排序输出
└────────┬────────┘
         ↓
┌─────────────────┐
│  技能索引        │ ← 自动从 config.yaml 发现目录
│  (indexer.py)   │ ← 增量更新 (hash 检测)
│                 │ ← 去重 + 元数据提取
└─────────────────┘
```

---

## 📦 安装

```bash
# pip 安装
pip install skill-aggregator

# 可选：安装中文分词支持
pip install jieba

# 开发安装
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e ".[dev]"
```

---

## 🌍 适用场景

- **个人开发者**：你有 50+ 个 AI 技能，经常忘记有哪些可以用
- **团队协作**：新人不知道团队积累了哪些 skill，用它快速发现
- **AI Agent 开发者**：你的 Agent 需要动态发现和推荐 skill
- **CI/CD 管道**：`skill-aggregator --clean --json` 检测 skill 健康状态

---

## 🤝 贡献

欢迎 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)

```bash
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e ".[dev]"
pytest tests/ -v
```

---

## 📄 许可证

MIT © 2026 [Vinger](https://github.com/Vinger-lee)

---

<p align="center">
  <sub>Made with ❤️ by Vinger · <a href="https://github.com/Vinger-lee/skill-aggregator">GitHub</a></sub>
</p>
