"""Check that the source layout works from outside the checkout directory."""

import os
from pathlib import Path
import shutil
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
    result = run_python([str(ROOT / "tests" / "tools" / "run_pipeline.py")], tmp_path)
    assert result.returncode != 0
    assert "检测逻辑尚未实现" in result.stderr
    assert not (tmp_path / "outputs").exists()


def test_preview_command_reads_the_bundled_data_from_any_directory(tmp_path):
    result = run_python([str(ROOT / "tests" / "tools" / "preview_data.py"), "-n", "2"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "symbol" in result.stdout
    assert "AAA" in result.stdout


def test_regenerate_command_can_write_to_an_explicit_path(tmp_path):
    target = tmp_path / "generated.csv"
    checkout = tmp_path / "checkout"
    shutil.copytree(ROOT / "src", checkout / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "tests" / "tools", checkout / "tests" / "tools")
    result = run_python(
        [str(checkout / "tests" / "tools" / "regenerate_data.py"), "--output", str(target)],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert target.is_file()
    assert len(target.read_text().splitlines()) == 181
    assert not (checkout / "data" / "sample_factors.csv").exists()
