# Copyright (c) 2026 Vinger. MIT License.

"""任务-技能匹配引擎 — 分析任务并推荐最适合的技能。

使用纯 Python 实现的 TF-IDF 和余弦相似度算法，无外部依赖。
"""

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import Counter


class TaskMatcher:
    """任务-技能匹配引擎。

    分析用户任务描述，提取特征并匹配最相关的技能。
    """

    def __init__(self, index_path: Path = None):
        """初始化匹配引擎。

        Args:
            index_path: 索引文件路径，默认为 ~/.skill-aggregator/index.json
        """
        if index_path is None:
            index_path = Path.home() / ".skill-aggregator" / "index.json"
        self.index_path = index_path
        self.index_data = self._load_index()

        # 核心工作流技能（优先级加权）
        self.priority_skills = {
            "systematic-debugging",
            "planning-with-files",
            "verification-before-completion",
            "testing-evidence-collector",
            "test-driven-development",
        }

    def _load_index(self) -> Dict:
        """加载技能索引。"""
        if not self.index_path.exists():
            # 索引不存在，尝试构建
            from .indexer import build_index

            return build_index(force=True)

        with open(self.index_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _tokenize(self, text: str) -> List[str]:
        """分词（简单实现）。

        Args:
            text: 输入文本

        Returns:
            词列表
        """
        # 转小写并提取单词
        text = text.lower()
        words = re.findall(r"\b\w+\b", text)
        # 过滤停用词
        stopwords = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "being",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "should",
            "can",
            "could",
            "may",
            "might",
            "must",
            "这",
            "是",
            "的",
            "了",
            "在",
            "和",
            "有",
            "我",
            "你",
            "他",
            "她",
            "它",
            "们",
            "个",
            "用",
            "给",
            "把",
            "让",
            "要",
            "会",
            "能",
            "可以",
        }
        return [w for w in words if w not in stopwords and len(w) > 1]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """计算词频（TF）。

        Args:
            tokens: 词列表

        Returns:
            词频字典
        """
        if not tokens:
            return {}
        counter = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in counter.items()}

    def _compute_idf(self, documents: List[List[str]]) -> Dict[str, float]:
        """计算逆文档频率（IDF）。

        Args:
            documents: 文档列表（每个文档是词列表）

        Returns:
            IDF 字典
        """
        if not documents:
            return {}

        num_docs = len(documents)
        word_doc_count = Counter()

        for doc in documents:
            unique_words = set(doc)
            word_doc_count.update(unique_words)

        idf = {}
        for word, doc_count in word_doc_count.items():
            idf[word] = math.log(num_docs / (1 + doc_count))

        return idf

    def _compute_tfidf(
        self, tf: Dict[str, float], idf: Dict[str, float]
    ) -> Dict[str, float]:
        """计算 TF-IDF。

        Args:
            tf: 词频字典
            idf: IDF 字典

        Returns:
            TF-IDF 字典
        """
        return {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}

    def _cosine_similarity(
        self, vec1: Dict[str, float], vec2: Dict[str, float]
    ) -> float:
        """计算余弦相似度。

        Args:
            vec1: 向量 1（词-权重字典）
            vec2: 向量 2（词-权重字典）

        Returns:
            余弦相似度（0-1）
        """
        if not vec1 or not vec2:
            return 0.0

        # 计算点积
        common_words = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[w] * vec2[w] for w in common_words)

        # 计算模长
        norm1 = math.sqrt(sum(v**2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v**2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def analyze(self, task: str) -> Dict:
        """分析任务描述，提取特征。

        Args:
            task: 任务描述

        Returns:
            任务特征字典
        """
        task_lower = task.lower()

        # 提取领域（domain）
        domain_patterns = {
            "coding": [
                "code",
                "bug",
                "fix",
                "debug",
                "implement",
                "refactor",
                "test",
                "代码",
                "修复",
                "实现",
                "重构",
                "测试",
            ],
            "design": [
                "design",
                "ui",
                "ux",
                "mockup",
                "prototype",
                "设计",
                "界面",
                "原型",
            ],
            "devops": [
                "deploy",
                "ci",
                "cd",
                "docker",
                "kubernetes",
                "部署",
                "容器",
            ],
            "data": [
                "data",
                "analysis",
                "visualization",
                "数据",
                "分析",
                "可视化",
            ],
            "finance": ["stock", "trading", "backtest", "量化", "回测", "股票"],
            "creative": ["animation", "3d", "canvas", "动画", "特效"],
        }

        domains = []
        for domain, keywords in domain_patterns.items():
            if any(kw in task_lower for kw in keywords):
                domains.append(domain)

        # 提取活动类型（activity）
        activity_patterns = {
            "create": ["create", "build", "make", "add", "创建", "构建", "添加"],
            "fix": ["fix", "debug", "solve", "修复", "解决", "调试"],
            "analyze": ["analyze", "review", "check", "分析", "检查", "审查"],
            "optimize": ["optimize", "improve", "enhance", "优化", "改进", "提升"],
            "test": ["test", "verify", "validate", "测试", "验证"],
            "deploy": ["deploy", "release", "publish", "部署", "发布"],
        }

        activities = []
        for activity, keywords in activity_patterns.items():
            if any(kw in task_lower for kw in keywords):
                activities.append(activity)

        # 提取技术栈
        tech_patterns = [
            r"\b(react|vue|angular|svelte|next\.?js)\b",
            r"\b(python|javascript|typescript|java|go|rust)\b",
            r"\b(three\.?js|p5\.?js|canvas|webgl)\b",
            r"\b(docker|kubernetes|terraform)\b",
            r"\b(django|flask|fastapi|express)\b",
        ]

        tech_stack = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, task_lower)
            tech_stack.extend(matches)

        # 提取关键词
        tokens = self._tokenize(task)

        return {
            "domain": domains or ["general"],
            "activity": activities or ["general"],
            "tech_stack": tech_stack,
            "keywords": tokens,
        }

    def match(self, task: str, top_n: int = 8) -> List[Dict]:
        """匹配任务与技能。

        Args:
            task: 任务描述
            top_n: 返回 Top-N 结果

        Returns:
            匹配结果列表（按得分降序）
        """
        # 分析任务
        task_features = self.analyze(task)
        task_tokens = task_features["keywords"]

        # 准备所有技能的文档（用于 IDF 计算）
        skills = self.index_data.get("skills", [])
        all_docs = []
        for skill in skills:
            skill_text = f"{skill['name']} {skill['description']} {' '.join(skill.get('tags', []))} {' '.join(skill.get('keywords', []))}"
            skill_tokens = self._tokenize(skill_text)
            all_docs.append(skill_tokens)

        # 计算 IDF
        idf = self._compute_idf([task_tokens] + all_docs)

        # 计算任务的 TF-IDF
        task_tf = self._compute_tf(task_tokens)
        task_tfidf = self._compute_tfidf(task_tf, idf)

        # 匹配每个技能
        results = []
        for skill in skills:
            # 1. 关键词精确匹配
            skill_text = f"{skill['name']} {skill['description']}".lower()
            keyword_matches = sum(
                1 for kw in task_features["keywords"] if kw in skill_text
            )
            keyword_score = min(keyword_matches / max(len(task_features["keywords"]), 1), 1.0)

            # 2. 领域匹配
            domain_score = 0.0
            skill_category = skill.get("category", "general").lower()
            if skill_category in task_features["domain"]:
                domain_score = 1.0
            elif "general" in task_features["domain"]:
                domain_score = 0.5

            # 3. TF-IDF 余弦相似度
            skill_tokens = self._tokenize(
                f"{skill['name']} {skill['description']} {' '.join(skill.get('tags', []))}"
            )
            skill_tf = self._compute_tf(skill_tokens)
            skill_tfidf = self._compute_tfidf(skill_tf, idf)
            similarity_score = self._cosine_similarity(task_tfidf, skill_tfidf)

            # 4. 优先级加权
            priority_bonus = 0.0
            if skill["name"] in self.priority_skills:
                priority_bonus = 0.15

            # 综合评分
            score = (
                keyword_score * 0.40
                + domain_score * 0.25
                + similarity_score * 0.20
                + priority_bonus * 0.15
            )

            results.append(
                {
                    "skill": skill["name"],
                    "score": score,
                    "description": skill["description"],
                    "category": skill.get("category", "general"),
                    "file_path": skill.get("file_path", ""),
                }
            )

        # 排序并返回 Top-N
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_n]


