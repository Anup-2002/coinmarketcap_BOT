from fastapi import APIRouter

from modules.chat_poster import post_all_messages

router = APIRouter()


@router.post("/post-chat")
def post_chat_api():

    try:

        result = post_all_messages()

        return {

            "status": "success",

            "processed": result["processed"],

            "failed": result["failed"],

            "next_index": result["next_index"],

            "remaining": result["remaining"]

        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }