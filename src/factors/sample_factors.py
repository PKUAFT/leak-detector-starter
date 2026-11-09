"""Sample factor definitions used for the onboarding exercise."""
from __future__ import annotations

import pandas as pd


def factor_momentum_ema(df: pd.DataFrame) -> pd.Series:
    """Lagged exponential moving average of 1-day returns (uses only past data)."""

    returns = df.groupby("symbol", sort=False)["close"].pct_change()
    ema = returns.groupby(df["symbol"], sort=False).transform(lambda s: s.ewm(span=3, adjust=False).mean())
    return ema.groupby(df["symbol"], sort=False).shift(1)


def factor_volume_mean5(df: pd.DataFrame) -> pd.Series:
    """Five-day rolling mean of volume, shifted by one day to avoid look-ahead."""

    rolling = df.groupby("symbol", sort=False)["volume"].transform(
        lambda s: s.rolling(window=5, min_periods=3).mean()
    )
    return rolling.groupby(df["symbol"], sort=False).shift(1)


def factor_future_return(df: pd.DataFrame) -> pd.Series:
    """Intentional leak: aligns tomorrow's return onto today's row."""

    forward_close = df.groupby("symbol", sort=False)["close"].shift(-1)
    return (forward_close - df["close"]) / df["close"]
