# Copyright (c) 2026 Vinger. MIT License.

"""技能清洗模块 — 扫描、检测和修复技能索引问题。

提供技能质量检测、问题报告和自动修复功能。
"""

import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from collections import Counter

from .colors import Colors

# 问题严重性级别
class Severity:
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


ISSUE_TYPES = {
    "missing_frontmatter": {
        "severity": "error",
        "emoji": "❌",
        "detail": "文件缺少 YAML frontmatter",
    },
    "broken_frontmatter": {
        "severity": "error",
        "emoji": "💥",
        "detail": "frontmatter 解析失败",
    },
    "missing_name": {
        "severity": "error",
        "emoji": "🏷️",
        "detail": "frontmatter 缺少 name 字段",
    },
    "missing_description": {
        "severity": "warning",
        "emoji": "⚠️",
        "detail": "description 太短或为空",
    },
    "empty_skill_dir": {
        "severity": "warning",
        "emoji": "📂",
        "detail": "目录存在但没有 SKILL.md",
    },
    "duplicate_name": {
        "severity": "info",
        "emoji": "🔄",
        "detail": "同名技能出现在多个目录",
    },
    "no_tags": {
        "severity": "info",
        "emoji": "🏷️",
        "detail": "缺少 tags 或 keywords 字段",
    },
    "stale_skill": {
        "severity": "info",
        "emoji": "🕐",
        "detail": "SKILL.md 超过 180 天未修改",
    },
}


