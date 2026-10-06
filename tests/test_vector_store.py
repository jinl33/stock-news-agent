import json

from vector_store import LocalVectorStore


def test_vector_search_returns_relevant_documents(monkeypatch):
    def fake_embed(text, model=None):
        if "fed" in text.lower():
            return [1.0, 0.0, 0.0]
        if "ai" in text.lower():
            return [0.0, 1.0, 0.0]
        return [0.0, 0.0, 1.0]

    monkeypatch.setattr("vector_store.generate_embedding", fake_embed)

    store = LocalVectorStore(path="data/test_vector_store.json")
    store.upsert({"id": "fed-1", "headline": "Fed signals rate cut", "summary": "Inflation is cooling.", "url": "https://example.com/fed"})
    store.upsert({"id": "ai-1", "headline": "AI chip demand strong", "summary": "New processors are boosting growth.", "url": "https://example.com/ai"})

    results = store.search("Fed rate cut and inflation", limit=2)

    assert results[0]["id"] == "fed-1"
    assert results[0]["score"] >= results[1]["score"]


def test_vector_store_persists_to_disk(tmp_path):
    path = tmp_path / "vectors.json"
    store = LocalVectorStore(path=str(path))
    store.upsert({"id": "doc-1", "headline": "Headline", "summary": "Summary", "url": "https://example.com/doc-1"})

    saved = json.loads(path.read_text())
    assert any(item["id"] == "doc-1" for item in saved["documents"])
