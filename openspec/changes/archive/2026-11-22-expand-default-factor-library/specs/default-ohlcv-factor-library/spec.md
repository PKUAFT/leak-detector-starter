# Spec Delta

## Purpose
Exercise the default replay detector with a wider set of daily price and volume features.

## ADDED Requirements

### Requirement: Inspect the expanded factor library
The default registry SHALL expose 20 factors, including the four existing factors and 16 additional OHLCV factors evaluated as of the daily close.

#### Scenario: Report on the default simulated sample
- **WHEN** the default pipeline runs on the standard sample
- **THEN** the report SHALL record 20 inspected factors and flag only the existing intentional future return factor

#### Scenario: Evaluate grouped historical windows
- **WHEN** factors are calculated on a time-ordered panel with multiple symbols
- **THEN** rolling calculations SHALL stay within each symbol and include only current or earlier rows
- **AND** incomplete windows and undefined ratios SHALL remain missing while preserving input index alignment