class SkillCleaner:
    """技能清洗器 — 扫描、报告和修复技能问题。"""

    def __init__(self, index_path: Path = None):
        if index_path is None:
            index_path = Path.home() / ".skill-aggregator" / "index.json"
        self.index_path = index_path
        self.skill_dirs = self._discover_skill_dirs()

    def _discover_skill_dirs(self) -> List[Path]:
        """发现技能目录（复用 indexer 的逻辑）。"""
        from skill_aggregator.indexer import _discover_skill_dirs as _discover
        return _discover()

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """解析 YAML frontmatter（复用 indexer 的逻辑）。"""
        from skill_aggregator.indexer import _parse_yaml_frontmatter
        return _parse_yaml_frontmatter(content)

    def scan(self) -> Dict[str, Any]:
        """扫描所有技能，检测问题。"""
        issues: List[Dict] = []
        seen_names: Dict[str, str] = {}
        total = 0

        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue

            for skill_file in skill_dir.rglob("SKILL.md"):
                total += 1
                file_issues, content = self._check_skill_file(skill_file)

                # 复用已读取的 content，避免重复读文件
                if content:
                    try:
                        frontmatter = self._parse_frontmatter(content)
                        if frontmatter:
                            name = frontmatter.get("name", "")
                            if name and name in seen_names:
                                issues.append({
                                    "skill": name,
                                    "file_path": str(skill_file),
                                    "type": "duplicate_name",
                                    "severity": ISSUE_TYPES["duplicate_name"]["severity"],
                                    "detail": f"与 {seen_names[name]} 重名",
                                })
                            else:
                                seen_names[name] = str(skill_file)
                    except Exception:
                        pass

                issues.extend(file_issues)

            # 检查空目录
            for subdir in skill_dir.iterdir():
                if subdir.is_dir() and not any(subdir.rglob("SKILL.md")):
                    issues.append({
                        "skill": subdir.name,
                        "file_path": str(subdir),
                        "type": "empty_skill_dir",
                        "severity": ISSUE_TYPES["empty_skill_dir"]["severity"],
                        "detail": ISSUE_TYPES["empty_skill_dir"]["detail"],
                    })

        valid = total - len([i for i in issues if i["severity"] == "error"])

        return {
            "total": total,
            "valid": valid,
            "issues": sorted(issues, key=lambda x: {
                "error": 0, "warning": 1, "info": 2
            }[x["severity"]]),
        }

    def _check_skill_file(self, file_path: Path) -> tuple:
        """检查单个技能文件，返回 (issues, content)。"""
        issues: List[Dict] = []
        skill_name = file_path.parent.name

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "broken_frontmatter",
                "severity": "error",
                "detail": "文件无法读取",
            })
            return issues, ""

        # 检查 frontmatter
        if not content.strip().startswith("---"):
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "missing_frontmatter",
                "severity": "error",
                "detail": ISSUE_TYPES["missing_frontmatter"]["detail"],
            })
            return issues, content

        frontmatter = self._parse_frontmatter(content)
        if frontmatter is None:
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "broken_frontmatter",
                "severity": "error",
                "detail": ISSUE_TYPES["broken_frontmatter"]["detail"],
            })
            return issues, content

        # 检查 name
        name = frontmatter.get("name", "")
        if not name:
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "missing_name",
                "severity": "error",
                "detail": ISSUE_TYPES["missing_name"]["detail"],
            })

        # 检查 description
        description = frontmatter.get("description", "")
        if not description or len(str(description).strip()) < 10:
            issues.append({
                "skill": name or skill_name,
                "file_path": str(file_path),
                "type": "missing_description",
                "severity": "warning",
                "detail": f"description 太短或为空 (当前: {len(str(description).strip())} 字符)",
            })

        # 检查 tags
        tags = frontmatter.get("tags", frontmatter.get("keywords", []))
        if not tags:
            issues.append({
                "skill": name or skill_name,
                "file_path": str(file_path),
                "type": "no_tags",
                "severity": "info",
                "detail": ISSUE_TYPES["no_tags"]["detail"],
            })

        # 检查是否过期
        try:
            mtime = file_path.stat().st_mtime
            age_days = (time.time() - mtime) / 86400
            if age_days > 180:
                issues.append({
                    "skill": name or skill_name,
                    "file_path": str(file_path),
                    "type": "stale_skill",
                    "severity": "info",
                    "detail": f"已 {int(age_days)} 天未修改",
                })
        except Exception:
            pass

        return issues, content

    def report(self) -> str:
        """生成人类可读的彩色报告。"""
        scan_result = self.scan()
        lines = [
            f"🧹 技能清洗报告",
            f"  ├─ 总技能数: {scan_result['total']}",
            f"  ├─ 有效技能: {scan_result['valid']}",
            f"  └─ 问题数量: {len(scan_result['issues'])}",
            "",
        ]

        # 按严重性分组
        grouped: Dict[str, List] = {"error": [], "warning": [], "info": []}
        for issue in scan_result["issues"]:
            grouped[issue["severity"]].append(issue)

        for severity in ["error", "warning", "info"]:
            issues = grouped[severity]
            if not issues:
                continue

            if severity == "error":
                color = Colors.RED
                label = "错误"
            elif severity == "warning":
                color = Colors.YELLOW
                label = "警告"
            else:
                color = Colors.BLUE
                label = "信息"

            lines.append(f"{color}{label} ({len(issues)}){Colors.RESET}")

            for issue in issues[:10]:
                emoji = ISSUE_TYPES.get(issue['type'], {}).get('emoji', '•')
                lines.append(f"  {emoji} {issue['skill']}")
                lines.append(f"     {Colors.DIM}{issue['detail']}{Colors.RESET}")
                lines.append(f"     {Colors.DIM}{issue['file_path']}{Colors.RESET}")

            if len(issues) > 10:
                lines.append(f"  {Colors.DIM}... 还有 {len(issues) - 10} 个{Colors.RESET}")

            lines.append("")

        return "\n".join(lines)

    def fix(self, dry_run: bool = True) -> Dict[str, Any]:
        """自动修复可修复的问题。"""
        scan_result = self.scan()
        fixed = []
        failed = []

        for issue in scan_result['issues']:
            handlers = {
                'missing_description': self._fix_missing_description,
                'missing_name': self._fix_missing_name,
                'no_tags': self._fix_no_tags,
            }
            handler = handlers.get(issue['type'])
            if not handler:
                continue
            if dry_run:
                fixed.append(issue)
            else:
                try:
                    handler(Path(issue['file_path']))
                    fixed.append(issue)
                except Exception as e:
                    failed.append({**issue, 'error': str(e)})

        return {
            'dry_run': dry_run,
            'fixed': len(fixed),
            'failed': len(failed),
            'details': {
                'fixed': fixed,
                'failed': failed,
            }
        }

    def _fix_missing_description(self, file_path: Path) -> None:
        """修复缺失的 description 字段。"""
        content = file_path.read_text(encoding="utf-8")
        frontmatter = self._parse_frontmatter(content)

        if not frontmatter:
            return

        skill_name = frontmatter.get("name", file_path.parent.name)
        default_desc = f"{skill_name} 技能"

        lines = content.splitlines()
        new_lines = []
        in_frontmatter = False
        added = False

        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    new_lines.append(line)
                else:
                    if not added:
                        new_lines.append(f"description: {default_desc}")
                        added = True
                    new_lines.append(line)
                    in_frontmatter = False
            else:
                new_lines.append(line)

        file_path.write_text("\n".join(new_lines), encoding="utf-8")

    def _fix_missing_name(self, file_path: Path) -> None:
        """修复缺失的 name 字段 — 从目录名生成。"""
        content = file_path.read_text(encoding="utf-8")
        dir_name = file_path.parent.name
        lines = content.splitlines()
        new_lines = []
        in_frontmatter = False
        added = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    new_lines.append(line)
                    new_lines.append(f"name: {dir_name}")
                    added = True
                else:
                    if not added:
                        new_lines.append(f"name: {dir_name}")
                    new_lines.append(line)
            else:
                new_lines.append(line)
        if not added:
            new_lines.insert(0, f"name: {dir_name}")
            new_lines.insert(0, "---")
            new_lines.append("---")
        file_path.write_text("\n".join(new_lines), encoding="utf-8")

    def _fix_no_tags(self, file_path: Path) -> None:
        """修复缺失的 tags — 从 description 提取关键词。"""
        content = file_path.read_text(encoding="utf-8")
        frontmatter = self._parse_frontmatter(content)
        if not frontmatter:
            return
        desc = frontmatter.get("description", "")
        if not desc:
            return
        words = re.findall(r"\b[a-z]+\b", str(desc).lower())
        stopwords = {"the", "a", "an", "and", "or", "in", "on", "to", "for",
                     "of", "with", "by", "from", "is", "are", "this", "that",
                     "use", "used", "can", "how", "your", "you"}
        tags = [w for w in words if w not in stopwords and len(w) > 2][:8]
        if not tags:
            return
        tag_line = f"tags: [{', '.join(tags)}]"
        lines = content.splitlines()
        new_lines = []
        in_frontmatter = False
        added = False
        for line in lines:
            if line.strip() == "---":
                if not in_frontmatter:
                    in_frontmatter = True
                    new_lines.append(line)
                else:
                    if not added:
                        new_lines.append(tag_line)
                    new_lines.append(line)
            else:
                new_lines.append(line)
        if not added:
            idx = next((i for i, l in enumerate(new_lines) if l.strip() == "---"), len(new_lines)-1)
            new_lines.insert(idx, tag_line)
        file_path.write_text("\n".join(new_lines), encoding="utf-8")
