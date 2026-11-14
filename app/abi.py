"""ABI of the AIRecord contract (source: contracts/AIRecord.sol)."""

ABI = [
    {
        "inputs": [
            {"internalType": "string", "name": "_text", "type": "string"},
            {"internalType": "string", "name": "_sentiment", "type": "string"},
        ],
        "name": "saveRecord",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "getRecord",
        "outputs": [
            {"internalType": "string", "name": "", "type": "string"},
            {"internalType": "string", "name": "", "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "latestRecord",
        "outputs": [
            {"internalType": "string", "name": "text", "type": "string"},
            {"internalType": "string", "name": "sentiment", "type": "string"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]
