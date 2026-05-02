# 使用示例

## 基本用法

### 1. 命令行查询

```bash
# 通过 console_scripts 入口（推荐）
skill-aggregator "修复 Three.js 地球的黑夜闪烁"
skill-aggregator "用 Canvas 给 feiyi-web 做墨水动画效果"
skill-aggregator "跑一下量化回测看看动量策略赚不赚钱"

# 通过 python -m
python3 -m skill_aggregator "修复 Three.js 地球的黑夜闪烁"

# 意图分析模式
skill-aggregator --intent-only "帮我搞一下那个动画"

# 澄清模式
skill-aggregator --clarify "做个水墨动画"
```

### 2. Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# 方式 1：直接推荐（自动处理意图分析）
results = recommend("修复 Three.js 地球的黑夜闪烁", top_n=5, verbose=False)
for result in results:
    print(f"{result['skill']}: {result['score']:.2%}")

# 方式 2：分步执行（三段式工作流）
# Phase 1: 意图分析
intent = analyze_intent("修复 Three.js 地球的黑夜闪烁")
print(f"领域: {intent['domain']}")
print(f"活动: {intent['activity']}")
print(f"技术栈: {intent['stack']}")

# Phase 2: 澄清确认（如果需要）
if intent.get('ambiguity', 0) > 0.3:
    print("需要澄清:", intent.get('clarifying'))

# Phase 3: 技能匹配
results = match_by_intent(intent, top_n=5)
for result in results:
    print(f"{result['skill']}: {result['score']:.2%}")
```

### 3. 索引管理

```bash
# 查看当前索引状态
python3 -c "import json; from pathlib import Path; data = json.load(open(Path.home() / '.skill-aggregator' / 'index.json')); print(f'Total skills: {data[\"total_skills\"]}')"

# 强制重建索引
python3 scripts/build_index.py --force --verbose

# 监听模式（自动检测文件变化）
python3 scripts/build_index.py --watch
```

## 高级用法

### 自定义匹配权重

编辑 `skill_aggregator/matcher.py` 中的评分公式:

```python
# 默认权重
score = (
    keyword_score * 0.40      # 关键词匹配
    + domain_score * 0.25     # 领域匹配
    + similarity_score * 0.20 # TF-IDF 相似度
    + priority_bonus * 0.15   # 优先级加权
)

# 自定义权重（例如：更重视领域匹配）
score = (
    keyword_score * 0.30
    + domain_score * 0.40
    + similarity_score * 0.20
    + priority_bonus * 0.10
)
```

### 添加优先级技能

编辑 `skill_aggregator/matcher.py` 中的 `priority_skills` 集合:

```python
self.priority_skills = {
    "systematic-debugging",
    "planning-with-files",
    "verification-before-completion",
    "testing-evidence-collector",
    "test-driven-development",
    # 添加你的优先级技能
    "your-custom-skill",
}
```

### 扩展技能目录

编辑 `skill_aggregator/indexer.py` 中的 `SKILL_DIRS`:

```python
SKILL_DIRS = [
    Path.home() / ".hermes" / "skills",
    Path.home() / ".claude" / "agents",
    Path.home() / ".claude" / "skills",
    # 添加自定义目录
    Path("/path/to/your/custom/skills"),
]
```

## 测试

```bash
# 运行匹配测试
python3 tests/test_matcher.py

# 测试特定任务
python3 -c "
from skill_aggregator import recommend
results = recommend('implement TDD for new feature', top_n=3, verbose=False)
for r in results:
    print(f'{r[\"skill\"]}: {r[\"score\"]:.2%}')
"
```

## 故障排查

### 索引未更新

```bash
# 手动强制重建
python3 scripts/build_index.py --force

# 检查哈希文件
cat ~/.skill-aggregator/files.hash
```

### 匹配结果不理想

1. 检查任务描述是否包含足够的关键词
2. 查看技能索引是否包含相关技能
3. 调整匹配权重（见"自定义匹配权重"）

### 找不到技能文件

```bash
# 检查技能目录是否存在
ls -la ~/.hermes/skills/
ls -la ~/.claude/agents/
ls -la ~/.claude/skills/

# 重新运行安装脚本
bash scripts/install.sh
```
