"""The regression alert threshold, derived from the judge's own run-to-run noise.

A threshold below the judge's noise fires false alerts; one far above it misses
real regressions. So it is a multiple of the measured noise, never a guess.
"""

from dataclasses import dataclass
from decimal import Decimal

_DEFAULT_MULTIPLE = Decimal("2")
_PLACES = Decimal("0.001")

# A measured noise of (near) zero — e.g. a variance probe that happened to hit
# the score ceiling every time — would otherwise produce a threshold of zero
# that alerts on any fluctuation at all. This floor is the smallest drop ever
# treated as a regression, regardless of what the noise measurement says.
_MINIMUM_THRESHOLD = Decimal("0.250")


@dataclass(frozen=True)
class Threshold:
    """The minimum drop that counts as a regression, and how it was derived."""

    value: Decimal
    derivation: str


def derive_threshold(judge_noise_stddev: Decimal, multiple: Decimal = _DEFAULT_MULTIPLE) -> Threshold:
    """Threshold = multiple × the judge's weighted-total standard deviation, floored so it can never be zero."""
    raw = (multiple * judge_noise_stddev).quantize(_PLACES)
    value = max(raw, _MINIMUM_THRESHOLD)
    derivation = f"{multiple} x judge run-to-run stddev ({judge_noise_stddev}) = {raw}"
    if value > raw:
        derivation += f", floored to the minimum {_MINIMUM_THRESHOLD} (a near-zero noise measurement cannot zero out the threshold)"
    derivation += "; a drop smaller than this is within the judge's own noise and is not alerted."
    return Threshold(value=value, derivation=derivation)
