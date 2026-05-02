# Copyright (c) 2026 Vinger. MIT License.

"""Skill Aggregator - AI Agent 元技能系统

通过三段式工作流（意图分析 → 澄清确认 → 技能匹配）自动分析任务并推荐最适合的技能。

核心功能：
- 意图分析：从自然语言任务描述中提取结构化意图
- 技能匹配：基于多维度算法匹配最相关的技能
- 自动索引：检测技能文件变化，自动重建索引

使用示例：
    >>> from skill_aggregator import analyze_intent, recommend
    >>>
    >>> # 方式 1：直接推荐（自动处理意图分析）
    >>> results = recommend("修复 Three.js 地球的黑夜闪烁", top_n=5)
    >>>
    >>> # 方式 2：分步执行
    >>> intent = analyze_intent("修复 Three.js 地球的黑夜闪烁")
    >>> from skill_aggregator import match_by_intent
    >>> results = match_by_intent(intent, top_n=5)

命令行使用：
    $ skill-aggregator "修复 Three.js 地球的黑夜闪烁"
    $ python3 -m skill_aggregator --intent-only "帮我搞一下那个动画"
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List

__version__ = "0.1.0"

# 导出核心函数
from .intent import analyze_intent
from .matcher import match, match_by_intent
from .aggregator import recommend

# 定义公开 API
__all__ = [
    "analyze_intent",
    "match",
    "match_by_intent",
    "recommend",
    "__version__",
]

# 索引文件路径
INDEX_DIR = Path.home() / ".skill-aggregator"
INDEX_FILE = INDEX_DIR / "index.json"
HASH_FILE = INDEX_DIR / "skills.hash"


def _compute_skills_hash() -> str:
    """计算所有 SKILL.md 文件的哈希值，用于检测变更。

    与 indexer.py 保持一致，只追踪 SKILL.md 文件。

    Returns:
        str: 所有 SKILL.md 文件修改时间的 MD5 哈希值
    """
    from .indexer import SKILL_DIRS

    file_mtimes = []
    for base_dir in SKILL_DIRS:
        if not base_dir.exists():
            continue
        for file_path in base_dir.rglob("SKILL.md"):
            if file_path.is_file():
                file_mtimes.append(f"{file_path}:{file_path.stat().st_mtime}")

    content = "\n".join(sorted(file_mtimes))
    return hashlib.md5(content.encode()).hexdigest()


def _load_saved_hash() -> Optional[str]:
    """加载上次保存的哈希值。"""
    if not HASH_FILE.exists():
        return None
    try:
        return HASH_FILE.read_text().strip()
    except Exception:
        return None


def _save_hash(hash_value: str) -> None:
    """保存当前哈希值。"""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    HASH_FILE.write_text(hash_value)


def check_and_rebuild_index() -> bool:
    """检查索引是否过期，如需要则自动重建。

    Returns:
        bool: 是否执行了重建
    """
    # 如果索引文件不存在，必须重建
    if not INDEX_FILE.exists():
        from .indexer import build_index

        build_index(force=True)
        return True

    # 计算当前哈希
    current_hash = _compute_skills_hash()
    saved_hash = _load_saved_hash()

    # 如果哈希不匹配，重建索引
    if current_hash != saved_hash:
        from .indexer import build_index

        build_index(force=True)
        return True

    return False


# 自动检查索引（仅在非脚本环境下）
if __name__ != "__main__":
    # 静默检查，不打印输出
    try:
        check_and_rebuild_index()
    except Exception:
        # 忽略错误，避免影响导入
        pass

