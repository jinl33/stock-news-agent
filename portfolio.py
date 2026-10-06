PORTFOLIO = {
    "PLTR": {"themes": ["AI", "Defense", "Government Software"], "risk": "government contracts"},
    "AAPL": {"themes": ["Consumer", "AI hardware", "Services"], "risk": "demand slowdown"},
    "AMZN": {"themes": ["Cloud", "E-commerce", "AI"], "risk": "margin pressure"},
    "MSFT": {"themes": ["Cloud", "AI", "Enterprise"], "risk": "valuation sensitivity"},
}


def infer_portfolio_impact(event_text: str, tickers: list[str] | None = None) -> list[dict]:
    selected = tickers or list(PORTFOLIO.keys())
    impacts = []
    text = (event_text or "").lower()

    for ticker in selected:
        profile = PORTFOLIO.get(ticker, {})
        themes = profile.get("themes", [])
        direction = "ambiguous"

        if any(term in text for term in ["rate cut", "rates lower", "dovish", "easing", "lower yields"]):
            if ticker in {"MSFT", "AAPL", "AMZN"}:
                direction = "positive"
        if any(term in text for term in ["inflation", "higher yields", "tightening", "hawkish"]):
            if ticker in {"AAPL", "MSFT", "AMZN"}:
                direction = "negative"
        if any(term in text for term in ["ai", "cloud", "software", "defense"]):
            if ticker in {"PLTR", "MSFT", "AMZN"}:
                direction = "positive"

        impacts.append({
            "ticker": ticker,
            "direction": direction,
            "horizon": "medium-term",
            "confidence": 0.68,
            "reason": f"{ticker} is exposed to {', '.join(themes[:2]) if themes else 'core growth themes'} and the event text aligns with that exposure.",
        })

    return impacts