def analyze(task: str) -> Dict:
    """分析任务（便捷函数）。

    Args:
        task: 任务描述

    Returns:
        任务特征字典
    """
    matcher = TaskMatcher()
    return matcher.analyze(task)


def match(task: str, top_n: int = 8) -> List[Dict]:
    """匹配任务与技能（便捷函数）。

    Args:
        task: 任务描述
        top_n: 返回 Top-N 结果

    Returns:
        匹配结果列表
    """
    matcher = TaskMatcher()
    return matcher.match(task, top_n=top_n)


def match_by_intent(intent: Dict, top_n: int = 8) -> List[Dict]:
    """根据意图分析结果匹配技能（比原始任务文本匹配更精准）。

    Args:
        intent: 意图分析结果字典（来自 intent.analyze_intent）
        top_n: 返回 Top-N 结果

    Returns:
        匹配结果列表（按得分降序）
    """
    # 构建增强查询文本
    query_parts = []

    # 添加领域
    if intent.get("domain") and intent["domain"] != "general":
        query_parts.append(intent["domain"])

    # 添加活动
    if intent.get("activity") and intent["activity"] != "general":
        query_parts.append(intent["activity"])

    # 添加技术栈
    if intent.get("stack"):
        query_parts.extend(intent["stack"])

    # 添加目标描述
    if intent.get("goal"):
        query_parts.append(intent["goal"])

    # 组合成查询文本
    enhanced_query = " ".join(query_parts)

    # 使用现有的匹配引擎
    matcher = TaskMatcher()
    results = matcher.match(enhanced_query, top_n=top_n)

    # 根据意图添加优先级加权
    for result in results:
        skill_category = result.get("category", "general").lower()

        # 领域匹配加权
        if intent.get("domain") and skill_category == intent["domain"]:
            result["score"] = min(result["score"] * 1.2, 1.0)

        # 技术栈匹配加权
        if intent.get("stack"):
            skill_desc = result.get("description", "").lower()
            stack_matches = sum(1 for tech in intent["stack"] if tech in skill_desc)
            if stack_matches > 0:
                result["score"] = min(result["score"] * (1.0 + stack_matches * 0.1), 1.0)

    # 重新排序
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_n]

