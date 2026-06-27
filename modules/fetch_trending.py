import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

CMC_API_KEY = os.getenv("CMC_API_KEY")

OUTPUT_FILE = "output/last_trending.json"


def fetch_trending_coins(
        limit=600
):

    headers = {

        "Accepts": "application/json",

        "X-CMC_PRO_API_KEY": CMC_API_KEY

    }

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    params = {

        "start": 1,

        "limit": limit,

        "convert": "USD"

    }

    try:

        response = requests.get(

            url,

            headers=headers,

            params=params,

            timeout=20

        )

        response.raise_for_status()

        data = response.json()

        credit_count = (

            data["status"]
            .get(
                "credit_count",
                0
            )
        )

        coins = []

        for coin in data["data"]:

            coins.append(

                {

                    "name":
                    coin["name"],

                    "symbol":
                    coin["symbol"],

                    "price":
                    round(
                        coin["quote"]["USD"]["price"],
                        6
                    ),

                    "change_1h":
                    coin["quote"]["USD"]["percent_change_1h"],

                    "change_24h":
                    coin["quote"]["USD"]["percent_change_24h"],

                    "change_7d":
                    coin["quote"]["USD"]["percent_change_7d"],     
                    "market_cap":
                    round(
                        coin["quote"]["USD"]["market_cap"],
                        2
                    ),
                    "volume_24h":
                    round(
                        coin["quote"]["USD"]["volume_24h"],
                        2
                    ),

                    "cmc_rank":
                    coin["cmc_rank"],

                    "slug":
                    coin["slug"],

                    "url":
                    f"https://coinmarketcap.com/currencies/{coin['slug']}/"

                }

            )

        Path(
            "output"
        ).mkdir(
            exist_ok=True
        )

        with open(

                OUTPUT_FILE,

                "w",

                encoding="utf-8"

        ) as f:

            json.dump(

                coins,

                f,

                indent=4,

                ensure_ascii=False

            )

        print(

            f"Fetched {len(coins)} coins"

        )

        print(

            f"Credits consumed: {credit_count}"

        )

        return {

            "status":
            "success",

            "credit_count":
            credit_count,

            "coins":
            coins

        }

    except Exception as e:

        return {

            "status":
            "error",

            "message":
            str(e)

        }


if __name__ == "__main__":

    result = fetch_trending_coins()

    print(

        result["credit_count"]

    )