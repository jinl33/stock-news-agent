import json
import os
import requests
import ollama
import re

SYSTEM_PROMPT = """\
You are an expert bilingual (English/Korean) financial analyst managing a high-net-worth portfolio. 
Review the provided market news and select the top 6 most critical stories. 

SECTOR RULES:
- MAIN-SECTORS: "Macro", "Tech/AI", "Space", and "E-Commerce".
- SUB-SECTORS: Biotech and any Research Breakthroughs
- PORTFOLIO TARGETS: Prioritize any news affecting Palantir (PLTR), SpaceX, Apple (AAPL), Amazon (AMZN), and Microsoft (MSFT).

For each story, provide a comprehensive, institutional-grade analysis in BOTH English and Korean.
You MUST respond strictly with a valid JSON array. Follow this exact structure:
[
  {
    "theme": "Portfolio Focus",
    "ticker": "PLTR",
    "importance": "high",
    "headline": "팔란티어, 대규모 국방 계약 체결",
    "analysis": "이번 계약은 정부 소프트웨어 분야에서 팔란티어의 지배력을 공고히 하며...",
    "source": "https://finance.yahoo.com/news/..."
  }
]
"""

def analyze(stock_data: list[dict]) -> list[dict]:
    # Feed the top 10 articles to protect the local model's context threshold
    payload = json.dumps(stock_data[:10], ensure_ascii=False)
    api_key = os.getenv("GEMINI_API_KEY")
    raw_output = ""

    # Cloud Execution Pathway
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nInput Data:\n{payload}"}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            raw_output = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"Cloud gateway inference failure: {e}")
            return []
    
    # Local Hardware Pathway (Gemma 4)
    else:
        try:
            response = ollama.chat(
                model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": payload}
                ],
                format="json",
                options={"keep_alive": 0}
            )
            raw_output = response["message"]["content"].strip()
        except Exception as e:
            print(f"Local hardware loop failure: {e}")
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