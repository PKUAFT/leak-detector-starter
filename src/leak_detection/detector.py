"""Starter file that students will complete with their leak detection logic."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping

import pandas as pd

from factors import FactorDefinition


@dataclass
class LeakViolation:
    """A single suspected leak signal."""

    column: str
    signal_type: str
    confidence: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeakDetectionResult:
    """Container for detector output used throughout the project."""

    inspected_columns: List[str]
    violations: List[LeakViolation] = field(default_factory=list)
    notes: str | None = None


def detect_leaks(
    df: pd.DataFrame,
    *,
    factor_definitions: Mapping[str, FactorDefinition],
    entity_col: str = "symbol",
    time_col: str = "date",
    tolerance: float = 1e-9,
) -> LeakDetectionResult:
    """Detect suspicious factor *code* that may leak future information.

    要求：遍历 ``factor_definitions`` 内的函数，构造足够的检验来识别未来信息泄露。
    建议思路：

    1. **时间前推重算 (forward-only replay)**：逐日滚动截取 ``df`` 的前缀，让因子函数在仅含 ``<= as_of`` 数据的情形下复现最后一行的取值，若结果与完整数据跑出来的不一致，说明函数依赖未来信息。
    2. **鲁棒性对比**：可对比训练/验证时间段、或不同切片下的统计量，找到与未来标签过于一致的因子。
    3. **自定义规则**：例如静态代码扫描、参数签名检查、或针对函数中 ``shift(-1)`` ``lead`` 等操作的简单 AST 分析。

    返回 ``LeakDetectionResult``，其中 ``violations`` 记录每个疑似泄露的因子函数。
    """

    raise NotImplementedError("请在练习中实现针对因子代码的泄露检测逻辑。")
