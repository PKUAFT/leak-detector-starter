# Proposal

## Why
默认量价因子库需要更多正例，以展示逐日前推重算能识别多种形式的未来依赖。

## What Changes
- 为五个既有量价因子分别增加教学用泄露版本。
- 默认管线检查 25 个因子，模拟样本上仅标记六个故意泄露案例。

## Capabilities
### New Capabilities

### Modified Capabilities
- `default-ohlcv-factor-library`：在扩展因子库变更之上增加五个故意泄露对照。

## Impact
默认注册表、验证和作业说明。独立七案例实验沿用自己的注册集。
