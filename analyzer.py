import json
import os
import requests
import ollama
import re

SYSTEM_PROMPT = """\
You are an expert bilingual (English/Korean) financial analyst managing a high-net-worth portfolio. 
Review the provided market news and select the top 6 most critical stories. 

SECTOR RULES:
- FOCUS: "Macro", "Tech/AI", "Space", and "E-Commerce".
- PORTFOLIO TARGETS: Prioritize any news affecting Palantir (PLTR), SpaceX, Apple (AAPL), Amazon (AMZN), and Microsoft (MSFT).
- SUB-SECTORS: Biotech and Pharma.

For each story, provide a comprehensive, institutional-grade analysis in BOTH English and Korean.
You MUST respond strictly with a valid JSON array. Follow this exact structure:
[
  {
    "theme": "Portfolio Focus",
    "ticker": "PLTR",
    "headline_en": "Palantir secures major defense contract",
    "headline_ko": "팔란티어, 대규모 국방 계약 체결",
    "analysis_en": "This contract solidifies Palantir's dominance in government software, expanding their ARR and establishing a strong moat.",
    "analysis_ko": "이번 계약은 정부 소프트웨어 분야에서 팔란티어의 지배력을 공고히 하며, 연간 반복 매출(ARR)을 확대하고 강력한 해자를 구축합니다."
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
            # Fallback to regex extraction if wrapped in conversational text
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
                        # Fallback smoothly to old single-language keys if the model reverts layout shapes
                        "headline_en": item.get("headline_en", item.get("headline", "Untitled")),
                        "headline_ko": item.get("headline_ko", item.get("headline", "제목 없음")),
                        "analysis_en": item.get("analysis_en", item.get("summary", "No analysis provided.")),
                        "analysis_ko": item.get("analysis_ko", item.get("summary", "분석 내용이 제공되지 않았습니다."))
                    }
                    normalized_list.append(normalized_item)
            return normalized_list
        
        return []
        
    except Exception as e:
        print(f"Error normalizing JSON payload: {e}")
        return []