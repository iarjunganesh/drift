"""Shared lifecycle contract for DRIFT pipeline agents."""

from abc import ABC, abstractmethod
from typing import Any

import structlog


class BaseAgent(ABC):
    """A small, typed-by-convention agent with observable execution."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.log = structlog.get_logger(agent=name)

    @abstractmethod
    async def run(self, input_data: Any) -> Any:  # noqa: ANN401
        """Transform input data into output data."""

    async def __call__(self, input_data: Any) -> Any:  # noqa: ANN401
        self.log.info("agent.start")
        try:
            result = await self.run(input_data)
            self.log.info("agent.complete")
            return result
        except Exception as exc:
            self.log.exception("agent.error", error=str(exc))
            raise
