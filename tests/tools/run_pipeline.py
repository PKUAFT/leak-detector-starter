"""CLI wrapper around the leak detection pipeline."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from leak_detection.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the leak detection pipeline")
    parser.add_argument("--data", type=Path, default=None, help="Path to the factors CSV")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/manual"),
        help="Directory where reports will be written",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-9,
        help="Numerical tolerance passed to the detector",
    )
    args = parser.parse_args()

    artefacts = run_pipeline(
        data_path=args.data,
        output_dir=args.output,
        tolerance=args.tolerance,
    )
    print("Generated artefacts:")
    for name, path in artefacts.items():
        print(f"- {name}: {path}")


if __name__ == "__main__":
    main()
