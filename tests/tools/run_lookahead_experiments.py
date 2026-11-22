"""Run the standalone look-ahead factor comparison."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = PROJECT_ROOT / "src"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from leak_detection.experiments import run_lookahead_experiments


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/lookahead-experiments"))
    args = parser.parse_args()

    for name, path in run_lookahead_experiments(args.output).items():
        print(f"{name}: {path}")


if __name__ == "__main__":
    main()
