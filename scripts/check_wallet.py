"""Show the wallet address derived from SEPOLIA_PRIVATE_KEY and its Sepolia balance.

Run from the repo root:  python -m scripts.check_wallet
"""

from eth_account import Account
from web3 import Web3

from app.config import get_settings

settings = get_settings()

if not settings.private_key:
    print("Private key not found. Check your local .env file.")
else:
    account = Account.from_key(settings.private_key)
    print("Wallet address:", account.address)

    w3 = Web3(Web3.HTTPProvider(settings.rpc_url))
    connected = w3.is_connected()
    print("Connected to Sepolia:", connected)
    if connected:
        print("Chain ID:", w3.eth.chain_id)
        print("Balance (ETH):", w3.from_wei(w3.eth.get_balance(account.address), "ether"))
