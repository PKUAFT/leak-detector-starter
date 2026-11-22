# 因子泄露检测入门项目

这是一个用于金融科技协会新生训练的 Python 脚手架。学员通过实现因子代码的未来信息泄露检测，练习时序数据分析、测试和使用编程 Agent。项目提供模拟行情生成器、示例因子和报告输出接口；模拟数据在本地生成，不随仓库提供。

**当前状态：** `detect_leaks` 已实现按日期前推重算。检测管线可在生成模拟数据后运行。

## 快速开始

需要 Python 3.10–3.12 和 Git。克隆后在仓库根目录执行：

```bash
git clone https://github.com/PKUAFT/leak-detector-starter.git
cd leak-detector-starter
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python tests/tools/regenerate_data.py
python tests/tools/preview_data.py -n 5
python -m pytest
```

只运行项目可使用 `python -m pip install -e .`；使用 `.[dev]` 会同时安装测试依赖。可编辑安装使项目模块可以在交互式 Python 中导入。工具脚本可从任意当前目录通过脚本路径调用。

依赖和 pytest 配置记录在 `pyproject.toml`。`requirements.txt` 暂时保留为兼容入口；`pytest.ini` 也暂时保留，并与 `pyproject.toml` 中的测试配置一致。pytest 默认读取 `pytest.ini`；可使用 `python -m pytest -c pyproject.toml` 显式选择新配置。

## 目录

```text
AGENTS.md                 Agent 工作指南
.agents/                  OpenSpec 技能及激活规则
CHANGELOG.md              变更记录
CONTRIBUTING.md           贡献与验证约定
README.md                 项目入口
src/factors/              因子注册表及安全/泄露示例
src/leak_detection/       数据、检测器、管线及报告
tests/                    自动化测试；tools/ 存放手动运行的命令入口
docs/                     参考资料及脚手架搭建指南
openspec/                 规格驱动变更的项目配置
```

## 练习

[`detect_leaks`](src/leak_detection/detector.py) 对注册因子进行只使用截至给定时点数据的前推重算，将疑似问题封装为 `LeakViolation` 和 `LeakDetectionResult`。有意泄露的例子是 [`factor_future_return`](src/factors/sample_factors.py)。

可运行 `python tests/tools/run_pipeline.py --output outputs/manual`，查看 CSV、JSON 和 Markdown 报告。命令默认在当前工作目录创建输出；模拟数据可用 `python tests/tools/regenerate_data.py` 重建，该命令默认写入并覆盖本地忽略的 `outputs/sample_factors.csv`；若要另存，可运行 `python tests/tools/regenerate_data.py --output outputs/other_sample.csv`。前推重算只能检查特定运行和输入下的未来依赖，不能证明输入字段的真实可得时间或整个研究流程没有泄露。

## 默认管线的因子

默认注册表有 25 个因子，包含原有四个示例、下列 16 个历史量价因子和 5 个故意泄露版本。设计参考 [Qlib Alpha158](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py#L889)，使用本项目的日频 OHLCV，无需安装 Qlib。

| 类别 | 新增因子 |
| --- | --- |
| 当日 K 线（4 个） | 带符号的实体比例、上影线比例、下影线比例、带符号的收盘位置 |
| 价格窗口（8 个） | 5/20 期收盘动量、均价比、价格标准差比、高低价区间位置 |
| 成交量与走势（4 个） | 5/20 期均量比、20 期收盘价与对数成交量相关系数、20 期上涨比例 |

表中的 16 个因子假定当天收盘后计算，滚动窗口包含当日，且只使用同一股票截至当日的记录。完整窗口不足或计算无定义时保留缺失。

五个泄露版本以 `factor_leaky_` 开头，分别使用下一期上影线、前向五期动量、居中五期均价、未来五期高低价区间和全样本均量。它们与原有的 `factor_future_return` 一起作为教学正例。默认模拟数据的报告会标记这六个因子。

## 前视偏差对比实验

从仓库根目录运行：

```powershell
python tests/tools/run_lookahead_experiments.py --output outputs/lookahead-experiments
```

命令自己生成固定种子的模拟行情，在 `comparison.csv` 和 `report.md` 中对照七个案例的前推重算和未来价格扰动结果。三组因子分别检查收益窗口、波动率分母、全样本标准化参数。每组都有只用历史数据的对照，均假定当天收盘后计算。

价格扰动只将检查日之后的收盘价乘以 1.5。仅依赖未来行是否存在的案例会被截断重算标记，却不会因为改价而改变；以其他字段为来源的依赖也需要对应扰动。默认 25 因子管线与七案例对比实验可分别运行。

入门阅读：[数据的前视偏差分析](docs/reference/数据的前视偏差分析.md)介绍历史时点可用性、数据修订、样本选择和自检方法；文中日期和数值均为假设示例。

更多说明见 [文档索引](docs/README.md)、[脚手架搭建指南](docs/homework/因子泄露检测脚手架搭建指南.md)、[贡献指南](CONTRIBUTING.md)、[变更记录](CHANGELOG.md) 和 [Agent 指南](AGENTS.md)。
