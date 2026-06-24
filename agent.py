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
    # Group by theme, preserving insertion order
    grouped: dict[str, list[dict]] = {}
    for story in stories:
        theme = story.get("theme", "Other")
        grouped.setdefault(theme, []).append(story)

    lines = ["[Global Macro Intelligence Report]", ""]
    for theme, items in grouped.items():
        icon = _THEME_ICON.get(theme, "📌")
        lines.append(f"{icon} {theme}")
        for item in items:
            imp_icon = _IMPORTANCE_ICON.get(item.get("importance", "medium"), "🟡")
            headline = item.get("headline", "")
            summary = item.get("summary", "")
            lines.append(f"  {imp_icon} {headline}")
            lines.append(f"     {summary}")
        lines.append("")

    return "\n".join(lines).rstrip()


def run():
    print("Fetching RSS feeds...")
    articles = fetch_articles()
    print(f"  {len(articles)} articles collected.")

    print("Analyzing with Gemma 4 via Ollama...")
    stories = analyze(articles)

    report = _format_report(stories)
    print("\n--- Report Preview ---")
    print(report)
    print("----------------------\n")

    print("Sending KakaoTalk notification...")
    send_message(report)
    print("Done.")


if __name__ == "__main__":
    run()
