from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

BASE_DIR = Path(".")

def read_json(file_path):
    if not file_path.exists():
        return {}
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except:
        return {}

@router.get("/status")
def get_status():

    progress = read_json(BASE_DIR / "progress.json")
    results = read_json(BASE_DIR / "results.json")
    messages = read_json(BASE_DIR / "generated_messages.json")

    # ---- SAFE EXTRACTION (no guessing logic) ----
    total = progress.get("total", 0)
    posted = progress.get("posted", 0)

    remaining = max(total - posted, 0)

    current_coin = progress.get("current_coin", "N/A")

    login_status = results.get("login", "unknown")

    # Decide status cleanly
    if posted == 0:
        status = "Not Started"
    elif posted < total:
        status = "Posting"
    else:
        status = "Completed"

    return {
        "status": status,
        "total": total,
        "posted": posted,
        "remaining": remaining,
        "current_coin": current_coin,
        "login": login_status
    }