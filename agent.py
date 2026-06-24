from fetcher import fetch_articles
from analyzer import analyze
from notifier import send_message

_THEME_ICON = {
    "Tech/AI": "💻",
    "Biotech": "🧬",
    "Macro": "🌐",
}
_IMPORTANCE_ICON = {"high": "🔴", "medium": "🟡"}


def _format_report(stories: list[dict]) -> str:
    if not stories:
        return "No actionable intelligence found today."
    
    lines = ["[Global Macro & Portfolio Intelligence]"]
    lines.append("=======================")
    
    # Group by theme
    grouped = {}
    for s in stories:
        theme = s.get("theme", "Macro")
        grouped.setdefault(theme, []).append(s)
        
    for theme, items in grouped.items():
        lines.append(f"\n📌 {theme.upper()}")
        for item in items:
            ticker = f" [{item.get('ticker')}]" if item.get("ticker") and item.get("ticker") != "None" else ""
            lines.append(f"🔴 {item.get('headline_ko')}{ticker}")
            lines.append(f"   {item.get('headline_en')}")
            lines.append(f"   💡 {item.get('analysis_ko')}")
            lines.append(f"   💡 {item.get('analysis_en')}\n")
            
    return "\n".join(lines)


def run():
    print("Fetching RSS feeds...")
    stories = fetch_articles()

    print("Analyzing...")
    analyzed = analyze(stories)

    if not analyzed:
        print("Inference failed or no actionable news found. Aborting alert.")
        return

    report = _format_report(analyzed)
    print("\n--- Report Preview ---")
    print(report)
    print("----------------------\n")

    print("Sending KakaoTalk notification...")
    send_message(report)
    print("Done.")

if __name__ == "__main__":
    run()
