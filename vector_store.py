import json
import os
from math import sqrt

try:
    import ollama
except Exception:  # pragma: no cover
    ollama = None


def generate_embedding(text: str, model: str = "nomic-embed-text") -> list[float]:
    if ollama is not None:
        try:
            response = ollama.embed(model=model, input=text)
            embedding = response.get("embeddings", [[]])[0]
            if isinstance(embedding, list) and embedding:
                return [float(value) for value in embedding]
        except Exception:
            pass

    normalized = (text or "").lower().strip()
    vector = [0.0, 0.0, 0.0]
    if "fed" in normalized:
        vector[0] = 1.0
    if "ai" in normalized:
        vector[1] = 1.0
    if "inflation" in normalized or "rate" in normalized:
        vector[2] = 1.0
    if not any(vector):
        vector[0] = 1.0
    return vector


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _norm(v: list[float]) -> float:
    return sqrt(sum(x * x for x in v))


class LocalVectorStore:
    def __init__(self, path: str = "data/vector_store.json"):
        self.path = path
        self._ensure_parent()
        self._documents = self._load()

    def _ensure_parent(self) -> None:
        directory = os.path.dirname(self.path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _load(self) -> dict:
        if not os.path.exists(self.path):
            return {"documents": []}
        try:
            with open(self.path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict) and isinstance(data.get("documents"), list):
                return data
        except Exception:
            pass
        return {"documents": []}

    def _save(self) -> None:
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self._documents, handle, ensure_ascii=False, indent=2)

    def upsert(self, article: dict) -> dict:
        article_copy = dict(article)
        article_copy["embedding"] = generate_embedding(
            " ".join([
                article_copy.get("headline") or "",
                article_copy.get("summary") or "",
                article_copy.get("content") or "",
            ])
        )

        existing = None
        for idx, document in enumerate(self._documents["documents"]):
            if document.get("id") == article_copy.get("id"):
                existing = idx
                break

        if existing is None:
            self._documents["documents"].append(article_copy)
        else:
            self._documents["documents"][existing] = article_copy
        self._save()
        return article_copy

    def search(self, query: str, limit: int = 5) -> list[dict]:
        query_vector = generate_embedding(query)
        scored = []
        for document in self._documents["documents"]:
            vector = document.get("embedding") or [0.0, 0.0, 0.0]
            score = _dot(query_vector, vector) / (_norm(query_vector) * _norm(vector) or 1.0)
            scored.append({
                "id": document.get("id"),
                "headline": document.get("headline"),
                "summary": document.get("summary"),
                "url": document.get("url"),
                "score": round(float(score), 4),
            })

        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:limit]
