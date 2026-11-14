import pytest
from fastapi.testclient import TestClient

from app import main


class FakeChain:
    """Stands in for BlockchainClient so no network access is needed."""

    def __init__(self):
        self.saved = []
        self.error = None

    def save_record(self, text, sentiment):
        if self.error:
            raise self.error
        self.saved.append((text, sentiment))
        return {
            "transaction_hash": "0xabc",
            "block_number": 123,
            "transaction_status": 1,
            "etherscan_url": "https://sepolia.etherscan.io/tx/0xabc",
        }

    def read_record(self):
        if self.error:
            raise self.error
        return self.saved[-1] if self.saved else ("", "")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("SEPOLIA_RPC_URL", "SEPOLIA_PRIVATE_KEY", "API_KEY", "CONTRACT_ADDRESS"):
        monkeypatch.delenv(name, raising=False)
    # Stop a developer's local .env from leaking into the tests.
    monkeypatch.setattr("app.config.load_dotenv", lambda *a, **k: None)
    main.write_limiter.reset()


@pytest.fixture
def chain(monkeypatch):
    fake = FakeChain()
    monkeypatch.setattr(main, "get_client", lambda: fake)
    return fake


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def write_enabled(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret")
    return {"X-API-Key": "secret"}
