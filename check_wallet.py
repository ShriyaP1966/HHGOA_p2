
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

load_dotenv()

private_key = os.getenv("SEPOLIA_PRIVATE_KEY")

if not private_key:
    print("Private key not found. Check your local .env file.")
else:
    account = Account.from_key(private_key)
    print("Wallet address:", account.address)

    w3 = Web3(Web3.HTTPProvider(os.getenv("SEPOLIA_RPC_URL")))
    print("Connected to Sepolia:", w3.is_connected())
    print("Chain ID:", w3.eth.chain_id if w3.is_connected() else "Unavailable")
