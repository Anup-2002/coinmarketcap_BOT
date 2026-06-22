# CoinMarketCap Bot
DEMO:https://youtu.be/vfLEb5vVKTw"
An automation service that:

1) fetches trending coins from CoinMarketCap,
2) generates a community-style message with an LLM,
3) opens a browser session and posts the message in the coin page editor.

This project exposes a small **FastAPI** HTTP API to run the steps.

> Note: This uses browser automation (Playwright) and relies on logged-in session cookies stored in `auth/state.json`.

---

## Features

- Fetch trending coins from CoinMarketCap (`/fetch-trending`)
- Generate a human-like community message (`/generate-message`)
- Post a message to a coin’s community/editor (`/post-chat`)
- Run the full pipeline: trending -> message -> post (`/full-flow`)
- Check whether the stored login session is still valid (`/check-login`)

---

## Project Structure

- `app.py`

  - FastAPI app entry point; registers API routers.
- `api/`

  - HTTP endpoints (routers):
    - `check_login.py`
    - `fetch_trending.py`
    - `generate_message.py`
    - `post_chat.py`
    - `full_flow.py`
- `modules/`

  - Core logic called by the API endpoints:
    - `fetch_trending.py` (Playwright scrape)
    - `message_generator.py` (Gemini/GLLM message generation)
    - `chat_poster.py` (Playwright posting)
    - `login.py` (helper for login/session check)
- `config/`

  - `settings.py`: reads environment variables.
- `auth/`

  - `state.json`: Playwright storage state (cookies/localStorage) for CoinMarketCap login.
- `logs/`

  - runtime logs (if configured/created).

---

## Prerequisites

- Python 3.10+ (recommended)
- Install Google Gemini API access (for message generation)
- Playwright dependencies installed

---

## Setup & Installation

### 1) Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows (cmd):**

```bat
.venv\Scripts\activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Install Playwright browsers

```bash
python -m playwright install
```

### 4) Configure environment variables

Create a `.env` file in the project root (or export variables in your shell).

Required for message generation:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Optional (currently loaded in `config/settings.py`):

- `HEADLESS=true|false` (posting uses `headless=False` in code; you can adjust if needed)
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `CMC_EMAIL`, `CMC_PASSWORD` (not required by the current message generator module)

> The API will not work correctly without `auth/state.json` containing a valid logged-in session.

---

## Login / Session Setup (`auth/state.json`)

The bot uses Playwright `storage_state="auth/state.json"`.

You must create/update `auth/state.json` for your CoinMarketCap account.

Typical approaches:

- Log in once via a Playwright script (not included as a full “login export” flow in this repo), then save the storage state to `auth/state.json`.
- Or manually generate `auth/state.json` using Playwright’s `context.storage_state(path=...)`.

After updating `auth/state.json`, verify session validity with:

- `GET /check-login`

---

## How to Run

### Run the FastAPI server

```bash
uvicorn app:app --reload --port 8000
```

Server base URL:

- `http://127.0.0.1:8000`

---

## API User Guide

### 1) Check login session

**Endpoint**

- `GET /check-login`

**Response example**

```json
{
  "status": "success",
  "message": "Session active"
}
```

If session is expired, you’ll receive an error status/message.

---

### 2) Fetch trending coins

**Endpoint**

- `GET /fetch-trending`

**Response example**

```json
{
  "status": "success",
  "count": 10,
  "coins": [
    {
      "name": "...",
      "symbol": "...",
      "price": "...",
      "change_1h": "...",
      "change_24h": "...",
      "market_cap": "...",
      "volume_24h": "...",
      "dex_liquidity": "...",
      "chain": "...",
      "age": "...",
      "buys_24h": "...",
      "sells_24h": "...",
      "total_txns_24h": "...",
      "url": "https://coinmarketcap.com/currencies/.../"
    }
  ]
}
```

---

### 3) Generate a message for a coin

**Endpoint**

- `POST /generate-message`

**Request body**

```json
{
  "coin": {
    "name": "Bitcoin",
    "symbol": "BTC",
    "price": "$63,000",
    "change_1h": "0.12%",
    "change_24h": "1.2%",
    "market_cap": "$1.2T",
    "volume_24h": "$18B",
    "chain": "",
    "age": "15y",
    "buys_24h": "",
    "sells_24h": "",
    "total_txns_24h": ""
  }
}
```

**Response example**

```json
{
  "status": "success",
  "message": "Interesting activity lately..."
}
```

---

### 4) Post a message

**Endpoint**

- `POST /post-chat`

**Query/body parameters (as used by FastAPI)**

- `coin_url` (string)
- `message` (string)
- `sentiment` (string, default: `bullish`)

**Example (curl)**

```bash
curl -X POST "http://127.0.0.1:8000/post-chat" \
  -H "Content-Type: application/json" \
  -d "{
    \"coin_url\": \"https://coinmarketcap.com/currencies/bitcoin/\",
    \"message\": \"Interesting activity lately...\",
    \"sentiment\": \"bullish\"
  }"
```

**Response example**

```json
{
  "status": "success",
  "message": "Post submitted"
}
```

---

### 5) Run the full flow (recommended for automation)

**Endpoint**

- `POST /full-flow`

Runs:

- fetch trending coins
- generate message for each coin
- post message for each coin

**Response example**

```json
{
  "status": "completed",
  "total_coins": 10,
  "success_count": 7,
  "failed_count": 3,
  "results": [
    {
      "url": "https://coinmarketcap.com/currencies/.../",
      "message": "...",
      "status": "success"
    }
  ]
}
```

---

## Notes / Behavior Details

- Posting uses Playwright with:

  - textbox selector: `[data-test="base-editor-editable"]`
  - sentiment buttons: `[data-test="editor-bullish-button"]` / `[data-test="editor-bearish-button"]`
  - post button: `[data-test="editor-post-button"]`
- If CoinMarketCap UI changes and selectors break, you’ll need to update selectors in:

  - `modules/chat_poster.py`
  - `modules/fetch_trending.py`
- Message generation:

  - Uses Gemini model `gemini-2.5-flash`
  - Prompts enforce: max 2 sentences, no emojis/hashtags/bullets, no financial advice.

---

## Troubleshooting

### Playwright errors

- Install browsers: `python -m playwright install`
- Ensure you can run Chromium.

### Session errors ("Log in" / session expired)

- Update `auth/state.json`
- Re-check with `GET /check-login`

### LLM / API key errors

- Ensure `.env` includes `GEMINI_API_KEY`
- Confirm network access to Gemini.

---
