# 因子泄露检测入门项目

这是一个用于金融科技协会新生训练的 Python 脚手架。学员通过实现因子代码的未来信息泄露检测，练习时序数据分析、测试和使用编程 Agent。项目提供模拟行情生成器、示例因子和报告输出接口；模拟数据在本地生成，不随仓库提供。

**当前状态：** `detect_leaks` 是有意留给学员完成的练习，直接运行检测管线会提示尚未实现。现有基础测试通过不代表检测器可用，也不能证明数据不存在泄露。

## 快速开始

需要 Python 3.10–3.12 和 Git。克隆后在仓库根目录执行：

```bash
git clone https://github.com/PKUAFT/leak-detector-starter.git
cd leak-detector-starter
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python tests/tools/regenerate_data.py
python tests/tools/preview_data.py -n 5
python -m pytest
```

只运行脚本可安装 `requirements.txt`；运行测试还需要 `requirements-dev.txt`。三个脚本可从任意当前目录通过脚本路径调用。仓库采用 `src/` 布局，若在交互式 Python 中导入包，可在仓库根目录执行 `PYTHONPATH=src python`（PowerShell 使用 `$env:PYTHONPATH = "src"`）。

## 目录

```text
AGENTS.md                 Agent 工作指南
CHANGELOG.md              变更记录
CONTRIBUTING.md           贡献与验证约定
README.md                 项目入口
src/factors/              因子注册表及安全/泄露示例
src/leak_detection/       数据、待实现的检测器、管线及报告
tests/                    自动化测试；tools/ 存放手动运行的命令入口
docs/                     任务、设计、参考资料与历史教学文档
```

## 练习

在 [`src/leak_detection/detector.py`](src/leak_detection/detector.py) 实现 `detect_leaks`：对注册因子进行只使用截至给定时点数据的前推重算，将疑似问题封装为 `LeakViolation` 和 `LeakDetectionResult`。有意泄露的例子是 [`factor_future_return`](src/factors/sample_factors.py)。

实现并添加有意义的测试后，可运行 `python tests/tools/run_pipeline.py --output outputs/manual`，查看 CSV、JSON 和 Markdown 报告。命令默认在当前工作目录创建输出；模拟数据可用 `python tests/tools/regenerate_data.py` 重建，该命令默认写入并覆盖本地忽略的 `outputs/sample_factors.csv`；若要另存，可运行 `python tests/tools/regenerate_data.py --output outputs/other_sample.csv`。前推重算只能检查特定运行和输入下的未来依赖，不能证明输入字段的真实可得时间或整个研究流程没有泄露。

入门阅读：[数据的前视偏差分析](docs/reference/数据的前视偏差分析.md)介绍历史时点可用性、数据修订、样本选择和自检方法；文中日期和数值均为假设示例。

更多说明见 [文档索引](docs/README.md)、[练习与设计说明](docs/exercise.md)、[贡献指南](CONTRIBUTING.md)、[变更记录](CHANGELOG.md) 和 [Agent 指南](AGENTS.md)。
