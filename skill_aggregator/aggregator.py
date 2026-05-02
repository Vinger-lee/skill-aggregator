# Copyright (c) 2026 Vinger. MIT License.

"""Skill Aggregator 主入口 — CLI 和 Python API。

提供命令行界面和 Python API，用于任务分析和技能推荐。
"""

import sys
from pathlib import Path
from typing import List, Dict

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from matcher import TaskMatcher, match_by_intent
from intent import analyze_intent


from .colors import Colors


def format_percentage(score: float) -> str:
    """格式化百分比显示。

    Args:
        score: 得分（0-1）

    Returns:
        格式化的百分比字符串
    """
    percentage = int(score * 100)
    if percentage >= 80:
        color = Colors.GREEN
    elif percentage >= 60:
        color = Colors.YELLOW
    else:
        color = Colors.DIM
    return f"{color}{percentage}%{Colors.RESET}"


def print_intent_analysis(intent: Dict) -> None:
    """打印意图分析结果。

    Args:
        intent: 意图分析结果字典
    """
    print(f"\n{Colors.CYAN}🎯 意图分析结果{Colors.RESET}")

    # 领域
    domain_conf = int(intent.get("domain_confidence", 0) * 100)
    domain_color = Colors.GREEN if domain_conf >= 70 else Colors.YELLOW if domain_conf >= 50 else Colors.DIM
    print(f"  ├─ 领域: {Colors.BOLD}{intent['domain']}{Colors.RESET} {domain_color}(可信度: {domain_conf}%){Colors.RESET}")

    # 活动
    activity_conf = int(intent.get("activity_confidence", 0) * 100)
    activity_color = Colors.GREEN if activity_conf >= 70 else Colors.YELLOW if activity_conf >= 50 else Colors.DIM
    print(f"  ├─ 活动: {Colors.BOLD}{intent['activity']}{Colors.RESET} {activity_color}(可信度: {activity_conf}%){Colors.RESET}")

    # 技术栈
    if intent.get("stack"):
        print(f"  ├─ 技术栈: {Colors.BOLD}{', '.join(intent['stack'])}{Colors.RESET}")

    # 项目
    if intent.get("project"):
        print(f"  ├─ 项目: {Colors.BOLD}{intent['project']}{Colors.RESET} 可能性最高")

    # 目标
    print(f"  ├─ 目标: {intent['goal']}")

    # 模糊度
    ambiguity = intent.get("ambiguity", 0)
    ambiguity_pct = int(ambiguity * 100)
    if ambiguity > 0.3:
        print(f"  └─ 模糊度: {Colors.RED}{ambiguity_pct}%{Colors.RESET} ⬅️ 需要确认")
    else:
        print(f"  └─ 模糊度: {Colors.GREEN}{ambiguity_pct}%{Colors.RESET} ✓ 足够明确")


def print_clarifying_questions(questions: List[Dict]) -> None:
    """打印澄清问题。

    Args:
        questions: 澄清问题列表
    """
    if not questions:
        return

    print(f"\n{Colors.YELLOW}💬 建议确认问题:{Colors.RESET}")
    for q in questions:
        print(f"  {Colors.BOLD}{q['option']}){Colors.RESET} {q['label']}")
        print(f"     {Colors.DIM}{q['detail']}{Colors.RESET}")


def print_analysis(task: str, features: Dict) -> None:
    """打印任务分析结果。

    Args:
        task: 任务描述
        features: 任务特征字典
    """
    print(f"\n{Colors.CYAN}🎯 任务分析{Colors.RESET}")
    print(f"  ├─ 领域: {Colors.BOLD}{' / '.join(features['domain'])}{Colors.RESET}")
    print(
        f"  ├─ 活动: {Colors.BOLD}{' / '.join(features['activity'])}{Colors.RESET}"
    )

    if features["tech_stack"]:
        print(
            f"  ├─ 技术栈: {Colors.BOLD}{', '.join(features['tech_stack'])}{Colors.RESET}"
        )

    keywords_str = ", ".join(features["keywords"][:10])
    if len(features["keywords"]) > 10:
        keywords_str += f" ... (+{len(features['keywords']) - 10} more)"
    print(f"  └─ 关键词: {Colors.DIM}{keywords_str}{Colors.RESET}")


def print_recommendations(results: List[Dict]) -> None:
    """打印技能推荐结果。

    Args:
        results: 匹配结果列表
    """
    print(f"\n{Colors.MAGENTA}📋 Top-{len(results)} 推荐技能{Colors.RESET}")
    print(
        f"  ┌─┬─ 匹配度 ─┬─ 技能名 {'─' * 40}"
    )

    for i, result in enumerate(results, 1):
        score_str = format_percentage(result["score"])
        skill_name = result["skill"]
        print(f"  ├─┼─ {score_str:>6} ──┼─ {Colors.BOLD}{skill_name}{Colors.RESET}")

    print(f"  └─┴────────┴─{'─' * 50}")

    # 组合建议
    if len(results) >= 2:
        top_skills = [r["skill"] for r in results[:2]]
        print(
            f"\n{Colors.YELLOW}💡 组合建议:{Colors.RESET} {Colors.BOLD}{top_skills[0]}{Colors.RESET} + {Colors.BOLD}{top_skills[1]}{Colors.RESET} 联动使用"
        )


