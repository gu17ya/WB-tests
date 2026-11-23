# WhiteBIT spot API tests

Python/pytest tests for the WhiteBIT Private HTTP API v4 (spot trading).

Covered flows:

- Market order buy/sell: response, executed history, deals, taker fee, balance changes
- Limit order buy/sell: creation, active orders, frozen funds, cancellation, funds returned
- Limit order validation: `postOnly` + `ioc` together are rejected with 422

## Project structure

- `config.py` – global constants (base URL, market, timeouts, response time limit)
- `data/` – test data: sides, order size multipliers, expected error bodies
- `models/` – data models such as `Market`
- `services/` – `BaseApiService` (session, logging) and WhiteBIT services built on it:
  `WhiteBitBaseService` (request signing) → `WhiteBitTradeService`; `WhiteBitPublicService`
- `helpers/` – shared test logic (prices, amounts, client order ids, balance parsing)
- `validators/` – reusable checks for responses, orders, fees and balances
- `tests/spot_tests/` – spot test coverage (`spt_XXX`)
- `utils/` – environment and logging helpers

## Requirements

- Docker (nothing else: Python and dependencies come with the image)
- WhiteBIT account with an API key that has trading access
- Positive DBTC and DUSDT balances on the spot (trade) account

## Configuration

```bash
cp example.env .env
```

Fill in the keys. Write values without quotes: `.env` is passed to Docker as is.

Required:

- `WB_API_KEY` – public API key
- `WB_API_SECRET` – private API key

Optional:

- `WB_BASE_URL` – defaults to `https://whitebit.com`
- `LOG_LEVEL` – defaults to `INFO`

## Running tests

With Docker:

```bash
docker compose run --rm --build tests
docker compose run --rm --build tests tests/spot_tests/spt_001_market_order_tests.py
```

Anything after `tests` is passed to pytest.

Without Docker (Python 3.10+):

Linux / WSL / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Windows (Git Bash):

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pytest
```

Each run writes an HTML report to `reports/report.html` (single file, open in a browser).
Every test in the report has its log: steps and requests with status code and response time.

## Notes

- The account should be used only by these tests: other trades break balance checks.
- Limit orders left open by a failed test are cancelled on teardown.
