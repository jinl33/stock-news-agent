import feedparser
from bs4 import BeautifulSoup
from config import NEWS_FEEDS

RSS_FEEDS = {
    "WSJ": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
    "CNBC": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Financial Times": "https://www.ft.com/?format=rss"
}


def _strip_html(raw: str) -> str:
    return BeautifulSoup(raw or "", "html.parser").get_text(separator=" ").strip()


def _parse_published(entry) -> int:
    t = getattr(entry, "published_parsed", None)
    if t:
        import calendar
        return calendar.timegm(t)
    return 0


def fetch_articles(limit_per_feed=4) -> list[dict]:
    articles = []
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:limit_per_feed]:
                article = {
                    "publisher": source_name,
                    "headline": entry.get("title", "No Title"),
                    "url": entry.get("link", "No Link")
                }
                articles.append(article)

        except Exception as e:
            print(f"Failed to fetch from {source_name}: {e}")

    print(f"Successfully aggregated {len(articles)} articles from sources.")
    return articles

if __name__ == "__main__":
    articles = fetch_articles()
    for a in articles:
        print(f"{a['publisher']} {a['headline']} - {a['url']}")