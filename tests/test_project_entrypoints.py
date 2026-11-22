"""Exercise generated-data and command entry points in an isolated checkout."""

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from leak_detection.pipeline import run_pipeline
from leak_detection.simulator import write_dataset


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


def test_pipeline_reports_an_unimplemented_detector(tmp_path):
    data_path = write_dataset(tmp_path / "sample.csv")
    output_dir = tmp_path / "reports"

    # 注入故意报错的检测器，真实检测器实现后仍可验证管线的错误提示。
    def unfinished_detector(*args, **kwargs):
        raise NotImplementedError

    with pytest.raises(RuntimeError, match="检测逻辑尚未实现"):
        run_pipeline(detector=unfinished_detector, data_path=data_path, output_dir=output_dir)
    assert not output_dir.exists()


def test_pipeline_cli_exports_consistent_results(checkout, tmp_path):
    generate_sample(checkout, tmp_path)
    output_dir = tmp_path / "reports"
    result = run_python(
        [str(checkout / "tests" / "tools" / "run_pipeline.py"), "--output", str(output_dir)],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr

    with (output_dir / "summary.csv").open(encoding="utf-8", newline="") as stream:
        summaries = {row["factor"]: row for row in csv.DictReader(stream)}
    violations = {
        row["column"]: row for row in json.loads(
            (output_dir / "violations.json").read_text(encoding="utf-8")
        )
    }
    report = (output_dir / "report.md").read_text(encoding="utf-8")
    # CSV 和 JSON 保留数值精度，Markdown 将置信度显示为三位小数。
    assert summaries.keys() == violations.keys()
    assert len(violations) == 6
    assert violations["factor_future_return"]["details"]["mismatch_count"] == 177
    for name, violation in violations.items():
        summary = summaries[name]
        assert summary["signal_type"] == violation["signal_type"]
        assert float(summary["confidence"]) == pytest.approx(violation["confidence"])
        assert f"| {name} | {violation['signal_type']} | {violation['confidence']:.3f} |" in report
    assert "Inspected 25 factor functions" in report
    assert "factor_momentum_ema" not in report
    assert "factor_volume_mean5" not in report


def test_experiment_cli_reports_all_cases_and_the_method_disagreement(checkout, tmp_path):
    output_dir = tmp_path / "experiments"
    result = run_python(
        [str(checkout / "tests" / "tools" / "run_lookahead_experiments.py"),
         "--output", str(output_dir)],
        tmp_path,
    )
    assert result.returncode == 0, result.stderr

    with (output_dir / "comparison.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 7
    assert all(row["replay_flagged"] == row["expected_leak"] for row in rows)
    [disagreement] = [row for row in rows if row["methods_agree"] == "False"]
    assert disagreement["factor"] == "next_row_exists"
    assert disagreement["perturbation_mismatches"] == "0"
    assert json.loads(disagreement["replay_example"])["replay_value"] == 0
    report = (output_dir / "report.md").read_text(encoding="utf-8")
    assert all(row["factor"] in report for row in rows)


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
