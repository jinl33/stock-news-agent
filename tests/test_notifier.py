import json

import notifier


def test_redirect_uri_comes_from_config(monkeypatch):
    monkeypatch.setattr(notifier, "KAKAO_REDIRECT_URI", "https://example.com/custom")
    assert notifier.KAKAO_REDIRECT_URI == "https://example.com/custom"


def test_initial_token_payload_hides_secrets(monkeypatch, capsys):
    captured = {}

    class DummyResponse:
        status_code = 200

        def json(self):
            return {"access_token": "token"}

        def raise_for_status(self):
            pass

    def fake_post(url, data):
        captured["payload"] = data
        return DummyResponse()

    monkeypatch.setattr(notifier.requests, "post", fake_post)
    monkeypatch.setattr(notifier, "KAKAO_REST_API_KEY", "secret-api-key")
    monkeypatch.setattr(notifier, "KAKAO_CLIENT_SECRET", "secret-client")
    monkeypatch.setattr(notifier, "KAKAO_AUTH_CODE", "secret-code")

    notifier._request_initial_tokens()

    assert captured["payload"]["client_id"] == "secret-api-key"
    assert captured["payload"]["code"] == "secret-code"
    out = capsys.readouterr().out
    assert "secret-api-key" not in out
    assert "secret-client" not in out
    assert "secret-code" not in out
