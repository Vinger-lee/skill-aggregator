# 使用示例

## 基本用法

### 1. 命令行查询

```bash
# 通过 console_scripts 入口（推荐）
skill-aggregator "用 React 写一个登录页面的表单验证"
skill-aggregator "部署一个 Docker 容器到云服务器"
skill-aggregator "分析这段 Python 代码的性能瓶颈"

# 通过 python -m
python3 -m skill_aggregator "给博客系统添加全文搜索功能"

# 意图分析模式
skill-aggregator --intent-only "帮我搞一下那个接口"

# 澄清模式
skill-aggregator --clarify "做个数据仪表盘"
```

### 2. Python API

```python
from skill_aggregator import analyze_intent, recommend, match_by_intent

# 方式 1：直接推荐（自动处理意图分析）
results = recommend("给 REST API 添加 JWT 认证", top_n=5, verbose=False)
for result in results:
    print(f"{result['skill']}: {result['score']:.2%}")

# 方式 2：分步执行（三段式工作流）
# Phase 1: 意图分析
intent = analyze_intent("给 REST API 添加 JWT 认证")
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
python3 -c "import json; from pathlib import Path; data = json.load(open(Path.home() / '.skill-aggregator' / 'index.json')); print(f'Total skills: {data[\"total_skills\"]}')\n"
# 强制重建索引
python3 -m skill_aggregator --force

# 技能健康检查
python3 -m skill_aggregator clean
python3 -m skill_aggregator clean --json
```

## 高级用法

### 技能清洗

```bash
# 扫描并报告问题
skill-aggregator clean
# 输出:
# 🧹 技能清洗报告
#   ├─ 总技能数: 390
#   ├─ 有效技能: 350
#   └─ 问题数量: 40

# JSON 输出（便于集成到 CI）
skill-aggregator clean --json | jq '.issues[] | select(.severity == "error")'

# 自动修复可修复的问题
skill-aggregator clean --fix
```

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
    "my-code-review-workflow",
}
```

### 扩展技能目录

Skill Aggregator 自动从 `~/.hermes/config.yaml` 读取技能目录。编辑配置文件即可：

```yaml
# ~/.hermes/config.yaml
skills:
  external_dirs:
    - ~/.hermes/skills
    - ~/my-agent/.hermes/skills    # 新增：你的项目技能目录
    - ~/team-shared/skills         # 新增：团队共享技能
```

保存后运行 `skill-aggregator --force` 重建索引即可生效。无需修改代码。

### 集成到开发流程

```bash
# 提交前检查：确保相关 skill 可用
git commit -m "feat: 用户认证模块"
# 提交后自动匹配相关 skill 建议
skill-aggregator "用户认证"

# CI 集成：检测技能健康状态
skill-aggregator clean --json | python3 -c "
import json, sys
data = json.load(sys.stdin)
errors = [i for i in data['issues'] if i['severity'] == 'error']
if errors:
    print(f'❌ {len(errors)} 个技能错误')
    sys.exit(1)
print('✅ 技能健康')
"
```

## 测试

```bash
# 运行匹配测试
python3 tests/test_matcher.py

# 测试特定任务
python3 -c "
from skill_aggregator import recommend
results = recommend('add unit tests for auth module', top_n=3, verbose=False)
for r in results:
    print(f'{r[\"skill\"]}: {r[\"score\"]:.2%}')
"
```

## 故障排查

### 索引未更新

```bash
# 手动强制重建
python3 -m skill_aggregator --force

# 检查索引文件
cat ~/.skill-aggregator/index.json | python3 -m json.tool | head -20
```

### 匹配结果不理想

1. 检查任务描述是否包含足够的关键词
2. 查看技能索引是否包含相关技能
3. 调整匹配权重（见"自定义匹配权重"）
4. 确认 jieba 分词已安装：`pip install jieba`

### 中文分词不生效

```bash
# 确认 jieba 已安装
python3 -c "import jieba; print('✅ jieba', jieba.__version__)"

# 如未安装
pip install jieba
# 然后重建索引
skill-aggregator --force
```

### 找不到技能文件

```bash
# 检查技能目录是否存在
ls -la ~/.hermes/skills/

# 检查 config.yaml 中的 external_dirs 配置
python3 -c "
from pathlib import Path
config = Path.home() / '.hermes' / 'config.yaml'
if config.exists():
    print(config.read_text())
"
```

### 代理/网络问题

如果你在中国大陆使用，GitHub 可能需要代理：

```bash
# 临时设置 git 代理
git config --local http.proxy 'http://127.0.0.1:7897'
git config --local https.proxy 'http://127.0.0.1:7897'

# 完成后清除代理设置
git config --local --unset http.proxy
git config --local --unset https.proxy
```
