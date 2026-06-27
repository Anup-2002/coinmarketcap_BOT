
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)
OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL"
)


CMC_EMAIL = os.getenv(
    "CMC_EMAIL"
)

CMC_PASSWORD = os.getenv(
    "CMC_PASSWORD"
)

HEADLESS = (
    os.getenv(
        "HEADLESS",
        "False"
    ).lower() == "true"
)