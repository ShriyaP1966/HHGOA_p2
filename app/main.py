import logging
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

from app.chain import (
    BlockchainClient,
    ChainError,
    ChainNotConfigured,
    InsufficientFunds,
    get_client,
)
from app.config import get_settings
from app.ratelimit import RateLimitExceeded, SlidingWindowLimiter
from app.sentiment import analyze_sentiment

logger = logging.getLogger("sentiment-api")

app = FastAPI(title="Sepolia Sentiment API", version="1.0.0")

write_limiter = SlidingWindowLimiter()


def chain_dependency() -> BlockchainClient:
    try:
        return get_client()
    except ChainNotConfigured:
        raise HTTPException(
            status_code=503, detail="Blockchain is not configured on this server"
        ) from None


def check_write_access(request: Request) -> None:
    """Gate for requests that spend gas: API key plus a per-client rate limit."""
    settings = get_settings()

    if not settings.api_key:
        raise HTTPException(
            status_code=503, detail="Blockchain writes are disabled (API_KEY not configured)"
        )

    supplied = request.headers.get("x-api-key", "")
    if not secrets.compare_digest(supplied.encode(), settings.api_key.encode()):
        raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key header")

    client_id = request.client.host if request.client else "unknown"
    try:
        write_limiter.check(client_id, settings.write_rate_limit, settings.write_rate_window)
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=429,
            detail="Too many blockchain writes, try again later",
            headers={"Retry-After": str(exc.retry_after)},
        ) from None


class TextInput(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    save_to_blockchain: bool = False


@app.get("/")
def home():
    return {"message": "Sepolia Sentiment API is working"}


@app.get("/health")
def health():
    """Cheap liveness probe: never touches the blockchain."""
    return {"status": "ok", "blockchain_configured": get_settings().chain_configured}


@app.get("/record")
def get_record(chain: BlockchainClient = Depends(chain_dependency)):
    try:
        text, sentiment = chain.read_record()
    except ChainError as exc:
        logger.warning("record read failed: %s", exc)
        raise HTTPException(status_code=502, detail="Could not read the Sepolia contract") from exc
    return {"text": text, "sentiment": sentiment}


@app.post("/analyze")
def analyze(request: Request, data: TextInput):
    text = data.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if data.save_to_blockchain:
        check_write_access(request)

    sentiment, score = analyze_sentiment(text)

    result = {
        "text": text,
        "sentiment": sentiment,
        "score": score,
        "blockchain": "not_requested",
        "contract_address": get_settings().contract_address,
    }

    if not data.save_to_blockchain:
        return result

    chain = chain_dependency()
    try:
        receipt = chain.save_record(text, sentiment)
    except InsufficientFunds:
        raise HTTPException(status_code=402, detail="Wallet has no Sepolia ETH for gas") from None
    except ChainError as exc:
        logger.warning("blockchain write failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Blockchain transaction failed. Check RPC, balance and transaction status.",
        ) from exc

    result.update({"blockchain": "saved", **receipt})
    return result
