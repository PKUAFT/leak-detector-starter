# Proposal

## Why
默认管线只有四个因子，难以展示不同的量价计算在同一检测流程中的表现。

## What Changes
- 参考 Qlib Alpha158，在原有四个因子之外增加 16 个收盘后可计算的量价因子。
- 验证总计 20 个因子被检查，仍只标记原有的故意泄露因子。

## Capabilities
### New Capabilities
- `default-ohlcv-factor-library`：默认管线中的量价因子及其历史窗口约定。

### Modified Capabilities

## Impact
影响默认因子注册表、测试和说明。独立的七案例对比实验沿用自身的因子集合，无需安装 Qlib。
