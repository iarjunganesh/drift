from backend import main
from backend.core.store import InsightStore
from backend.models.schema import ChangeSeverity, Insight


def test_reviewed_notes_are_never_exposed_publicly(api_client) -> None:
    secret = "PRIVATE reviewer rationale that must never reach a public response."
    reviewed = Insight(
        id=999,
        raw_item_ids=[999],
        title="vllm reviewed release note",
        summary="A direct source fact about the vllm runtime.",
        why_it_matters="A labelled interpretation.",
        what_to_check="Run one bounded check.",
        severity=ChangeSeverity.MINOR,
        affected_libraries=["vllm"],
        source_citations=["https://example.com/vllm-release"],
        confidence=0.99,
        model_used="gpt-5.6-luna",
        human_review_notes=secret,
    )
    store = main.app.state.insight_store
    main.app.state.insight_store = InsightStore([*store.all(), reviewed])

    briefing = api_client.get("/briefing", params={"top_n": 10})
    search = api_client.get("/search", params={"q": "vllm reviewed release note"})

    assert briefing.status_code == 200
    assert search.status_code == 200
    # The secret text must not appear anywhere in the serialized payloads...
    assert secret not in briefing.text
    assert secret not in search.text
    # ...and the field key itself must be absent from every returned insight.
    assert all("human_review_notes" not in item["insight"] for item in briefing.json())
    assert all("human_review_notes" not in item for item in search.json())


def test_health_and_briefing(api_client) -> None:
    root = api_client.get("/")
    health = api_client.get("/health")

    assert health.json()["version"] == "1.0.0"
    briefing = api_client.get("/briefing")

    assert root.status_code == 200
    assert root.json()["service"] == "DRIFT"
    assert root.json()["docs"] == "/docs"
    assert health.status_code == 200
    assert health.json()["mode"] == "fixture"
    assert briefing.status_code == 200
    assert briefing.json()[0]["insight"]["source_citations"]


def test_openapi_routes_have_clear_groups(api_client) -> None:
    schema = api_client.get("/openapi.json").json()

    assert "human_review_notes" not in str(schema)
    assert [tag["name"] for tag in schema["tags"]] == [
        "system",
        "briefing",
        "search",
        "chat",
    ]
    assert schema["paths"]["/"]["get"]["tags"] == ["system"]
    assert schema["paths"]["/health"]["get"]["tags"] == ["system"]
    assert schema["paths"]["/briefing"]["get"]["tags"] == ["briefing"]
    assert schema["paths"]["/search"]["get"]["tags"] == ["search"]
    assert schema["paths"]["/chat"]["post"]["tags"] == ["chat"]


def test_api_docs_and_brand_assets_use_canonical_banners(api_client) -> None:
    docs = api_client.get("/docs")
    dark = api_client.get("/brand/dark.svg")
    light = api_client.get("/brand/light.svg")
    missing = api_client.get("/brand/unknown.svg")

    assert docs.status_code == 200
    assert "/brand/dark.svg" in docs.text
    assert "/brand/light.svg" in docs.text
    assert "background: #edf4ff" in docs.text
    assert "@media (prefers-color-scheme: dark)" in docs.text
    assert dark.headers["content-type"].startswith("image/svg+xml")
    assert light.headers["content-type"].startswith("image/svg+xml")
    assert b"DRIFT" in dark.content
    assert b"DRIFT" in light.content
    assert missing.status_code == 404


def test_search_and_grounded_chat(api_client) -> None:
    search = api_client.get("/search", params={"q": "vllm runtime"})
    chat = api_client.post("/chat", json={"question": "What should I check for vllm?"})

    assert search.status_code == 200
    assert search.json()[0]["id"] == 1
    assert chat.status_code == 200
    assert chat.json()["source_citations"]


def test_chat_returns_not_found_without_grounding(api_client) -> None:
    response = api_client.post("/chat", json={"question": "KubernetesXYZ"})

    assert response.status_code == 404
    assert response.json()["detail"] == "No matching DRIFT insights."
