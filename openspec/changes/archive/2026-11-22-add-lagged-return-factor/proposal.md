# Proposal

## Why
作业需要用自定义因子检验检测器。将滞后收益率因子加入默认管线，便于直接观察它与故意泄露示例的检测结果。

## What Changes
- 新增并注册上一交易日收益率因子。
- 验证因子的计算结果和默认管线的报告。

## Capabilities
### New Capabilities
- `lagged-return-sample-factor`：按股票计算并检查上一条收益率观测值。

### Modified Capabilities

## Impact
影响默认因子注册表、测试和变更记录。
