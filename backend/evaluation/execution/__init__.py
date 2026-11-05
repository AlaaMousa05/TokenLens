"""Execution layer: everything between a ModelSpec and prompt and a reliable ModelResponse."""

from evaluation.execution.cache import CacheBackend, FileCache, InMemoryCache
from evaluation.execution.caching_client import CacheStats, cache_key
from evaluation.execution.composition import ExecutionClient, build_execution_client
from evaluation.execution.concurrency import DEFAULT_PROVIDER_CONCURRENCY, ProviderConcurrency
from evaluation.execution.fanout import FanOutResult, fan_out
from evaluation.execution.retry import RetryPolicy

__all__ = [
    "CacheBackend",
    "InMemoryCache",
    "FileCache",
    "CacheStats",
    "cache_key",
    "ProviderConcurrency",
    "DEFAULT_PROVIDER_CONCURRENCY",
    "RetryPolicy",
    "ExecutionClient",
    "build_execution_client",
    "FanOutResult",
    "fan_out",
]
