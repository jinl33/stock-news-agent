def build_report(stories: list[dict], market_snapshot: dict | None = None, portfolio_context: list[dict] | None = None) -> str:
    lines = ["[Global Macro & Portfolio Intelligence]"]
    lines.append("=======================")
    lines.append("Macro update")

    for story in stories:
        title = story.get("headline") or "Untitled story"
        analysis = story.get("analysis") or "No analysis provided."
        source = story.get("source") or "Source unavailable"
        theme = story.get("theme") or "Macro"
        ticker = story.get("ticker") or "N/A"
        lines.append(f"\n📌 {theme}: {title} [{ticker}]")
        lines.append(f"   💡 {analysis}")
        lines.append(f"   🔗 {source}")

    if market_snapshot:
        lines.append("\n📈 Market snapshot")
        for symbol, values in market_snapshot.items():
            daily_change = values.get("daily_change", 0)
            lines.append(f"   - {symbol}: daily {daily_change:.2f}%")

    if portfolio_context:
        lines.append("\n👤 Portfolio context")
        for item in portfolio_context:
            ticker = item.get("ticker")
            direction = item.get("direction", "ambiguous")
            confidence = item.get("confidence", 0.0)
            lines.append(f"   - {ticker}: {direction} (confidence {confidence:.2f})")

    return "\n".join(lines).strip()
