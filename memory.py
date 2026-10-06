import hashlib
import json
import os
import re
from collections import defaultdict
from urllib.parse import parse_qsl, urlencode, urlunparse, urlparse

DEFAULT_DB_PATH = os.path.join("data", "news.db")


def _normalize_title(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def canonicalize_url(url: str | None) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
    filtered_pairs = [
        (key, value)
        for key, value in query_pairs
        if not key.lower().startswith("utm") and key.lower() not in {"gclid", "gbraid"}
    ]
    return urlunparse(parsed._replace(query=urlencode(filtered_pairs, doseq=True)))


def article_id(article: dict) -> str:
    canonical = canonicalize_url(article.get("url"))
    headline = article.get("headline") or article.get("summary") or "untitled"
    raw = canonical if canonical else headline
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def deduplicate_articles(articles: list[dict]) -> list[dict]:
    deduped: dict[str, dict] = {}
    for article in articles:
        candidate = dict(article)
        if not candidate.get("id"):
            candidate["id"] = article_id(candidate)
        candidate["url"] = canonicalize_url(candidate.get("url"))

        signature = candidate.get("url") or _normalize_title(candidate.get("headline", ""))
        if signature in deduped:
            current = deduped[signature]
            if (candidate.get("published_at") or 0) >= (current.get("published_at") or 0):
                deduped[signature] = candidate
        else:
            deduped[signature] = candidate

    return list(deduped.values())


def _title_similarity(a: str, b: str) -> float:
    left = set(_normalize_title(a).split())
    right = set(_normalize_title(b).split())
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    overlap = left & right
    return len(overlap) / max(len(left | right), 1)


def _is_same_event(article_a: dict, article_b: dict) -> bool:
    a_url = canonicalize_url(article_a.get("url"))
    b_url = canonicalize_url(article_b.get("url"))
    if a_url and b_url and a_url == b_url:
        return True

    a_title = article_a.get("headline") or ""
    b_title = article_b.get("headline") or ""
    title_match = _title_similarity(a_title, b_title)
    if title_match >= 0.35:
        return True

    a_time = int(article_a.get("published_at") or 0)
    b_time = int(article_b.get("published_at") or 0)
    if a_time and b_time and abs(a_time - b_time) <= 86400:
        overlap = set(_normalize_title(a_title).split()) & set(_normalize_title(b_title).split())
        return len(overlap) >= 2

    return False


def cluster_articles(articles: list[dict]) -> list[dict]:
    clusters: list[dict] = []
    for article in sorted(articles, key=lambda item: item.get("published_at", 0), reverse=False):
        matched = False
        for cluster in clusters:
            cluster_article = cluster["articles"][0]
            if _is_same_event(article, cluster_article):
                cluster["articles"].append(article)
                matched = True
                break

        if not matched:
            clusters.append({
                "headline": article.get("headline") or "Untitled event",
                "articles": [article],
            })

    return clusters


def _ensure_parent_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _connect(db_path: str = DEFAULT_DB_PATH):
    _ensure_parent_dir(db_path)
    conn = __import__("sqlite3").connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            publisher TEXT,
            headline TEXT,
            summary TEXT,
            content TEXT,
            url TEXT,
            published_at INTEGER,
            fetched_at INTEGER,
            payload TEXT
        )
        """
    )
    return conn


def save_articles(articles: list[dict], db_path: str = DEFAULT_DB_PATH) -> int:
    deduped = deduplicate_articles(articles)
    conn = _connect(db_path)
    try:
        for article in deduped:
            article_copy = dict(article)
            article_copy["id"] = article_copy.get("id") or article_id(article_copy)
            article_copy["url"] = canonicalize_url(article_copy.get("url"))
            conn.execute(
                """
                INSERT OR REPLACE INTO articles (
                    id, publisher, headline, summary, content, url, published_at, fetched_at, payload
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    article_copy["id"],
                    article_copy.get("publisher"),
                    article_copy.get("headline"),
                    article_copy.get("summary"),
                    article_copy.get("content"),
                    article_copy.get("url"),
                    int(article_copy.get("published_at") or 0),
                    int(article_copy.get("fetched_at") or 0),
                    json.dumps(article_copy, ensure_ascii=False),
                ),
            )
        conn.commit()
    finally:
        conn.close()
    return len(deduped)


def load_articles(db_path: str = DEFAULT_DB_PATH) -> list[dict]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT id, publisher, headline, summary, content, url, published_at, fetched_at, payload
            FROM articles
            ORDER BY published_at DESC
            """
        ).fetchall()
    finally:
        conn.close()

    articles: list[dict] = []
    for row in rows:
        payload = row[8]
        if payload:
            article = json.loads(payload)
        else:
            article = {
                "id": row[0],
                "publisher": row[1],
                "headline": row[2],
                "summary": row[3],
                "content": row[4],
                "url": row[5],
                "published_at": row[6],
                "fetched_at": row[7],
            }
        articles.append(article)
    return articles
