# Copyright (c) 2026 Vinger. MIT License.

"""技能索引构建器 — 扫描并索引所有可用的 AI Agent 技能。

从 Hermes 技能目录中提取技能元数据，构建可搜索的 JSON 索引。
自动从 ~/.hermes/config.yaml 发现技能存放目录，支持增量更新。
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


# ---------------------------------------------------------------------------
# 技能目录发现 — 从 ~/.hermes/config.yaml 读取 skills.external_dirs
# ---------------------------------------------------------------------------

def _discover_skill_dirs() -> List[Path]:
    """自动发现用户本地安装的 AI Agent 技能目录。

    读取顺序：
    1. 如果 ~/.hermes/config.yaml 存在且有 skills.external_dirs，使用其中列出的目录
    2. 否则回退到 ~/.hermes/skills/

    Returns:
        技能目录路径列表（已展开 ~ 符号）
    """
    config_path = Path.home() / ".hermes" / "config.yaml"
    fallback = [Path.home() / ".hermes" / "skills"]

    if not config_path.exists():
        return fallback

    try:
        content = config_path.read_text(encoding="utf-8")
    except Exception:
        return fallback

    lines = content.splitlines()
    dirs: List[Path] = []
    in_external_dirs = False
    external_dirs_indent = -1

    for line in lines:
        stripped = line.strip()

        # 跳过空行和注释
        if not stripped or stripped.startswith("#"):
            continue

        # 检测 skills: 块开始
        if re.match(r"^skills\s*:", stripped):
            in_external_dirs = False
            continue

        # 检测 external_dirs: 在 skills 块内
        if re.match(r"^external_dirs\s*:", stripped):
            in_external_dirs = True
            external_dirs_indent = len(line) - len(line.lstrip())
            continue

        if in_external_dirs:
            current_indent = len(line) - len(line.lstrip())

            # 缩进小于 external_dirs 本身 → 退出段落
            # 注意：列表项与 external_dirs: 同缩进是合法的 YAML
            if current_indent < external_dirs_indent:
                in_external_dirs = False
                continue

            # 解析列表项
            if stripped.startswith("- "):
                path_str = stripped[2:].strip().strip('"').strip("'")
                if path_str:
                    expanded = Path(path_str).expanduser()
                    dirs.append(expanded)

    return dirs if dirs else fallback


# 模块级常量：在导入时自动发现技能目录
# 供 __init__.py 的 _compute_skills_hash 等外部模块使用
SKILL_DIRS = _discover_skill_dirs()


# ---------------------------------------------------------------------------
# YAML frontmatter 解析（零外部依赖）
# ---------------------------------------------------------------------------

def _parse_yaml_frontmatter(content: str) -> Optional[Dict[str, Any]]:
    """解析 Markdown 文件中的 YAML frontmatter（--- 之间的内容）。

    纯 Python 实现，不依赖 pyyaml / ruamel.yaml。

    Args:
        content: Markdown 文件原始内容

    Returns:
        解析后的元数据字典；如果不存在 frontmatter 则返回 None
    """
    content_stripped = content.strip()
    if not content_stripped.startswith("---"):
        return None

    # 找到第二个 ---
    end_idx = content_stripped.find("---", 3)
    if end_idx == -1:
        return None

    frontmatter = content_stripped[3:end_idx].strip()

    metadata: Dict[str, Any] = {}
    current_list_key: Optional[str] = None

    for line in frontmatter.splitlines():
        raw_line = line
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # 检测是否为列表项（- value）—— 延续上一个列表键
        list_match = re.match(r"^-\s+(.+)$", line)
        if list_match and current_list_key is not None:
            val = list_match.group(1).strip().strip('"').strip("'")
            if isinstance(metadata.get(current_list_key), list):
                metadata[current_list_key].append(val)
            continue

        # 匹配 key: value
        kv_match = re.match(r"^(\w[\w_-]*)\s*:\s*(.*?)\s*$", line)
        if not kv_match:
            continue

        key = kv_match.group(1).lower()
        value = kv_match.group(2).strip()
        current_list_key = None  # 重置列表上下文

        # --- 处理 tags: [a, b, c] 行内列表 ---
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            items = [
                t.strip().strip('"').strip("'")
                for t in inner.split(",")
                if t.strip()
            ]
            metadata[key] = items
            continue

        # --- 处理以 [ 开头但跨多行的列表（首行） ---
        if value.startswith("[") and not value.endswith("]"):
            items = [value[1:].strip().strip('"').strip("'")] if len(value) > 1 else []
            metadata[key] = items
            current_list_key = key
            continue

        # --- 处理缩进列表开始（key 后无值，下一行是 - item） ---
        if not value:
            indent = len(raw_line) - len(raw_line.lstrip())
            # 检查下一行是否为列表项（由调用方处理）
            metadata[key] = []
            current_list_key = key
            continue

        # --- 普通键值对 ---
        metadata[key] = value

    return metadata if metadata else None


# ---------------------------------------------------------------------------
# 技能索引构建器
# ---------------------------------------------------------------------------

class SkillIndexer:
    """技能索引构建器。

    从 Hermes 技能目录中扫描 SKILL.md 文件，提取元数据并构建索引。
    支持增量更新：通过文件哈希检测变更，避免不必要的重建。
    """

    def __init__(self, index_dir: Optional[Path] = None):
        """初始化索引构建器。

        Args:
            index_dir: 索引文件存储目录，默认为 ~/.skill-aggregator/
        """
        self.index_dir = index_dir or Path.home() / ".skill-aggregator"
        self.index_file = self.index_dir / "index.json"
        self.hash_file = self.index_dir / "files.hash"
        self.skill_dirs = _discover_skill_dirs()

    # ------------------------------------------------------------------
    # 内部辅助方法
    # ------------------------------------------------------------------

    def _ensure_index_dir(self) -> None:
        """确保索引目录存在。"""
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def _compute_files_hash(self) -> str:
        """计算所有技能文件的哈希值，用于检测变更。

        Returns:
            所有 SKILL.md 文件修改时间的 MD5 哈希值
        """
        file_mtimes: List[str] = []
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue
            for skill_file in skill_dir.rglob("SKILL.md"):
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

    # ------------------------------------------------------------------
    # SKILL.md 元数据提取
    # ------------------------------------------------------------------

    def _extract_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """从 SKILL.md 文件中提取技能元数据。

        提取策略（按优先级）：
        1. 解析 YAML frontmatter（--- 之间的内容），获取 name、description、
           category、tags
        2. 如果 frontmatter 不存在或字段缺失，fallback 到正则表达式扫描
        3. 如果仍然缺 name，使用文件名（不含扩展名）

        Args:
            file_path: SKILL.md 文件路径

        Returns:
            技能元数据字典，如果文件无法读取则返回 None
        """
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return None

        # --- 尝试解析 YAML frontmatter ---
        metadata: Dict[str, Any] = {}
        frontmatter = _parse_yaml_frontmatter(content)

        if frontmatter:
            # 从 frontmatter 提取结构化字段
            name = (
                frontmatter.get("name")
                or frontmatter.get("skill")
                or frontmatter.get("id")
            )
            description = (
                frontmatter.get("description")
                or frontmatter.get("desc")
                or frontmatter.get("summary")
            )
            category = (
                frontmatter.get("category")
                or frontmatter.get("type")
                or frontmatter.get("domain")
            )
            tags_raw = frontmatter.get("tags") or frontmatter.get("keywords") or []

            if name:
                metadata["name"] = str(name).strip()
            if description:
                metadata["description"] = str(description).strip()
            if category:
                metadata["category"] = str(category).strip().lower()
            if tags_raw:
                if isinstance(tags_raw, str):
                    # 逗号/分号分隔的字符串
                    tags_raw = re.split(r"[,;]", tags_raw)
                metadata["tags"] = [
                    t.strip().lower() for t in tags_raw if t and t.strip()
                ]

        # --- Frontmatter 缺失或字段不全 → fallback 正则扫描 ---
        if "name" not in metadata:
            name = self._extract_name(content, file_path)
            if name:
                metadata["name"] = name

        if "description" not in metadata:
            desc = self._extract_description(content)
            if desc:
                metadata["description"] = desc

        if "category" not in metadata:
            cat = self._extract_field(content, r"(?:category|type|domain)")
            if cat:
                metadata["category"] = cat.lower()
            else:
                metadata["category"] = "general"

        if "tags" not in metadata:
            tags = self._extract_tags(content)
            metadata["tags"] = tags

        # --- 关键词提取（技术栈、工具名等） ---
        keywords: Set[str] = set()
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
            "name": metadata.get("name", file_path.stem),
            "description": metadata.get("description", ""),
            "category": metadata.get("category", "general"),
            "tags": metadata.get("tags", []),
            "keywords": sorted(keywords),
            "file_path": str(file_path),
        }

    @staticmethod
    def _extract_name(content: str, file_path: Path) -> Optional[str]:
        """从内容中提取技能名称。

        优先级：Markdown 一级标题 > 文件名
        """
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        return file_path.stem

    @staticmethod
    def _extract_description(content: str) -> Optional[str]:
        """从内容中提取技能描述。

        优先级：description:/desc:/summary: 字段 > 第一段非标题文本
        """
        desc_match = re.search(
            r"(?:description|desc|summary):\s*(.+?)(?:\n|$)",
            content,
            re.IGNORECASE,
        )
        if desc_match:
            return desc_match.group(1).strip()

        paragraphs = re.findall(r"^(?!#)(.+)$", content, re.MULTILINE)
        if paragraphs:
            return paragraphs[0].strip()
        return None

    @staticmethod
    def _extract_field(content: str, field_pattern: str) -> Optional[str]:
        """通用：从内容中提取某个字段的值。"""
        match = re.search(
            rf"({field_pattern}):\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if match:
            return match.group(2).strip()
        return None

    @staticmethod
    def _extract_tags(content: str) -> List[str]:
        """从内容中提取标签。"""
        tags_match = re.search(
            r"(?:tags|keywords):\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if tags_match:
            tags_str = tags_match.group(1)
            return sorted(
                {
                    tag.strip().lower()
                    for tag in re.split(r"[,;]", tags_str)
                    if tag.strip()
                }
            )
        return []

    # ------------------------------------------------------------------
    # 扫描 & 索引构建
    # ------------------------------------------------------------------

    def scan_skills(self) -> List[Dict[str, Any]]:
        """扫描所有技能目录，查找并提取 SKILL.md 文件元数据。

        同名技能（如不同目录下的相同 skill）仅保留首次出现的版本。

        Returns:
            去重后的技能元数据列表
        """
        skills: List[Dict[str, Any]] = []
        seen_names: Set[str] = set()
        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue

            for skill_file in skill_dir.rglob("SKILL.md"):
                metadata = self._extract_metadata(skill_file)
                if metadata:
                    name = metadata["name"]
                    if name not in seen_names:
                        seen_names.add(name)
                        skills.append(metadata)

        return skills

    def build_index(self, force: bool = False) -> Dict[str, Any]:
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
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)

        # 扫描技能
        skills = self.scan_skills()

        # 构建索引
        index_data: Dict[str, Any] = {
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


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------

def build_index(force: bool = False) -> Dict[str, Any]:
    """构建技能索引（便捷函数）。

    Args:
        force: 是否强制重建索引

    Returns:
        索引数据字典
    """
    indexer = SkillIndexer()
    return indexer.build_index(force=force)
