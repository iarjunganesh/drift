from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from backend.agents import synthesizer
from backend.models.schema import ChangeSeverity, RawItem


def make_item(identifier: int, content: str = "release notes") -> RawItem:
    return RawItem(
        id=identifier,
        source_id="example",
        title=f"Release {identifier}",
        url=f"https://example.com/releases/{identifier}",
        published_at=datetime(2026, 7, 15, tzinfo=UTC),
        raw_content=content,
    )


class FakeClient:
    def __init__(self) -> None:
        self.embedding_calls: list[dict] = []
        self.response_calls: list[dict] = []

        class Embeddings:
            def __init__(inner_self, outer: FakeClient) -> None:
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.embedding_calls.append(kwargs)
                return SimpleNamespace(
                    data=[
                        SimpleNamespace(index=1, embedding=[0.0, 1.0]),
                        SimpleNamespace(index=0, embedding=[1.0, 0.0]),
                    ]
                )

        class Responses:
            def __init__(inner_self, outer: FakeClient) -> None:
                inner_self.outer = outer

            def create(inner_self, **kwargs):
                inner_self.outer.response_calls.append(kwargs)
                return SimpleNamespace(output_text='{"severity":"breaking"}')

        self.embeddings = Embeddings(self)
        self.responses = Responses(self)
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_embed_items_batches_text_through_embedding_model() -> None:
    client = FakeClient()

    result = synthesizer.embed_items([make_item(1), make_item(2)], client=client)

    assert result == [[1.0, 0.0], [0.0, 1.0]]
    assert client.embedding_calls[0]["model"] == "text-embedding-3-small"
    assert client.embedding_calls[0]["input"] == [
        "Release 1\nrelease notes",
        "Release 2\nrelease notes",
    ]


def test_embed_items_empty_input_does_not_call_provider() -> None:
    assert synthesizer.embed_items([]) == []


def test_embed_items_closes_owned_client(monkeypatch) -> None:
    client = FakeClient()
    monkeypatch.setattr(synthesizer, "create_client", lambda *_args: client)

    assert synthesizer.embed_items([make_item(1)])
    assert client.closed is True


def test_cluster_items_groups_similar_vectors_deterministically() -> None:
    items = [make_item(1), make_item(2), make_item(3)]
    embeddings = [[1.0, 0.0], [0.99, 0.01], [0.0, 1.0]]

    clusters = synthesizer.cluster_items(items, embeddings, similarity_threshold=0.9)

    assert [[item.id for item in cluster] for cluster in clusters] == [[1, 2], [3]]
    assert [[item.title for item in cluster] for cluster in clusters] == [
        ["Release 1", "Release 2"],
        ["Release 3"],
    ]


def test_cluster_items_rejects_mismatched_embeddings() -> None:
    with pytest.raises(ValueError, match="exactly one embedding"):
        synthesizer.cluster_items([make_item(1)], [])


def test_cluster_items_validates_threshold_and_empty_input() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        synthesizer.cluster_items([make_item(1)], [[1.0]], similarity_threshold=1.1)

    assert synthesizer.cluster_items([], []) == []
    assert synthesizer._cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
    with pytest.raises(ValueError, match="dimensions"):
        synthesizer._cosine_similarity([1.0], [1.0, 0.0])


def test_classify_change_uses_dev_tier_and_structured_severity() -> None:
    client = FakeClient()

    result = synthesizer.classify_change([make_item(1, "A security fix")], client=client)

    assert result is ChangeSeverity.BREAKING
    assert client.response_calls[0]["model"] == "gpt-5.6-luna"
    assert client.response_calls[0]["text"]["format"]["name"] == "change_severity"
    assert "A security fix" in client.response_calls[0]["input"]


def test_classify_change_rejects_invalid_provider_output() -> None:
    client = FakeClient()
    client.responses.create = lambda **_kwargs: SimpleNamespace(output_text="not-json")

    with pytest.raises(ValueError, match="invalid severity JSON"):
        synthesizer.classify_change([make_item(1)], client=client)


def test_classify_change_rejects_empty_cluster() -> None:
    with pytest.raises(ValueError, match="empty cluster"):
        synthesizer.classify_change([])


def test_classify_change_rejects_unsupported_severity() -> None:
    client = FakeClient()
    client.responses.create = lambda **_kwargs: SimpleNamespace(output_text='{"severity":"unknown"}')

    with pytest.raises(ValueError, match="unsupported severity"):
        synthesizer.classify_change([make_item(1)], client=client)


def test_classify_change_closes_owned_client(monkeypatch) -> None:
    client = FakeClient()
    monkeypatch.setattr(synthesizer, "create_client", lambda *_args: client)

    assert synthesizer.classify_change([make_item(1)]) is ChangeSeverity.BREAKING
    assert client.closed is True


def test_run_synthesizer_closes_one_shared_owned_client(monkeypatch) -> None:
    client = FakeClient()
    monkeypatch.setattr(synthesizer, "create_client", lambda *_args: client)

    result = synthesizer.run_synthesizer([make_item(1), make_item(2)])

    assert len(result) == 2
    assert result[0][0][0].id == 1
    assert result[0][1] is ChangeSeverity.BREAKING
    assert client.closed is True
