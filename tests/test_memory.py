from memory import cluster_articles, deduplicate_articles, load_articles, save_articles


def test_deduplicate_articles_by_url_and_title(tmp_path):
    articles = [
        {
            "id": "a1",
            "publisher": "Yahoo Finance",
            "headline": "Fed signals potential rate cut",
            "summary": "Summary A",
            "url": "https://example.com/fed-rate-cut",
            "published_at": 1700000000,
        },
        {
            "id": "a2",
            "publisher": "WSJ",
            "headline": "Fed signals potential rate cut",
            "summary": "Summary B",
            "url": "https://example.com/fed-rate-cut?utm=1",
            "published_at": 1700000100,
        },
    ]

    deduped = deduplicate_articles(articles)

    assert len(deduped) == 1
    assert deduped[0]["headline"] == "Fed signals potential rate cut"


def test_cluster_articles_groups_near_duplicate_events(tmp_path):
    db_path = tmp_path / "memory.db"
    articles = [
        {
            "id": "evt-1",
            "publisher": "Yahoo Finance",
            "headline": "Fed holds rates steady amid slowing inflation",
            "summary": "The Fed kept rates unchanged.",
            "url": "https://example.com/fed-1",
            "published_at": 1700000000,
        },
        {
            "id": "evt-2",
            "publisher": "WSJ",
            "headline": "Fed keeps rates unchanged as inflation cools",
            "summary": "The central bank left rates unchanged.",
            "url": "https://example.com/fed-2",
            "published_at": 1700000600,
        },
    ]

    save_articles(articles, db_path=str(db_path))
    clustered = cluster_articles(load_articles(db_path=str(db_path)))

    assert len(clustered) == 1
    assert clustered[0]["headline"] == "Fed holds rates steady amid slowing inflation"
    assert len(clustered[0]["articles"]) == 2
