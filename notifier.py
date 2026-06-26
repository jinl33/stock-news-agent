import json
import os
import requests
from config import KAKAO_REST_API_KEY, KAKAO_AUTH_CODE, KAKAO_TOKEN_FILE, KAKAO_CLIENT_SECRET

_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_SEND_URL = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
_REDIRECT_URI = "https://example.com/oauth"

def _load_tokens() -> dict | None:
    if os.path.exists(KAKAO_TOKEN_FILE):
        with open(KAKAO_TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def _save_tokens(tokens: dict) -> None:
    with open(KAKAO_TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

def _request_initial_tokens() -> dict:
    payload = {
        "grant_type": "authorization_code",
        "client_id": KAKAO_REST_API_KEY,
        "client_secret": KAKAO_CLIENT_SECRET,
        "redirect_uri": _REDIRECT_URI,
        "code": KAKAO_AUTH_CODE,
    }
    
    print("\n--- DEBUG PAYLOAD ---")
    print(f"API Key: {KAKAO_REST_API_KEY}")
    print(f"Client Secret: {KAKAO_CLIENT_SECRET}")
    print(f"Auth Code: {KAKAO_AUTH_CODE}")
    print("---------------------\n")
    
    resp = requests.post(_TOKEN_URL, data=payload)
    
    if resp.status_code != 200:
        print("\n=== KAKAO API ERROR ===")
        print(resp.text)
        print("=======================\n")
        
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
            "client_secret": KAKAO_CLIENT_SECRET,
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

def get_friend_uuids(access_token: str) -> list[str]:
    url = "https://kapi.kakao.com/v1/api/talk/friends"
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        print(f"가족 목록 로드 실패 (권한 없음 또는 동의한 친구 없음): {resp.text}")
        return []
        
    elements = resp.json().get("elements", [])
    return [friend["uuid"] for friend in elements][:5]

def send_message(report: str):
    access_token = _get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    
    uuids = get_friend_uuids(access_token)
    
    paragraphs = report.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(current_chunk) + len(p) < 900:
            current_chunk += p + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = p + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
        
    me_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    friends_url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
    
    for i, chunk in enumerate(chunks):
        page_marker = f"[{i+1}/{len(chunks)}]\n" if len(chunks) > 1 else ""
        template = json.dumps({
            "object_type": "text",
            "text": page_marker + chunk,
            "link": {"web_url": "https://finance.yahoo.com"}
        }, ensure_ascii=False)
        
        # Send to me
        requests.post(me_url, headers=headers, data={"template_object": template}).raise_for_status()
        
        # Send to others
        if uuids:
            data_friends = {
                "receiver_uuids": json.dumps(uuids),
                "template_object": template
            }
            resp_friends = requests.post(friends_url, headers=headers, data=data_friends)
            if resp_friends.status_code != 200:
                print(f"가족 전송 실패: {resp_friends.text}")

        print(f"Message part {i+1}/{len(chunks)} sent successfully.")