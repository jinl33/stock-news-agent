import json
import os
import re

import ollama
import requests

from config import TOP_STORY_COUNT
from market import get_market_snapshot
from portfolio import infer_portfolio_impact
from retriever import retrieve_context

SYSTEM_PROMPT = f"""\
You are an expert bilingual (English/Korean) financial analyst managing a high-net-worth portfolio. 
Use only the supplied context for factual claims. Do not invent numbers or sources. 
Review the provided market news and select the top {TOP_STORY_COUNT} most critical stories. 

SECTOR RULES:
- MAIN-SECTORS: "Macro", "Tech/AI", "Space", and "E-Commerce".
- SUB-SECTORS: Biotech and any Research Breakthroughs
- PORTFOLIO TARGETS: Prioritize any news affecting Palantir (PLTR), SpaceX, Apple (AAPL), Amazon (AMZN), and Microsoft (MSFT).

For each story, provide a comprehensive, institutional-grade analysis in BOTH English and Korean.
You MUST respond strictly with a valid JSON array. Follow this exact structure:
[
  {{
    "theme": "Portfolio Focus",
    "ticker": "PLTR",
    "importance": "high",
    "headline": "팔란티어, 대규모 국방 계약 체결",
    "analysis": "이번 계약은 정부 소프트웨어 분야에서 팔란티어의 지배력을 공고히 하며...",
    "source": "https://finance.yahoo.com/news/..."
  }}
]
"""

def analyze(stock_data: list[dict]) -> list[dict]:
    # Feed the top configured articles to protect the local model's context threshold
    payload = json.dumps(stock_data[:TOP_STORY_COUNT], ensure_ascii=False)
    context_items = []
    for item in stock_data[:TOP_STORY_COUNT]:
        event_text = (item.get("headline") or "") + " " + (item.get("summary") or "")
        if event_text.strip():
            context_items.extend(retrieve_context(event_text, max_results=3))

    market_context = get_market_snapshot(["SPY", "QQQ", "^TNX", "^VIX"])
    portfolio_context = infer_portfolio_impact(
        " ".join((item.get("headline") or "") for item in stock_data[:TOP_STORY_COUNT]),
        ["MSFT", "AAPL", "AMZN", "PLTR"],
    )
    api_key = os.getenv("GEMINI_API_KEY")
    use_local_llm = os.getenv("USE_LOCAL_LLM", "false").strip().lower() in {"1", "true", "yes", "on"}
    raw_output = ""

    # Default to the GitHub Actions cloud path; local Ollama is only for explicit local runs.
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nContext Data:\n{json.dumps({'articles': stock_data[:TOP_STORY_COUNT], 'retrieved_context': context_items, 'market_context': market_context, 'portfolio_context': portfolio_context}, ensure_ascii=False)}\n\nInput Data:\n{payload}"}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            raw_output = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Cloud gateway inference failure: {e}")
            return []
    elif use_local_llm:
        try:
            response = ollama.chat(
                model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": json.dumps({
                        "articles": stock_data[:TOP_STORY_COUNT],
                        "retrieved_context": context_items,
                        "market_context": market_context,
                        "portfolio_context": portfolio_context,
                    }, ensure_ascii=False)}
                ],
                format="json",
                options={"keep_alive": 0}
            )
            raw_output = response["message"]["content"].strip()
        except Exception as e:
            print(f"Local hardware loop failure: {e}")
            return []
    else:
        print("No GEMINI_API_KEY configured and local Ollama is disabled (USE_LOCAL_LLM=false). Skipping synthesis.")
        return []

    print("\n--- RAW LLM OUTPUT (Debug) ---")
    print(raw_output)
    print("------------------------------\n")

    try:
        parsed_data = None
        
        # Attempt direct structural load
        try:
            parsed_data = json.loads(raw_output)
        except json.JSONDecodeError:
            match = re.search(r'\[.*\]', raw_output, re.DOTALL)
            if match:
                parsed_data = json.loads(match.group(0))

        # Handle dictionary envelopes like {"analysis": [...]} or {"top_stories": [...]}
        if isinstance(parsed_data, dict):
            for val in parsed_data.values():
                if isinstance(val, list):
                    parsed_data = val
                    break

        # Normalize and construct verified payload elements
        if isinstance(parsed_data, list):
            normalized_list = []
            for item in parsed_data:
                if isinstance(item, str):
                    item = {"headline_en": item, "headline_ko": item}
                
                if isinstance(item, dict):
                    normalized_item = {
                        "theme": item.get("theme", "Macro"),
                        "ticker": item.get("ticker", "None"),
                        "importance": item.get("importance", "medium"),
                        "headline": item.get("headline", item.get("headline_ko", "제목 없음")),
                        "analysis": item.get("analysis", item.get("analysis_ko", "분석 내용이 제공되지 않았습니다.")),
                        "source": item.get("source", "출처 미상") # <-- 새로 추가된 부분
                    }
                    normalized_list.append(normalized_item)
            return normalized_list
        
        return []
        
    except Exception as e:
        print(f"Error normalizing JSON payload: {e}")
        return []