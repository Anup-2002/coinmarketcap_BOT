# CoinMarketCap Bot

DEMO Video: https://youtu.be/vfLEb5vVKTw

An automation service that:

1) fetches trending coins from CoinMarketCap,
2) generates a community-style message with an LLM,
3) opens a browser session and posts the message in the coin page editor.

This project exposes a small **FastAPI** HTTP API to run the steps.

> Uses browser automation (Playwright) and requires a logged-in session stored in `auth/state.json`.

---

## Overview

**Goal:** automate posting short, human-like community comments for trending cryptocurrencies.

**High-level pipeline**
- scrape trending coins →
- generate a short message (Gemini, with optional Groq fallback) →
- post the comment to CoinMarketCap using your logged-in session.

---

## Workflow diagram

```mermaid
graph TD
  A[Start] --> B[GET /check-login]
  B -->|Session active| C[POST /full-flow]
  B -->|Session expired| Z[Regenerate auth/state.json]


  C --> D[Fetch trending coins\nmodules/fetch_trending.py]
  D --> E[For each coin]
  E --> F[Generate message\nmodules/message_generator.py]
  F --> G[Post message\nmodules/chat_poster.py]
  G --> H[Collect results]
  H --> Y[Write outputs\noutput/last_trending.json\noutput/results.json]

  G -->|failure| H
  F -->|Gemini fails| F2[Try Groq (if GROQ_API_KEY is set)]
  F2 -->|still fails| F3[Use FALLBACK_MESSAGES]

```

---

## Features (API)

- `GET /check-login` — verify `auth/state.json` session
- `GET /fetch-trending` — fetch top trending coins
- `POST /generate-message` — generate a short community message for a coin
- `POST /post-chat` — post a message to a coin community editor
- `POST /full-flow` — run end-to-end: trending → message → post

---

## Project structure

- `app.py`
  - FastAPI app entry point; registers API routers.
- `api/`
  - HTTP endpoints:
    - `check_login.py`
    - `fetch_trending.py`
    - `generate_message.py`
    - `post_chat.py`
    - `full_flow.py`
- `modules/`
  - Core logic called by endpoints:
    - `fetch_trending.py` (Playwright scrape of CoinMarketCap trending page)
    - `message_generator.py` (Gemini + Groq fallback)
    - `chat_poster.py` (Playwright posting with selectors)
    - `login.py` (helper; session is mainly driven by `auth/state.json`)
- `config/`
  - `settings.py`: environment configuration
- `auth/`
  - `state.json`: Playwright storage state (cookies/localStorage) for CoinMarketCap login
- `output/`
  - runtime results:
    - `last_trending.json`
    - `results.json`

---

## Prerequisites

- Python 3.10+
- Playwright + Chromium
- LLM API access:
  - `GEMINI_API_KEY` (required for Gemini generation)
  - `GROQ_API_KEY` (optional fallback)

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

---

## Environment variables (.env)

`modules/message_generator.py` loads:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key   # optional
```

> `config/settings.py` may read additional env vars, but message generation in this repo primarily uses Gemini + optional Groq.

---

## Login / Session setup (`auth/state.json`)

The bot uses Playwright `storage_state="auth/state.json"` for:
- posting comments (`modules/chat_poster.py`)
- scraping (context creation in `modules/fetch_trending.py`)
- login validity check (`GET /check-login`)

### What you must do

1) Log into CoinMarketCap in a Playwright browser context (one-time).
2) Export storage state to `auth/state.json`.
3) Validate session using:

- `GET /check-login`

> If you see errors like **"Log in" / "Session expired"**, your session state is no longer valid. Regenerate `auth/state.json`.

---

## Run the FastAPI server

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

**Body (JSON)**

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

### 5) Run the full flow (recommended)

**Endpoint**
- `POST /full-flow`

Runs:
- fetch trending coins
- generate a message for each coin
- post the message for each coin

**Output files**
- `output/last_trending.json` (the coins used in this run)
- `output/results.json` (per-coin status)

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

## Data contracts

### Coin object (produced by `fetch_trending_coins`)

Expected fields in each coin dictionary:
- `name`, `symbol`, `price`
- `change_1h`, `change_24h`
- `market_cap`, `volume_24h`
- `dex_liquidity`, `chain`
- `age`
- `buys_24h`, `sells_24h`, `total_txns_24h`
- `url` (CoinMarketCap currency page URL)

### Message generation

`modules/message_generator.py` builds a prompt using:
- coin name/symbol/price/24h change/market cap/volume

Rules in the prompt:
- 1–2 sentences
- no emojis
- no hashtags
- no financial advice
- output text only

### Posting selectors (CoinMarketCap UI)

`modules/chat_poster.py` uses these selectors:
- textbox: `[data-test="base-editor-editable"]`
- sentiment buttons:
  - bullish: `[data-test="editor-bullish-button"]`
  - bearish: `[data-test="editor-bearish-button"]`
- post button: `[data-test="editor-post-button"]`

If CoinMarketCap changes their UI/DOM, update selectors in `modules/chat_poster.py`.

---

## Troubleshooting

### Playwright errors
- Install browsers: `python -m playwright install`
- Confirm Chromium can launch on your system

### Session errors ("Log in" / session expired)
- Regenerate `auth/state.json`
- Re-check with `GET /check-login`

### LLM / API key errors
- Ensure `.env` includes `GEMINI_API_KEY`
- If Gemini fails, the module may fall back to `GROQ_API_KEY` (if provided)

