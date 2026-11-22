from statistics import mean, pstdev

import pandas as pd
import pytest

from factors import FactorDefinition
from factors.experiment_factors import (
    composite_momentum,
    experiment_cases,
    market_relative_return,
    volatility_adjusted_momentum,
)
from leak_detection.detector import compare_future_prices, detect_leaks


@pytest.fixture
def panel():
    prices = {
        "A": [10, 11, 10, 13, 12, 15, 18, 16, 21, 22, 26, 25, 31, 29],
        "B": [30, 28, 31, 32, 31, 33, 35, 38, 36, 39, 41, 40, 44, 42],
    }
    return pd.DataFrame(
        [(symbol, day, close) for symbol, values in prices.items()
         for day, close in enumerate(values)],
        columns=["symbol", "date", "close"],
    )


def test_market_relative_return_uses_three_observation_endpoints(panel):
    future = market_relative_return(panel, forward=True)
    historical = market_relative_return(panel, forward=False)

    # 去掉两只股票的平均值后，A 的结果等于两只股票收益差的一半。
    assert future.loc[3] == pytest.approx((18 / 13 - 35 / 32) / 2)
    assert historical.loc[3] == pytest.approx((13 / 10 - 32 / 30) / 2)
    assert pd.isna(historical.loc[0])
    assert pd.isna(future.loc[13])


def test_momentum_volatility_uses_the_expected_five_return_window(panel):
    # A 的第 7 日以第 2 日为动量起点。
    momentum = 16 / 10 - 1
    trailing = [13 / 10 - 1, 12 / 13 - 1, 15 / 12 - 1, 18 / 15 - 1, 16 / 18 - 1]
    centered = [15 / 12 - 1, 18 / 15 - 1, 16 / 18 - 1, 21 / 16 - 1, 22 / 21 - 1]

    assert volatility_adjusted_momentum(panel, centered=False).loc[7] == pytest.approx(
        momentum / pstdev(trailing)
    )
    assert volatility_adjusted_momentum(panel, centered=True).loc[7] == pytest.approx(
        momentum / pstdev(centered)
    )


def test_composite_fits_historical_z_score_before_current_day(panel):
    past = [15 / 10 - 1, 18 / 11 - 1, 16 / 10 - 1, 21 / 13 - 1, 22 / 12 - 1]
    current = 26 / 15 - 1
    full = past + [current, 25 / 18 - 1, 31 / 16 - 1, 29 / 21 - 1]
    # A 的当日动量大于 B (41/33 - 1)，百分位为 1。
    for full_sample, values in [(False, past), (True, full)]:
        expected = (1 + (current - mean(values)) / pstdev(values)) / 2
        assert composite_momentum(panel, full_sample=full_sample).loc[10] == pytest.approx(
            expected
        )
    assert pd.isna(composite_momentum(panel, full_sample=False).loc[9])


def test_insufficient_cross_section_and_zero_dispersion_are_missing(panel):
    only_a = panel[panel["symbol"] == "A"]
    assert market_relative_return(only_a, forward=False).isna().all()
    assert composite_momentum(only_a, full_sample=False).isna().all()
    constant = panel.assign(close=10)
    for centered in (False, True):
        assert volatility_adjusted_momentum(constant, centered=centered).isna().all()
    for full_sample in (False, True):
        assert composite_momentum(constant, full_sample=full_sample).isna().all()


def test_forward_replay_flags_leaky_cases_only(panel):
    cases = experiment_cases()
    result = detect_leaks(panel, factor_definitions={c.factor.name: c.factor for c in cases})

    assert len(result.inspected_columns) == 7
    assert {v.column for v in result.violations} == {
        "forward_market_relative_return",
        "centered_volatility_momentum",
        "full_sample_composite_momentum",
        "next_row_exists",
    }


def test_perturbation_preserves_input_and_changes_only_future_close(panel):
    df = panel[panel["date"] <= 2].assign(volume=100, close=lambda d: d["close"].astype(float))
    original = df.copy()
    inputs = []

    def inspect(data):
        inputs.append(data.copy())
        # 倒序返回，比较时仍应按原索引对齐。
        return data["close"].iloc[::-1]

    result = compare_future_prices(
        df, factor_definitions={"inspect": FactorDefinition("inspect", inspect, "Current close")}
    )["inspect"]

    assert result.compared_rows == 4
    assert not result.mismatches
    assert len(inputs) == 3  # 全量基准、前两个检查日。最后一天没有未来行。
    for cutoff, data in enumerate(inputs[1:]):
        expected = original.copy()
        expected.loc[expected["date"] > cutoff, "close"] *= 1.5
        pd.testing.assert_frame_equal(data, expected)
    pd.testing.assert_frame_equal(df, original)


def test_perturbation_distinguishes_price_dependence_from_row_existence(panel):
    cases = experiment_cases()
    results = compare_future_prices(
        panel, factor_definitions={c.factor.name: c.factor for c in cases}
    )

    assert {name for name, result in results.items() if result.mismatches} == {
        "forward_market_relative_return",
        "centered_volatility_momentum",
        "full_sample_composite_momentum",
    }
    assert results["next_row_exists"].compared_rows == 26
    assert results["forward_market_relative_return"].mismatches[0] == {
        "date": "0",
        "symbol": "A",
        "full_value": pytest.approx((13 / 10 - 32 / 30) / 2),
        "perturbed_value": pytest.approx((13 / 10 - 32 / 30) * 1.5 / 2),
    }
