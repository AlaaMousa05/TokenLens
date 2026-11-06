"""Decimal mean and standard deviation, kept together so no mean is ever reported alone."""

from dataclasses import dataclass
from decimal import Decimal

_PLACES = Decimal("0.001")


@dataclass(frozen=True)
class Stat:
    """A mean and its sample standard deviation over a known number of values."""

    mean: Decimal
    stddev: Decimal
    count: int

    def __str__(self) -> str:
        return f"{self.mean}±{self.stddev} (n={self.count})"


def summarize(values: list[Decimal]) -> Stat:
    """Mean and sample (n-1) standard deviation; stddev is 0 for a single value."""
    if not values:
        raise ValueError("summarize requires at least one value.")
    count = len(values)
    mean = sum(values, Decimal("0")) / count
    if count == 1:
        stddev = Decimal("0")
    else:
        variance = sum(((value - mean) ** 2 for value in values), Decimal("0")) / (count - 1)
        stddev = variance.sqrt()
    return Stat(mean=mean.quantize(_PLACES), stddev=stddev.quantize(_PLACES), count=count)
