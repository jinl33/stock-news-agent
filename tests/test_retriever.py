import retriever


def test_retrieve_context_prioritizes_keyword_matches(monkeypatch):
    articles = [
        {
            "id": "fed-1",
            "headline": "Fed signals potential rate cut",
            "summary": "The Federal Reserve may cut rates as inflation cools.",
            "url": "https://example.com/fed-1",
            "publisher": "Yahoo Finance",
            "published_at": 1700000000,
        },
        {
            "id": "tech-1",
            "headline": "NVIDIA launches new AI chip",
            "summary": "Chip demand remains strong in the AI sector.",
            "url": "https://example.com/ai-1",
            "publisher": "WSJ",
            "published_at": 1700000100,
        },
    ]

    monkeypatch.setattr(retriever, "load_articles", lambda db_path="data/news.db": articles)

    results = retriever.retrieve_context("Fed rate cut and inflation", max_results=5)

    assert results[0]["headline"] == "Fed signals potential rate cut"
    assert results[0]["score"] >= results[1]["score"]


def test_specialized_retrieval_modes_apply_time_windows(monkeypatch):
    articles = [
        {
            "id": "old-fed",
            "headline": "Fed rate cut historical context",
            "summary": "Earlier easing cycle comparisons.",
            "url": "https://example.com/old-fed",
            "publisher": "Reuters",
            "published_at": 1600000000,
        },
        {
            "id": "new-fed",
            "headline": "Fresh market reaction after rate decision",
            "summary": "The Fed decision is driving yields lower.",
            "url": "https://example.com/new-fed",
            "publisher": "Bloomberg",
            "published_at": 1700000000,
        },
    ]

    monkeypatch.setattr(retriever, "load_articles", lambda db_path="data/news.db": articles)

    historical = retriever.retrieve_historical_analogues("Fed rate cut", max_results=5)
    breaking = retriever.retrieve_breaking_news("Fed rate cut", max_results=5)

    assert historical[0]["headline"] == "Fed rate cut historical context"
    assert breaking[0]["headline"] == "Fresh market reaction after rate decision"
