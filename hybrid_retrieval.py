from retriever import retrieve_context
from vector_store import generate_embedding
from memory import load_articles


def _document_vector(text: str) -> list[float]:
    return generate_embedding(text)


def hybrid_retrieve(query: str, limit: int = 5) -> list[dict]:
    lexical = retrieve_context(query, max_results=limit * 3)
    lex_map = {item.get("id") or item.get("url") or item.get("headline"): item for item in lexical}

    docs = load_articles()
    scored = []
    query_vector = _document_vector(query)
    for item in docs:
        text = " ".join([item.get("headline") or "", item.get("summary") or "", item.get("content") or ""])
        doc_vector = _document_vector(text)
        semantic = sum(a * b for a, b in zip(query_vector, doc_vector))
        base = lex_map.get(item.get("id") or item.get("url") or item.get("headline"), {})
        lexical_score = float(base.get("score", 0.0))
        final_score = (0.7 * lexical_score) + (0.3 * max(semantic, 0.0))
        scored.append({
            "id": item.get("id"),
            "headline": item.get("headline"),
            "summary": item.get("summary"),
            "url": item.get("url"),
            "score": round(final_score, 4),
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:limit]
