# Copyright (c) 2026 Vinger. MIT License.

"""意图分析引擎 — 从自然语言任务中提取结构化意图。

完全基于规则和关键词匹配，无外部 AI API 依赖。
"""

import re
from typing import Dict, List, Optional


# 预编译正则表达式（模块级优化）
_DOMAIN_REGEX = None
_ACTIVITY_REGEX = None


def _get_domain_regex():
    """获取预编译的领域关键词正则表达式。"""
    global _DOMAIN_REGEX
    if _DOMAIN_REGEX is None:
        _DOMAIN_REGEX = {
            domain: re.compile('|'.join(re.escape(kw) for kw in keywords), re.IGNORECASE)
            for domain, keywords in DOMAIN_KEYWORDS.items()
        }
    return _DOMAIN_REGEX


def _get_activity_regex():
    """获取预编译的活动关键词正则表达式。"""
    global _ACTIVITY_REGEX
    if _ACTIVITY_REGEX is None:
        _ACTIVITY_REGEX = {
            activity: re.compile('|'.join(re.escape(kw) for kw in keywords), re.IGNORECASE)
            for activity, keywords in ACTIVITY_KEYWORDS.items()
        }
    return _ACTIVITY_REGEX


# 领域判定关键词表
DOMAIN_KEYWORDS = {
    "coding": [
        "代码", "修复", "bug", "写", "改", "重构", "编译", "部署", "api",
        "后端", "前端", "react", "python", "javascript", "typescript",
        "java", "go", "rust", "vue", "angular", "django", "flask",
        "fastapi", "express", "node", "npm", "pip", "git", "github",
        "代码库", "函数", "类", "方法", "变量", "接口", "服务",
    ],
    "creative": [
        "动画", "设计", "视觉", "艺术", "绘画", "音乐", "3d", "canvas",
        "颜色", "布局", "主题", "特效", "渲染", "shader", "材质",
        "粒子", "水墨", "墨水", "滚动", "过渡", "缓动", "动效",
    ],
    "finance": [
        "股票", "量化", "回测", "策略", "交易", "资金", "买", "卖",
        "etf", "k线", "涨跌", "收益", "风险", "仓位", "止损",
        "指标", "因子", "alpha", "beta", "夏普", "最大回撤",
    ],
    "devops": [
        "部署", "服务器", "docker", "ci", "cd", "配置", "环境",
        "安装", "容器", "kubernetes", "k8s", "nginx", "监控",
        "日志", "运维", "发布", "上线", "回滚",
    ],
    "research": [
        "研究", "搜索", "查", "资料", "论文", "学习", "阅读",
        "了解", "调研", "分析", "探索", "文档", "教程",
    ],
    "data": [
        "数据", "分析", "统计", "生成", "报表", "图表", "可视化",
        "数据库", "sql", "查询", "导出", "导入", "清洗",
    ],
    "design": [
        "ui", "布局", "样式", "颜色", "字体", "主题", "暗色",
        "响应式", "组件", "界面", "交互", "用户体验", "ux",
    ],
    "social": [
        "发", "分享", "tg", "telegram", "推送", "通知", "消息",
        "邮件", "微信", "钉钉", "飞书", "slack",
    ],
}

# 活动判定关键词表
ACTIVITY_KEYWORDS = {
    "create": [
        "创建", "写", "做", "搞", "生成", "新建", "开发", "实现",
        "构建", "制作", "添加", "加", "增加", "建立",
    ],
    "fix": [
        "修复", "修", "改", "bug", "问题", "错误", "不正常",
        "不工作", "失败", "报错", "异常", "故障",
    ],
    "analyze": [
        "分析", "查", "看", "研究", "评估", "检查", "审查",
        "诊断", "排查", "调查", "了解", "理解",
    ],
    "review": [
        "审查", "检查", "review", "看代码", "代码审查",
        "评审", "复查", "验收",
    ],
    "deploy": [
        "部署", "发布", "上线", "推", "发版", "release",
        "交付", "投产",
    ],
    "test": [
        "测试", "验证", "跑", "试一下", "检查", "测一下",
        "试试", "验证一下",
    ],
    "optimize": [
        "优化", "加速", "改进", "改善", "提升", "性能",
        "效率", "快一点", "慢",
    ],
    "debug": [
        "调试", "排查", "问题", "不工作", "不跑", "为什么",
        "怎么回事", "出错",
    ],
    "learn": [
        "学习", "学", "了解", "认识", "教程", "怎么用",
        "如何", "教我",
    ],
    "design": [
        "设计", "布局", "ui", "美化", "样式", "好看",
        "界面", "交互",
    ],
    "configure": [
        "配置", "设置", "安装", "装", "配", "初始化",
        "setup", "config",
    ],
}

# 技术栈关键词模式
TECH_STACK_PATTERNS = [
    r"\b(react|vue|angular|svelte|next\.?js|nuxt)\b",
    r"\b(python|javascript|typescript|java|go|rust|php|ruby|swift|kotlin)\b",
    r"\b(three\.?js|p5\.?js|canvas|webgl|pixi\.?js)\b",
    r"\b(docker|kubernetes|k8s|terraform|ansible)\b",
    r"\b(django|flask|fastapi|express|spring|rails)\b",
    r"\b(mysql|postgresql|mongodb|redis|elasticsearch)\b",
    r"\b(aws|azure|gcp|阿里云|腾讯云)\b",
]

# 项目名称模式（可扩展）
PROJECT_PATTERNS = [
    r"\bskill[-_]?aggregator\b",
]

# 模糊词列表
AMBIGUOUS_WORDS = [
    "搞一下", "弄一弄", "那个", "这个", "东西", "玩意",
    "整一下", "来一个", "帮我", "给我", "一下",
]


