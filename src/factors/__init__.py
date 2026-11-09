"""Factor registry for the onboarding exercise."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

import pandas as pd

from . import sample_factors

FactorFunction = Callable[[pd.DataFrame], pd.Series]


@dataclass(frozen=True)
class FactorDefinition:
    """Metadata for a factor function."""

    name: str
    function: FactorFunction
    description: str
    is_intentional_leak: bool = False


def get_registered_factors() -> Dict[str, FactorDefinition]:
    """Return the factor definitions that ship with the starter project."""

    return {
        "factor_momentum_ema": FactorDefinition(
            name="factor_momentum_ema",
            function=sample_factors.factor_momentum_ema,
            description="Lagged EMA of 1-day returns (should be safe)",
        ),
        "factor_volume_mean5": FactorDefinition(
            name="factor_volume_mean5",
            function=sample_factors.factor_volume_mean5,
            description="Lagged mean volume over a 5-day window",
        ),
        "factor_future_return": FactorDefinition(
            name="factor_future_return",
            function=sample_factors.factor_future_return,
            description="Intentional leak: aligns future return onto today's row",
            is_intentional_leak=True,
        ),
    }
