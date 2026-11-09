# Changelog

记录影响使用者或贡献者的实质性变化。未发布的变化放在 `Unreleased` 下，按需使用 Added、Changed、Fixed、Removed；发布时再记录真实版本与日期。不要为尚未实现的功能填写完成记录。

## [Unreleased]

### Added

- 增加 `AGENTS.md`、文档索引、练习设计说明、贡献指南及分析记录模板。
- 增加从仓库外使用源码和命令行入口的检查。

### Changed

- 将 `factors` 和 `leak_detection` 核心包移至 `src/`，将原新生指导文档移至 `docs/` 并标为历史资料。
- 更新 README、测试路径配置和运行脚本的源码与数据定位。
- 仓库改为公开，README 使用公开 HTTPS 克隆地址。

### Fixed

- 补充数据预览所需的 `tabulate` 和测试所需的 `pytest` 开发依赖。
- 忽略虚拟环境、测试缓存与覆盖率输出。

### 已知状态

- `detect_leaks` 仍为有意保留的教学占位；运行检测管线需要先实现练习。
