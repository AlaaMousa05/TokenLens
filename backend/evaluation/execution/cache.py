"""Pluggable storage for cached responses: one interface, an in-memory and a local-file backend.

A Redis-backed backend can be added here without touching callers.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from evaluation.contracts import ModelResponse


class CacheBackend(ABC):
    """Stores serialized ModelResponses by key."""

    @abstractmethod
    async def get(self, key: str) -> ModelResponse | None: ...

    @abstractmethod
    async def set(self, key: str, response: ModelResponse) -> None: ...


class InMemoryCache(CacheBackend):
    """Process-local cache; serializes on store so it behaves like a durable backend."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> ModelResponse | None:
        raw = self._store.get(key)
        return ModelResponse.model_validate_json(raw) if raw is not None else None

    async def set(self, key: str, response: ModelResponse) -> None:
        self._store[key] = response.model_dump_json()


class FileCache(CacheBackend):
    """Cache persisted as one JSON file per key under a directory."""

    def __init__(self, directory: Path) -> None:
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._directory / f"{key}.json"

    async def get(self, key: str) -> ModelResponse | None:
        path = self._path(key)
        if not path.exists():
            return None
        return ModelResponse.model_validate_json(path.read_text(encoding="utf-8"))

    async def set(self, key: str, response: ModelResponse) -> None:
        self._path(key).write_text(response.model_dump_json(), encoding="utf-8")
