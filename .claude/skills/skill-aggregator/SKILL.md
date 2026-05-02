---
name: skill-aggregator
description: "🧠 任务意图分析 + 技能匹配引擎"
---

# Skill Aggregator

## 三阶段工作流
1. **意图分析**: 分析自然语言任务 → domain/activity/stack/goal/ambiguity
2. **需求确认**: 模糊时问用户澄清
3. **加载技能**: 匹配 Top-5 技能开始工作

## 用法
```bash
python3 ~/skill-aggregator/skill_aggregator/aggregator.py "任务描述"
```

## 自动更新索引
当检测到 `.hermes/skills/` 或 `.claude/agents/` 有新文件时重建：
```bash
python3 ~/skill-aggregator/scripts/build_index.py --force
```
