import calendar
import time

import feedparser
from bs4 import BeautifulSoup

from config import NEWS_FEEDS


def _strip_html(raw: str) -> str:
    return BeautifulSoup(raw or "", "html.parser").get_text(separator=" ").strip()


def _parse_published(entry) -> int:
    if isinstance(entry, dict):
        published_parsed = entry.get("published_parsed")
        published = entry.get("published") or entry.get("updated")
    else:
        published_parsed = getattr(entry, "published_parsed", None)
        published = getattr(entry, "published", None) or getattr(entry, "updated", None)

    if published_parsed:
        return calendar.timegm(published_parsed)

    if not published:
        return 0

    try:
        return int(time.mktime(time.strptime(published, "%a, %d %b %Y %H:%M:%S %z")))
    except ValueError:
        try:
            return int(time.mktime(time.strptime(published, "%Y-%m-%dT%H:%M:%S%z")))
        except ValueError:
            return 0


def fetch_articles(limit_per_feed=4) -> list[dict]:
    articles: list[dict] = []
    feed_map = NEWS_FEEDS
    if isinstance(feed_map, list):
        feed_map = {f"source_{index}": url for index, url in enumerate(feed_map)}

    for source_name, feed_url in feed_map.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:limit_per_feed]:
                summary_html = entry.get("summary") or entry.get("description") or ""
                content = _strip_html(summary_html)
                published_at = _parse_published(entry)
                article = {
                    "publisher": source_name,
                    "headline": entry.get("title", "No Title"),
                    "summary": content,
                    "url": entry.get("link", "No Link"),
                    "published_at": published_at,
                    "author": entry.get("author", ""),
                    "tags": entry.get("tags", []),
                    "content": content,
                    "fetched_at": int(time.time()),
                }
                articles.append(article)
        except Exception as e:
            print(f"Failed to fetch from {source_name}: {e}")

    articles.sort(key=lambda item: item.get("published_at", 0), reverse=True)
    print(f"Successfully aggregated {len(articles)} articles from sources.")
    return articles


if __name__ == "__main__":
    articles = fetch_articles()
    for article in articles:
        print(f"{article['publisher']} {article['headline']} - {article['url']}")