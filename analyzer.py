import json
import os
import requests
import ollama

SYSTEM_PROMPT = """\
You are a Chief Market Strategist at a top-tier global investment bank. \
You will receive up to 20 raw financial news articles as a JSON array.

Your task: identify the 5 most critical stories that materially affect \
Tech/AI, Biotech, or Macro growth themes. Synthesize each into one authoritative sentence.

Respond ONLY with a valid JSON array of exactly 5 objects. No markdown, no codeblocks.
Each object must conform to this schema exactly:
{
  "theme": "Tech/AI" | "Biotech" | "Macro",
  "importance": "high" | "medium",
  "headline": "the original or a tightened version of the article headline",
  "summary": "One authoritative sentence synthesising the market-moving implication."
}\
"""


def analyze(articles: list[dict]) -> list[dict]:
    payload = json.dumps(articles, ensure_ascii=False)
    api_key = os.getenv("GEMINI_API_KEY")

    # Cloud Execution Pathway (GitHub Actions Cloud Container)
    if api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT}\n\nArticles:\n{payload}"}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(raw_text)
        except Exception as e:
            print(f"Cloud gateway inference failure: {e}")
            return []

    # Local Hardware Fallback Pathway (Native MacBook / Ollama)
    try:
        response = ollama.chat(
            model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": payload},
            ],
            format="json",
            options={"keep_alive": 0},
        )
        return json.loads(response["message"]["content"].strip())
    except Exception as e:
        print(f"Local hardware loop failure: {e}")
        return []
