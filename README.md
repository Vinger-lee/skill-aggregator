# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/github/stars/Vinger-lee/skill-aggregator?style=social" alt="Stars">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/dependencies-zero_stdlib%2B-22bb33" alt="Zero Deps">
  <img src="https://img.shields.io/badge/中文-支持-ff6600" alt="中文支持">
  <br>
  <b>🤖 Your AI agent has 400+ skills. You only know 10. This finds the right one.</b>
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

## 🚀 What is Skill Aggregator?

**Skill Aggregator is a search engine for AI agent skills.** Describe what you want in plain English (or Chinese), and it instantly tells you which skill/plugin/tool to use — no more browsing folders or guessing skill names.

```bash
# One command to find the right skill
skill-aggregator "Build a particle animation with Canvas"
# 👉 p5js (65%) + pixel-art (45%) + ideation (30%)
```

## ⚡ Quick Start

```bash
# Zero deps — pure Python stdlib
pip install skill-aggregator

# Or clone and run instantly
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
python src/aggregator.py "Add JWT authentication to my API"
```

### 🔥 What you get

```
🎯 Intent Analysis
  ├─ Domain: coding (80%)
  ├─ Activity: create (66%)
  └─ Ambiguity: 10% ✓ Clear enough

📋 Top-8 Recommendations
  ├─ 65%  systematic-debugging
  ├─ 45%  test-driven-development
  ├─ 40%  node-inspect-debugger
  ├─ 30%  code-review
  ├─ 25%  writing-plans
  └─ 15%  security-review

💡 Combo: TDD + systematic-debugging
```

---

## ✨ Features

| Feature | What it does | Why you care |
|---------|-------------|--------------|
| 🧠 **Intent Engine** | Detects what you're *really* doing — fixing? building? designing? | Stops suggesting the wrong skill |
| 🈯 **Chinese + English** | jieba segmentation + regex | Works for both languages natively |
| 🔄 **Auto-Discovery** | Scans `config.yaml` for skill directories | Zero config needed |
| 🎯 **4D Scoring** | Keywords(40%) + Domain(25%) + TF-IDF(20%) + Priority(15%) | Smarter than grep |
| 🧹 **Health Check** | Scans 400+ skills for errors, missing fields, duplicates | Catch broken skills instantly |
| 📦 **Zero Dependencies** | Pure Python stdlib + optional jieba | Install in 2 seconds |
| 🔌 **Python API** | `from skill_aggregator import recommend` | One-liner integration |

---

## 📖 Usage

### Intent Analysis (auto-detect ambiguity)

```bash
# Vague? It asks clarifying questions
skill-aggregator --intent-only "fix that thing in the API"
# ⚠️ Ambiguity: 80%
# ❓ Which endpoint? REST or GraphQL?
# ❓ Bug, feature, or refactor?
```

### Skill Health Check

```bash
# Scan all skills for problems
skill-aggregator --clean
# 🧹 Total: 390 | Valid: 350 | Issues: 40
#   8 errors — broken frontmatter
#   10 warnings — missing descriptions

# JSON output for CI
skill-aggregator --clean --json | jq '.issues[] | select(.severity == "error")'

# Auto-fix what can be fixed
skill-aggregator --clean --fix
```

### Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# One-line recommendation
results = recommend("Add JWT auth to the API", top_n=5)
for r in results:
    print(f"{r['skill']}: {r['score']:.0%}")

# 3-phase: Intent → Clarify → Match
intent = analyze_intent("Optimize database queries")
if intent['ambiguity'] > 0.3:
    for q in intent['clarifying_questions']:
        print(f"❓ {q}")
else:
    results = match_by_intent(intent, top_n=5)
```

---

## 🔧 Architecture

```
Your task description
      ↓
┌─────────────────┐
│  Intent Engine   │ → Domain + Activity + Ambiguity
└────────┬────────┘
         ↓ Vague? → generates clarifying questions
         ↓ Clear? →
┌─────────────────┐
│  Match Engine    │ → TF-IDF + 4-dimension scoring
└────────┬────────┘
         ↓
┌──────────────────────┐
│  Skill Index          │ ← auto-discovered from config
│  + Cleaner            │ ← health scan + dedup
└──────────────────────┘
```

---

## 🆚 Why Not Just Grep?

| Solution | Smart Matching | Chinese | Auto-Discover | Health Scan |
|----------|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ TF-IDF | ✅ jieba | ✅ | ✅ |
| Browse folders | ❌ | ❌ | ❌ | ❌ |
| Ask AI directly | ⚠️ | ⚠️ | ❌ | ❌ |
| `grep -r` | ❌ | ❌ | ❌ | ❌ |

---

## 🌍 Who Needs This?

- **Solo devs** — 50+ AI skills installed, can't remember them all
- **Teams** — newcomers don't know what skills the team has accumulated
- **Agent builders** — dynamically recommend skills in your AI agent pipeline
- **CI pipelines** — `--clean --json` for automated skill health monitoring

---

## 📦 Install

```bash
pip install skill-aggregator
pip install jieba          # optional, for Chinese NLP

# Dev install
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e ".[dev]"
```

---

## 🤝 Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📊 Stats

<p align="center">
  <img src="https://img.shields.io/github/last-commit/Vinger-lee/skill-aggregator" alt="Last commit">
  <img src="https://img.shields.io/github/repo-size/Vinger-lee/skill-aggregator" alt="Repo size">
  <img src="https://img.shields.io/github/languages/code-size/Vinger-lee/skill-aggregator" alt="Code size">
  <img src="https://img.shields.io/github/languages/top/Vinger-lee/skill-aggregator" alt="Top language">
</p>

---

MIT © 2026 [Vinger](https://github.com/Vinger-lee)

<p align="center">
  <sub>Made with ❤️ · <a href="https://github.com/Vinger-lee/skill-aggregator">GitHub</a></sub>
</p>
