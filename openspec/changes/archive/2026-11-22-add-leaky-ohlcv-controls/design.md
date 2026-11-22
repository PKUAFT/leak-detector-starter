# Design

## Context
`expand-default-factor-library` established the 20-factor baseline. Apply this change after that baseline when syncing specs.

## Decisions

| 历史对照 | 故意泄露版 |
| --- | --- |
| 当日上影线比例 | 使用下一条观测的上影线 |
| 五期收盘动量 | 使用当日至未来第五期的收益 |
| 五期均价比 | 用居中窗口，将未来两期纳入均价 |
| 五期区间位置 | 用未来五期的最高和最低价作为区间 |
| 二十期均量比 | 用同一股票整个样本的均量作分子 |

正例名称和注册元数据明确标记其教学用途。检测逻辑继续只读因子计算结果。维持三种默认报告，并以行数和实例核查结果。
