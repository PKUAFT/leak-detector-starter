# Spec Delta

## MODIFIED Requirements

### Requirement: Inspect the expanded factor library
The default registry SHALL expose the existing 20 factors plus five intentionally leaky variants of the OHLCV factors.

#### Scenario: Report on the default simulated sample
- **WHEN** the default pipeline runs on the standard sample
- **THEN** all three reports SHALL flag the six intentional leakage controls and no historical factors
- **AND** the report SHALL record 25 inspected factors

#### Scenario: Evaluate grouped historical windows
- **WHEN** historical factors are calculated on a time-ordered panel with multiple symbols
- **THEN** rolling calculations SHALL stay within each symbol and include only current or earlier rows
- **AND** incomplete windows and undefined ratios SHALL remain missing while preserving input index alignment

#### Scenario: Evaluate five new leakage controls
- **WHEN** the variants evaluate the same panel as their controls
- **THEN** their calculations SHALL reflect next-observation candle data, forward momentum, a centered mean, a future range, and a full-sample volume mean, respectively
