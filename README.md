# AI Sentiment Analysis with Sepolia Blockchain

A Python-based sentiment analysis REST API integrated with a Solidity smart contract deployed on the Ethereum Sepolia testnet. The application analyzes text, classifies its sentiment as positive, negative, or neutral, and optionally stores the result on the blockchain for verification.

## Features

- **Sentiment Analysis:** Classifies text as positive, negative, or neutral using rule-based sentiment analysis.
- **REST API:** Uses FastAPI to process sentiment analysis requests.
- **Blockchain Integration:** Uses Web3.py to interact with a deployed Solidity smart contract.
- **On-Chain Record Storage:** Optionally stores analyzed text and its sentiment on the Ethereum Sepolia testnet.
- **Transaction Verification:** Returns transaction details and an Etherscan link when blockchain storage succeeds.
- **Input Validation:** Handles empty text, missing fields, invalid data types, and malformed JSON requests.
- **API Documentation:** Provides interactive API documentation through Swagger UI.

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
3. The sentiment analyzer processes the text and calculates a sentiment score.
4. The application classifies the sentiment as positive, negative, or neutral.
5. If blockchain storage is requested, the application interacts with the deployed smart contract.
6. The transaction is submitted to the Sepolia testnet.
7. The API returns the sentiment result and, when applicable, transaction details.
8. The saved record can be verified using the smart contract's read function or Etherscan.

## Sentiment Scoring

| Sentiment | Score |
|---|---:|
| Positive | 1 |
| Neutral | 0 |
| Negative | -1 |

The current implementation uses a word-list-based, rule-based approach. It is a prototype and does not use a trained machine learning model.

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
├── .gitignore
├── README.md
├── .env                 # Local only; do not commit
└── venv/                # Local virtual environment; do not commit
```

The `.env` file and virtual environment are local resources and must not be uploaded to GitHub.

## Prerequisites

- Python installed
- Git installed
- A MetaMask wallet configured for Sepolia
- Sepolia test ETH for blockchain transactions
- An Alchemy Sepolia RPC endpoint
- The deployed `AIRecord` smart contract

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

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file in the project root directory with the following variables:

```env
SEPOLIA_RPC_URL=your_alchemy_sepolia_rpc_url
SEPOLIA_PRIVATE_KEY=your_wallet_private_key
```

Replace the placeholder values with your own configuration.

**Security precautions:**
- Never commit the `.env` file to GitHub.
- Never share your wallet private key or an RPC URL containing credentials.
- Do not paste secrets into source code.
- Use Sepolia test ETH during development.

The application reads the RPC URL and private key from these environment variables. The contract address is configured in `main.py`.

### 5. Run the API

```powershell
python -m uvicorn main:app --reload
```

The API runs locally at:

`http://127.0.0.1:8000`

Open the interactive Swagger documentation at:

`http://127.0.0.1:8000/docs`

To stop the server, press `Ctrl+C` in the terminal.

## API Usage

### 1. Home endpoint

**Method:** `GET`

**Endpoint:** `/`

Checks whether the API is running.

### 2. Analyze sentiment

**Method:** `POST`

**Endpoint:** `/analyze`

#### Example request without blockchain storage

```json
{
  "text": "This is an excellent result",
  "save_to_blockchain": false
}
```

Example response:

```json
{
  "text": "This is an excellent result",
  "sentiment": "positive",
  "score": 1,
  "blockchain": "not_requested",
  "contract_address": "YOUR_DEPLOYED_CONTRACT_ADDRESS"
}
```

The contract address shown in a real response is the address configured by the application.

#### Example request with blockchain storage

```json
{
  "text": "This is an excellent result",
  "save_to_blockchain": true
}
```

When blockchain storage succeeds, the response also includes the transaction hash, block number, transaction status, and Etherscan transaction URL.

**Note:** This request can submit a real transaction to Sepolia and consume test ETH.

### 3. Read the latest blockchain record

**Method:** `GET`

**Endpoint:** `/record`

Reads the latest record exposed by the deployed smart contract.

The response contains the stored text and sentiment. If the contract read fails, the API returns an error response.

## Input Validation and Error Handling

The API validates incoming requests and handles common errors, including:

- Empty or whitespace-only text
- Missing required fields
- Invalid input data types
- Malformed JSON
- Missing Sepolia configuration
- Blockchain connection and transaction failures

Text must contain at least one non-whitespace character and must not exceed 1,000 characters.

Blockchain-related errors return an appropriate HTTP error response. Successful sentiment analysis without a blockchain request does not require a transaction.

## Testing

The following behaviors were tested during development:

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
- Controlled simulation of a blockchain failure response

The controlled failure test was temporary and was removed after testing.

## Security Notes

- Never upload private keys or `.env` files.
- Never expose RPC credentials in source code or logs.
- Keep `.env` listed in `.gitignore`.
- Use testnet credentials and Sepolia test ETH during development.
- Keep dependencies listed in `requirements.txt`.
- Avoid logging sensitive credentials.
- Review Git history before making a repository public.

This project is a prototype. The rule-based classifier can misclassify nuanced, sarcastic, or context-dependent text. Blockchain availability also depends on RPC connectivity, wallet funds, and transaction execution.

## Future Improvements

- Replace rule-based sentiment analysis with a trained machine learning model.
- Add automated unit and integration tests.
- Improve error handling for RPC outages and reverted transactions.
- Add structured logging and API rate limiting.
- Improve deployment configuration.
- Add support for more advanced sentiment scoring.

## Author

**Shriya Patil**

Hacker House Goa — Person 2  
AI Sentiment Analysis and Blockchain Integration

## Repository

[GitHub: HHGOA_p2](https://github.com/ShriyaP1966/HHGOA_p2)
