from decimal import Decimal

from evaluation.execution.caching_client import CacheStats
from evaluation.measurement.cache_savings import cache_savings
from tests.measurement.conftest import make_response


def test_savings_sum_the_served_responses() -> None:
    stats = CacheStats(hits=2, misses=2)
    served = [make_response(10, 5), make_response(20, 0)]

    savings = cache_savings(stats, served)

    assert savings.hit_rate == Decimal("0.500")
    assert savings.tokens_saved == 35
    assert savings.cost_avoided == Decimal("0.000040")
