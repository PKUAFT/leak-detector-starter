# Changelog

记录影响使用者或贡献者的实质性变化。未发布的变化放在 `Unreleased` 下，按需使用 Added、Changed、Fixed、Removed；发布时再记录真实版本与日期。不要为尚未实现的功能填写完成记录。

## [Unreleased]

### Added

- 加入 OpenSpec 官方生成的 `.agent/` 技能，并在 `AGENTS.md` 中设置使用条件和工作阶段路由。
- 加入前视偏差入门参考文档，并在 README、Agent 指南和文档索引中提供入口。
- 增加 `AGENTS.md`、文档索引、练习设计说明、贡献指南及分析记录模板。
- 增加从仓库外使用源码和命令行入口的检查。

### Changed

- 将新生指导文档改为因子泄露检测脚手架搭建指南，移除 Codex CLI 内容并更新相关入口。

- 将历史新生指导文档移至 `docs/homework/`，移除重复练习说明和历史分析目录，并更新文档入口。
- 将 OpenSpec 技能从 `.agent/` 移至 Codex 可发现的 `.agents/skills/`，并添加项目路由文件 `.agents/activation.toml`。
- 新增 `pyproject.toml` 集中声明项目依赖和 pytest 设置；`requirements.txt` 保留为兼容入口，`pytest.ini` 暂保留并与新配置同步。
- 删除 `requirements-dev.txt`，开发依赖通过 `python -m pip install -e ".[dev]"` 安装。
- 移除已提交的模拟 CSV；默认样本按需在本地 `outputs/` 生成，测试在临时目录生成数据。
- 将数据预览、生成与检测命令入口移至 `tests/tools/`；这些手动工具不是 pytest 自动化测试。

- 将 `factors` 和 `leak_detection` 核心包移至 `src/`，将原新生指导文档移至 `docs/` 并标为历史资料。
- 更新 README、测试路径配置和运行脚本的源码与数据定位。
- 仓库改为公开，README 使用公开 HTTPS 克隆地址。

### Fixed

- 数据生成命令支持 `--output` 指定目标，避免忽略参数而覆盖默认样本；未知参数会报错。

- 补充数据预览所需的 `tabulate` 和测试所需的 `pytest` 开发依赖。
- 忽略虚拟环境、测试缓存与覆盖率输出。

### 已知状态

- `detect_leaks` 仍为有意保留的教学占位；运行检测管线需要先实现练习。
