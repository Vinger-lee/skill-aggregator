# Copyright (c) 2026 Vinger. MIT License.

"""让 python3 -m skill_aggregator 能工作。

这个模块使得可以通过 `python3 -m skill_aggregator` 命令运行 CLI。
"""

from .aggregator import cli_main

if __name__ == "__main__":
    cli_main()
