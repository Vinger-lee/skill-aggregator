# Changelog

## [0.1.0] - 2026-05-02

### Added
- 🎯 三段式工作流：意图分析 → 需求确认 → 加载技能
- 🧠 纯规则意图分析引擎（8领域 × 11活动）
- 💬 模糊度计算 + 自动生成澄清问题
- 🔄 按需索引重建（新 skill 触发）
- 📦 pip install 支持（pyproject.toml）
- 🎨 emoji 彩色 CLI 输出
- 📝 完整文档：README, DESIGN, CONTRIBUTING, CODE_OF_CONDUCT
- 🧪 单元测试

### Changed
- 从 `src/` 重命名为 `skill_aggregator/` Python 包
- 匹配引擎升级为四路评分（关键词+领域+TF-IDF+优先级）
- README 更新为三段式工作流描述

### Fixed
- 中文查询匹配优化（领域分类 + 关键词判定）
- 索引重建不依赖定时任务（按需触发，节省 API）

### 初始版本
- 技能索引构建器（扫描 623 个技能文件）
- TF-IDF 多维评分匹配引擎
- 自动增量更新机制
- Hermes Agent + Claude Code 双平台集成
