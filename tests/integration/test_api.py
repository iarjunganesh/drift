def test_health_and_briefing(api_client) -> None:
    root = api_client.get("/")
    health = api_client.get("/health")
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
