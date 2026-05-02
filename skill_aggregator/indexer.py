# Copyright (c) 2026 Vinger. MIT License.

"""技能索引构建器 — 扫描并索引所有可用的 AI Agent 技能。

从 Hermes 和 Claude Code 的技能目录中提取技能元数据，构建可搜索的 JSON 索引。
支持增量更新和自动检测新技能。
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime


# 技能目录配置
SKILL_DIRS = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".claude" / "agents",
    Path.home() / ".claude" / "skills",
]


class SkillIndexer:
    """技能索引构建器。

    扫描 Hermes 和 Claude Code 的技能目录，提取技能元数据并构建索引。
    """

    def __init__(self, index_dir: Optional[Path] = None):
        """初始化索引构建器。

        Args:
            index_dir: 索引文件存储目录，默认为 ~/.skill-aggregator/
        """
        self.index_dir = index_dir or Path.home() / ".skill-aggregator"
        self.index_file = self.index_dir / "index.json"
        self.hash_file = self.index_dir / "files.hash"
        self.skill_dirs = SKILL_DIRS

    def _ensure_index_dir(self) -> None:
        """确保索引目录存在。"""
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _compute_files_hash(self) -> str:
        """计算所有技能文件的哈希值。

        Returns:
            所有技能文件修改时间的哈希值
        """
        file_mtimes = []
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue
            for skill_file in skill_dir.rglob("*.md"):
                if skill_file.is_file():
                    mtime = skill_file.stat().st_mtime
                    file_mtimes.append(f"{skill_file}:{mtime}")

        content = "\n".join(sorted(file_mtimes))
        return hashlib.md5(content.encode()).hexdigest()

    def _load_saved_hash(self) -> Optional[str]:
        """加载上次保存的哈希值。"""
        if not self.hash_file.exists():
            return None
        try:
            return self.hash_file.read_text().strip()
        except Exception:
            return None

    def _save_hash(self, hash_value: str) -> None:
        """保存当前哈希值。"""
        self._ensure_index_dir()
        self.hash_file.write_text(hash_value)

    def _extract_metadata(self, file_path: Path) -> Optional[Dict]:
        """从 Markdown 文件中提取技能元数据。

        Args:
            file_path: 技能文件路径

        Returns:
            技能元数据字典，如果提取失败则返回 None
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        # 提取技能名称（从文件名或第一个标题）
        name = file_path.stem
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            name = title_match.group(1).strip()

        # 提取描述（第一段文本或 description 字段）
        description = ""
        desc_match = re.search(
            r"(?:description|desc|summary):\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if desc_match:
            description = desc_match.group(1).strip()
        else:
            # 提取第一段非标题文本
            paragraphs = re.findall(r"^(?!#)(.+)$", content, re.MULTILINE)
            if paragraphs:
                description = paragraphs[0].strip()

        # 提取分类
        category = "general"
        cat_match = re.search(
            r"(?:category|type|domain):\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if cat_match:
            category = cat_match.group(1).strip().lower()

        # 提取标签
        tags: Set[str] = set()
        tags_match = re.search(
            r"(?:tags|keywords):\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if tags_match:
            tags_str = tags_match.group(1)
            tags = {
                tag.strip().lower()
                for tag in re.split(r"[,;]", tags_str)
                if tag.strip()
            }

        # 从内容中提取关键词（技术栈、工具名等）
        keywords: Set[str] = set()
        # 常见技术栈关键词
        tech_patterns = [
            r"\b(react|vue|angular|svelte|next\.?js|nuxt)\b",
            r"\b(python|javascript|typescript|java|go|rust|c\+\+)\b",
            r"\b(docker|kubernetes|k8s|terraform|ansible)\b",
            r"\b(three\.?js|p5\.?js|canvas|webgl|svg)\b",
            r"\b(django|flask|fastapi|express|spring)\b",
            r"\b(postgres|mysql|mongodb|redis|elasticsearch)\b",
            r"\b(aws|gcp|azure|vercel|netlify)\b",
            r"\b(git|github|gitlab|ci/cd)\b",
        ]
        for pattern in tech_patterns:
            matches = re.findall(pattern, content.lower())
            keywords.update(matches)

        return {
            "name": name,
            "description": description,
            "category": category,
            "tags": list(tags),
            "keywords": list(keywords),
            "file_path": str(file_path),
        }

    def scan_skills(self) -> List[Dict]:
        """扫描所有技能目录并提取元数据。

        Returns:
            技能元数据列表
        """
        skills = []
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue

            # 扫描 SKILL.md 文件
            for skill_file in skill_dir.rglob("SKILL.md"):
                metadata = self._extract_metadata(skill_file)
                if metadata:
                    skills.append(metadata)

            # 扫描 agents 目录下的所有 .md 文件
            if "agents" in str(skill_dir):
                for md_file in skill_dir.rglob("*.md"):
                    if md_file.name != "SKILL.md":
                        metadata = self._extract_metadata(md_file)
                        if metadata:
                            skills.append(metadata)

        return skills

    def build_index(self, force: bool = False) -> Dict:
        """构建技能索引。

        Args:
            force: 是否强制重建索引（忽略哈希检查）

        Returns:
            索引数据字典
        """
        self._ensure_index_dir()

        # 检查是否需要重建
        if not force:
            current_hash = self._compute_files_hash()
            saved_hash = self._load_saved_hash()
            if current_hash == saved_hash and self.index_file.exists():
                # 索引未过期，直接加载
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        # 扫描技能
        skills = self.scan_skills()

        # 构建索引
        index_data = {
            "version": "1.0",
            "built_at": datetime.now().isoformat(),
            "total_skills": len(skills),
            "skills": skills,
        }

        # 保存索引
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        # 保存哈希
        current_hash = self._compute_files_hash()
        self._save_hash(current_hash)

        return index_data


def build_index(force: bool = False) -> Dict:
    """构建技能索引（便捷函数）。

    Args:
        force: 是否强制重建索引

    Returns:
        索引数据字典
    """
    indexer = SkillIndexer()
    return indexer.build_index(force=force)


