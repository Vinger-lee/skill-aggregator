#!/usr/bin/env python3
# Copyright (c) 2026 Vinger. MIT License.

"""pytest 测试套件 — 验证意图分析和匹配算法。"""

import pytest
from skill_aggregator import recommend, analyze_intent


class TestIntentAnalysis:
    def test_coding_domain(self):
        intent = analyze_intent("修复登录页面的 JWT 认证 bug")
        assert intent["domain"] == "coding"
        assert intent["activity"] == "fix"
        assert intent["ambiguity"] < 0.5

    def test_creative_domain(self):
        intent = analyze_intent("用 Canvas 做粒子动画效果")
        assert intent["domain"] == "creative"
        assert intent["activity"] == "create"

    def test_vague_intent(self):
        intent = analyze_intent("帮我搞一下那个")
        assert intent["ambiguity"] > 0.5
        assert len(intent.get("clarifying", [])) > 0

    def test_chinese_english_mixed(self):
        intent = analyze_intent("用 React 写一个登录页面")
        assert intent["domain"] == "coding"
        assert "react" in [s.lower() for s in intent.get("stack", [])]

    def test_finance_domain(self):
        intent = analyze_intent("跑一下股票回测看看策略表现")
        assert intent["domain"] == "finance"


class TestRecommendations:
    def test_recommend_returns_results(self):
        results = recommend("用 Python 写单元测试", top_n=5, verbose=False)
        assert len(results) > 0
        assert all("skill" in r for r in results)
        assert all("score" in r for r in results)

    def test_recommend_sorted_by_score(self):
        results = recommend("部署 Docker 容器到云服务器", top_n=8, verbose=False)
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_empty_input_graceful(self):
        results = recommend("", top_n=3, verbose=False)
        assert isinstance(results, list)

    def test_pure_english(self):
        results = recommend("fix auth bug in login page", top_n=3, verbose=False)
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
