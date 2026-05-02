# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-jieba%20%7C%20stdlib-green" alt="Dependencies">
  <br>
  <b>🧠 Your AI assistant has 400+ skills. You only know 10. Skill Aggregator finds the right one.</b>
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

## 🤔 The Problem

You've installed Superpowers, Karpathy's Planning with Files, and dozens of plugins. Your AI agent has **400+ built-in skills**.

But every time you start a new task:
- 🔴 You write prompts from scratch
- 🔴 You manually browse folders looking for skill names
- 🔴 You have no idea there's a skill that does exactly what you need

**Skill Aggregator is a search engine for AI skills** — describe what you want, it tells you which skill to use.

```
You: "Build a particle animation with Canvas"
Skill Aggregator: 👉 p5js (65%) + pixel-art (45%) + creative-ideation (30%)
```

---

## ⚡ Quick Start

```bash
pip install skill-aggregator

# Describe your task in natural language
skill-aggregator "Add JWT authentication to my REST API"
```

Output:
```
🎯 Intent Analysis
  ├─ Domain: coding (confidence: 80%)
  ├─ Activity: create (confidence: 66%)
  └─ Ambiguity: 10% ✓ Clear enough

📋 Top-8 Recommendations
  ├─ 65%  systematic-debugging
  ├─ 45%  test-driven-development
  ├─ 40%  node-inspect-debugger
  ├─ 30%  planning-with-files
  ├─ 25%  github-code-review
  └─ 15%  security-review

💡 Combo: TDD + systematic-debugging
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Intent Understanding** | Detects what you're really doing — fixing a bug? designing UI? |
| 🈯 **Chinese + English** | jieba segmentation for Chinese, regex for English |
| 🔄 **Environment-Aware** | Auto-discovers skill dirs from `~/.hermes/config.yaml` |
| 🎯 **4-Dimensional Scoring** | Keywords (40%) + Domain (25%) + TF-IDF (20%) + Priority (15%) |
| 🧹 **Skill Health Check** | Scan 400+ skills for corruption, missing fields, duplicates |
| 📦 **Lightweight** | Pure stdlib + optional jieba |
| 🔌 **Python API** | `from skill_aggregator import recommend` — one line |

---

## 🆚 Comparison

| Solution | Smart Matching | Chinese NLP | Env-Aware | Health Scan | Zero Config |
|----------|:--:|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ TF-IDF | ✅ jieba | ✅ auto | ✅ | ✅ |
| Browse folders | ❌ | ❌ | ❌ | ❌ | — |
| Ask AI directly | ⚠️ partial | ⚠️ partial | ❌ | ❌ | ✅ |
| grep search | ⚠️ keyword | ❌ | ❌ | ❌ | ✅ |

---

## 📖 Usage

### Intent Analysis Mode

```bash
skill-aggregator --intent-only "fix that thing in the API"
# ⚠️ Ambiguity: 80% — needs clarification
# ❓ Which API endpoint? REST or GraphQL?
# ❓ Are you fixing a bug, adding a feature, or refactoring?
```

### Skill Health Check

```bash
skill-aggregator --clean
# 🧹 Health Report
#   ├─ Total: 390  | Valid: 350  | Issues: 40
#   💥 8 errors — broken frontmatter
#   ⚠️ 10 warnings — missing descriptions

# JSON output (CI-friendly)
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
    for q in intent['clarifying']:
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
│  Intent Engine   │ → Domain + Activity + Stack + Ambiguity
└────────┬────────┘
         ↓ Vague? → generates clarifying questions
         ↓ Clear? →
┌─────────────────┐
│  Match Engine    │ → TF-IDF + jieba + 4-dimension scoring
└────────┬────────┘
         ↓
┌─────────────────┐
│  Skill Index     │ ← auto-discovered from config.yaml
│  + Cleaner       │ ← incremental + dedup + health scan
└─────────────────┘
```

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

## 🌍 Who Needs This?

- **Solo devs** — 50+ AI skills installed, can't remember them all
- **Teams** — newcomers don't know what skills the team has accumulated
- **Agent builders** — dynamically recommend skills in your AI agent pipeline
- **CI pipelines** — `--clean --json` for skill health monitoring

---

## 🤝 Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

MIT © 2026 [Vinger](https://github.com/Vinger-lee)

<p align="center">
  <sub>Made with ❤️ by Vinger · <a href="https://github.com/Vinger-lee/skill-aggregator">GitHub</a></sub>
</p>
