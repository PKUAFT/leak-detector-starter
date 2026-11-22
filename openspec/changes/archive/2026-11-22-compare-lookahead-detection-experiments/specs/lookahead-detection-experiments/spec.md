# Spec Delta

## Purpose
Compare two dynamic checks on the same labeled factor cases and expose the evidence behind each result.

## ADDED Requirements

### Requirement: Compare leaking factors against historical controls
The experiment runner SHALL evaluate the same deterministic simulated panel using forward replay and future price perturbation. Expected case labels SHALL be kept separate from the detector decisions.

#### Scenario: Multi-step factors use future values in different stages
- **WHEN** the runner checks forward three-observation market-relative return, momentum divided by centered volatility, and a composite of daily cross-sectional rank and full-sample time-series Z-score on the standard experiment data
- **THEN** both methods SHALL flag each factor
- **AND** neither method SHALL flag the respective controls with trailing returns, trailing volatility, and standardization fit strictly before the evaluation date

#### Scenario: Factor history is insufficient or has zero dispersion
- **WHEN** an observation lacks sufficient history, has an insufficient cross-section, or requires division by zero dispersion
- **THEN** the affected factor value SHALL be missing and a matching missing value across evaluations SHALL not be flagged

#### Scenario: Dependency on future row existence
- **WHEN** a factor checks whether the current symbol has another observation in its input
- **THEN** the report SHALL show a forward replay mismatch and no price perturbation mismatch

### Requirement: Isolate future price changes
For each cutoff with future rows, the perturbation check SHALL modify only future close values on a fresh copy, preserve all rows and index labels, and compare only rows at the cutoff with the unmodified baseline. It SHALL apply absolute tolerance and consider two missing values equal.

#### Scenario: Entire cross-section remains available
- **WHEN** multiple symbols have observations at the cutoff
- **THEN** every row at that cutoff SHALL participate in the comparison
- **AND** original data and values at or before the cutoff SHALL remain unchanged

#### Scenario: No future rows remain
- **WHEN** a cutoff has no future rows
- **THEN** the perturbation check SHALL skip that cutoff and exclude its rows from comparison counts

### Requirement: Export reproducible comparison results
The separate experiment command SHALL produce CSV and Markdown with each case's expected label, source of future dependence or historical control, both decisions, and comparison and mismatch counts. Detected mismatches SHALL include at least one example with the date, symbol, baseline and comparison value for each method that flags the case.

#### Scenario: Run the standard experiment suite
- **WHEN** the user runs the dedicated command on the fixed-seed sample
- **THEN** both reports SHALL include all seven cases and distinguish method disagreement from agreement
- **AND** the default pipeline SHALL retain its existing registered factors and report behavior
