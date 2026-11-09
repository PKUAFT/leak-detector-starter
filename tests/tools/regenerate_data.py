"""Regenerate the simulated factor dataset."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from leak_detection.simulator import write_dataset


def main(target: str | Path | None = None) -> Path:
    """Write the dataset to ``target`` (defaults to outputs/sample_factors.csv)."""

    path = write_dataset(Path(target) if target else None)
    print(f"Dataset saved to {path}")
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regenerate the simulated market dataset")
    parser.add_argument(
        "--output", type=Path, default=None,
        help="Output CSV path (default: repository outputs/sample_factors.csv)",
    )
    args = parser.parse_args()
    main(args.output)
