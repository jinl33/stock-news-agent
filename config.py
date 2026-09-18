import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
USE_LOCAL_LLM = os.getenv("USE_LOCAL_LLM", "false").strip().lower() in {"1", "true", "yes", "on"}
TOP_STORY_COUNT = int(os.getenv("TOP_STORY_COUNT", "5"))

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_AUTH_CODE = os.getenv("KAKAO_AUTH_CODE")

KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "https://example.com/oauth")
KAKAO_TOKEN_FILE = "kakao_tokens.json"

NEWS_FEEDS = {
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Investing.com": "https://www.investing.com/rss/news_25.rss",
    "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
}