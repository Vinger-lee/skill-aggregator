# Copyright (c) 2026 Vinger. MIT License.

"""ANSI 颜色代码 — 终端彩色输出支持。

提供统一的颜色常量，用于终端输出格式化。
"""


class Colors:
    """ANSI 颜色代码常量。"""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
