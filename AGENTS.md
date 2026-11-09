# Agent 工作指南

## 项目目的与边界

这是未来信息泄露检测的教学脚手架，不是已经完成或经过真实市场数据验证的检测器。`src/leak_detection/detector.py` 的 `NotImplementedError` 是练习的一部分；除非任务明确要求实现检测器，不要补全它或把占位状态描述为缺陷已修复。模拟行情不代表真实市场或 point-in-time 数据。

## 从哪里开始

- `README.md`：安装、运行和项目状态；`CONTRIBUTING.md`：贡献和验证约定；`CHANGELOG.md`：实质变更记录。
- `docs/exercise.md`：检测目标、接口和时序边界；`docs/README.md` 是文档索引。
- `docs/reference/数据的前视偏差分析.md`：前视偏差和历史时点可用性的入门参考；分析数据可得时间、版本或样本选择时阅读。文中示例是假设情景，不是本项目检测效果的证据。
- `src/factors/`：注册表及两个历史因子、一个故意泄露未来收益的示例。
- `src/leak_detection/data.py`、`detector.py`、`pipeline.py`、`reporting.py`：数据、练习入口、管线和输出。
- `tests/`：pytest 自动化测试；`tests/tools/`：手动运行的数据预览、生成与检测命令，它们不是 pytest 测试。

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
- 涉及研究或分析结论时，按 `docs/analysis/TEMPLATE.md` 保存来源、方法、结果与局限；不为简单改动创建空报告。
- 修改时间序列逻辑时写针对正例、负例和边界情况的测试。注意同一时点的完整截面、顺序、缺失值和索引；不要以全量数据拟合的结果冒充截至当时可得信息。
- 记录验证命令和结果。基础测试通过不等于检测器已实现或不存在泄露；不要把相关性或前推重算当成无泄露证明。
- 保留模拟数据生成器和历史文档；不要提交生成的数据、虚拟环境、缓存、输出、密钥或私人数据。
- 旧的 Codex CLI 指导文档仅供历史参考；产品安装和命令以当前官方文档为准。
