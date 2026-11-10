# Agent 工作指南

## 项目目的与边界

这是未来信息泄露检测的教学脚手架，不是已经完成或经过真实市场数据验证的检测器。`src/leak_detection/detector.py` 的 `NotImplementedError` 是练习的一部分；除非任务明确要求实现检测器，不要补全它或把占位状态描述为缺陷已修复。模拟行情不代表真实市场或 point-in-time 数据。

## 从哪里开始

- `README.md`：安装、运行和项目状态；`CONTRIBUTING.md`：贡献和验证约定；`CHANGELOG.md`：实质变更记录。
- `docs/README.md`：文档索引；`docs/homework/`：脚手架搭建及课程练习指南。
- `docs/reference/数据的前视偏差分析.md`：前视偏差和历史时点可用性的入门参考；分析数据可得时间、版本或样本选择时阅读。文中示例是假设情景，不是本项目检测效果的证据。
- `src/factors/`：注册表及两个历史因子、一个故意泄露未来收益的示例。
- `src/leak_detection/data.py`、`detector.py`、`pipeline.py`、`reporting.py`：数据、练习入口、管线和输出。
- `tests/`：pytest 自动化测试；`tests/tools/`：手动运行的数据预览、生成与检测命令，它们不是 pytest 测试。

## OpenSpec 技能与激活条件

用户明确要求 OpenSpec、规范驱动开发或指定现有 OpenSpec change 时使用；涉及多模块行为、公共接口或需要先确认设计的重大变更，也可使用。简单文档、路径、配置调整和局部修复直接处理，不强制创建提案。用户当前指令和仓库实际情况优先于生成的技能模板；不得因模板中的工具名称而调用不可用工具或擅自派发子任务。

技能位于 `.agents/skills/`，激活条件与阶段路由记录在 `.agents/activation.toml`；涉及 OpenSpec 时先读取该文件，再按任务读取对应 `SKILL.md`：

- 新建提案、设计、规格和任务：`openspec-propose`。
- 在 OpenSpec 变更上下文中探索需求和设计取舍：`openspec-explore`。
- 实施或继续已存在的 OpenSpec 变更：`openspec-apply-change`。
- 修改现有变更的规划文件：`openspec-update-change`。
- 按已授权的流程将变更规格同步至主规格：`openspec-sync-specs`。
- 用户要求归档已完成的 OpenSpec 变更：`openspec-archive-change`；这不等同于归档 GitHub 仓库。

Codex 可发现 `.agents/skills/` 的技能，并根据各自 `SKILL.md` 的描述匹配任务；`.agents/activation.toml` 是本项目的补充说明，不是 Codex 原生自动加载的激活配置。执行前用 `openspec --version` 检查本机 CLI；如缺失，说明限制并遵循用户指示，不静默安装全局软件。`openspec/config.yaml` 保存本项目上下文。OpenSpec 生成器可能重建 `.agent/` 并覆盖原始技能描述，更新后应检查目录与激活条件。

## 本地工作

使用 Python 3.10–3.12，在仓库根目录执行：

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python tests/tools/regenerate_data.py
python tests/tools/preview_data.py -n 5
python -m pytest
```

依赖和测试配置见 `pyproject.toml`。暂存的 `pytest.ini` 是 pytest 的默认配置，须与其中的测试配置保持一致；可用 `python -m pytest -c pyproject.toml` 显式验证新配置。可编辑安装后可直接导入项目模块。检测管线在未实现时应报明确错误，不应伪造成功报告。`python tests/tools/regenerate_data.py` 默认生成并覆盖未跟踪的 `outputs/sample_factors.csv`；可用 `--output outputs/other_sample.csv` 另存。测试自行使用临时目录生成数据，无需预先生成默认样本。

## 修改约定

- 保持任务范围清晰；维护入口、文档和测试，使它们与实际目录及行为一致。面向用户或贡献者的实质变化记录到 `CHANGELOG.md` 的 `Unreleased`。
- 涉及研究或分析结论时，记录来源、方法、结果与局限；不为简单改动创建空报告。
- 修改时间序列逻辑时写针对正例、负例和边界情况的测试。注意同一时点的完整截面、顺序、缺失值和索引；不要以全量数据拟合的结果冒充截至当时可得信息。
- 记录验证命令和结果。基础测试通过不等于检测器已实现或不存在泄露；不要把相关性或前推重算当成无泄露证明。
- 保留模拟数据生成器和历史文档；不要提交生成的数据、虚拟环境、缓存、输出、密钥或私人数据。
