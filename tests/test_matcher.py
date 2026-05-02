#!/usr/bin/env python3
# Copyright (c) 2026 Vinger. MIT License.

"""测试脚本 — 验证匹配算法。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from matcher import TaskMatcher

# 测试任务
test_tasks = [
    "修复 Three.js 地球的黑夜闪烁",
    "用 Canvas 给 feiyi-web 做墨水动画效果",
    "跑一下量化回测看看动量策略赚不赚钱",
    "debug React component state issue",
    "implement TDD for new feature",
]

matcher = TaskMatcher()

for task in test_tasks:
    print(f"\n{'=' * 60}")
    print(f"任务: {task}")
    print(f"{'=' * 60}")

    # 分析任务
    features = matcher.analyze(task)
    print(f"\n特征:")
    print(f"  - 领域: {features['domain']}")
    print(f"  - 活动: {features['activity']}")
    print(f"  - 技术栈: {features['tech_stack']}")
    print(f"  - 关键词: {features['keywords'][:10]}")

    # 匹配技能
    results = matcher.match(task, top_n=5)
    print(f"\nTop-5 匹配:")
    for i, result in enumerate(results, 1):
        print(
            f"  {i}. [{result['score']:.2f}] {result['skill']} ({result['category']})"
        )
