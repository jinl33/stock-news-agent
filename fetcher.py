import feedparser
from bs4 import BeautifulSoup
from config import NEWS_FEEDS


def _strip_html(raw: str) -> str:
    return BeautifulSoup(raw or "", "html.parser").get_text(separator=" ").strip()


def _parse_published(entry) -> int:
    t = getattr(entry, "published_parsed", None)
    if t:
        import calendar
        return calendar.timegm(t)
    return 0


def fetch_articles() -> list[dict]:
    articles = []
    for feed_url in NEWS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            articles.append(
                {
                    "title": entry.get("title", "").strip(),
                    "link": entry.get("link", ""),
                    "summary": _strip_html(entry.get("summary", "")),
                    "_published_ts": _parse_published(entry),
                }
            )

    articles.sort(key=lambda a: a["_published_ts"], reverse=True)

    # Drop internal sort key before returning
    for a in articles:
        del a["_published_ts"]

    return articles[:20]
