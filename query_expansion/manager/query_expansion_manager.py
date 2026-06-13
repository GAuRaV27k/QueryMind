from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from query_expansion.providers import discover_providers, get_registered_providers
from query_expansion.types import (
    ProviderFailure,
    ProviderHealth,
    QueryExpansionProvider,
    QueryExpansionResult,
    RetryPolicy,
)
from query_expansion.utils import compute_backoff, is_retryable_exception, normalize_queries

logger = logging.getLogger(__name__)


def _load_default_providers() -> List[QueryExpansionProvider]:
    discover_providers()
    providers: List[QueryExpansionProvider] = []
    for provider_cls in get_registered_providers():
        try:
            providers.append(provider_cls())
        except Exception as exc:
            logger.warning("Failed to initialize provider %s: %s", provider_cls, exc)
    return providers


def _apply_priority_order(
    providers: Iterable[QueryExpansionProvider],
) -> List[QueryExpansionProvider]:
    providers_list = list(providers)
    order_env = os.getenv("QUERY_EXPANSION_PROVIDER_ORDER", "").strip()
    if not order_env:
        return sorted(providers_list, key=lambda item: item.priority)

    order = [name.strip().lower() for name in order_env.split(",") if name.strip()]
    provider_map = {provider.name.lower(): provider for provider in providers_list}
    ordered: List[QueryExpansionProvider] = []
    for name in order:
        provider = provider_map.pop(name, None)
        if provider:
            ordered.append(provider)
    remaining = sorted(provider_map.values(), key=lambda item: item.priority)
    return ordered + remaining


@dataclass
class QueryExpansionManager:
    providers: List[QueryExpansionProvider] = field(default_factory=_load_default_providers)
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_s: float | None = None
    health: Dict[str, ProviderHealth] = field(init=False)
    last_result: QueryExpansionResult | None = None

    def __post_init__(self) -> None:
        if self.timeout_s is None:
            env_timeout = os.getenv("QUERY_EXPANSION_TIMEOUT_S", "").strip()
            if env_timeout:
                self.timeout_s = float(env_timeout)
        available = [provider for provider in self.providers if provider.is_available()]
        self.providers = _apply_priority_order(available)
        self.health = {
            provider.name: ProviderHealth(provider=provider.name) for provider in self.providers
        }
        self._health_lock = threading.Lock()

    async def expand(self, query: str) -> List[str]:
        result = await self.expand_with_metadata(query)
        return result.queries

    async def expand_with_metadata(self, query: str) -> QueryExpansionResult:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        attempts: List[str] = []
        failures: List[ProviderFailure] = []
        for provider in self.providers:
            attempts.append(provider.name)
            try:
                expanded, latency_ms = await self._call_provider(provider, query)
            except Exception as exc:
                reason = str(exc)
                retryable = is_retryable_exception(exc)
                failures.append(
                    ProviderFailure(provider=provider.name, reason=reason, retryable=retryable)
                )
                self._record_failure(provider.name, reason)
                logger.warning(
                    "Query expansion provider %s failed: %s", provider.name, reason, exc_info=exc
                )
                continue

            normalized = normalize_queries(query, expanded)
            self._record_success(provider.name, latency_ms)
            result = QueryExpansionResult(
                queries=normalized,
                provider=provider.name,
                attempts=attempts,
                failures=failures,
                latency_ms=latency_ms,
                fallback_used=False,
            )
            self.last_result = result
            return result

        fallback = QueryExpansionResult(
            queries=[query.strip()],
            provider=None,
            attempts=attempts,
            failures=failures,
            latency_ms=None,
            fallback_used=True,
        )
        self.last_result = fallback
        return fallback

    async def _call_provider(
        self, provider: QueryExpansionProvider, query: str
    ) -> tuple[List[str], float]:
        last_exc: Exception | None = None
        start_time = time.perf_counter()
        for attempt in range(self.retry_policy.max_retries + 1):
            try:
                expanded = await self._call_provider_once(provider, query)
                latency_ms = (time.perf_counter() - start_time) * 1000
                return expanded, latency_ms
            except Exception as exc:
                last_exc = exc
                retryable = is_retryable_exception(exc)
                if not retryable or attempt >= self.retry_policy.max_retries:
                    break
                delay = compute_backoff(
                    attempt,
                    self.retry_policy.base_delay_s,
                    self.retry_policy.max_delay_s,
                    self.retry_policy.backoff_multiplier,
                    self.retry_policy.jitter_s,
                )
                logger.warning(
                    "Query expansion provider %s attempt %d/%d failed; retrying in %.2fs: %s",
                    provider.name,
                    attempt + 1,
                    self.retry_policy.max_retries + 1,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)
        if last_exc:
            raise last_exc
        raise RuntimeError(f"Query expansion provider {provider.name} failed with no error")

    async def _call_provider_once(
        self, provider: QueryExpansionProvider, query: str
    ) -> List[str]:
        if self.timeout_s is None:
            return await provider.expand(query)
        return await asyncio.wait_for(provider.expand(query), timeout=self.timeout_s)

    def _record_success(self, provider_name: str, latency_ms: float) -> None:
        with self._health_lock:
            self.health.setdefault(provider_name, ProviderHealth(provider=provider_name)).record_success(
                latency_ms
            )

    def _record_failure(self, provider_name: str, reason: str) -> None:
        with self._health_lock:
            self.health.setdefault(provider_name, ProviderHealth(provider=provider_name)).record_failure(
                reason
            )
