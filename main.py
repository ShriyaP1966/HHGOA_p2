
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from web3 import Web3
from eth_account import Account

load_dotenv()

app = FastAPI(title="Hacker House AI API")

# Connect to Sepolia
rpc_url = os.getenv("SEPOLIA_RPC_URL")
private_key = os.getenv("SEPOLIA_PRIVATE_KEY")

if not rpc_url or not private_key:
    raise RuntimeError("Missing Sepolia settings in .env")

w3 = Web3(Web3.HTTPProvider(rpc_url))

if not w3.is_connected() or w3.eth.chain_id != 11155111:
    raise RuntimeError("Could not connect to Ethereum Sepolia")

account = Account.from_key(private_key)

# Existing deployed Sepolia contract
contract_address = Web3.to_checksum_address(
    "0x39E7cccCA9A0AC85F19Bb1DE7F88D48bA7c5FF19"
)

abi = [
    {
        "inputs": [
            {"internalType": "string", "name": "_text", "type": "string"},
            {"internalType": "string", "name": "_sentiment", "type": "string"}
        ],
        "name": "saveRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getRecord",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "string", "name": "", "type": "string"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

if not w3.eth.get_code(contract_address):
    raise RuntimeError("No deployed contract found at the configured address")

contract = w3.eth.contract(address=contract_address, abi=abi)


class TextInput(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    save_to_blockchain: bool = False


@app.get("/")
def home():
    return {"message": "Hacker House AI API is working"}


@app.get("/record")
def get_record():
    try:
        result = contract.functions.getRecord().call()
        return {"text": result[0], "sentiment": result[1]}
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Could not read the Sepolia contract"
        )


@app.post("/analyze")
def analyze(data: TextInput):
    text = data.text.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )

    positive = ["good", "great", "excellent", "happy"]
    negative = ["bad", "poor", "terrible", "sad"]

    words = text.lower().split()
    score = sum(word in positive for word in words)
    score -= sum(word in negative for word in words)

    if score > 0:
        sentiment = "positive"
    elif score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    result = {
        "text": text,
        "sentiment": sentiment,
        "score": score,
        "blockchain": "not_requested",
        "contract_address": contract_address
    }

    if not data.save_to_blockchain:
        return result

    try:
        balance = w3.eth.get_balance(account.address)
        if balance == 0:
            raise HTTPException(
                status_code=402,
                detail="Wallet has no Sepolia ETH for gas"
            )

        nonce = w3.eth.get_transaction_count(account.address)

        function_call = contract.functions.saveRecord(
            text, sentiment
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

        signed_tx = account.sign_transaction(transaction)
        tx_hash = w3.eth.send_raw_transaction(
            signed_tx.raw_transaction
        )

        receipt = w3.eth.wait_for_transaction_receipt(
            tx_hash, timeout=120
        )

        if receipt.status != 1:
            raise HTTPException(
                status_code=502,
                detail="Blockchain transaction failed"
            )

        result.update({
            "blockchain": "saved",
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber,
            "transaction_status": receipt.status,
            "etherscan_url": (
                "https://sepolia.etherscan.io/tx/" + tx_hash.hex()
            )
        })

        return result

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Blockchain transaction failed. Check RPC, balance and transaction status."
        )
