from pathlib import Path

import pandas as pd
import pytest

from factors import get_registered_factors
from leak_detection.data import DEFAULT_DATA_PATH, describe_dataset, load_sample_factors
from leak_detection.simulator import write_dataset


@pytest.fixture
def sample_file(tmp_path):
    return write_dataset(tmp_path / "sample_factors.csv")


def test_default_sample_is_generated_under_ignored_outputs():
    assert DEFAULT_DATA_PATH == Path(__file__).resolve().parents[1] / "outputs" / "sample_factors.csv"


def test_sample_dataset_columns_and_order(sample_file):
    df = load_sample_factors(sample_file)
    expected = ["date", "symbol", "open", "high", "low", "close", "volume", "ret_1d"]
    assert list(df.columns) == expected
    sorted_df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    pd.testing.assert_frame_equal(df, sorted_df)


def test_descriptor_summary(sample_file):
    df = load_sample_factors(sample_file)
    descriptor = describe_dataset(df)
    assert descriptor.rows == 180
    assert descriptor.symbols == ["AAA", "BBB", "CCC"]
    assert descriptor.start_date <= descriptor.end_date


def test_registered_factors_align_with_dataset(sample_file):
    df = load_sample_factors(sample_file)
    factors = get_registered_factors()
    for name, definition in factors.items():
        series = definition.function(df.copy())
        assert len(series) == len(df), f"{name} output length mismatch"
        pd.testing.assert_index_equal(series.index, df.index)
