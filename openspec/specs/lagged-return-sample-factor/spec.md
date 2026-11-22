# lagged-return-sample-factor Specification

## Purpose
Provide a historical return factor that can be checked alongside the existing examples in the default pipeline.

## Requirements

### Requirement: Lagged return by symbol
The default registry SHALL include `factor_lagged_return`, which returns each symbol's immediately preceding `ret_1d` in time-ordered data and preserves the input index.

#### Scenario: Compute returns for interleaved symbols
- **WHEN** two symbols have multiple observations in time order
- **THEN** each symbol's first observation is missing and subsequent values come from the preceding observation for that symbol

#### Scenario: Detect leaks on default sample data
- **WHEN** the pipeline checks the initial four-factor set (lagged EMA, lagged volume mean, lagged return, and future return) on generated sample data
- **THEN** it checks the lagged return factor and reports only the intentional future return leak
