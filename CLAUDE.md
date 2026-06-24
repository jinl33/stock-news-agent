# Global Macro Intelligence Agent

Automated pipeline that aggregates RSS financial news, synthesises the top 5 macro stories with a local LLM (Gemma 4 via Ollama, with a Gemini cloud fallback), and delivers a themed report to KakaoTalk "Send to Me".

## Module Layout

| File | Role |
|------|------|
| `config.py` | Loads all env vars via python-dotenv; defines `NEWS_FEEDS` and Kakao constants |
| `fetcher.py` | Parses RSS feeds with feedparser, strips HTML via BeautifulSoup, returns the 20 most recent articles |
| `analyzer.py` | Sends articles to Gemma 4 (Ollama local) or Gemini 2.5 Flash (cloud); returns 5 thematic JSON stories |
| `notifier.py` | Manages Kakao OAuth tokens (file cache → refresh → initial grant) and sends a text memo |
| `agent.py` | Orchestrator: fetch → analyze → format by theme → notify |

## Environment Variables (`.env`)

```
# LLM
OLLAMA_MODEL=gemma4:e4b          # default local model
GEMINI_API_KEY=                  # set to enable cloud pathway (GitHub Actions etc.)

# KakaoTalk
KAKAO_REST_API_KEY=
KAKAO_AUTH_CODE=                 # one-time code from browser redirect
KAKAO_REDIRECT_URI=https://example.com/oauth   # must match app settings
```

## Inference Pathway

1. If `GEMINI_API_KEY` is set → Gemini 2.5 Flash via REST (cloud/CI).
2. Otherwise → Gemma 4 via local Ollama (`gemma4:e4b`).

## Token Flow

1. First run: `KAKAO_AUTH_CODE` is exchanged for access + refresh tokens, saved to `kakao_tokens.json`.
2. Subsequent runs: refresh token is used to obtain a fresh access token before each send.
3. `kakao_tokens.json` is gitignored and must never be committed.

## RSS Feeds

Defined in `config.NEWS_FEEDS`:
- Yahoo Finance Markets RSS
- Investing.com Markets RSS
- WSJ Markets RSS

## Running

```bash
pip install -r requirements.txt
python agent.py
```
