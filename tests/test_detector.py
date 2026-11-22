import pandas as pd
import pytest

from factors import FactorDefinition, get_registered_factors
from leak_detection.detector import detect_leaks
from leak_detection.simulator import generate_dataset


def test_registered_lagged_return_uses_the_previous_value_for_each_symbol():
    df = pd.DataFrame({
        "symbol": ["A", "B", "A", "B", "A"],
        "date": [1, 1, 2, 2, 3],
        "ret_1d": [0.01, -0.02, None, 0.04, 0.05],
    }, index=[7, 12, 3, 24, 19])

    factor = get_registered_factors()["factor_lagged_return"].function
    expected = pd.Series([None, None, 0.01, -0.02, None], index=df.index, name="ret_1d")

    pd.testing.assert_series_equal(factor(df), expected)


def test_detects_all_six_controls_without_flagging_historical_factors():
    factors = get_registered_factors()
    df = generate_dataset()
    result = detect_leaks(df, factor_definitions=factors)

    assert result.inspected_columns == list(factors)
    violations = {item.column: item for item in result.violations}
    assert {name: item.details["mismatch_count"] for name, item in violations.items()} == {
        "factor_future_return": 177,
        "factor_leaky_next_upper_shadow_ratio": 177,
        "factor_leaky_forward_momentum5": 165,
        "factor_leaky_centered_close_ma_ratio5": 168,
        "factor_leaky_forward_range_position5": 165,
        "factor_leaky_full_sample_volume_ma_ratio": 177,
    }
    violation = violations["factor_future_return"]
    # 三只股票各有一天没有下一日数据，此时全量计算和重算都缺失。
    assert violation.confidence == pytest.approx(177 / 180)
    assert violation.details["mismatch_count"] == 177
    assert violation.details["mismatches"][0] == {
        "date": "2021-01-04",
        "symbol": "AAA",
        "full_value": pytest.approx(df.at[1, "close"] / df.at[0, "close"] - 1),
        "replay_value": None,
    }


def test_replay_preserves_cross_section_and_aligns_shuffled_rows():
    # 刻意打乱输入并重复原始行索引，检验日期截面和行对齐。
    df = pd.DataFrame({
        "date": [2, 1, 2, 1],
        "symbol": ["B", "A", "A", "B"],
        "close": [40., 10., 30., 20.],
    }, index=[70, 10, 70, 30])
    original = df.copy()

    def same_day_rank(data):
        # 同日排名需要当天所有股票。倒序返回可以检验是否按索引对齐。
        return data.groupby("date")["close"].rank().sort_index(ascending=False)

    def next_close(data):
        return data.groupby("symbol")["close"].shift(-1)

    factors = {
        "rank": FactorDefinition("rank", same_day_rank, "Same-day rank"),
        "custom": FactorDefinition("custom", next_close, "Next close"),
    }
    [violation] = detect_leaks(df, factor_definitions=factors).violations

    assert violation.column == "custom"
    assert violation.details["mismatches"] == [
        {"date": "1", "symbol": "A", "full_value": 30., "replay_value": None},
        {"date": "1", "symbol": "B", "full_value": 40., "replay_value": None},
    ]
    pd.testing.assert_frame_equal(df, original)


@pytest.mark.parametrize(("tolerance", "flagged"), [(0.125, False), (0.0625, True)])
def test_replay_uses_absolute_tolerance(tolerance, flagged):
    df = pd.DataFrame({"date": [1, 2], "symbol": ["A", "A"], "close": [1000., 1000.]})

    def factor(data):
        # 第一天完整计算有两行，截断重算只有一行，差值恰好为 0.125。
        return data["close"] + len(data) * 0.125

    result = detect_leaks(
        df,
        factor_definitions={"custom": FactorDefinition("custom", factor, "Length-dependent")},
        tolerance=tolerance,
    )

    assert bool(result.violations) is flagged


def test_duplicate_entity_time_keys_fail_clearly():
    df = pd.DataFrame({"date": [1, 1], "symbol": ["A", "A"]})
    with pytest.raises(ValueError, match="unique"):
        detect_leaks(df, factor_definitions=get_registered_factors())
