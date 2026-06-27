from fastapi import APIRouter
from modules.message_batch_generator import (
    generate_all_messages
)

router = APIRouter()


@router.post("/generate-message")
def generate_message_api():

    try:

        messages = generate_all_messages()

        return {

            "status": "success",

            "count": len(messages),

            "message":
            "Message generation completed successfully.",

            "output_file":
            "output/generated_messages.json"

        }

    except FileNotFoundError as e:

        return {

            "status": "error",

            "message":
            f"Required file not found: {str(e)}"

        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }