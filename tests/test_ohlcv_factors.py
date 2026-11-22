import numpy as np
import pandas as pd
import pytest

from factors import get_registered_factors


def test_ohlcv_factors_match_formulas_for_interleaved_symbols():
    close = np.array([100 + day + 3 * (day % 2) for day in range(22)], dtype=float)
    volume = np.array([1000 + day**2 for day in range(22)], dtype=float)
    df = pd.DataFrame({
        "symbol": ["A", "B"] * len(close),
        "close": np.column_stack((close, close * 10)).ravel(),
        "volume": np.column_stack((volume, volume * 2)).ravel(),
    }, index=np.arange(100, 100 + 2 * len(close)))
    df = df.assign(open=df["close"] - 1, high=df["close"] + 2, low=df["close"] - 3)
    first, last = df.index[0], df.index[-2]
    expected = {
        "factor_candle_body_ratio": 1 / 5,
        "factor_upper_shadow_ratio": 2 / 5,
        "factor_lower_shadow_ratio": 2 / 5,
        "factor_candle_close_position": 1 / 5,
    }
    for window in (5, 20):
        recent = close[-window:]
        expected.update({
            f"factor_close_momentum{window}": close[-1] / close[-window - 1] - 1,
            f"factor_close_ma_ratio{window}": recent.mean() / close[-1],
            f"factor_close_std_ratio{window}": recent.std(ddof=1) / close[-1],
            f"factor_range_position{window}": (
                (close[-1] - recent.min() + 3) / (recent.max() - recent.min() + 5)
            ),
            f"factor_volume_ma_ratio{window}": volume[-window:].mean() / volume[-1],
        })
    expected["factor_price_volume_corr20"] = np.corrcoef(close[-20:], np.log1p(volume[-20:]))[0, 1]
    expected["factor_up_day_share20"] = np.mean(np.diff(close[-21:]) > 0)

    registry = get_registered_factors()
    assert len(registry) == 25
    for name, value in expected.items():
        series = registry[name].function(df)
        pd.testing.assert_index_equal(series.index, df.index)
        assert series.loc[last] == pytest.approx(value, abs=1e-9), name
        if "candle" not in name and "shadow" not in name:
            assert pd.isna(series.loc[first]), name


def test_undefined_ranges_and_constant_volume_are_missing():
    df = pd.DataFrame({
        "symbol": ["A"] * 21,
        **dict.fromkeys(("open", "close", "high", "low"), 10.0),
        "volume": 0.0,
    })
    factors = get_registered_factors()
    for name in (
        "factor_candle_body_ratio", "factor_range_position20",
        "factor_volume_ma_ratio20", "factor_price_volume_corr20",
    ):
        assert factors[name].function(df).isna().all(), name


def test_leaky_variants_match_their_future_windows():
    close = np.arange(10.0, 18.0)
    volume = np.arange(100.0, 180.0, 10.0)
    df = pd.DataFrame({
        "symbol": ["A"] * len(close),
        "close": close,
        "open": close - 1,
        "high": close + np.arange(1, 9),
        "low": close - 2,
        "volume": volume,
    })
    expected_at_day_two = {
        "factor_leaky_next_upper_shadow_ratio": 4 / 6,
        "factor_leaky_forward_momentum5": 17 / 12 - 1,
        "factor_leaky_centered_close_ma_ratio5": close[:5].mean() / 12,
        "factor_leaky_forward_range_position5": (12 - 11) / (25 - 11),
        "factor_leaky_full_sample_volume_ma_ratio": volume.mean() / 120,
    }
    factors = get_registered_factors()
    for name, expected in expected_at_day_two.items():
        definition = factors[name]
        assert definition.is_intentional_leak
        assert definition.function(df).loc[2] == pytest.approx(expected), name
