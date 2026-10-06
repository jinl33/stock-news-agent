import math
import os
from datetime import datetime, timedelta

from memory import load_articles


def _keyword_score(text: str, query: str) -> float:
    if not text or not query:
        return 0.0

    query_terms = {term.lower() for term in query.replace("-", " ").split() if term}
    if not query_terms:
        return 0.0

    text_terms = {term.lower() for term in text.replace("-", " ").split() if term}
    overlap = query_terms & text_terms
    if not overlap:
        return 0.0
    return len(overlap) / len(query_terms)


def _recency_score(published_at: int | None, max_age_days: int = 3650) -> float:
    if not published_at:
        return 0.0
    now = datetime.utcnow().timestamp()
    age_days = max((now - published_at) / 86400.0, 0.0)
    if age_days >= max_age_days:
        return 0.0
    return 1.0 - (age_days / max_age_days)


def _entity_overlap(article: dict, query: str) -> float:
    if not query:
        return 0.0
    article_text = " ".join(
        [
            article.get("headline") or "",
            article.get("summary") or "",
            article.get("publisher") or "",
        ]
    ).lower()
    query_tokens = {token for token in query.lower().replace("-", " ").split() if token}
    if not query_tokens:
        return 0.0
    hits = sum(1 for token in query_tokens if token in article_text)
    return min(hits / max(len(query_tokens), 1), 1.0)


def _score_article(article: dict, query: str, *, max_age_days: int = 3650) -> float:
    text = " ".join([
        article.get("headline") or "",
        article.get("summary") or "",
    ])
    semantic = _keyword_score(text, query)
    keyword = _keyword_score(text, query)
    entity = _entity_overlap(article, query)
    recency = _recency_score(article.get("published_at"), max_age_days=max_age_days)
    source_weight = 0.5 if article.get("publisher", "").lower() in {"wsj", "reuters", "bloomberg"} else 0.3
    return (0.45 * semantic) + (0.25 * keyword) + (0.15 * entity) + (0.10 * recency) + (0.05 * source_weight)


def retrieve_context(query: str, *, start_date=None, end_date=None, tickers=None, themes=None, regions=None, max_results=12) -> list[dict]:
    articles = load_articles()
    filtered = []
    for article in articles:
        if not article.get("headline") and not article.get("summary"):
            continue

        if tickers:
            article_tickers = set(str(article.get("tickers") or "").split(","))
            if article_tickers and not set(tickers) & article_tickers:
                continue

        published_at = article.get("published_at") or 0
        if start_date and published_at < start_date.timestamp():
            continue
        if end_date and published_at > end_date.timestamp():
            continue

        score = _score_article(article, query, max_age_days=3650)
        if score <= 0:
            continue
        filtered.append({**article, "score": round(score, 4)})

    filtered.sort(key=lambda item: item["score"], reverse=True)
    return filtered[:max_results]


def retrieve_breaking_news(query: str, max_results: int = 5) -> list[dict]:
    articles = retrieve_context(query, max_results=max_results)
    return sorted(articles, key=lambda item: item.get("published_at", 0), reverse=True)[:max_results]


def retrieve_historical_analogues(query: str, max_results: int = 5) -> list[dict]:
    articles = retrieve_context(query, max_results=max_results * 3)
    return sorted(articles, key=lambda item: item.get("published_at", 0), reverse=False)[:max_results]


def retrieve_market_reaction(query: str, max_results: int = 5) -> list[dict]:
    return retrieve_breaking_news(query, max_results=max_results)


def retrieve_portfolio_impact(query: str, tickers=None, max_results: int = 5) -> list[dict]:
    return retrieve_context(query, tickers=tickers, max_results=max_results)


def retrieve_macro_regime(query: str, max_results: int = 5) -> list[dict]:
    return retrieve_context(query, max_results=max_results)
