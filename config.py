import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_AUTH_CODE = os.getenv("KAKAO_AUTH_CODE")

KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "https://example.com/oauth")
KAKAO_TOKEN_FILE = "kakao_tokens.json"

NEWS_FEEDS = [
    "https://finance.yahoo.com/news/rssindex",
    "https://www.investing.com/rss/news_25.rss",
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
]