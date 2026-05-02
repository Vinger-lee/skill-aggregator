# 🔮 Skill Aggregator

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/dependencies-jieba%20%7C%20stdlib-green" alt="Dependencies">
  <br>
  <b>🧠 你的 AI 助手有 400+ 个技能，但你只知道 10 个。<br>Skill Aggregator 帮你找出该用哪个。</b>
</p>

[English](README.md) | 简体中文

---

## 🤔 这是解决什么问题的？

你给 AI 助手装了 Superpowers、Karpathy 的 Planning with Files、还有一堆插件……实际积累了 **400+ 个内置技能**。

但每次遇到新任务：
- 🔴 自己手写 prompt
- 🔴 去文件夹里翻 skill 名字
- 🔴 根本不知道有个 skill 正好能干这事

**Skill Aggregator 就是 AI 技能的"搜索引擎"**——说你要干什么，它告诉你该用哪个 skill。

```
你: "用 Canvas 做粒子动画"
Skill Aggregator: 👉 p5js (65%) + pixel-art (45%) + creative-ideation (30%)
```

---

## ⚡ 三秒上手

```bash
pip install skill-aggregator

# 用自然语言描述任务
skill-aggregator "给用户系统加 JWT 登录验证"
```

输出：
```
🎯 意图分析结果
  ├─ 领域: coding (可信度: 80%)
  ├─ 活动: create (可信度: 66%)
  └─ 模糊度: 10% ✓ 足够明确

📋 Top-8 推荐技能
  ├─ 65%  systematic-debugging
  ├─ 45%  test-driven-development
  ├─ 40%  node-inspect-debugger
  ├─ 30%  planning-with-files
  ├─ 25%  github-code-review
  ├─ 20%  chinese-code-review
  └─ 15%  security-review

💡 组合建议: TDD + systematic-debugging 联动
```

---

## ✨ 亮点

| 功能 | 说明 |
|------|------|
| 🧠 **意图理解** | 不仅看关键词——你在修 bug 还是在做设计？自动判断 |
| 🈯 **中文原生** | jieba 分词，中文/中英混合随便写，精确匹配 |
| 🔄 **环境自适应** | 自动读 `~/.hermes/config.yaml`，不用配置目录 |
| 🎯 **四维评分** | 关键词(40%) + 领域(25%) + TF-IDF(20%) + 优先级(15%) |
| 🧹 **技能体检** | 400 个 skill 一键扫描：损坏的、缺描述的、重复的 |
| 📦 **极简依赖** | 纯标准库 + 可选 jieba |
| 🔌 **Python API** | `from skill_aggregator import recommend` 即可 |

---

## 🆚 对比

| 方案 | 智能匹配 | 中文分词 | 环境感知 | 技能清洗 | 零配置 |
|------|:--:|:--:|:--:|:--:|:--:|
| **Skill Aggregator** | ✅ | ✅ | ✅ | ✅ | ✅ |
| 手动翻文件夹 | ❌ | ❌ | ❌ | ❌ | — |
| 直接问 AI | ⚠️ | ⚠️ | ❌ | ❌ | ✅ |
| grep 搜 | ⚠️ | ❌ | ❌ | ❌ | ✅ |

---

## 📖 场景示例

### 模糊任务 → 自动澄清

```bash
skill-aggregator --intent-only "帮我搞一下那个"
# ⚠️  模糊度: 80% — 太模糊了，需要确认：
#   1. 你想搞什么？网页、接口、还是数据库？
#   2. 是要新增功能、修 bug、还是重构？
```

### 技能健康体检

```bash
skill-aggregator clean
# 🧹 技能清洗报告
#   ├─ 总技能数: 390
#   ├─ 有效技能: 350
#   └─ 问题数量: 40
#
# 💥 8 个错误 — frontmatter 损坏，建议修复
# ⚠️  10 个警告 — 缺描述，可自动修复
# ℹ️  22 个提示 — 缺 tags

# 自动修复
skill-aggregator clean --fix
```

### 集成到代码里

```python
from skill_aggregator import analyze_intent, recommend

# 自动匹配
results = recommend("写一个 WebSocket 实时聊天", top_n=3)
for r in results:
    print(f"✅ {r['skill']} (匹配度 {r['score']:.0%})")

# 需要确认时
intent = analyze_intent("优化一下性能")
if intent['ambiguity'] > 0.3:
    print("🤔 需要确认：")
    for q in intent['clarifying']:
        print(f"  ❓ {q}")
```

---

## 🔧 架构

```
你的任务描述
      ↓
┌─────────────────┐
│  意图分析引擎    │ → 领域识别 + 活动类型 + 技术栈 + 模糊度
└────────┬────────┘
         ↓ 模糊？→ 生成澄清问题
         ↓ 清晰？→
┌─────────────────┐
│  技能匹配引擎    │ → TF-IDF + jieba 分词 + 四维评分
└────────┬────────┘
         ↓
┌─────────────────┐
│  技能索引        │ ← 自动发现 config.yaml 里的目录
│  + 清洗器        │ ← 增量更新 + 去重 + 健康检测
└─────────────────┘
```

---

## 📦 安装

```bash
pip install skill-aggregator
pip install jieba          # 可选，中文分词

# 开发用
git clone https://github.com/Vinger-lee/skill-aggregator.git
cd skill-aggregator
pip install -e ".[dev]"
```

---

## 🌍 谁需要这个？

- **个人开发者** — 装了 50+ 个 AI 技能，根本记不住
- **团队** — 新人不知道团队积累了什么 skill，用它快速发现
- **Agent 开发者** — 写 AI Agent 时，用它动态推荐技能
- **CI 管道** — `clean --json` 检测技能健康

---

## 🤝 贡献

欢迎 PR，详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 📄 许可证

MIT © 2026 [Vinger](https://github.com/Vinger-lee)

---

<p align="center">
  <sub>Made with ❤️ by Vinger · <a href="https://github.com/Vinger-lee/skill-aggregator">GitHub</a></sub>
</p>