def analyze_intent(task: str) -> Dict:
    """分析用户任务的意图。

    Args:
        task: 用户任务描述

    Returns:
        意图分析结果字典，包含:
        - domain: 领域
        - activity: 活动类型
        - stack: 技术栈列表
        - goal: 简化的目标描述
        - ambiguity: 模糊度 (0.0-1.0)
        - clarifying: 澄清问题列表（如果模糊度 > 0.3）
    """
    task_lower = task.lower()

    # 1. 提取领域（使用预编译正则）
    domain_regex = _get_domain_regex()
    domain_scores = {}
    for domain, regex in domain_regex.items():
        matches = regex.findall(task_lower)
        if matches:
            domain_scores[domain] = len(matches)

    # 选择得分最高的领域
    if domain_scores:
        domain = max(domain_scores, key=domain_scores.get)
        domain_confidence = min(domain_scores[domain] / 3.0, 1.0)
    else:
        domain = "general"
        domain_confidence = 0.3

    # 2. 提取活动类型（使用预编译正则）
    activity_regex = _get_activity_regex()
    activity_scores = {}
    for activity, regex in activity_regex.items():
        matches = regex.findall(task_lower)
        if matches:
            activity_scores[activity] = len(matches)

    if activity_scores:
        activity = max(activity_scores, key=activity_scores.get)
        activity_confidence = min(activity_scores[activity] / 2.0, 1.0)
    else:
        activity = "general"
        activity_confidence = 0.3

    # 3. 提取技术栈
    stack = []
    for pattern in TECH_STACK_PATTERNS:
        matches = re.findall(pattern, task_lower, re.IGNORECASE)
        stack.extend(matches)
    stack = list(set(stack))  # 去重

    # 4. 提取项目名称
    project = None
    for pattern in PROJECT_PATTERNS:
        match = re.search(pattern, task_lower, re.IGNORECASE)
        if match:
            project = match.group(0)
            break

    # 5. 计算模糊度
    ambiguity = 0.5  # 基础模糊度

    # 包含具体技术名词 → 更明确
    if stack:
        ambiguity -= 0.2

    # 包含具体项目名 → 更明确
    if project:
        ambiguity -= 0.3

    # 包含具体活动动词 → 更明确
    if activity != "general":
        ambiguity -= 0.2

    # 句子很短 → 更模糊
    if len(task) < 5:
        ambiguity += 0.3

    # 包含模糊词 → 更模糊
    if any(word in task_lower for word in AMBIGUOUS_WORDS):
        ambiguity += 0.3

    # 无技术栈关键词 → 更模糊
    if not stack and domain == "general":
        ambiguity += 0.2

    # Clamp 到 0.0-1.0
    ambiguity = max(0.0, min(1.0, ambiguity))

    # 6. 生成简化目标描述
    goal = task.strip()
    if len(goal) > 50:
        goal = goal[:47] + "..."

    # 7. 生成澄清问题（如果模糊度 > 0.3）
    clarifying = None
    if ambiguity > 0.3:
        clarifying = _generate_clarifying_questions(
            task, domain, activity, stack, project, domain_confidence, activity_confidence
        )

    return {
        "domain": domain,
        "domain_confidence": domain_confidence,
        "activity": activity,
        "activity_confidence": activity_confidence,
        "stack": stack,
        "project": project,
        "goal": goal,
        "ambiguity": ambiguity,
        "clarifying": clarifying,
    }


def _generate_clarifying_questions(
    task: str,
    domain: str,
    activity: str,
    stack: List[str],
    project: Optional[str],
    domain_confidence: float,
    activity_confidence: float,
) -> List[Dict]:
    """生成澄清问题。

    Args:
        task: 原始任务
        domain: 检测到的领域
        activity: 检测到的活动
        stack: 技术栈
        project: 项目名称
        domain_confidence: 领域置信度
        activity_confidence: 活动置信度

    Returns:
        澄清问题列表
    """
    questions = []

    # 如果领域不确定
    if domain_confidence < 0.6:
        questions.append({
            "option": "A",
            "label": "代码开发/修复",
            "detail": "编写代码、修复 bug、重构代码等编程任务",
        })
        questions.append({
            "option": "B",
            "label": "视觉设计/动画",
            "detail": "创建动画效果、视觉设计、UI 美化等创意任务",
        })
        questions.append({
            "option": "C",
            "label": "量化回测/数据分析",
            "detail": "量化策略、数据分析、图表生成等数据任务",
        })

    # 如果项目不确定
    if not project:
        questions.append({
            "option": "A" if not questions else chr(ord(questions[-1]["option"]) + 1),
            "label": "在前端项目",
            "detail": "Web 前端项目（React/Vue、UI 动画效果）",
        })
        questions.append({
            "option": chr(ord(questions[-1]["option"]) + 1),
            "label": "在后端/数据项目",
            "detail": "后端服务或数据处理项目（API、数据分析）",
        })
        questions.append({
            "option": chr(ord(questions[-1]["option"]) + 1),
            "label": "新建项目",
            "detail": "创建一个全新的项目",
        })

    # 如果活动不确定
    if activity_confidence < 0.6:
        questions.append({
            "option": "A" if not questions else chr(ord(questions[-1]["option"]) + 1),
            "label": "创建新功能",
            "detail": "从零开始实现一个新的功能或模块",
        })
        questions.append({
            "option": chr(ord(questions[-1]["option"]) + 1),
            "label": "修复问题",
            "detail": "修复现有代码的 bug 或问题",
        })
        questions.append({
            "option": chr(ord(questions[-1]["option"]) + 1),
            "label": "分析/研究",
            "detail": "分析代码、研究问题、了解实现原理",
        })

    return questions if questions else None
