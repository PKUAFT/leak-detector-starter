# Proposal

## Why
检测管线目前因检测器未实现而无法生成报告。完成前推重算后，可用仓库自带的三个因子验证未来依赖检测。

## What Changes
- 实现按日期截断数据并比较因子结果的检测器。
- 验证一个未来收益因子、两个历史因子以及报告生成。

## Capabilities
### New Capabilities
- `factor-leak-detection`：通过时间前推重算识别疑似未来数据行依赖。

### Modified Capabilities

## Impact
影响检测器、测试和项目使用说明。沿用现有因子、管线接口和依赖。
