
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

rpc_url = os.getenv("SEPOLIA_RPC_URL")
w3 = Web3(Web3.HTTPProvider(rpc_url))

contract_address = Web3.to_checksum_address(
    "0x39E7cccCA9A0AC85F19Bb1DE7F88D48bA7c5FF19"
)

abi = [
    {
        "inputs": [],
        "name": "getRecord",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "string", "name": "", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "latestRecord",
        "outputs": [
            {"internalType": "string", "name": "text", "type": "string"},
            {"internalType": "string", "name": "sentiment", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

contract = w3.eth.contract(
    address=contract_address,
    abi=abi
)

print("Connected to AIRecord contract!")
print("Latest saved record:", contract.functions.getRecord().call())
