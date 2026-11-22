"""Paired look-ahead examples for the standalone experiment."""

from dataclasses import dataclass
from functools import partial

import pandas as pd

from . import FactorDefinition, FactorFunction


def market_relative_return(df: pd.DataFrame, *, forward: bool) -> pd.Series:
    close = df["close"]
    by_symbol = close.groupby(df["symbol"], sort=False)
    if forward:
        returns = by_symbol.shift(-3) / close - 1
    else:
        returns = close / by_symbol.shift(3) - 1
    cross_section = returns.groupby(df["date"], sort=False)
    return (returns - cross_section.transform("mean")).where(
        cross_section.transform("count") >= 2
    )


def _five_day_momentum(df: pd.DataFrame) -> pd.Series:
    return df["close"] / df.groupby("symbol", sort=False)["close"].shift(5) - 1


def volatility_adjusted_momentum(df: pd.DataFrame, *, centered: bool) -> pd.Series:
    by_symbol = df.groupby("symbol", sort=False)["close"]
    daily_return = df["close"] / by_symbol.shift(1) - 1
    volatility = daily_return.groupby(df["symbol"], sort=False).transform(
        lambda s: s.rolling(5, min_periods=5, center=centered).std(ddof=0)
    )
    return _five_day_momentum(df) / volatility.where(volatility > 0)


def composite_momentum(df: pd.DataFrame, *, full_sample: bool) -> pd.Series:
    momentum = _five_day_momentum(df)
    cross_section = momentum.groupby(df["date"], sort=False)
    rank = cross_section.rank(method="average", pct=True).where(
        cross_section.transform("count") >= 2
    )
    by_symbol = momentum.groupby(df["symbol"], sort=False)
    if full_sample:
        mean = by_symbol.transform("mean").where(by_symbol.transform("count") >= 5)
        std = by_symbol.transform("std", ddof=0)
    else:
        # 先滞后一行再拟合，确保当天的动量也不会进入标准化参数。
        past = by_symbol.shift(1).groupby(df["symbol"], sort=False)
        mean = past.transform(lambda s: s.expanding(min_periods=5).mean())
        std = past.transform(lambda s: s.expanding(min_periods=5).std(ddof=0))
    z_score = (momentum - mean) / std.where(std > 0)
    return (rank + z_score) / 2


def next_row_exists(df: pd.DataFrame) -> pd.Series:
    # 倒序的组内计数只依赖后续行是否存在，不读取价格。
    return df.groupby("symbol", sort=False).cumcount(ascending=False).gt(0)


@dataclass(frozen=True)
class ExperimentCase:
    factor: FactorDefinition
    expected_leak: bool


def experiment_cases() -> tuple[ExperimentCase, ...]:
    def case(name: str, fn: FactorFunction, reason: str, leaks: bool) -> ExperimentCase:
        return ExperimentCase(FactorDefinition(name, fn, reason), leaks)

    return (
        case("forward_market_relative_return", partial(market_relative_return, forward=True),
             "收益窗口使用未来三日收盘价", True),
        case("trailing_market_relative_return", partial(market_relative_return, forward=False),
             "收益窗口截至当天，横截面使用当天可得值", False),
        case("centered_volatility_momentum", partial(volatility_adjusted_momentum, centered=True),
             "波动率分母使用未来两日日收益", True),
        case("trailing_volatility_momentum", partial(volatility_adjusted_momentum, centered=False),
             "波动率和动量只使用截至当天的数据", False),
        case("full_sample_composite_momentum", partial(composite_momentum, full_sample=True),
             "时序 Z 分数用全样本拟合均值和标准差", True),
        case("historical_composite_momentum", partial(composite_momentum, full_sample=False),
             "Z 分数仅用此前历史拟合，排名只用当天截面", False),
        case("next_row_exists", next_row_exists, "依赖同一股票后续行是否存在", True),
    )
