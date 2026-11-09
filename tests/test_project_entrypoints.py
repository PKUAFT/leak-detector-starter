"""Exercise generated-data and command entry points in an isolated checkout."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def checkout(tmp_path):
    root = tmp_path / "checkout"
    shutil.copytree(ROOT / "src", root / "src", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "tests" / "tools", root / "tests" / "tools")
    return root


def run_python(args, cwd, *, source_root=None):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    if source_root:
        env["PYTHONPATH"] = str(source_root / "src")
    return subprocess.run(
        [sys.executable, *args], cwd=cwd, env=env, capture_output=True, text=True
    )


def generate_sample(checkout, cwd):
    result = run_python([str(checkout / "tests" / "tools" / "regenerate_data.py")], cwd)
    assert result.returncode == 0, result.stderr
    assert (checkout / "outputs" / "sample_factors.csv").is_file()


def test_default_data_requires_generation_with_clear_guidance(checkout, tmp_path):
    result = run_python([str(checkout / "tests" / "tools" / "preview_data.py")], tmp_path)
    assert result.returncode != 0
    assert "tests/tools/regenerate_data.py" in result.stderr
    assert not (checkout / "outputs").exists()


def test_source_import_and_generated_data_outside_checkout(checkout, tmp_path):
    generate_sample(checkout, tmp_path)
    result = run_python(
        ["-c", "from leak_detection.data import load_sample_factors; "
         "print(len(load_sample_factors()))"],
        tmp_path,
        source_root=checkout,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "180"


def test_pipeline_reports_the_intentional_exercise_placeholder(checkout, tmp_path):
    generate_sample(checkout, tmp_path)
    result = run_python([str(checkout / "tests" / "tools" / "run_pipeline.py")], tmp_path)
    assert result.returncode != 0
    assert "检测逻辑尚未实现" in result.stderr
    assert not (tmp_path / "outputs").exists()


def test_preview_command_reads_generated_data_from_any_directory(checkout, tmp_path):
    generate_sample(checkout, tmp_path)
    result = run_python([str(checkout / "tests" / "tools" / "preview_data.py"), "-n", "2"], tmp_path)
    assert result.returncode == 0, result.stderr
    assert "symbol" in result.stdout
    assert "AAA" in result.stdout


def test_regenerate_command_can_write_to_an_explicit_path(checkout, tmp_path):
    target = tmp_path / "generated.csv"
    result = run_python(
        [str(checkout / "tests" / "tools" / "regenerate_data.py"), "--output", str(target)],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert target.is_file()
    assert len(target.read_text().splitlines()) == 181
    assert not (checkout / "outputs" / "sample_factors.csv").exists()
