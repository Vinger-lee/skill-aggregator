# 我写了个零依赖的 AI 技能搜索引擎，中英文都能用

作为一个重度 AI 编程用户，我的 agent 里装了 400+ 个技能/插件，但每次要写代码的时候还是得手动翻文件夹找技能名，或者在 prompt 里碰运气。

于是就写了个小工具：**Skill Aggregator**。

## 它能干啥

你用自然语言描述想做的事，它自动分析意图，然后推荐最合适的技能：

```
$ skill-aggregator "用 Canvas 做个粒子动画"
👉 p5js (65%) + pixel-art (45%) + ideation (30%)
```

如果你描述得模糊，它会反问澄清：
```
$ skill-aggregator --intent-only "修一下那个接口"
⚠️ 模糊度: 80%
❓ 哪个接口？REST 还是 GraphQL？
❓ 修 bug、加功能、还是重构？
```

## 特点

- **零依赖** — 纯 Python 标准库 + 可选的 jieba 分词
- **中文/英文** 都支持
- **四维评分** — 关键词(40%) + 领域(25%) + TF-IDF(20%) + 优先级(15%)
- **自动发现** — 扫描配置文件里的技能目录，不用手动配置
- **健康检查** — 检测损坏的技能文件，支持 CI 集成

## 适用场景

- 装了 N 个 AI 插件但记不住名字的开发者
- 团队新人想快速了解团队的技能积累
- 想在 CI 里监控技能健康状态
- 中英文混合的开发环境

## 链接

GitHub: https://github.com/Vinger-lee/skill-aggregator

```bash
pip install skill-aggregator
```

刚上线不久，求 star 求反馈 🙏 有什么想法和建议直接提 issue~
