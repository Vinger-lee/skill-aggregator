---
name: skill-aggregator
description: "🧠 全能任务分析引擎 — 分析用户模糊的自然语言意图 → 确认需求 → 自动匹配并加载最优技能组合"
---

# 🧠 Skill Aggregator — 任务意图分析 + 技能推荐

## 核心流程（三段式工作流）

### Phase 1: 🎯 意图分析（Intent Analysis）
当用户说出一个自然语言任务时：

1. **收集信息**: 用户说了什么？项目上下文是什么？
2. **提取关键维度**:
   - **领域 (Domain)**: coding / creative / devops / research / data / finance / design / social / ...
   - **活动 (Activity)**: create / fix / analyze / review / deploy / test / optimize / debug / learn / design / configure / ...
   - **技术栈 (Stack)**: 
     - 前端: react / three.js / canvas / css / animejs / framer-motion / tailwind
     - 后端: python / node / fastapi / docker
     - 数据: pandas / akshare / backtrader / gradio
     - AI: openai / claude / coze / tts
   - **项目目标**: 用户想达到什么结果？
3. **调用分析引擎**:
   ```python
   from skill_aggregator import analyze_intent
   result = analyze_intent("用户的任务描述")
   # 返回: {domain, activity, stack, goal, ambiguity, skill_suggestions}
   ```

### Phase 2: 💬 需求确认（Clarify with User）
如果用户意图**模糊**（ambiguity > 0.3），使用 `clarify` 工具跟用户确认：

```python
from skill_aggregator import intent
# intent.ambiguity == 0.7 → 模糊，需要确认
clarify(question="我理解你想做关于...对吗？方向是A还是B？")
```

**确认原则**:
- 不要问太多问题（最多 4 个选项）
- 先说自己理解再问
- 用 emoji 让交流更友好

**如果意图明确**（ambiguity ≤ 0.3），跳过确认，直接到 Phase 3。

### Phase 3: 🔄 自动加载技能（Auto-Load Skills）
根据确认后的意图，自动加载 Top-5 最匹配的技能：

1. **查询匹配引擎**:
   ```bash
   python3 ~/skill-aggregator/skill_aggregator/aggregator.py "确认后的任务"
   ```
   或 Python API:
   ```python
   from skill_aggregator import recommend
   skills = recommend("确认后的任务", top_n=5)
   ```

2. **加载技能**: 对每个推荐技能调用 `skill_view(name)`
3. **开始工作**: 按技能指导逐步执行任务

## 更新机制
每次新加 skill 后，立即手动重建索引：
```bash
python3 ~/skill-aggregator/scripts/build_index.py --force
```
（已经内置在 `skill_manage` 创建流程中）

## 示例

### 用户说: "帮我搞一下那个网站的动画"
```
Phase 1: 意图分析
  ├─ 领域: creative / coding
  ├─ 活动: create / fix
  ├─ 技术栈: canvas, css, animation
  ├─ 目标: 网站动画效果
  └─ 模糊度: 0.7 ⬅️ 模糊，需要确认

Phase 2: 确认
  问: "你的项目是 Web 前端项目吗？
      你想做哪种动画？
      1️⃣ 3D 场景出场动效
      2️⃣ 页面滚动视差效果
      3️⃣ 卡片 hover 交互动画
      4️⃣ 其他（你来说）"


Phase 3: 加载技能
  → 水墨 → 加载: pixel-art, p5js, creative-ideation, systematic-debugging
  → 开始工作！
```

### 用户说: "跑一下动量回测，看看3000块能赚多少"
```
Phase 1: 意图分析
  ├─ 领域: finance / data
  ├─ 活动: analyze
  ├─ 技术栈: akshare, backtrader, python
  ├─ 目标: 动量策略回测，3000元本金
  └─ 模糊度: 0.1 ⬅️ 很明确，跳过 Phase 2

Phase 3: 加载技能
  → 加载: systematic-debugging, test-driven-development
  → 直接干活！
```
