"""Pipeline utilities to run a detector and persist its outputs."""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Mapping

import pandas as pd

from factors import FactorDefinition, get_registered_factors

from .data import describe_dataset, load_sample_factors
from .detector import LeakDetectionResult, detect_leaks
from .reporting import export_all

DetectorFn = Callable[..., LeakDetectionResult]


def run_pipeline(
    detector: DetectorFn = detect_leaks,
    *,
    data_path: Path | None = None,
    output_dir: Path | str = "outputs/manual",
    factor_definitions: Mapping[str, FactorDefinition] | None = None,
    tolerance: float = 1e-9,
) -> Dict[str, Path]:
    """Run the leak detector end-to-end and persist reports.

    Returns a mapping with keys ``summary``/``json``/``markdown`` pointing to the generated artefacts.
    """

    df = load_sample_factors(data_path)
    descriptor = describe_dataset(df)

    factor_definitions = factor_definitions or get_registered_factors()

    try:
        result = detector(
            df,
            factor_definitions=factor_definitions,
            entity_col="symbol",
            time_col="date",
            tolerance=tolerance,
        )
    except NotImplementedError as exc:  # pragma: no cover - clarity for students
        raise RuntimeError(
            "检测逻辑尚未实现。请先在 leak_detection/detector.py 中完成 detect_leaks 函数。"
        ) from exc

    if result.notes is None:
        span = f"{descriptor.symbols[0]}…{descriptor.symbols[-1]}" if descriptor.symbols else "N/A"
        result.notes = (
            f"Inspected {len(result.inspected_columns)} factor functions across {descriptor.rows} rows "
            f"({span}) from {descriptor.start_date} to {descriptor.end_date}."
        )

    output_dir = Path(output_dir)
    artefacts = export_all(result, output_dir)
    return artefacts


def preview_dataset(rows: int = 5, *, data_path: Path | None = None) -> pd.DataFrame:
    """Return the first ``rows`` rows of the dataset for quick inspection."""

    df = load_sample_factors(data_path)
    return df.head(rows).copy()
