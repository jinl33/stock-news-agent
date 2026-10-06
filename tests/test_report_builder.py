from report_builder import build_report


def test_build_report_embeds_market_and_portfolio_context():
    stories = [
        {
            "headline": "Fed signals rate cut",
            "analysis": "The Fed may ease as inflation cools.",
            "source": "https://example.com/fed",
            "theme": "Macro",
            "ticker": "MSFT",
        }
    ]
    market = {"SPY": {"daily_change": -1.5}, "QQQ": {"daily_change": -2.1}}
    portfolio = [{"ticker": "MSFT", "direction": "positive", "confidence": 0.74}]

    report = build_report(stories, market_snapshot=market, portfolio_context=portfolio)

    assert "[Global Macro & Portfolio Intelligence]" in report
    assert "SPY" in report
    assert "MSFT" in report
    assert "positive" in report.lower()
