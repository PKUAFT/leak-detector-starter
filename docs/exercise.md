# 练习与设计说明

## 目标

实现 `src/leak_detection/detector.py` 的 `detect_leaks`，接收行情 DataFrame 和因子注册表，返回 `LeakDetectionResult`，用 `LeakViolation` 描述疑似问题。当前实现刻意抛出 `NotImplementedError`，这是练习起点。

示例数据由 `src/leak_detection/simulator.py` 生成；`src/factors/sample_factors.py` 包含两个基于历史数据的因子及一个故意引用下一日收盘价的因子。管线读取数据、调用检测器，再通过 reporting 写出 CSV、JSON 和 Markdown。

## 推荐方法

在每个选定的 `as_of` 时点，保留所有该时点及之前可用的行，对同一因子重算，并与完整输入下该时点的结果对齐比较。先明确数据排序、实体和时间键、相同时间的截面、窗口预热期、NaN 和容差。对差异记录可重现的因子、时点、实体和比较值；因子计算失败应单独报告，不能当作安全。

测试至少覆盖故意泄露的因子、历史因子、边界和缺失值。可扩展静态规则，但需要记录其适用范围与误报、漏报。不要把因子注册表中的 `is_intentional_leak` 标记直接用作检测结果；它是教学用标签。

## 使用边界

前推重算检查的是给定函数和输入在实际执行路径上的时序依赖，不证明原始字段在历史时点可得，也不能独立排除事后修订、预计算特征、全样本拟合、标签重叠或选模泄露。模拟数据和测试结果不构成真实市场验证。

实现后运行 `python -m pytest`，再运行 `python tests/tools/run_pipeline.py --output outputs/manual`。检查泄露示例被标记、非泄露示例未被错误标记，并人工检查报告和测试覆盖的限制。当前基础测试仅验证脚手架运行，并非检测器验收。
