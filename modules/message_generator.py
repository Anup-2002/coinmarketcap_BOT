import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=OPENAI_API_KEY
)


def build_prompt(coins):

    data = []

    for coin in coins:

        data.append(
            {
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "price": coin.get("price"),
                "change_24h": coin.get("change_24h"),
                "change_7d": coin.get("change_7d"),
                "volume_24h": coin.get("volume_24h"),
                "cmc_rank": coin.get("cmc_rank")
            }
        )

    return f"""
Generate ONE unique CoinMarketCap community comment for EACH coin.

Requirements:

- 1 to 2 short sentences
- Human sounding
- Mention the coin name or symbol
- Use the provided market data naturally
- Focus on trend, momentum and activity
- No emojis
- No hashtags
- No financial advice
- No copy-paste style comments
- Use different sentence structures
- Avoid repeatedly saying:
- trading volume suggests
- community interest
- market activity remains active
- worth watching
- Do not include explanations.
- Do not wrap JSON in markdown.
- Return valid JSON only

Format:

{{
    "messages": [
        {{
            "symbol": "BTC",
            "message": "BTC has seen steady activity recently. Trading volume remains active and market participants continue to watch its next move."
        }}
    ]
}}

Coins:

{json.dumps(data, ensure_ascii=False)}
"""


def openai_generate_messages(prompt):

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.8,

        response_format={
            "type": "json_object"
        },

        max_tokens=4000
    )

    return response.choices[0].message.content.strip()


def build_fallback_message(coin):

    symbol = coin.get(
        "symbol",
        "Coin"
    )

    change_24h = coin.get(
        "change_24h",
        0
    )

    try:

        change_24h = float(change_24h)

    except Exception:

        change_24h = 0

    if change_24h > 10:

        return (
            f"{symbol} has been showing strong momentum recently. "
            f"Market activity remains elevated and traders appear highly engaged."
        )

    elif change_24h > 0:

        return (
            f"{symbol} has been moving steadily over the last day. "
            f"It continues to attract attention from market participants."
        )

    else:

        return (
            f"{symbol} has experienced some recent pressure in the market. "
            f"It will be interesting to see how activity develops from here."
        )


def generate_messages(coins):

    prompt = build_prompt(coins)

    try:
        content = openai_generate_messages(
            prompt
        )

        with open(
            "output/debug_response.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(content)

        result = json.loads(
            content
        )

        if (
            isinstance(result, dict)
            and "messages" in result
        ):

            return result[
                "messages"
            ]

        raise Exception(
            "Invalid JSON returned"
        )

    except Exception as e:

        print(
            "OpenAI failed:",
            e
        )

        fallback = []

        for coin in coins:

            fallback.append(
                {
                    "symbol": coin.get(
                        "symbol",
                        ""
                    ),
                    "message": build_fallback_message(
                        coin
                    )
                }
            )

        return fallback


if __name__ == "__main__":

    sample = [

        {
            "name": "Bitcoin",
            "symbol": "BTC",
            "price": 108000,
            "change_24h": 2.3,
            "change_7d": 5.1,
            "volume_24h": 45000000000,
            "cmc_rank": 1
        },

        {
            "name": "Ethereum",
            "symbol": "ETH",
            "price": 2600,
            "change_24h": -1.1,
            "change_7d": -4.2,
            "volume_24h": 18000000000,
            "cmc_rank": 2
        }

    ]

    print(
        json.dumps(
            generate_messages(
                sample
            ),
            indent=4
        )
    )