"""Detect potential future dependencies by replaying factor calculations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping

import numpy as np
import pandas as pd

from factors import FactorDefinition


@dataclass
class LeakViolation:
    """A single suspected leak signal."""

    column: str
    signal_type: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeakDetectionResult:
    """Container for detector output used throughout the project."""

    inspected_columns: List[str]
    violations: List[LeakViolation] = field(default_factory=list)
    notes: str | None = None


@dataclass
class FactorComparison:
    compared_rows: int
    mismatches: list[dict[str, Any]] = field(default_factory=list)


def detect_leaks(
    df: pd.DataFrame,
    *,
    factor_definitions: Mapping[str, FactorDefinition],
    entity_col: str = "symbol",
    time_col: str = "date",
    tolerance: float = 1e-9,
) -> LeakDetectionResult:
    """Compare each factor's full-data values with its values as of each time.

    Use absolute tolerance and treat two missing values as equal. Confidence
    is the fraction of compared rows that differ, not a statistical probability.
    Time values must sort chronologically (e.g. timestamps or ISO date strings).
    """
    # 先排好每只股票的时间顺序，再分配唯一行索引。
    # 截取数据时保留这些索引，方便把重算结果与全量基准对齐。
    ordered = _ordered_panel(df, entity_col, time_col, tolerance).reset_index(drop=True)
    by_time = list(ordered.groupby(time_col, sort=True, observed=True).groups.items())
    result = LeakDetectionResult(inspected_columns=[])
    if ordered.empty:
        return result

    for name, factor in factor_definitions.items():
        baseline = _evaluate(name, factor, ordered)
        mismatches = []
        for as_of, rows in by_time:
            # 重算保留截至当天的历史和当天所有股票，比较时只取当天的行。
            prefix = ordered.loc[ordered[time_col] <= as_of]
            replayed = _evaluate(name, factor, prefix)
            full_values = baseline.loc[rows].to_numpy()
            replay_values = replayed.loc[rows].to_numpy()
            for position in _different_positions(full_values, replay_values, tolerance):
                row = rows[position]
                mismatches.append({
                    time_col: str(as_of),
                    entity_col: str(ordered.at[row, entity_col]),
                    "full_value": _report_value(full_values[position]),
                    "replay_value": _report_value(replay_values[position]),
                })

        result.inspected_columns.append(name)
        if mismatches:
            result.violations.append(LeakViolation(
                column=name,
                signal_type="forward_replay_mismatch",
                confidence=len(mismatches) / len(ordered),
                details={
                    "compared_rows": len(ordered),
                    "mismatch_count": len(mismatches),
                    "mismatches": mismatches,
                },
            ))
    return result


def compare_future_prices(
    df: pd.DataFrame,
    *,
    factor_definitions: Mapping[str, FactorDefinition],
    tolerance: float = 1e-9,
) -> dict[str, FactorComparison]:
    """Multiply closes strictly after each cutoff by 1.5 and compare that day."""
    ordered = _ordered_panel(df, "symbol", "date", tolerance)
    if not ordered.index.is_unique:
        # 有重复标签时使用内部行号；两次计算仍拿到相同的索引。
        ordered = ordered.reset_index(drop=True)
    results = {name: FactorComparison(0) for name in factor_definitions}
    if ordered.empty:
        return results

    baselines = {
        name: _evaluate(name, factor, ordered) for name, factor in factor_definitions.items()
    }
    for as_of, rows in ordered.groupby("date", sort=True, observed=True).groups.items():
        future = ordered["date"] > as_of
        if not future.any():
            continue
        # 每次都从原数据复制，扰动不在检查日之间累积。
        altered = ordered.copy()
        altered["close"] = ordered["close"].where(~future, ordered["close"] * 1.5)
        for name, factor in factor_definitions.items():
            original = baselines[name].loc[rows].to_numpy()
            changed = _evaluate(name, factor, altered).loc[rows].to_numpy()
            result = results[name]
            result.compared_rows += len(rows)
            for position in _different_positions(original, changed, tolerance):
                result.mismatches.append({
                    "date": str(as_of),
                    "symbol": str(ordered.at[rows[position], "symbol"]),
                    "full_value": _report_value(original[position]),
                    "perturbed_value": _report_value(changed[position]),
                })
    return results


def _ordered_panel(
    df: pd.DataFrame, entity_col: str, time_col: str, tolerance: float
) -> pd.DataFrame:
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and non-negative")
    keys = [entity_col, time_col]
    missing = [key for key in keys if key not in df.columns]
    if missing:
        raise ValueError(f"Missing entity/time columns: {missing}")
    if df[keys].isna().any().any() or df.duplicated(keys).any():
        raise ValueError("Entity/time keys must be non-missing and unique")
    return df.sort_values(keys)


def _different_positions(original: np.ndarray, other: np.ndarray, tolerance: float) -> np.ndarray:
    # 只用绝对容差。两边都缺失视为一致，只有一边缺失则记为差异。
    return np.flatnonzero(~np.isclose(original, other, atol=tolerance, rtol=0, equal_nan=True))


def _evaluate(name: str, factor: FactorDefinition, data: pd.DataFrame) -> pd.Series:
    # 用副本隔离因子对输入的修改，避免影响其他日期或其他因子的计算。
    values = factor.function(data.copy())
    # 返回顺序可以不同，但每条输入记录必须有且仅有一个同索引的结果。
    if (
        not isinstance(values, pd.Series)
        or not values.index.is_unique
        or len(values) != len(data)
        or not data.index.isin(values.index).all()
    ):
        raise ValueError(f"Factor {name!r} must return a Series aligned to the input index")
    numeric = pd.to_numeric(values, errors="raise")
    if np.iscomplexobj(numeric.to_numpy()):
        raise ValueError(f"Factor {name!r} must return real values")
    return pd.Series(numeric.to_numpy(dtype=float, na_value=np.nan), index=values.index)


def _report_value(value: float) -> float | str | None:
    # JSON 没有 NaN 或无穷大数值，用 null 和字符串分别表示。
    if np.isnan(value):
        return None
    if np.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"
    return float(value)
