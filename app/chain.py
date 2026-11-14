"""Sepolia client for the AIRecord contract. Connects lazily, on first use."""

import threading
from functools import lru_cache

from eth_account import Account
from web3 import Web3

from app.abi import ABI
from app.config import SEPOLIA_CHAIN_ID, Settings, get_settings

ETHERSCAN_TX_URL = "https://sepolia.etherscan.io/tx/"
RECEIPT_TIMEOUT_SECONDS = 120


class ChainError(Exception):
    """Base class for blockchain failures."""


class ChainNotConfigured(ChainError):
    pass


class ChainUnavailable(ChainError):
    pass


class InsufficientFunds(ChainError):
    pass


class TransactionFailed(ChainError):
    pass


def _to_0x_hex(value) -> str:
    text = value.hex()
    return text if text.startswith("0x") else "0x" + text


class BlockchainClient:
    # Serialises nonce selection + sending so concurrent requests do not
    # reuse a nonce. The (slow) receipt wait happens outside the lock.
    _send_lock = threading.Lock()

    def __init__(self, settings: Settings, w3: Web3 | None = None):
        if not settings.chain_configured:
            raise ChainNotConfigured("SEPOLIA_RPC_URL / SEPOLIA_PRIVATE_KEY not set")

        self.w3 = w3 or Web3(Web3.HTTPProvider(settings.rpc_url, request_kwargs={"timeout": 30}))
        self.account = Account.from_key(settings.private_key)
        self.contract_address = Web3.to_checksum_address(settings.contract_address)
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=ABI)
        self._verified = False

    def _ensure_ready(self) -> None:
        """Check network and contract once, on first use (not at import time)."""
        if self._verified:
            return
        try:
            if not self.w3.is_connected():
                raise ChainUnavailable("Could not connect to the Sepolia RPC endpoint")
            if self.w3.eth.chain_id != SEPOLIA_CHAIN_ID:
                raise ChainUnavailable("RPC endpoint is not Ethereum Sepolia")
            if not self.w3.eth.get_code(self.contract_address):
                raise ChainUnavailable("No contract deployed at the configured address")
        except ChainError:
            raise
        except Exception as exc:
            raise ChainUnavailable("Could not reach the Sepolia network") from exc
        self._verified = True

    def read_record(self) -> tuple[str, str]:
        self._ensure_ready()
        try:
            text, sentiment = self.contract.functions.getRecord().call()
        except Exception as exc:
            raise ChainUnavailable("Could not read the Sepolia contract") from exc
        return text, sentiment

    def save_record(self, text: str, sentiment: str) -> dict:
        self._ensure_ready()
        try:
            if self.w3.eth.get_balance(self.account.address) == 0:
                raise InsufficientFunds("Wallet has no Sepolia ETH for gas")

            call = self.contract.functions.saveRecord(text, sentiment)
            gas = call.estimate_gas({"from": self.account.address}) + 10_000

            with self._send_lock:
                tx = call.build_transaction(
                    {
                        "from": self.account.address,
                        "nonce": self.w3.eth.get_transaction_count(self.account.address, "pending"),
                        "chainId": SEPOLIA_CHAIN_ID,
                        "gas": gas,
                        "gasPrice": self.w3.eth.gas_price,
                    }
                )
                signed = self.account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)

            receipt = self.w3.eth.wait_for_transaction_receipt(
                tx_hash, timeout=RECEIPT_TIMEOUT_SECONDS
            )
        except ChainError:
            raise
        except Exception as exc:
            raise TransactionFailed(
                "Blockchain transaction failed. Check RPC, balance and transaction status."
            ) from exc

        if receipt.status != 1:
            raise TransactionFailed("Blockchain transaction reverted")

        tx_hex = _to_0x_hex(tx_hash)
        return {
            "transaction_hash": tx_hex,
            "block_number": receipt.blockNumber,
            "transaction_status": receipt.status,
            "etherscan_url": ETHERSCAN_TX_URL + tx_hex,
        }


@lru_cache(maxsize=1)
def get_client() -> BlockchainClient:
    return BlockchainClient(get_settings())
