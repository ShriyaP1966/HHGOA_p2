
import os
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

# Load environment variables
load_dotenv()

rpc_url = os.getenv("SEPOLIA_RPC_URL")
private_key = os.getenv("SEPOLIA_PRIVATE_KEY")

if not rpc_url or not private_key:
    raise ValueError("Missing RPC URL or private key in .env")

# Connect to Sepolia
w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected():
    raise ConnectionError("Could not connect to Sepolia")

if w3.eth.chain_id != 11155111:
    raise RuntimeError("Wrong network. Please connect to Sepolia.")

# Load the wallet locally
account = Account.from_key(private_key)

# Existing deployed contract address
contract_address = Web3.to_checksum_address(
    "0x39E7cccCA9A0AC85F19Bb1DE7F88D48bA7c5FF19"
)

# ABI for saveRecord()
abi = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "_text",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "_sentiment",
                "type": "string"
            }
        ],
        "name": "saveRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

# Test record
text_to_save = "Hacker House Goa blockchain integration test"
sentiment_to_save = "positive"

print("Connected to Sepolia")
print("Wallet address:", account.address)
print("Contract address:", contract_address)

# Check that the deployed address contains contract code
if w3.eth.get_code(contract_address) in (b"", b"\x00"):
    raise RuntimeError("No contract code found at this address")

# Check wallet balance
balance = w3.eth.get_balance(account.address)
print("Sepolia ETH balance:", w3.from_wei(balance, "ether"))

if balance == 0:
    raise RuntimeError("Wallet has no Sepolia ETH for gas")

# Build the transaction
nonce = w3.eth.get_transaction_count(account.address)

function_call = contract.functions.saveRecord(
    text_to_save,
    sentiment_to_save
)

transaction = function_call.build_transaction({
    "from": account.address,
    "nonce": nonce,
    "chainId": 11155111,
    "gas": function_call.estimate_gas({
        "from": account.address
    }) + 10000,
    "gasPrice": w3.eth.gas_price
})

# Sign and submit the transaction
signed_tx = account.sign_transaction(transaction)
tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

print("Transaction submitted:", tx_hash.hex())
print("Waiting for confirmation...")

# Wait for the blockchain receipt
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print("Transaction status:", receipt.status)
print("Block number:", receipt.blockNumber)

if receipt.status == 1:
    print("Record saved successfully!")
    print("Saved text:", text_to_save)
    print("Saved sentiment:", sentiment_to_save)
    print(
        "View on Etherscan: "
        + "https://sepolia.etherscan.io/tx/"
        + tx_hash.hex()
    )
else:
    print("Transaction failed. Check the transaction on Etherscan.")
