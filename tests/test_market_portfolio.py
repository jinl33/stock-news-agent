from market import get_market_snapshot
from portfolio import infer_portfolio_impact


class FakeSeries:
    def __init__(self, values):
        self.values = list(values)


class FakeFrame:
    def __init__(self, values):
        self._values = values

    def __getitem__(self, key):
        return self._values[key]


def test_get_market_snapshot_uses_symbol_names(monkeypatch):
    def fake_download(tickers, period, interval):
        data = {
            "SPY": FakeFrame({"Close": [101.0, 100.0]}),
            "QQQ": FakeFrame({"Close": [200.0, 198.0]}),
            "^TNX": FakeFrame({"Close": [4.2, 4.0]}),
            "^VIX": FakeFrame({"Close": [17.0, 15.0]}),
        }
        return data[tickers[0]] if len(tickers) == 1 else data

    monkeypatch.setattr("market.yf.download", fake_download)
    snapshot = get_market_snapshot(["SPY", "QQQ", "^TNX", "^VIX"])

    assert "SPY" in snapshot
    assert snapshot["SPY"]["daily_change"] < 0
    assert "^TNX" in snapshot


def test_infer_portfolio_impact_returns_ticker_direction():
    impact = infer_portfolio_impact("Fed rate cut may support growth stocks", ["MSFT", "AAPL", "AMZN"])

    assert any(item["ticker"] in {"MSFT", "AAPL", "AMZN"} for item in impact)
    assert impact[0]["direction"] in {"positive", "negative", "mixed", "ambiguous"}