def recommend(task: str, top_n: int = 8, verbose: bool = True) -> List[Dict]:
    """推荐技能（主函数）。

    Args:
        task: 任务描述
        top_n: 返回 Top-N 结果
        verbose: 是否打印详细输出

    Returns:
        匹配结果列表
    """
    # 检查索引是否需要重建
    from indexer import SkillIndexer

    indexer = SkillIndexer()
    index_path = indexer.index_file

    if not index_path.exists():
        if verbose:
            print(
                f"{Colors.YELLOW}⚠️  索引文件不存在，正在构建...{Colors.RESET}"
            )
        indexer.build_index(force=True)
        if verbose:
            print(f"{Colors.GREEN}✓ 索引构建完成{Colors.RESET}")
    else:
        # 检查是否过期
        current_hash = indexer._compute_files_hash()
        saved_hash = indexer._load_saved_hash()
        if current_hash != saved_hash:
            if verbose:
                print(
                    f"{Colors.YELLOW}⚠️  检测到新技能，正在更新索引...{Colors.RESET}"
                )
            indexer.build_index(force=True)
            if verbose:
                print(f"{Colors.GREEN}✓ 索引更新完成{Colors.RESET}")

    # 匹配技能（复用已构建的索引数据，避免重复读取）
    import json
    with open(index_path, "r", encoding="utf-8") as f:
        index_data = json.load(f)

    matcher = TaskMatcher(index_data=index_data)
    features = matcher.analyze(task)
    results = matcher.match(task, top_n=top_n)

    # 打印结果
    if verbose:
        print_analysis(task, features)
        print_recommendations(results)

    return results


def cli_main():
    """CLI 入口点（用于 console_scripts）。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Skill Aggregator - 任务意图分析 + 技能匹配引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 标准模式：分析任务并推荐技能
  skill-aggregator "用 React 写一个登录页面的表单验证"

  # 意图分析模式：只分析意图，不匹配技能
  skill-aggregator --intent-only "帮我搞一下那个接口"

  # 澄清模式：输出澄清建议
  skill-aggregator --clarify "做个数据仪表盘"

  # 技能清洗：扫描并检测技能问题
  skill-aggregator --clean
  skill-aggregator --clean --json
  skill-aggregator --clean --fix
        """,
    )

    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__import__('skill_aggregator').__version__}"
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="禁用彩色输出（适用于 CI/管道）"
    )
    parser.add_argument(
        "--intent-only",
        action="store_true",
        help="只分析意图，不匹配技能（Phase 1）",
    )
    parser.add_argument(
        "--clarify",
        action="store_true",
        help="输出澄清建议（Phase 2）",
    )
    parser.add_argument(
        "--top-n", type=int, default=8, help="返回 Top-N 结果"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="扫描并检测技能问题"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="配合 --clean 使用：自动修复可修复的问题"
    )
    parser.add_argument(
        "--json", action="store_true",
        help="配合 --clean 使用：输出 JSON 格式"
    )
    parser.add_argument("task", nargs="*", help="任务描述")

    args = parser.parse_args()

    # 处理 clean 命令
    if args.clean:
        from skill_aggregator.cleaner import SkillCleaner
        import json as json_module

        cleaner = SkillCleaner()

        if args.fix:
            result = cleaner.fix(dry_run=False)
            print(f"{Colors.GREEN}✓ 修复完成{Colors.RESET}")
            print(f"  ├─ 已修复: {result['fixed']}")
            print(f"  └─ 失败: {result['failed']}")
            sys.exit(0)

        if args.json:
            scan_result = cleaner.scan()
            print(json_module.dumps(scan_result, indent=2, ensure_ascii=False))
            sys.exit(0)

        # 默认：打印报告
        report = cleaner.report()
        print(report)
        sys.exit(0)

    # 检查任务描述
    if not args.task:
        parser.print_help()
        sys.exit(1)

    task = " ".join(args.task)

    # 检查索引
    from indexer import SkillIndexer

    indexer = SkillIndexer()
    index_path = indexer.index_file

    if not index_path.exists():
        print(f"{Colors.YELLOW}⚠️  索引文件不存在，正在构建...{Colors.RESET}")
        indexer.build_index(force=True)
        print(f"{Colors.GREEN}✓ 索引构建完成{Colors.RESET}")
    else:
        # 检查是否过期
        current_hash = indexer._compute_files_hash()
        saved_hash = indexer._load_saved_hash()
        if current_hash != saved_hash:
            print(f"{Colors.YELLOW}⚠️  检测到新技能，正在更新索引...{Colors.RESET}")
            indexer.build_index(force=True)
            print(f"{Colors.GREEN}✓ 索引更新完成{Colors.RESET}")

    # Phase 1: 意图分析
    intent = analyze_intent(task)

    if args.intent_only:
        # 只输出意图分析
        print_intent_analysis(intent)
        if intent.get("clarifying"):
            print_clarifying_questions(intent["clarifying"])
        sys.exit(0)

    if args.clarify or (intent.get("ambiguity", 0) > 0.3 and intent.get("clarifying")):
        # 输出澄清建议
        print_intent_analysis(intent)
        if intent.get("clarifying"):
            print_clarifying_questions(intent["clarifying"])
        sys.exit(0)

    # Phase 3: 技能匹配（基于意图）
    results = match_by_intent(intent, top_n=args.top_n)

    # 打印结果
    print_intent_analysis(intent)
    print_recommendations(results)


def main():
    """向后兼容的 CLI 入口（直接运行脚本时使用）。"""
    cli_main()


if __name__ == "__main__":
    main()
