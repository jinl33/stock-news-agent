import json
import os
import requests
from config import KAKAO_REST_API_KEY, KAKAO_AUTH_CODE, KAKAO_TOKEN_FILE, KAKAO_REDIRECT_URI

_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

def _load_tokens() -> dict | None:
    if os.path.exists(KAKAO_TOKEN_FILE):
        with open(KAKAO_TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def _save_tokens(tokens: dict) -> None:
    with open(KAKAO_TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def _request_initial_tokens() -> dict:
    resp = requests.post(
        _TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": KAKAO_AUTH_CODE,
        },
    )
    resp.raise_for_status()
    tokens = resp.json()
    _save_tokens(tokens)
    return tokens

def _refresh_tokens(refresh_token: str) -> dict:
    resp = requests.post(
        _TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": KAKAO_REST_API_KEY,
            "refresh_token": refresh_token,
        },
    )
    resp.raise_for_status()
    new_tokens = resp.json()
    if "refresh_token" not in new_tokens:
        existing = _load_tokens() or {}
        new_tokens["refresh_token"] = existing.get("refresh_token", refresh_token)
    _save_tokens(new_tokens)
    return new_tokens

def _get_access_token() -> str:
    tokens = _load_tokens()
    if tokens is None:
        tokens = _request_initial_tokens()
    else:
        tokens = _refresh_tokens(tokens["refresh_token"])
    return tokens["access_token"]

def send_message(text: str) -> None:
    access_token = _get_access_token()
    template = {
        "object_type": "text",
        "text": text,
        "link": {"web_url": "", "mobile_web_url": ""},
    }
    resp = requests.post(
        _SEND_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        data={"template_object": json.dumps(template)},
    )
    resp.raise_for_status()
    result = resp.json()
    if result.get("result_code") != 0:
        raise RuntimeError(f"KakaoTalk send failed: {result}")