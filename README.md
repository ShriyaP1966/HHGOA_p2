# AI Sentiment Analysis with Sepolia Blockchain

A Python-based sentiment analysis API integrated with a Solidity smart contract deployed on the Ethereum Sepolia testnet. The application analyzes text, classifies its sentiment, and optionally stores the result on the blockchain for verification.

## Features

- **Sentiment Analysis:** Classifies text as positive, negative, or neutral using rule-based sentiment analysis.
- **REST API:** Built with FastAPI for processing sentiment analysis requests.
- **Blockchain Integration:** Uses Web3.py to interact with a deployed smart contract.
- **On-Chain Record Storage:** Optionally saves the analyzed text and sentiment to the Sepolia testnet.
- **Transaction Verification:** Returns transaction details and an Etherscan link when blockchain storage succeeds.
- **Input Validation:** Handles empty text, missing fields, invalid data types, and malformed JSON requests.

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Web3.py
- Solidity
- Ethereum Sepolia Testnet
- Alchemy RPC
- Remix IDE
- MetaMask

## System Workflow

1. The user submits text through the API.
2. FastAPI validates the request.
3. The sentiment analyzer classifies the text and generates a score.
4. If blockchain storage is requested, the application interacts with the deployed smart contract.
5. The transaction is submitted to Sepolia.
6. The API returns the sentiment result and, when applicable, transaction details.
7. The saved record can be verified using the smart contract's read functions or Etherscan.

## Sentiment Scoring

| Sentiment | Score |
|---|---:|
| Positive | 1 |
| Neutral | 0 |
| Negative | -1 |

The current implementation uses rule-based sentiment analysis rather than a trained machine learning model.

## Project Structure

```text
HHGOA_Person2/
├── main.py
├── check_wallet.py
├── deploy_contract.py
├── test_sepolia.py
├── write_contract.py
├── test_invalid_json.py
├── requirements.txt
├── .env
├── .gitignore
└── venv/
```

**Note:** `.env` and `venv/` are local files/folders and should not be committed to GitHub. They are shown here to explain the local project setup.

## Prerequisites

- Python installed
- A MetaMask wallet configured for Sepolia
- Sepolia test ETH for blockchain transactions
- An Alchemy Sepolia RPC endpoint
- The deployed `AIRecord` smart contract address

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/ShriyaP1966/HHGOA_p2.git
cd HHGOA_p2
```

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project directory and configure the variables expected by the application, including:

```env
SEPOLIA_RPC_URL=your_alchemy_sepolia_rpc_url
PRIVATE_KEY=your_wallet_private_key
CONTRACT_ADDRESS=your_deployed_contract_address
```

Use your actual local configuration values. Never commit `.env` or share your private key. The variable names must match those read by your Python code.

### 5. Run the API

```bash
python -m uvicorn main:app --reload
```

The API will be available locally at:

`http://127.0.0.1:8000`

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

## API Usage

### Endpoint

`POST /analyze`

Example request without blockchain storage:

```json
{
  "text": "This is an excellent result",
  "save_to_blockchain": false
}
```

Example request with blockchain storage:

```json
{
  "text": "This is an excellent result",
  "save_to_blockchain": true
}
```

The second request may submit a transaction to Sepolia and consume test ETH.

The response includes the input text, sentiment, score, blockchain status, and contract address. When a transaction succeeds, it can also include the transaction hash, block number, transaction status, and Etherscan URL.

## Testing

The following behaviors have been tested during development:

- Empty and whitespace-only text rejection
- Positive sentiment classification
- Negative sentiment classification
- Neutral sentiment classification
- Longer text input
- Missing required fields
- Invalid input data types
- Malformed JSON handling
- Blockchain transaction submission
- Transaction verification on Sepolia
- Reading the saved sentiment record from the deployed smart contract

## Security Notes

- Never upload private keys, `.env` files, or RPC URLs containing secrets.
- Use testnet credentials and Sepolia test ETH during development.
- Keep `.env` listed in `.gitignore`.
- Avoid logging sensitive credentials.
- This project is a prototype; rule-based sentiment classification may misclassify nuanced or context-dependent text.

## Future Improvements

- Replace rule-based sentiment analysis with a trained machine learning model.
- Add automated unit and integration tests.
- Improve error handling for RPC failures and reverted transactions.
- Add logging and API rate limiting.
- Improve documentation and deployment configuration.

## Author

**Shriya Patil**

Hacker House Goa — Person 2  
AI Sentiment Analysis and Blockchain Integration

## Repository

[GitHub: HHGOA_p2](https://github.com/ShriyaP1966/HHGOA_p2)
