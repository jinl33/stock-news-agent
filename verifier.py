def verify_claims(claims: list[dict]) -> list[dict]:
    verified = []
    for claim in claims:
        text = claim.get("text") or ""
        source = claim.get("source") or "unknown"
        status = "supported" if text and source else "unsupported"
        verified.append({
            "text": text,
            "status": status,
            "source": source,
        })
    return verified
