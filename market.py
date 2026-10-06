from __future__ import annotations

import yfinance as yf


def _extract_close_values(data, symbol: str | None = None):
    if data is None:
        return []

    if isinstance(data, dict):
        if symbol and symbol in data:
            data = data[symbol]
        else:
            series = data.get("Close")
            if series is not None:
                return list(series)
            for candidate in data.values():
                if hasattr(candidate, "__getitem__") and "Close" in getattr(candidate, "_values", {}):
                    candidate_series = candidate["Close"]
                    if hasattr(candidate_series, "tolist"):
                        return list(candidate_series.tolist())
                    return list(candidate_series)
            return []

    if hasattr(data, "__getitem__") and "Close" in getattr(data, "_values", {}):
        series = data["Close"]
        if hasattr(series, "tolist"):
            return list(series.tolist())
        return list(series)

    if hasattr(data, "Close"):
        series = data["Close"]
        if hasattr(series, "tolist"):
            return list(series.tolist())
        return list(series)

    if hasattr(data, "tolist"):
        return list(data.tolist())

    return list(data)


def get_market_snapshot(symbols: list[str]) -> dict:
    snapshot: dict[str, dict] = {}
    for symbol in symbols:
        try:
            data = yf.download(symbol, period="5d", interval="1d")
            closes = _extract_close_values(data, symbol)
            if len(closes) < 2:
                continue
            current = float(closes[-1])
            prev = float(closes[-2])
            daily_change = ((current - prev) / prev) * 100 if prev else 0.0
            first = float(closes[0])
            snapshot[symbol] = {
                "daily_change": round(daily_change, 4),
                "current_price": round(current, 4),
                "five_day_change": round(((current - first) / first) * 100, 4) if first else 0.0,
            }
        except Exception:
            continue
    return snapshot
