from types import SimpleNamespace

import fetcher


def test_fetcher_uses_configured_feeds_and_collects_metadata(monkeypatch):
    def fake_parse(url):
        if "feed-a" in url:
            return SimpleNamespace(
                entries=[
                    {
                        "title": "Old headline",
                        "link": "https://example.com/article-old",
                        "summary": "<p>Old summary</p>",
                        "published_parsed": (2024, 1, 1, 10, 0, 0, 0, 0, 0),
                    },
                    {
                        "title": "New headline",
                        "link": "https://example.com/article-new",
                        "summary": "<p>New summary</p>",
                        "published_parsed": (2025, 2, 2, 12, 0, 0, 0, 0, 0),
                    },
                ]
            )
        return SimpleNamespace(entries=[])

    monkeypatch.setattr(fetcher, "NEWS_FEEDS", {"Alpha": "https://example.com/feed-a"})
    monkeypatch.setattr(fetcher.feedparser, "parse", fake_parse)

    articles = fetcher.fetch_articles(limit_per_feed=2)

    assert len(articles) == 2
    assert articles[0]["headline"] == "New headline"
    assert articles[0]["publisher"] == "Alpha"
    assert articles[0]["summary"] == "New summary"
    assert articles[0]["url"] == "https://example.com/article-new"
    assert articles[0]["published_at"] > 0
