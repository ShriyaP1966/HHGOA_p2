from app.chain import ChainUnavailable, InsufficientFunds, TransactionFailed


def test_home(client):
    assert client.get("/").json() == {"message": "Sepolia Sentiment API is working"}


def test_health_needs_no_blockchain(client):
    body = client.get("/health").json()
    assert body == {"status": "ok", "blockchain_configured": False}


def test_analyze_without_blockchain(client):
    r = client.post("/analyze", json={"text": "This is an excellent result"})
    assert r.status_code == 200
    body = r.json()
    assert body["sentiment"] == "positive"
    assert body["blockchain"] == "not_requested"
    assert body["contract_address"].startswith("0x")


def test_analyze_strips_text(client):
    r = client.post("/analyze", json={"text": "  great  "})
    assert r.json()["text"] == "great"


def test_whitespace_only_text_rejected(client):
    r = client.post("/analyze", json={"text": "   "})
    assert r.status_code == 400


def test_empty_text_rejected(client):
    assert client.post("/analyze", json={"text": ""}).status_code == 422


def test_text_too_long_rejected(client):
    assert client.post("/analyze", json={"text": "a" * 1001}).status_code == 422


def test_missing_field_rejected(client):
    assert client.post("/analyze", json={}).status_code == 422


def test_wrong_type_rejected(client):
    assert client.post("/analyze", json={"text": 123}).status_code == 422


def test_malformed_json_rejected(client):
    r = client.post("/analyze", content="{", headers={"Content-Type": "application/json"})
    assert r.status_code == 422


# --- blockchain writes -------------------------------------------------------


def test_write_disabled_without_api_key_config(client, chain):
    r = client.post("/analyze", json={"text": "great", "save_to_blockchain": True})
    assert r.status_code == 503
    assert chain.saved == []


def test_write_requires_api_key(client, chain, write_enabled):
    r = client.post("/analyze", json={"text": "great", "save_to_blockchain": True})
    assert r.status_code == 401

    r = client.post(
        "/analyze",
        json={"text": "great", "save_to_blockchain": True},
        headers={"X-API-Key": "wrong"},
    )
    assert r.status_code == 401
    assert chain.saved == []


def test_write_success(client, chain, write_enabled):
    r = client.post(
        "/analyze",
        json={"text": "great", "save_to_blockchain": True},
        headers=write_enabled,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["blockchain"] == "saved"
    assert body["transaction_hash"] == "0xabc"
    assert body["etherscan_url"].endswith("0xabc")
    assert chain.saved == [("great", "positive")]


def test_write_rate_limited(client, chain, write_enabled, monkeypatch):
    monkeypatch.setenv("WRITE_RATE_LIMIT", "2")
    payload = {"text": "great", "save_to_blockchain": True}

    assert client.post("/analyze", json=payload, headers=write_enabled).status_code == 200
    assert client.post("/analyze", json=payload, headers=write_enabled).status_code == 200
    r = client.post("/analyze", json=payload, headers=write_enabled)
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) >= 1


def test_rate_limit_does_not_affect_plain_analysis(client, monkeypatch):
    monkeypatch.setenv("WRITE_RATE_LIMIT", "1")
    for _ in range(5):
        assert client.post("/analyze", json={"text": "great"}).status_code == 200


def test_write_no_funds(client, chain, write_enabled):
    chain.error = InsufficientFunds("no gas")
    r = client.post(
        "/analyze",
        json={"text": "great", "save_to_blockchain": True},
        headers=write_enabled,
    )
    assert r.status_code == 402


def test_write_failure_hides_internals(client, chain, write_enabled):
    chain.error = TransactionFailed("secret rpc url https://example/key123")
    r = client.post(
        "/analyze",
        json={"text": "great", "save_to_blockchain": True},
        headers=write_enabled,
    )
    assert r.status_code == 502
    assert "key123" not in r.text


def test_write_without_chain_config(client, write_enabled):
    # No SEPOLIA_* variables set and get_client not patched.
    from app import chain as chain_module

    chain_module.get_client.cache_clear()
    r = client.post(
        "/analyze",
        json={"text": "great", "save_to_blockchain": True},
        headers=write_enabled,
    )
    assert r.status_code == 503


# --- /record -----------------------------------------------------------------


def test_record(client, chain):
    chain.saved.append(("hello", "neutral"))
    r = client.get("/record")
    assert r.status_code == 200
    assert r.json() == {"text": "hello", "sentiment": "neutral"}


def test_record_read_failure(client, chain):
    chain.error = ChainUnavailable("down")
    assert client.get("/record").status_code == 502


def test_record_without_chain_config(client):
    from app import chain as chain_module

    chain_module.get_client.cache_clear()
    assert client.get("/record").status_code == 503
