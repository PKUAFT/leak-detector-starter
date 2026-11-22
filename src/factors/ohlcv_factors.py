"""Daily OHLCV factors inspired by Qlib's Alpha158, evaluated after the close."""

from collections.abc import Callable, Iterator
from functools import partial

import numpy as np
import pandas as pd


def _ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.where(denominator.ne(0))


def _candle_ratio(df: pd.DataFrame, *, measure: str) -> pd.Series:
    opening, close, high, low = (df[column] for column in ("open", "close", "high", "low"))
    if measure == "body":
        numerator = close - opening
    elif measure == "upper":
        numerator = high - df[["open", "close"]].max(axis=1, skipna=False)
    elif measure == "lower":
        numerator = df[["open", "close"]].min(axis=1, skipna=False) - low
    else:
        numerator = 2 * close - high - low
    return _ratio(numerator, high - low)


def _rolling(
    values: pd.Series, symbols: pd.Series, window: int, operation: str, *, centered: bool = False
) -> pd.Series:
    # 默认以当天为窗口右端。居中窗口仅用于故意泄露的对照。
    return values.groupby(symbols, sort=False).transform(
        lambda series: series.rolling(window, min_periods=window, center=centered).agg(operation)
    )


def _momentum(df: pd.DataFrame, *, window: int, forward: bool = False) -> pd.Series:
    close = df["close"]
    by_symbol = close.groupby(df["symbol"], sort=False)
    if forward:
        return _ratio(by_symbol.shift(-window), close) - 1
    return _ratio(close, by_symbol.shift(window)) - 1


def _rolling_ratio(
    df: pd.DataFrame, *, column: str, window: int, operation: str, centered: bool = False
) -> pd.Series:
    values = df[column]
    return _ratio(_rolling(values, df["symbol"], window, operation, centered=centered), values)


def _range_position(df: pd.DataFrame, *, window: int, forward: bool = False) -> pd.Series:
    symbols = df["symbol"]
    low = _rolling(df["low"], symbols, window, "min")
    high = _rolling(df["high"], symbols, window, "max")
    if forward:
        # 将窗口末端从 t 移到 t+window，使窗口恰好覆盖 t+1 至 t+window。
        low = low.groupby(symbols, sort=False).shift(-window)
        high = high.groupby(symbols, sort=False).shift(-window)
    return _ratio(df["close"] - low, high - low)


def _price_volume_corr20(df: pd.DataFrame) -> pd.Series:
    result = np.full(len(df), np.nan)
    for positions in df.groupby("symbol", sort=False).indices.values():
        close = df["close"].iloc[positions].reset_index(drop=True)
        volume = df["volume"].iloc[positions].reset_index(drop=True)
        log_volume = np.log1p(volume.where(volume.ge(0)))
        correlation = close.rolling(20).corr(log_volume)
        # 同时检查窗口内的变化，恒定序列的相关性无定义。
        has_variation = close.rolling(20).max().gt(close.rolling(20).min())
        has_variation &= log_volume.rolling(20).max().gt(log_volume.rolling(20).min())
        result[positions] = correlation.where(has_variation & np.isfinite(correlation)).clip(-1, 1)
    return pd.Series(result, index=df.index)


def _up_day_share20(df: pd.DataFrame) -> pd.Series:
    change = df.groupby("symbol", sort=False)["close"].diff()
    is_up = change.gt(0).astype(float).where(change.notna())
    return _rolling(is_up, df["symbol"], 20, "mean")


def ohlcv_factor_functions() -> Iterator[tuple[str, Callable[[pd.DataFrame], pd.Series], str]]:
    """Yield factor names, functions and descriptions for the default registry."""
    yield "factor_candle_body_ratio", partial(_candle_ratio, measure="body"), "Signed candle body / daily range"
    yield "factor_upper_shadow_ratio", partial(_candle_ratio, measure="upper"), "Upper shadow / daily range"
    yield "factor_lower_shadow_ratio", partial(_candle_ratio, measure="lower"), "Lower shadow / daily range"
    yield "factor_candle_close_position", partial(_candle_ratio, measure="position"), "Signed close position in daily range"

    for window in (5, 20):
        yield f"factor_close_momentum{window}", partial(
            _momentum, window=window
        ), f"Close return over {window} observations"
        yield f"factor_close_ma_ratio{window}", partial(
            _rolling_ratio, column="close", window=window, operation="mean"
        ), f"{window}-observation mean close / current close"
        yield f"factor_close_std_ratio{window}", partial(
            _rolling_ratio, column="close", window=window, operation="std"
        ), f"{window}-observation sample standard deviation of close / current close"
        yield f"factor_range_position{window}", partial(
            _range_position, window=window
        ), f"Close position in the {window}-observation high–low range"
        yield f"factor_volume_ma_ratio{window}", partial(
            _rolling_ratio, column="volume", window=window, operation="mean"
        ), f"{window}-observation mean volume / current volume"

    yield "factor_price_volume_corr20", _price_volume_corr20, "20-observation correlation of close and log(1 + volume)"
    yield "factor_up_day_share20", _up_day_share20, "Share of rising closes over 20 observed price changes"


def _next_upper_shadow(df: pd.DataFrame) -> pd.Series:
    shadow = _candle_ratio(df, measure="upper")
    return shadow.groupby(df["symbol"], sort=False).shift(-1)


def _full_sample_volume_ratio(df: pd.DataFrame) -> pd.Series:
    mean_volume = df.groupby("symbol", sort=False)["volume"].transform("mean")
    return _ratio(mean_volume, df["volume"])


def leaky_ohlcv_factor_functions() -> Iterator[tuple[str, Callable[[pd.DataFrame], pd.Series], str]]:
    """Yield intentional leakage controls paired with historical OHLCV factors."""
    yield "factor_leaky_next_upper_shadow_ratio", _next_upper_shadow, (
        "Uses the next observation's upper shadow ratio"
    )
    yield "factor_leaky_forward_momentum5", partial(_momentum, window=5, forward=True), (
        "Uses close five observations ahead"
    )
    yield "factor_leaky_centered_close_ma_ratio5", partial(
        _rolling_ratio, column="close", window=5, operation="mean", centered=True
    ), "Includes two future closes in the moving average"
    yield "factor_leaky_forward_range_position5", partial(_range_position, window=5, forward=True), (
        "Uses highs and lows of the next five observations"
    )
    yield "factor_leaky_full_sample_volume_ma_ratio", _full_sample_volume_ratio, (
        "Uses the symbol's full-sample mean volume"
    )
