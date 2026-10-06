import vector_store


def test_generate_embedding_uses_local_ollama_backend(monkeypatch):
    class FakeOllama:
        @staticmethod
        def embed(model, input):
            return {"embeddings": [[0.9, 0.1, 0.0]]}

    monkeypatch.setattr(vector_store, "ollama", FakeOllama(), raising=False)

    embedding = vector_store.generate_embedding("Fed rate cut")

    assert isinstance(embedding, list)
    assert len(embedding) >= 3
    assert embedding[0] > 0.5
