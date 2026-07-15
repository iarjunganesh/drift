"""Bounded async resilience primitives for external model calls."""

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TypeVar

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)

T = TypeVar("T")


class ModelCapacityExceededError(RuntimeError):
    """Raised when all model-call slots remain busy beyond the queue timeout."""


class ProviderCircuitOpenError(RuntimeError):
    """Raised while the provider circuit is open after transient failures."""


@dataclass(frozen=True)
class ResilientResult[T]:
    """A successful response plus the number of provider attempts it consumed."""

    value: T
    attempts: int


def is_transient_provider_error(error: Exception) -> bool:
    """Return whether an error is safe to retry without changing request semantics."""
    if isinstance(error, (APITimeoutError, APIConnectionError, RateLimitError, InternalServerError)):
        return True
    return isinstance(error, APIStatusError) and error.status_code >= 500


@dataclass
class CircuitBreaker:
    """A single-process closed/open/half-open circuit breaker."""

    failure_threshold: int
    reset_seconds: float
    clock: Callable[[], float] = time.monotonic
    _consecutive_failures: int = field(default=0, init=False)
    _opened_at: float | None = field(default=None, init=False)
    _probe_in_flight: bool = field(default=False, init=False)

    def before_call(self) -> None:
        if self._opened_at is None:
            return
        retry_after = self.reset_seconds - (self.clock() - self._opened_at)
        if retry_after > 0:
            raise ProviderCircuitOpenError(
                f"Model provider circuit is open; retry in {max(1, round(retry_after))} seconds."
            )
        if self._probe_in_flight:
            raise ProviderCircuitOpenError("Model provider recovery probe is already in progress.")
        self._probe_in_flight = True

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._opened_at = None
        self._probe_in_flight = False

    def record_transient_failure(self) -> None:
        self._consecutive_failures += 1
        self._probe_in_flight = False
        if self._consecutive_failures >= self.failure_threshold:
            self._opened_at = self.clock()

    def abandon_call(self) -> None:
        """Release a half-open probe without treating caller cancellation as failure."""
        self._probe_in_flight = False


@dataclass(frozen=True)
class RetryPolicy:
    timeout_seconds: float
    max_attempts: int
    base_delay_seconds: float
    max_delay_seconds: float

    def delay_for(self, attempt_number: int) -> float:
        capped = min(self.max_delay_seconds, self.base_delay_seconds * (2 ** (attempt_number - 1)))
        return capped * random.uniform(0.5, 1.0)


@dataclass
class ModelCallResilience:
    """Execute one logical provider request with timeout, retry, and circuit state."""

    retry_policy: RetryPolicy
    circuit_breaker: CircuitBreaker

    async def execute(self, operation: Callable[[], Awaitable[T]]) -> ResilientResult[T]:
        self.circuit_breaker.before_call()
        try:
            attempt_number = 0
            while True:
                attempt_number += 1
                try:
                    async with asyncio.timeout(self.retry_policy.timeout_seconds):
                        result = await operation()
                except asyncio.CancelledError:
                    self.circuit_breaker.abandon_call()
                    raise
                except Exception as error:
                    retryable = is_transient_provider_error(error) or isinstance(error, TimeoutError)
                    if not retryable:
                        self.circuit_breaker.abandon_call()
                        raise
                    if attempt_number == self.retry_policy.max_attempts:
                        self.circuit_breaker.record_transient_failure()
                        raise
                    await asyncio.sleep(self.retry_policy.delay_for(attempt_number))
                else:
                    self.circuit_breaker.record_success()
                    return ResilientResult(value=result, attempts=attempt_number)
        except asyncio.CancelledError:
            raise

    def execute_sync(self, operation: Callable[[], T]) -> ResilientResult[T]:
        """Execute one synchronous provider request with the same retry policy.

        The batch pipeline uses the synchronous OpenAI client so it can share
        one client across embedding, classification, and Insight calls. Its
        client timeout is configured at construction time; this method applies
        the same transient-error, retry, and circuit policy as live chat.
        """
        self.circuit_breaker.before_call()
        attempt_number = 0
        while True:
            attempt_number += 1
            try:
                result = operation()
            except Exception as error:
                retryable = is_transient_provider_error(error) or isinstance(error, TimeoutError)
                if not retryable:
                    self.circuit_breaker.abandon_call()
                    raise
                if attempt_number == self.retry_policy.max_attempts:
                    self.circuit_breaker.record_transient_failure()
                    raise
                time.sleep(self.retry_policy.delay_for(attempt_number))
            else:
                self.circuit_breaker.record_success()
                return ResilientResult(value=result, attempts=attempt_number)


async def acquire_model_capacity(
    limiter: asyncio.Semaphore, queue_timeout_seconds: float
) -> None:
    """Acquire a bulkhead slot without leaving cancelled waiters behind."""
    try:
        await asyncio.wait_for(limiter.acquire(), timeout=queue_timeout_seconds)
    except TimeoutError as error:
        raise ModelCapacityExceededError(
            "Model call capacity is temporarily exhausted; retry shortly."
        ) from error
