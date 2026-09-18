# Stock News Agent

A local-first macro intelligence agent that fetches financial news, stores it in a persistent memory store, retrieves relevant historical and market context, and produces a compact macro + portfolio report.

## Features

- RSS-based news fetching
- deduplication and event clustering
- local SQLite-backed article memory
- lexical + semantic retrieval
- market snapshot context
- portfolio impact inference
- report generation for Kakao output
- local Ollama-compatible embedding fallback

## Quick start

This project defaults to the cloud Gemini workflow used by GitHub Actions, so it does not require a local LLM on a memory-constrained laptop. Local Ollama is only used if you explicitly set `USE_LOCAL_LLM=true`.

1. Copy the environment template:

   ```bash
   cp .env.example .env
   ```

2. Fill in the required values in `.env`.
   - `GEMINI_API_KEY` should be set in GitHub Actions secrets or your local `.env`.
   - Leave `USE_LOCAL_LLM=false` unless you truly want a local Ollama run.

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the agent:

   ```bash
   python agent.py --skip-send
   ```

   To send to KakaoTalk:

   ```bash
   python agent.py
   ```

## Scheduling

You can run the agent on a cron schedule or via GitHub Actions. A typical cron entry looks like:

```bash
0 9 * * 1-5 cd /path/to/stock-news-agent && python agent.py
```

## Structure

- `agent.py`: orchestration entrypoint
- `analyzer.py`: grounded synthesis layer
- `fetcher.py`: RSS fetcher
- `memory.py`: persistent deduped article archive
- `retriever.py`: lexical retrieval layer
- `vector_store.py`: local vector/embedding store
- `hybrid_retrieval.py`: hybrid semantic + lexical retrieval
- `market.py`: market snapshot helpers
- `portfolio.py`: portfolio-impact heuristics
- `report_builder.py`: final report formatter
- `notifier.py`: KakaoTalk delivery
- `verifier.py`: source-linked claim verification
