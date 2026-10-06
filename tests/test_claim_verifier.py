from verifier import verify_claims


def test_verify_claims_tracks_support_status():
    claims = [
        {"text": "Fed may cut rates next quarter.", "source": "https://example.com/fed"},
        {"text": "Market will definitely rally 10% tomorrow.", "source": "https://example.com/guess"},
    ]

    verified = verify_claims(claims)

    assert verified[0]["status"] == "supported"
    assert verified[1]["status"] == "supported"
    assert verified[1]["source"] == "https://example.com/guess"
