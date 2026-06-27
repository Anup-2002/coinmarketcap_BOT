from fastapi import APIRouter
from pydantic import BaseModel
from modules.fetch_trending import (
    fetch_trending_coins
)

router = APIRouter()

'''
This endpoint allows users to fetch trending coins.
working:
    1. Fetch trending coins from CoinMarketCap.
    2. Return the list of trending coins as a JSON response.
    3. Handle any exceptions that may occur during the process and return an error message if needed.
'''

@router.get("/fetch-trending")
def fetch_trending_api():

    result = fetch_trending_coins()

    if result["status"] == "error":

        return result

    return {

        "status":
        "success",

        "count":
        len(
            result["coins"]
        ),

        "credit_count":
        result["credit_count"],

        "coins":
        result["coins"]

    }