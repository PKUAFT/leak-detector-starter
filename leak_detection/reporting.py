"""Helpers for serialising leak detection results."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .detector import LeakDetectionResult, LeakViolation


def to_summary_frame(result: LeakDetectionResult) -> pd.DataFrame:
    """Convert detector output to a tidy pandas DataFrame."""

    if not result.violations:
        return pd.DataFrame(columns=["factor", "signal_type", "confidence", "extra"])
    records = [
        {
            "factor": v.column,
            "signal_type": v.signal_type,
            "confidence": v.confidence,
            "extra": v.details,
        }
        for v in result.violations
    ]
    return pd.DataFrame.from_records(records)


def write_csv(result: LeakDetectionResult, path: Path) -> Path:
    """Persist the summary frame as CSV."""

    frame = to_summary_frame(result)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def write_json(result: LeakDetectionResult, path: Path) -> Path:
    """Persist the full violation list as JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "column": v.column,
            "signal_type": v.signal_type,
            "confidence": v.confidence,
            "details": v.details,
        }
        for v in result.violations
    ]
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def write_markdown_overview(result: LeakDetectionResult, path: Path) -> Path:
    """Export a lightweight Markdown overview for students to tweak."""

    frame = to_summary_frame(result)
    lines: list[str] = ["# Leak Detection Summary", ""]

    if frame.empty:
        lines.append("未发现可疑的泄露信号。")
    else:
        lines.append("发现如下可疑因子：")
        lines.append("")
        header = "| factor | signal_type | confidence |"
        separator = "| --- | --- | --- |"
        lines.extend([header, separator])
        for _, row in frame.iterrows():
            lines.append(f"| {row['factor']} | {row['signal_type']} | {row['confidence']:.3f} |")
        lines.append("")

    if result.notes:
        lines.append("## Notes")
        lines.append(result.notes)
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def export_all(result: LeakDetectionResult, output_dir: Path) -> dict[str, Path]:
    """Write CSV/JSON/Markdown artefacts for a detector run."""

    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "summary.csv"
    json_path = output_dir / "violations.json"
    markdown_path = output_dir / "report.md"

    return {
        "summary": write_csv(result, summary_path),
        "json": write_json(result, json_path),
        "markdown": write_markdown_overview(result, markdown_path),
    }
