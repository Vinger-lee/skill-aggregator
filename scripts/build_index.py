#!/usr/bin/env python3
# Copyright (c) 2026 Vinger. MIT License.

"""手动重建索引脚本。

提供命令行工具用于手动重建技能索引。
"""

import argparse
import sys
import time
from pathlib import Path

# 添加项目根目录到路径（使 skill_aggregator 可导入）
sys.path.insert(0, str(Path(__file__).parent.parent))

from skill_aggregator.indexer import SkillIndexer


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(description="构建技能索引")
    parser.add_argument(
        "--force", "-f", action="store_true", help="强制重建索引（忽略哈希检查）"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="显示详细输出"
    )
    parser.add_argument(
        "--watch", "-w", action="store_true", help="监听模式（持续监控文件变化）"
    )

    args = parser.parse_args()

    indexer = SkillIndexer()

    if args.watch:
        print("🔍 监听模式启动，按 Ctrl+C 退出...")
        try:
            last_hash = None
            while True:
                current_hash = indexer._compute_files_hash()
                if current_hash != last_hash:
                    print(f"\n⚡ 检测到文件变化，重建索引...")
                    start_time = time.time()
                    index_data = indexer.build_index(force=True)
                    elapsed = time.time() - start_time

                    print(f"✓ 索引构建完成")
                    print(f"  - 技能数量: {index_data['total_skills']}")
                    print(f"  - 耗时: {elapsed:.2f}s")
                    last_hash = current_hash

                time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n👋 监听已停止")
            sys.exit(0)
    else:
        # 单次构建
        if args.verbose:
            print("🔨 开始构建索引...")

        start_time = time.time()
        index_data = indexer.build_index(force=args.force)
        elapsed = time.time() - start_time

        print(f"✓ 索引构建完成")
        print(f"  - 索引文件: {indexer.index_file}")
        print(f"  - 技能数量: {index_data['total_skills']}")
        print(f"  - 构建时间: {index_data['built_at']}")
        print(f"  - 耗时: {elapsed:.2f}s")

        if args.verbose:
            print(f"\n📋 扫描的目录:")
            for skill_dir in indexer.skill_dirs:
                exists = "✓" if skill_dir.exists() else "✗"
                print(f"  {exists} {skill_dir}")


if __name__ == "__main__":
    main()
