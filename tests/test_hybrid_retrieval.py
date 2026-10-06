from hybrid_retrieval import hybrid_retrieve


def test_hybrid_retrieve_blends_score_types(monkeypatch):
    docs = [
        {"id": "fed", "headline": "Fed signals rate cut", "summary": "Inflation is easing.", "url": "https://example.com/fed", "published_at": 1700000000},
        {"id": "ai", "headline": "AI chip demand strong", "summary": "Semiconductor demand remains high.", "url": "https://example.com/ai", "published_at": 1700000200},
    ]

    monkeypatch.setattr("hybrid_retrieval.load_articles", lambda db_path="data/news.db": docs)
    monkeypatch.setattr("hybrid_retrieval.generate_embedding", lambda text, model="nomic-embed-text": [1.0, 0.0, 0.0] if "fed" in text.lower() else [0.0, 1.0, 0.0])

    out = hybrid_retrieve("Fed rate cut and inflation", limit=2)

    assert out[0]["id"] == "fed"
    assert out[0]["score"] >= out[1]["score"]
