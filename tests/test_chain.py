from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from eth_account import Account

from app.chain import (
    BlockchainClient,
    ChainNotConfigured,
    ChainUnavailable,
    InsufficientFunds,
    TransactionFailed,
)
from app.config import DEFAULT_CONTRACT_ADDRESS, Settings

# Throwaway key used only for these tests; it controls nothing.
TEST_KEY = "0x" + "11" * 32


def make_settings(**overrides):
    values = dict(
        rpc_url="http://localhost:8545",
        private_key=TEST_KEY,
        contract_address=DEFAULT_CONTRACT_ADDRESS,
        api_key="k",
        write_rate_limit=5,
        write_rate_window=60,
    )
    values.update(overrides)
    return Settings(**values)


def make_client(w3=None):
    w3 = w3 or MagicMock()
    w3.is_connected.return_value = True
    w3.eth.chain_id = 11155111
    w3.eth.get_code.return_value = b"\x60\x80"
    w3.eth.get_balance.return_value = 10**18
    client = BlockchainClient(make_settings(), w3=w3)
    client.account = MagicMock(address=Account.from_key(TEST_KEY).address)
    return client, w3


def test_not_configured():
    with pytest.raises(ChainNotConfigured):
        BlockchainClient(make_settings(rpc_url="", private_key=""))


def test_construction_makes_no_network_calls():
    w3 = MagicMock()
    BlockchainClient(make_settings(), w3=w3)
    w3.is_connected.assert_not_called()


def test_wrong_network_rejected():
    client, w3 = make_client()
    w3.eth.chain_id = 1
    with pytest.raises(ChainUnavailable):
        client.read_record()


def test_not_connected_rejected():
    client, w3 = make_client()
    w3.is_connected.return_value = False
    with pytest.raises(ChainUnavailable):
        client.read_record()


def test_missing_contract_rejected():
    client, w3 = make_client()
    w3.eth.get_code.return_value = b""
    with pytest.raises(ChainUnavailable):
        client.read_record()


def test_read_record():
    client, _ = make_client()
    client.contract = MagicMock()
    client.contract.functions.getRecord.return_value.call.return_value = ("hi", "positive")
    assert client.read_record() == ("hi", "positive")


def test_read_failure_wrapped():
    client, _ = make_client()
    client.contract = MagicMock()
    client.contract.functions.getRecord.return_value.call.side_effect = RuntimeError("boom")
    with pytest.raises(ChainUnavailable):
        client.read_record()


def test_save_without_funds():
    client, w3 = make_client()
    w3.eth.get_balance.return_value = 0
    with pytest.raises(InsufficientFunds):
        client.save_record("hi", "positive")


def test_save_success_uses_pending_nonce():
    client, w3 = make_client()
    client.contract = MagicMock()
    tx_hash = bytes.fromhex("ab" * 32)
    w3.eth.send_raw_transaction.return_value = tx_hash
    w3.eth.wait_for_transaction_receipt.return_value = SimpleNamespace(status=1, blockNumber=7)
    client.account.sign_transaction.return_value = SimpleNamespace(raw_transaction=b"raw")

    result = client.save_record("hi", "positive")

    assert result["transaction_hash"] == "0x" + "ab" * 32
    assert result["block_number"] == 7
    assert result["etherscan_url"].endswith("ab" * 32)
    w3.eth.get_transaction_count.assert_called_once_with(client.account.address, "pending")


def test_reverted_transaction():
    client, w3 = make_client()
    client.contract = MagicMock()
    w3.eth.send_raw_transaction.return_value = bytes(32)
    w3.eth.wait_for_transaction_receipt.return_value = SimpleNamespace(status=0, blockNumber=7)
    client.account.sign_transaction.return_value = SimpleNamespace(raw_transaction=b"raw")
    with pytest.raises(TransactionFailed):
        client.save_record("hi", "positive")


def test_send_error_wrapped():
    client, w3 = make_client()
    client.contract = MagicMock()
    w3.eth.send_raw_transaction.side_effect = RuntimeError("rpc exploded")
    client.account.sign_transaction.return_value = SimpleNamespace(raw_transaction=b"raw")
    with pytest.raises(TransactionFailed):
        client.save_record("hi", "positive")
