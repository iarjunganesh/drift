import asyncio

import httpx
import pytest
from openai import APIConnectionError

from backend.core.resilience import (
    CircuitBreaker,
    ModelCallResilience,
    ModelCapacityExceededError,
    ProviderCircuitOpenError,
    RetryPolicy,
    acquire_model_capacity,
    is_transient_provider_error,
)


def policy(max_attempts: int = 3) -> RetryPolicy:
    return RetryPolicy(
        timeout_seconds=1,
        max_attempts=max_attempts,
        base_delay_seconds=0,
        max_delay_seconds=0,
    )


@pytest.mark.asyncio
async def test_resilience_retries_transient_timeout_and_closes_circuit() -> None:
    attempts = 0
    breaker = CircuitBreaker(failure_threshold=2, reset_seconds=10)
    resilience = ModelCallResilience(policy(), breaker)

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError("slow provider")
        return "ok"

    result = await resilience.execute(operation)
    assert result.value == "ok"
    assert result.attempts == 3
    assert attempts == 3
    breaker.before_call()
    assert is_transient_provider_error(TimeoutError("not an SDK error")) is False
    assert is_transient_provider_error(APIConnectionError(request=httpx.Request("GET", "https://x")))


@pytest.mark.asyncio
async def test_resilience_opens_then_recovers_circuit_with_one_probe() -> None:
    now = [0.0]
    breaker = CircuitBreaker(failure_threshold=2, reset_seconds=10, clock=lambda: now[0])
    resilience = ModelCallResilience(policy(max_attempts=1), breaker)

    async def fail() -> None:
        raise TimeoutError("slow provider")

    with pytest.raises(TimeoutError):
        await resilience.execute(fail)
    with pytest.raises(TimeoutError):
        await resilience.execute(fail)
    with pytest.raises(ProviderCircuitOpenError, match="retry in"):
        await resilience.execute(fail)

    now[0] = 10.0
    breaker.before_call()
    with pytest.raises(ProviderCircuitOpenError, match="probe"):
        breaker.before_call()
    breaker.abandon_call()
    recovered = await resilience.execute(lambda: asyncio.sleep(0, result="recovered"))
    assert recovered.value == "recovered"
    assert recovered.attempts == 1
    breaker.before_call()


@pytest.mark.asyncio
async def test_resilience_releases_half_open_probe_on_cancellation() -> None:
    now = [10.0]
    breaker = CircuitBreaker(failure_threshold=1, reset_seconds=5, clock=lambda: now[0])
    resilience = ModelCallResilience(policy(max_attempts=1), breaker)

    async def fail() -> None:
        raise TimeoutError("slow provider")

    with pytest.raises(TimeoutError):
        await resilience.execute(fail)
    now[0] = 15.0

    task = asyncio.create_task(resilience.execute(lambda: asyncio.sleep(60)))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    available = await resilience.execute(lambda: asyncio.sleep(0, result="available"))
    assert available.value == "available"


@pytest.mark.asyncio
async def test_model_capacity_times_out_and_can_be_reused() -> None:
    limiter = asyncio.Semaphore(1)
    await limiter.acquire()

    with pytest.raises(ModelCapacityExceededError, match="exhausted"):
        await acquire_model_capacity(limiter, queue_timeout_seconds=0.01)

    limiter.release()
    await acquire_model_capacity(limiter, queue_timeout_seconds=0.01)
    limiter.release()
