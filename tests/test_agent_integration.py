import analyzer
import agent


def test_analyze_does_not_use_local_ollama_by_default(monkeypatch):
    local_attempted = {"value": False}

    def fake_retrieve_context(*args, **kwargs):
        return []

    def fake_get_market_snapshot(*args, **kwargs):
        return {}

    def fake_infer_portfolio_impact(*args, **kwargs):
        return []

    class FakeOllama:
        def chat(self, *args, **kwargs):
            local_attempted["value"] = True
            raise AssertionError("local Ollama path should not be used by default")

    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("USE_LOCAL_LLM", "false")
    monkeypatch.setattr(analyzer, "retrieve_context", fake_retrieve_context)
    monkeypatch.setattr(analyzer, "get_market_snapshot", fake_get_market_snapshot)
    monkeypatch.setattr(analyzer, "infer_portfolio_impact", fake_infer_portfolio_impact)
    monkeypatch.setattr(analyzer, "ollama", FakeOllama(), raising=False)

    result = analyzer.analyze([{"headline": "Fed signals rate cut", "summary": "Inflation cools", "url": "https://example.com/fed"}])

    assert result == []
    assert local_attempted["value"] is False


def test_run_uses_report_builder_and_storage(monkeypatch):
    captured = {}

    def fake_fetch():
        return [{"headline": "Fed signals rate cut", "summary": "Inflation cools", "url": "https://example.com/fed", "published_at": 1700000000}]

    def fake_save(articles):
        captured["saved"] = articles

    def fake_cluster(articles):
        return [{"headline": "Fed signals rate cut", "articles": articles}]

    def fake_analyze(stories):
        return [{"headline": "Fed signals rate cut", "analysis": "Good for growth stocks.", "source": "https://example.com/fed", "theme": "Macro", "ticker": "MSFT"}]

    def fake_send(report):
        captured["report"] = report

    monkeypatch.setattr(agent, "fetch_articles", fake_fetch)
    monkeypatch.setattr(agent, "save_articles", fake_save)
    monkeypatch.setattr(agent, "cluster_articles", fake_cluster)
    monkeypatch.setattr(agent, "analyze", fake_analyze)
    monkeypatch.setattr(agent, "send_message", fake_send)
    monkeypatch.setattr(agent, "build_report", lambda stories, market_snapshot=None, portfolio_context=None: "BUILT REPORT")

    report = agent.run()

    assert captured["saved"]
    assert report == "BUILT REPORT"
