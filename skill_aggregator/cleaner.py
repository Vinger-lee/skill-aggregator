# Copyright (c) 2026 Vinger. MIT License.

"""技能清洗模块 — 扫描、检测和修复技能索引问题。

提供技能质量检测、问题报告和自动修复功能。
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from collections import Counter


# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


# 问题严重性级别
class Severity:
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


# 问题类型定义
ISSUE_TYPES = {
    "missing_frontmatter": {
        "severity": Severity.ERROR,
        "description": "SKILL.md 没有 YAML frontmatter",
        "emoji": "❌",
    },
    "broken_frontmatter": {
        "severity": Severity.ERROR,
        "description": "frontmatter 存在但解析失败",
        "emoji": "💥",
    },
    "missing_name": {
        "severity": Severity.ERROR,
        "description": "frontmatter 缺 name 字段",
        "emoji": "🚫",
    },
    "missing_description": {
        "severity": Severity.WARNING,
        "description": "description 为空或太短(<10字符)",
        "emoji": "⚠️",
    },
    "empty_skill_dir": {
        "severity": Severity.WARNING,
        "description": "目录存在但没有 SKILL.md",
        "emoji": "📁",
    },
    "duplicate_name": {
        "severity": Severity.INFO,
        "description": "同名技能出现在多个目录",
        "emoji": "ℹ️",
    },
    "no_tags": {
        "severity": Severity.INFO,
        "description": "没有 tags/keywords 字段",
        "emoji": "🏷️",
    },
    "stale_skill": {
        "severity": Severity.INFO,
        "description": "SKILL.md 超过 180 天未修改",
        "emoji": "⏰",
    },
}


class SkillCleaner:
    """技能清洗器。

    扫描所有技能目录，检测问题并提供修复建议。
    """

    def __init__(self, index_path: Optional[Path] = None):
        """初始化清洗器。

        Args:
            index_path: 索引文件路径，默认为 ~/.skill-aggregator/index.json
        """
        if index_path is None:
            index_path = Path.home() / ".skill-aggregator" / "index.json"
        self.index_path = index_path
        self.skill_dirs = self._discover_skill_dirs()

    def _discover_skill_dirs(self) -> List[Path]:
        """发现技能目录（复用 indexer 的逻辑）。"""
        from .indexer import SKILL_DIRS
        return SKILL_DIRS

    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """解析 YAML frontmatter（复用 indexer 的逻辑）。"""
        from .indexer import _parse_yaml_frontmatter
        return _parse_yaml_frontmatter(content)

    def scan(self) -> Dict[str, Any]:
        """扫描所有技能，检测问题。

        Returns:
            扫描结果字典，包含总数、有效数和问题列表
        """
        issues: List[Dict[str, Any]] = []
        skill_names: Dict[str, List[str]] = {}
        total_skills = 0
        valid_skills = 0

        for skill_dir in self.skill_dirs:
            if not skill_dir.exists():
                continue

            for skill_file in skill_dir.rglob("SKILL.md"):
                total_skills += 1
                file_issues = self._check_skill_file(skill_file)

                if not file_issues:
                    valid_skills += 1

                issues.extend(file_issues)

                try:
                    content = skill_file.read_text(encoding="utf-8")
                    frontmatter = self._parse_frontmatter(content)
                    if frontmatter and frontmatter.get("name"):
                        name = frontmatter["name"]
                        if name not in skill_names:
                            skill_names[name] = []
                        skill_names[name].append(str(skill_file))
                except Exception:
                    pass

        for name, paths in skill_names.items():
            if len(paths) > 1:
                for path in paths:
                    issues.append({
                        "skill": name,
                        "file_path": path,
                        "type": "duplicate_name",
                        "severity": Severity.INFO,
                        "detail": f"同名技能出现在 {len(paths)} 个目录",
                    })

        return {
            "total": total_skills,
            "valid": valid_skills,
            "issues": issues,
        }

    def _check_skill_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """检查单个技能文件。"""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            issues.append({
                "skill": file_path.parent.name,
                "file_path": str(file_path),
                "type": "broken_frontmatter",
                "severity": Severity.ERROR,
                "detail": f"文件读取失败: {str(e)}",
            })
            return issues

        if not content.strip().startswith("---"):
            issues.append({
                "skill": file_path.parent.name,
                "file_path": str(file_path),
                "type": "missing_frontmatter",
                "severity": Severity.ERROR,
                "detail": "文件缺少 YAML frontmatter",
            })
            return issues

        frontmatter = self._parse_frontmatter(content)
        if not frontmatter:
            issues.append({
                "skill": file_path.parent.name,
                "file_path": str(file_path),
                "type": "broken_frontmatter",
                "severity": Severity.ERROR,
                "detail": "frontmatter 解析失败",
            })
            return issues

        skill_name = frontmatter.get("name") or file_path.parent.name

        if not frontmatter.get("name"):
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "missing_name",
                "severity": Severity.ERROR,
                "detail": "frontmatter 缺少 name 字段",
            })

        description = frontmatter.get("description", "")
        if not description or len(str(description).strip()) < 10:
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "missing_description",
                "severity": Severity.WARNING,
                "detail": f"description 太短或为空 (当前: {len(str(description).strip())} 字符)",
            })

        tags = frontmatter.get("tags") or frontmatter.get("keywords")
        if not tags or (isinstance(tags, list) and len(tags) == 0):
            issues.append({
                "skill": skill_name,
                "file_path": str(file_path),
                "type": "no_tags",
                "severity": Severity.INFO,
                "detail": "缺少 tags 或 keywords 字段",
            })

        try:
            mtime = file_path.stat().st_mtime
            days_old = (time.time() - mtime) / 86400
            if days_old > 180:
                issues.append({
                    "skill": skill_name,
                    "file_path": str(file_path),
                    "type": "stale_skill",
                    "severity": Severity.INFO,
                    "detail": f"文件已 {int(days_old)} 天未修改",
                })
        except Exception:
            pass

        return issues

    def report(self) -> str:
        """生成人类可读的报告（终端彩色输出）。"""
        scan_result = self.scan()

        lines = []
        lines.append(f"\n{Colors.CYAN}🧹 技能清洗报告{Colors.RESET}")
        lines.append(f"  ├─ 总技能数: {Colors.BOLD}{scan_result['total']}{Colors.RESET}")
        lines.append(f"  ├─ 有效技能: {Colors.GREEN}{scan_result['valid']}{Colors.RESET}")
        lines.append(f"  └─ 问题数量: {Colors.RED}{len(scan_result['issues'])}{Colors.RESET}\n")

        if not scan_result['issues']:
            lines.append(f"{Colors.GREEN}✓ 所有技能都通过检查！{Colors.RESET}")
            return "\n".join(lines)

        issues_by_severity = {
            Severity.ERROR: [],
            Severity.WARNING: [],
            Severity.INFO: [],
        }

        for issue in scan_result['issues']:
            issues_by_severity[issue['severity']].append(issue)

        for severity in [Severity.ERROR, Severity.WARNING, Severity.INFO]:
            issues = issues_by_severity[severity]
            if not issues:
                continue

            if severity == Severity.ERROR:
                color = Colors.RED
                label = "错误"
            elif severity == Severity.WARNING:
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
            if issue['type'] == 'missing_description':
                if dry_run:
                    fixed.append(issue)
                else:
                    try:
                        self._fix_missing_description(Path(issue['file_path']))
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
