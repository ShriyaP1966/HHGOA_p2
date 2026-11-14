from app.config import DEFAULT_CONTRACT_ADDRESS, get_settings


def test_defaults():
    s = get_settings()
    assert s.contract_address == DEFAULT_CONTRACT_ADDRESS
    assert (s.write_rate_limit, s.write_rate_window) == (5, 60)
    assert not s.chain_configured


def test_blank_contract_address_falls_back(monkeypatch):
    monkeypatch.setenv("CONTRACT_ADDRESS", "   ")
    assert get_settings().contract_address == DEFAULT_CONTRACT_ADDRESS


def test_invalid_numbers_fall_back(monkeypatch):
    monkeypatch.setenv("WRITE_RATE_LIMIT", "lots")
    monkeypatch.setenv("WRITE_RATE_WINDOW_SECONDS", "-5")
    s = get_settings()
    assert (s.write_rate_limit, s.write_rate_window) == (5, 60)


def test_chain_configured_needs_both_values(monkeypatch):
    monkeypatch.setenv("SEPOLIA_RPC_URL", "https://example.invalid")
    assert not get_settings().chain_configured
    monkeypatch.setenv("SEPOLIA_PRIVATE_KEY", "0x" + "11" * 32)
    assert get_settings().chain_configured
