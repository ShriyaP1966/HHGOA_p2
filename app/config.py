"""Runtime configuration, read from environment variables (or a local .env)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

SEPOLIA_CHAIN_ID = 11155111
DEFAULT_CONTRACT_ADDRESS = "0x39E7cccCA9A0AC85F19Bb1DE7F88D48bA7c5FF19"


@dataclass(frozen=True)
class Settings:
    rpc_url: str
    private_key: str
    contract_address: str
    api_key: str
    write_rate_limit: int
    write_rate_window: int

    @property
    def chain_configured(self) -> bool:
        return bool(self.rpc_url and self.private_key)


def _int_env(name: str, default: int) -> int:
    """Read a positive integer; fall back to the default if unset, blank or invalid."""
    try:
        value = int(os.getenv(name, "").strip())
    except ValueError:
        return default
    return value if value > 0 else default


def get_settings() -> Settings:
    """Read settings fresh from the environment so tests can override them."""
    return Settings(
        rpc_url=os.getenv("SEPOLIA_RPC_URL", "").strip(),
        private_key=os.getenv("SEPOLIA_PRIVATE_KEY", "").strip(),
        # `or` (not a getenv default) so a blank CONTRACT_ADDRESS also falls back.
        contract_address=os.getenv("CONTRACT_ADDRESS", "").strip() or DEFAULT_CONTRACT_ADDRESS,
        api_key=os.getenv("API_KEY", "").strip(),
        write_rate_limit=_int_env("WRITE_RATE_LIMIT", 5),
        write_rate_window=_int_env("WRITE_RATE_WINDOW_SECONDS", 60),
    )
