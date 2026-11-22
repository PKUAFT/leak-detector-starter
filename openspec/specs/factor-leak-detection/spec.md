# factor-leak-detection Specification

## Purpose
通过对完整行情和截至指定时点可见行情分别计算因子，识别可观察的未来行依赖，并保留疑似记录供复核。
同日比较覆盖完整股票截面，管线将结果导出为可核对的摘要和逐行证据。

## Requirements

### Requirement: Compare factor values at each observation time
The detector SHALL compare full-history and as-of factor values for every entity at the observation time using the complete cross-section and the configured absolute tolerance.

#### Scenario: Future return depends on the next row
- **WHEN** the registered future return factor is evaluated on the default simulated data
- **THEN** the detector reports mismatches because the next close is unavailable during replay

#### Scenario: Historical observations and warmup values are stable
- **WHEN** the registered lagged EMA and volume mean factors are evaluated on the default simulated data
- **THEN** the detector reports no violations for either factor, including rows with missing values in both evaluations

#### Scenario: Shuffled observations include multiple entities
- **WHEN** a deterministic same-day cross-sectional factor is evaluated on shuffled observations with distinct entity-time keys
- **THEN** each replay includes the full cross-section and matching values are not reported

### Requirement: Expose suspected dependencies in pipeline reports
The pipeline SHALL export each flagged factor to CSV, JSON and Markdown, with observation details available in the JSON report.

#### Scenario: Run the pipeline with the supplied sample factors
- **WHEN** the pipeline processes the generated sample using only the original three factors (lagged EMA, lagged volume mean, and future return)
- **THEN** all three reports identify the future return factor as the only suspect
