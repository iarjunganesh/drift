"""Read-only fixture repository used by the no-key judge demo mode."""

import json
import re
from collections.abc import Iterable
from pathlib import Path

from backend.models.schema import Insight


class InsightStore:
    def __init__(self, insights: Iterable[Insight]) -> None:
        self._insights = list(insights)

    @classmethod
    def from_json(cls, path: str | Path) -> InsightStore:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(Insight.model_validate(item) for item in payload)

    def all(self) -> list[Insight]:
        return list(self._insights)

    def search(self, query: str, limit: int = 5) -> list[Insight]:
        terms = set(re.findall(r"[a-z0-9]+", query.lower()))

        def score(insight: Insight) -> tuple[int, float]:
            document = " ".join(
                [insight.title, insight.summary, insight.why_it_matters,
                 insight.what_to_check, *insight.affected_libraries]
            ).lower()
            return (sum(term in document for term in terms), insight.confidence)

        return [item for item in sorted(self._insights, key=score, reverse=True)
                if score(item)[0] > 0][:limit]
