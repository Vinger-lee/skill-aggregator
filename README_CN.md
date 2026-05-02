# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/github/stars/Vinger-lee/skill-aggregator?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-zero_stdlib%2B-22bb33" alt="零依赖">
  <img src="https://img.shields.io/badge/中文-支持-ff6600" alt="中文支持">
  <br>
  <b>🤖 你的 AI 助手会 400+ 个技能，但你只知道 10 个。这个工具帮你找到该用哪个。</b>
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

## 🚀 这是啥？

**Skill Aggregator 是一个 AI 技能搜索引擎。** 你用中文或英文描述想做的事，它立刻告诉你该用哪个技能/插件/工具——再也不用翻文件夹瞎猜了。

```bash
# 一句话就能找到对的技能
skill-aggregator "用 Canvas 做个粒子动画"
# 👉 p5js (65%) + pixel-art (45%) + ideation (30%)
```

## ⚡ 快速开始

```bash
# 零依赖安装——纯 Python 标准库
pip install skill-aggregator

# 或者直接克隆跑
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
python src/aggregator.py "给 API 添加 JWT 认证"
```

### 🔥 效果

```
🎯 意图分析
  ├─ 领域: coding (80%)
  ├─ 活动: create (66%)
  └─ 模糊度: 10% ✓ 足够清晰

📋 Top-8 推荐
  ├─ 65%  systematic-debugging
  ├─ 45%  test-driven-development
  ├─ 40%  node-inspect-debugger
  ├─ 30%  code-review
  ├─ 25%  writing-plans
  └─ 15%  security-review

💡 推荐组合: TDD + systematic-debugging
```

---

## ✨ 功能特性

| 功能 | 说明 | 为什么重要 |
|------|------|-----------|
| 🧠 **意图引擎** | 自动分析你真正在做什么——修 bug？搭 UI？ | 不会推荐错的技能 |
| 🈯 **中英文双语** | jieba 分词 + 英文正则 | 输入中文英文都能用 |
| 🔄 **自动发现** | 扫描 `config.yaml` 里的技能目录 | 装好即用，零配置 |
| 🎯 **四维评分** | 关键词(40%) + 领域(25%) + TF-IDF(20%) + 优先级(15%) | 比 grep 聪明得多 |
| 🧹 **健康检查** | 扫描 400+ 技能，检测错误/缺失/重复 | 秒发现坏掉的技能 |
| 📦 **零依赖** | 纯 Python 标准库 + 可选 jieba | 2 秒装完 |
| 🔌 **Python API** | `from skill_aggregator import recommend` | 一行代码集成 |

---

## 📖 使用方式

### 意图分析（自动检测模糊度）

```bash
# 说得模糊？它会反问澄清
skill-aggregator --intent-only "修一下 API 那个东西"
# ⚠️ 模糊度: 80%
# ❓ 哪个端点？REST 还是 GraphQL？
# ❓ 修 bug、加功能、还是重构？
```

### 技能健康检查

```bash
# 扫描所有技能的问题
skill-aggregator --clean
# 🧹 总数: 390 | 有效: 350 | 问题: 40
#   8 个错误 —— frontmatter 损坏
#   10 个警告 —— 缺少描述

# JSON 输出给 CI 用
skill-aggregator --clean --json | jq '.issues[] | select(.severity == "error")'

# 自动修复
skill-aggregator --clean --fix
```

### Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# 一行推荐
results = recommend("给 API 加 JWT 认证", top_n=5)
for r in results:
    print(f"{r['skill']}: {r['score']:.0%}")

# 三阶段：意图 → 澄清 → 匹配
intent = analyze_intent("优化数据库查询")
if intent['ambiguity'] > 0.3:
    for q in intent['clarifying_questions']:
        print(f"❓ {q}")
else:
    results = match_by_intent(intent, top_n=5)
```

---

## 🔧 架构

```
你的任务描述
      ↓
┌─────────────────┐
│  意图引擎        │ → 领域 + 活动 + 模糊度
└────────┬────────┘
         ↓ 模糊？→ 生成澄清问题
         ↓ 清晰？→
┌─────────────────┐
│  匹配引擎        │ → TF-IDF + 四维评分
└────────┬────────┘
         ↓
┌──────────────────────┐
│  技能索引             │ ← 自动从配置发现
│  + 清洁器             │ ← 健康检查 + 去重
└──────────────────────┘
```

---

## 🆚 为什么不用 grep？

| 方案 | 智能匹配 | 中文支持 | 自动发现 | 健康检查 |
|------|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ TF-IDF | ✅ jieba | ✅ | ✅ |
| 手动翻文件夹 | ❌ | ❌ | ❌ | ❌ |
| 直接问 AI | ⚠️ | ⚠️ | ❌ | ❌ |
| `grep -r` 搜 | ❌ | ❌ | ❌ | ❌ |

---

## 🌍 谁需要这个？

- **独立开发者** — 装了 50+ 个 AI 技能，记不住所有
- **团队** — 新人不知道团队积累了什么技能
- **Agent 构建者** — 在 AI agent 工作流中动态推荐技能
- **CI 流水线** — `--clean --json` 自动化监测技能健康

---

## 📦 安装

```bash
pip install skill-aggregator
pip install jieba          # 可选，用于中文分词

# 开发模式
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e ".[dev]"
```

---

## 🤝 贡献

欢迎 PR！见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📊 统计

<p align="center">
  <img src="https://img.shields.io/github/last-commit/Vinger-lee/skill-aggregator" alt="最近提交">
  <img src="https://img.shields.io/github/repo-size/Vinger-lee/skill-aggregator" alt="仓库大小">
  <img src="https://img.shields.io/github/languages/code-size/Vinger-lee/skill-aggregator" alt="代码大小">
  <img src="https://img.shields.io/github/languages/top/Vinger-lee/skill-aggregator" alt="主要语言">
</p>

---

MIT © 2026 [Vinger](https://github.com/Vinger-lee)

<p align="center">
  <sub>用 ❤️ 制作 · <a href="https://github.com/Vinger-lee/skill-aggregator">GitHub</a></sub>
</p>
