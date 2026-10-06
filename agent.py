import argparse

from fetcher import fetch_articles
from analyzer import analyze
from memory import cluster_articles, save_articles
from report_builder import build_report
from notifier import send_message

_THEME_ICON = {
    "Tech/AI": "💻",
    "Biotech": "🧬",
    "Macro": "🌐",
}
_IMPORTANCE_ICON = {"high": "🔴", "medium": "🟡"}

def _format_report(stories: list[dict]) -> str:
    return build_report(stories)

def run():
    print("Fetching RSS feeds...")
    stories = fetch_articles()
    save_articles(stories)

    clustered = cluster_articles(stories)
    if clustered:
        print(f"Detected {len(clustered)} clustered macro events.")
        stories = [event["articles"][0] for event in clustered]

    print("Analyzing...")
    analyzed = analyze(stories)

    if not analyzed:
        print("Inference failed or no actionable news found. Aborting alert.")
        return

    market_snapshot = {}
    try:
        from market import get_market_snapshot
        market_snapshot = get_market_snapshot(["SPY", "QQQ", "^TNX", "^VIX"])
    except Exception:
        market_snapshot = {}

    try:
        from portfolio import infer_portfolio_impact
        portfolio_context = infer_portfolio_impact(
            " ".join((item.get("headline") or "") for item in analyzed),
            ["MSFT", "AAPL", "AMZN", "PLTR"],
        )
    except Exception:
        portfolio_context = []

    report = build_report(analyzed, market_snapshot=market_snapshot, portfolio_context=portfolio_context)
    print("\n--- Report Preview ---")
    print(report)
    print("----------------------\n")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the global macro + portfolio intelligence agent.")
    parser.add_argument("--skip-send", action="store_true", help="Generate the report without sending to KakaoTalk.")
    args = parser.parse_args()

    report = run()
    if args.skip_send:
        print("Report generated without sending to KakaoTalk.")
        return

    if report:
        print("Sending KakaoTalk notification...")
        send_message(report)
        print("Done.")


if __name__ == "__main__":
    main()