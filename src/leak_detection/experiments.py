"""Run and report the forward replay and future price perturbation experiments."""

import json
from pathlib import Path

import pandas as pd

from factors.experiment_factors import experiment_cases

from .detector import compare_future_prices, detect_leaks
from .simulator import generate_dataset


def run_lookahead_experiments(output_dir: Path) -> dict[str, Path]:
    """Evaluate the seven labeled cases on the same fixed-seed data."""
    data = generate_dataset(seed=42)
    cases = experiment_cases()
    factors = {case.factor.name: case.factor for case in cases}
    replay = detect_leaks(data, factor_definitions=factors)
    replay_details = {v.column: v.details for v in replay.violations}
    perturbations = compare_future_prices(data, factor_definitions=factors)

    records = []
    examples = []
    for case in cases:
        name = case.factor.name
        replay_mismatches = replay_details.get(name, {}).get("mismatches", [])
        perturbation = perturbations[name]
        record = {
            "factor": name,
            "reason": case.factor.description,
            "expected_leak": case.expected_leak,
            "methods_agree": bool(replay_mismatches) == bool(perturbation.mismatches),
        }
        for method, count, mismatches in (
            ("replay", len(data), replay_mismatches),
            ("perturbation", perturbation.compared_rows, perturbation.mismatches),
        ):
            record[f"{method}_flagged"] = bool(mismatches)
            record[f"{method}_compared_rows"] = count
            record[f"{method}_mismatches"] = len(mismatches)
            evidence = json.dumps(mismatches[0], ensure_ascii=False) if mismatches else ""
            record[f"{method}_example"] = evidence
            if evidence:
                examples.append(f"- `{name}` ({method}): `{evidence}`")
        records.append(record)

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "comparison.csv"
    markdown_path = output_dir / "report.md"
    pd.DataFrame.from_records(records).to_csv(csv_path, index=False)
    table = pd.DataFrame([
        {
            "因子": record["factor"],
            "依赖或历史对照": record["reason"],
            "预期泄露": "是" if record["expected_leak"] else "否",
            "前推重算": _comparison_summary(record, "replay"),
            "未来价格扰动": _comparison_summary(record, "perturbation"),
            "方法一致": "是" if record["methods_agree"] else "否",
        }
        for record in records
    ])
    markdown_path.write_text(
        "\n".join([
            "# 前视偏差实验",
            "",
            "使用固定种子 42 的模拟行情。数字为差异行数 / 比较行数。",
            "价格扰动只把检查日之后的收盘价乘以 1.5，并跳过没有未来行的最后一个日期。",
            "",
            table.to_markdown(index=False),
            "",
            "## 差异示例",
            "",
            *examples,
            "",
            "仅依赖未来行是否存在的因子不会受到价格扰动。无差异只表示本次比较没有观察到变化。",
            "",
        ]),
        encoding="utf-8",
    )
    return {"csv": csv_path, "markdown": markdown_path}


def _comparison_summary(record: dict, method: str) -> str:
    status = "标记" if record[f"{method}_flagged"] else "无差异"
    return f"{status} ({record[f'{method}_mismatches']}/{record[f'{method}_compared_rows']})"
