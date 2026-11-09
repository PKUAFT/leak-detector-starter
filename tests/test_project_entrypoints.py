"""Check that the source layout works from outside the checkout directory."""

import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run_python(args, cwd, *, source_path=False):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    if source_path:
        env["PYTHONPATH"] = str(ROOT / "src")
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True
    )


def test_source_import_and_default_data_outside_checkout(tmp_path):
    result = run_python(
        ["-c", "from leak_detection.data import load_sample_factors; "
         "print(len(load_sample_factors()))"],
        tmp_path,
        source_path=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "180"


def test_pipeline_reports_the_intentional_exercise_placeholder(tmp_path):
    result = run_python([str(ROOT / "scripts" / "run_pipeline.py")], tmp_path)
    assert result.returncode != 0
    assert "检测逻辑尚未实现" in result.stderr
    assert not (tmp_path / "outputs").exists()
