from fastapi import APIRouter

from modules.chat_poster import create_browser_session, verify_session,close_browser_session

router = APIRouter()
'''
This endpoint allows users to check if they are logged in to CoinMarketCap.
It verifies the session and returns the login status.
'''



@router.post("/check-login")
def check_login():
    session = create_browser_session(headless=True)
    try:
        result = verify_session(session)
        return {"logged_in": result}
    finally:
        close_browser_session(session)