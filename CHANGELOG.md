# Changelog

## 1.0.0

### Changed
- Sentiment analysis now uses VADER instead of an 8-word list. It handles negation ("not good"), punctuation and intensity. `score` is now the VADER compound score in [-1, 1] instead of an integer count.
- Code moved into an `app/` package (config, chain client, sentiment, rate limiter). Run with `uvicorn app.main:app`.
- The Sepolia connection is now made lazily on first use instead of at import time, so the app starts without credentials and `/health` always works.
- `requirements.txt` rewritten as UTF-8 with direct dependencies only (dropped the Windows-only `pywin32`).
- Helper scripts moved to `scripts/` and now share the ABI and config with the app.

### Added
- `API_KEY` protection (`X-API-Key` header) and a per-client rate limit on `save_to_blockchain` requests.
- Nonce lock and `pending` nonce so concurrent writes do not collide.
- `GET /health` endpoint.
- Solidity source for the contract (`contracts/AIRecord.sol`).
- pytest suite (sentiment, API, blockchain client with mocked web3), ruff lint, GitHub Actions CI.
- Dockerfile, `render.yaml`, `.env.example`, LICENSE.

## 0.1.0
- Initial prototype: word-list sentiment, FastAPI, Sepolia integration.
