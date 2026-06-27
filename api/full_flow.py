from fastapi import APIRouter

from modules.fetch_trending import fetch_trending_coins
from modules.message_batch_generator import generate_all_messages
from modules.chat_poster import post_all_messages

router = APIRouter()

"""
Complete workflow

1. Fetch latest coins
2. Generate all messages
3. Post next batch
"""


@router.post("/full-flow")
def full_flow():

    try:

        # -------------------------------------
        # Fetch Latest Coins
        # -------------------------------------

        fetch_result = fetch_trending_coins()

        if fetch_result["status"] != "success":

            return fetch_result

        # -------------------------------------
        # Generate Messages
        # -------------------------------------

        generated = generate_all_messages()

        # -------------------------------------
        # Post Batch
        # -------------------------------------

        return {

            "status": "success",

            "fetch": {

                "coins": len(fetch_result["coins"]),

                "credits": fetch_result["credit_count"]

            },

            "messages_generated": len(generated),


        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }