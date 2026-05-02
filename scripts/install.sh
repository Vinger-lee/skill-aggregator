#!/bin/bash
# Copyright (c) 2026 Vinger. MIT License.

# Skill Aggregator 安装脚本
# 创建符号链接到 Hermes 和 Claude Code 的 skill 目录

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Skill Aggregator 安装脚本${NC}\n"

# 检查必要的目录
HERMES_SKILLS="$HOME/.hermes/skills"
CLAUDE_AGENTS="$HOME/.claude/agents"
CLAUDE_SKILLS="$HOME/.claude/skills"
AGGREGATOR_DIR="$HOME/.skill-aggregator"

# 创建 aggregator 目录
if [ ! -d "$AGGREGATOR_DIR" ]; then
    echo -e "${YELLOW}📁 创建目录: $AGGREGATOR_DIR${NC}"
    mkdir -p "$AGGREGATOR_DIR"
fi

# 检查技能目录
echo -e "${BLUE}📋 检查技能目录:${NC}"

if [ -d "$HERMES_SKILLS" ]; then
    echo -e "  ${GREEN}✓${NC} Hermes skills: $HERMES_SKILLS"
else
    echo -e "  ${YELLOW}⚠${NC}  Hermes skills 不存在: $HERMES_SKILLS"
fi

if [ -d "$CLAUDE_AGENTS" ]; then
    echo -e "  ${GREEN}✓${NC} Claude agents: $CLAUDE_AGENTS"
else
    echo -e "  ${YELLOW}⚠${NC}  Claude agents 不存在: $CLAUDE_AGENTS"
fi

if [ -d "$CLAUDE_SKILLS" ]; then
    echo -e "  ${GREEN}✓${NC} Claude skills: $CLAUDE_SKILLS"
else
    echo -e "  ${YELLOW}⚠${NC}  Claude skills 不存在: $CLAUDE_SKILLS"
    echo -e "  ${YELLOW}→${NC}  创建目录: $CLAUDE_SKILLS"
    mkdir -p "$CLAUDE_SKILLS"
fi

# 构建初始索引
echo -e "\n${BLUE}🔨 构建初始索引...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/build_index.py" --force --verbose

echo -e "\n${GREEN}✓ 安装完成！${NC}"
echo -e "\n${BLUE}使用方法:${NC}"
echo -e "  python3 $SCRIPT_DIR/../skill_aggregator/aggregator.py '任务描述'"
echo -e "\n${BLUE}示例:${NC}"
echo -e "  python3 $SCRIPT_DIR/../skill_aggregator/aggregator.py '修复 Three.js 地球的黑夜闪烁'"
