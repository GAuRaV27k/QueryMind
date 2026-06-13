from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class RetryPolicy:
    max_retries: int = 2
    base_delay_s: float = 0.5
    max_delay_s: float = 4.0
    backoff_multiplier: float = 2.0
    jitter_s: float = 0.1


@dataclass(slots=True)
class ProviderFailure:
    provider: str
    reason: str
    retryable: bool


@dataclass(slots=True)
class ProviderHealth:
    provider: str
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    last_failure_reason: str | None = None

    def record_success(self, latency_ms: float) -> None:
        self.success_count += 1
        if self.success_count == 1:
            self.avg_latency_ms = latency_ms
            return
        self.avg_latency_ms = (
            (self.avg_latency_ms * (self.success_count - 1)) + latency_ms
        ) / self.success_count

    def record_failure(self, reason: str) -> None:
        self.failure_count += 1
        self.last_failure_reason = reason


@dataclass(slots=True)
class QueryExpansionResult:
    queries: List[str]
    provider: str | None
    attempts: List[str]
    failures: List[ProviderFailure]
    latency_ms: float | None
    fallback_used: bool


class QueryExpansionProvider(ABC):
    name: str = "unknown"
    priority: int = 100

    def is_available(self) -> bool:
        return True

    @abstractmethod
    async def expand(self, query: str) -> List[str]:
        raise NotImplementedError
