import json
import os
import random
import time
from pathlib import Path

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError
)
# ==========================================================
# Configuration
# ==========================================================

AUTH_STATE = "auth/state.json"

GENERATED_MESSAGES_FILE = "output/generated_messages.json"

RESULTS_FILE = "output/results.json"

POST_PROGRESS_FILE = "output/post_progress.json"

# Number of coins to post per execution
POST_BATCH_SIZE = 50

# Restart browser after these many successful posts
RESTART_BROWSER_AFTER = 50

# Retry configuration
MAX_RETRIES = 2

# Delay between successful posts
MIN_DELAY = 3
MAX_DELAY = 6

# Browser restart delay
RESTART_DELAY = (5, 10)

# Typing delay
TYPE_DELAY_MIN = 32
TYPE_DELAY_MAX = 80

# Page load wait
PAGE_LOAD_MIN = 1200
PAGE_LOAD_MAX = 2200

# Wait after clicking Post
POST_WAIT_MIN = 2000
POST_WAIT_MAX = 3500

# ==========================================================
# Output Directory
# ==========================================================

Path("output").mkdir(
    exist_ok=True
)

# ==========================================================
# Utility Functions
# ==========================================================

def load_json(path, default):

    try:

        if not os.path.exists(path):

            return default

        with open(

            path,

            "r",

            encoding="utf-8"

        ) as f:

            return json.load(f)

    except Exception:

        return default


def save_json(path, data):

    with open(

        path,

        "w",

        encoding="utf-8"

    ) as f:

        json.dump(

            data,

            f,

            indent=4,

            ensure_ascii=False

        )


# ==========================================================
# Progress
# ==========================================================

def load_post_progress():

    progress = load_json(

        POST_PROGRESS_FILE,

        {

            "next_index": 0

        }

    )

    return max(
        0,
        progress.get("next_index", 0)
    )


def save_post_progress(index):

    save_json(

        POST_PROGRESS_FILE,

        {

            "next_index": index

        }

    )


# ==========================================================
# Delay Helpers
# ==========================================================

def random_pause():

    time.sleep(

        random.uniform(

            MIN_DELAY,

            MAX_DELAY

        )

    )


def random_typing_delay():

    return random.randint(

        TYPE_DELAY_MIN,

        TYPE_DELAY_MAX

    )


def random_page_wait(page):

    page.wait_for_timeout(

        random.randint(

            PAGE_LOAD_MIN,

            PAGE_LOAD_MAX

        )

    )


def random_post_wait(page):

    page.wait_for_timeout(

        random.randint(

            POST_WAIT_MIN,

            POST_WAIT_MAX

        )

    )
# ==========================================================
# Browser Session Management
# ==========================================================

import asyncio


async def create_browser_session(headless=True):

    p = await async_playwright().start()

    browser = p.chromium.launch(

        headless=headless,

        args=[

            "--disable-blink-features=AutomationControlled",

            "--disable-dev-shm-usage",

            "--no-sandbox"

        ]

    )

    context = await browser.new_context(

        storage_state=AUTH_STATE,

        viewport={

            "width": 1366,

            "height": 768

        }

    )

    page = await context.new_page()

    page.set_default_timeout(40000)

    page.set_default_navigation_timeout(70000)

    return {

        "playwright": p,

        "browser": browser,

        "context": context,

        "page": page

    }


def close_browser_session(session):

    try:

        session["page"].close()

    except Exception:

        pass

    try:

        session["context"].close()

    except Exception:

        pass

    try:

        session["browser"].close()

    except Exception:

        pass

    try:

        session["playwright"].stop()

    except Exception:

        pass


def verify_session(session):

    page = session["page"]

    try:

        page.goto(

            "https://coinmarketcap.com/currencies/bitcoin/",

            wait_until="domcontentloaded"

        )

        random_page_wait(page)

        if "login" in page.url.lower():
            print("Redirected to login page.")
            return False

        textbox = page.locator(
            '[data-test="base-editor-editable"]'
        )

        try:
            textbox.wait_for(
                state="visible",
                timeout=15000
            )
        except PlaywrightTimeoutError:
            print("Comment editor not visible.")
            return False

        post_button = page.locator(
            '[data-test="editor-post-button"]'
        )

        try:
            post_button.wait_for(
                state="visible",
                timeout=10000
            )
        except PlaywrightTimeoutError:
            print("Post button not visible.")
            return False
        button_text = (

            post_button

            .inner_text()

            .strip()

            .lower()

        )

        if "log in" in button_text:

            print("Session expired.")

            return False

        print("Session verified.")

        return True

    except PlaywrightTimeoutError:

        print("Timeout while verifying session.")

        return False

    except Exception as e:

        print("Session verification failed:", e)

        return False


# ==========================================================
# Restart Browser
# ==========================================================

def restart_browser(session):

    print("\nRestarting browser...\n")

    close_browser_session(session)

    time.sleep(

        random.randint(

            *RESTART_DELAY

        )

    )

    session = create_browser_session(

        headless=False

    )

    if not verify_session(session):

        raise Exception(

            "Session invalid after restart."

        )

    return session
# ==========================================================
# Post Chat (Optimized)
# ==========================================================

def post_chat_with_session(

    session,

    coin_url,

    message,

    sentiment="bullish"

):

    page = session["page"]

    try:

        # --------------------------------------------------
        # Open Coin Page
        # --------------------------------------------------

        page.goto(

            coin_url,

            wait_until="domcontentloaded"

        )

        random_page_wait(page)



        if "login" in page.url.lower():

            return {

                "status": "expired",

                "message": "Redirected to login."

            }

        # --------------------------------------------------
        # Captcha Detection
        # --------------------------------------------------

        page_text = page.locator("body").inner_text().lower()

        captcha_keywords = [
            "captcha",
            "verify you are human",
            "security check",
            "cloudflare",
            "challenge",
            "checking your browser",
            "attention required",
            "please verify",
            "are you a robot"
        ]

        for word in captcha_keywords:

            if word in page_text:

                return {

                    "status": "captcha",

                    "message": "Captcha detected"

                }

        # --------------------------------------------------
        # Editor
        # --------------------------------------------------

        textbox = page.locator(
            '[data-test="base-editor-editable"]'
        )

        try:
            textbox.wait_for(
                state="visible",
                timeout=15000
            )
        except PlaywrightTimeoutError:
            return {
                "status":"error",
                "message":"Comment editor not found."
            }

        page.mouse.wheel(
            0,
            random.randint(200,600)
        )

        page.wait_for_timeout(
            random.randint(300,700)
        )
        textbox.click()

        page.keyboard.press(

            "Control+A"

        )

        page.keyboard.press(

            "Backspace"

        )

        page.keyboard.type(

            message,

            delay=random_typing_delay()

        )

        page.wait_for_timeout(

            400

        )

        # --------------------------------------------------
        # Sentiment
        # --------------------------------------------------

        if sentiment.lower() == "bullish":

            sentiment_button = page.locator(

                '[data-test="editor-bullish-button"]'

            )

        else:

            sentiment_button = page.locator(

                '[data-test="editor-bearish-button"]'

            )

        if sentiment_button.count():

            sentiment_button.click()

        page.wait_for_timeout(

            300

        )

        # --------------------------------------------------
        # Post Button
        # --------------------------------------------------

        post_button = page.locator(
            '[data-test="editor-post-button"]'
        )

        try:
            post_button.wait_for(
                state="visible",
                timeout=10000
            )
        except PlaywrightTimeoutError:
            return {
                "status":"error",
                "message":"Post button not found."
            }

        button_text = (

            post_button

            .inner_text()

            .strip()

            .lower()

        )

        if "log in" in button_text:

            return {

                "status": "expired",

                "message": "Session expired."

            }

        # --------------------------------------------------
        # Submit
        # --------------------------------------------------
        page.mouse.move(
            random.randint(300,900),
            random.randint(200,600)
        )

        page.wait_for_timeout(
            random.randint(200,700)
        )
        post_button.click()

        random_post_wait(page)

        page_text = page.locator(
            "body"
        ).inner_text().lower()

        # Captcha
        for word in captcha_keywords:
            if word in page_text:
                return {
                    "status":"captcha",
                    "message":"Captcha detected"
                }

        # Login expired
        if "log in" in page_text:
            return {
                "status":"expired",
                "message":"Session expired"
            }

        # Rate limit
        rate_limit_keywords = [
            "too many requests",
            "try again later",
            "please wait",
            "rate limit"
        ]

        for word in rate_limit_keywords:
            if word in page_text:
                return {
                    "status":"retry",
                    "message":"Rate limited"
                }

        return {
            "status":"success",
            "message":"Posted successfully"
        }

    except PlaywrightTimeoutError:

        return {

            "status": "retry",

            "message": "Page timeout"

        }

    except Exception as e:

        return {

            "status": "retry",

            "message": str(e)

        }
# ==========================================================
# Retry Wrapper
# ==========================================================

def post_with_retry(

    session,

    coin_url,

    message,

    sentiment="bullish"

):

    last_result = None

    for attempt in range(

        1,

        MAX_RETRIES + 1

    ):

        result = post_chat_with_session(

            session=session,

            coin_url=coin_url,

            message=message,

            sentiment=sentiment

        )

        status = result.get(

            "status",

            "error"

        )

        # --------------------------------------
        # Success
        # --------------------------------------

        if status == "success":

            return result

        # --------------------------------------
        # Login Expired
        # --------------------------------------

        if status == "expired":

            print(

                "\nSession expired."

            )

            return result

        # --------------------------------------
        # Captcha
        # --------------------------------------

        if status == "captcha":

            print(

                "\nCaptcha detected."

            )

            return result

        # --------------------------------------
        # Retry
        # --------------------------------------

        if status == "retry":

            print(

                f"Retry {attempt}/{MAX_RETRIES} ->",

                result["message"]

            )

            last_result = result

            time.sleep(

                random.randint(

                    2,

                    5

                )

            )

            continue

        # --------------------------------------
        # Other Error
        # --------------------------------------

        print(

            f"Retry {attempt}/{MAX_RETRIES} ->",

            result["message"]

        )

        last_result = result

        time.sleep(

            random.randint(

                2,

                5

            )

        )

    # ------------------------------------------
    # Failed after retries
    # ------------------------------------------

    return {

        "status": "failed",

        "message": (

            last_result["message"]

            if last_result

            else

            "Unknown error"

        )

    }


# ==========================================================
# Restart Decision
# ==========================================================

def should_restart_browser(

    successful_posts

):

    return (

        successful_posts

        >=

        RESTART_BROWSER_AFTER

    )
    # ==========================================================
# Batch Posting
# ==========================================================

def post_all_messages():

    messages = load_json(

        GENERATED_MESSAGES_FILE,

        []

    )

    if len(messages) == 0:

        raise Exception(

            "generated_messages.json is empty."

        )

    results = load_json(

        RESULTS_FILE,

        []

    )

    start_index = load_post_progress()

    total = len(messages)

    # Reset progress if message file changed
    if start_index > total:
        print("Progress file is ahead of generated messages.")
        print("Resetting progress to 0.")

        start_index = 0
        save_post_progress(0)
    start_index = min(start_index, total)
    end_index = min(

        start_index + POST_BATCH_SIZE,

        total

    )

    processed = 0

    successful_posts = 0

    failed_posts = 0

    session = create_browser_session(

        headless=False

    )

    try:

        if not verify_session(session):

            raise Exception(

                "Session verification failed."

            )

        for index in range(

            start_index,

            end_index

        ):

            item = messages[index]

            print(

                "\n============================================================"

            )

            print(

                f"Posting {index+1}/{total}"

            )

            print(

                item["symbol"]

            )

            result = post_with_retry(

                session=session,

                coin_url=item["url"],

                message=item["message"],

                sentiment="bullish"

            )

            results.append(

                {

                    "name": item["name"],

                    "symbol": item["symbol"],

                    "url": item["url"],

                    "status": result["status"],

                    "message": result["message"]

                }

            )

            save_json(

                RESULTS_FILE,

                results

            )

            # -----------------------------------
            # Success
            # -----------------------------------

            if result["status"] == "success":

                successful_posts += 1

                processed += 1

                save_post_progress(

                    index + 1

                )

                if (
                    should_restart_browser(successful_posts)
                    and
                    index != end_index - 1
                ):
                    session = restart_browser(session)
                    successful_posts = 0

                random_pause()

                continue

            # -----------------------------------
            # Captcha
            # -----------------------------------

            if result["status"] == "captcha":

                print(

                    "\nCaptcha detected."

                )

                continue

            # -----------------------------------
            # Session Expired
            # -----------------------------------

            if result["status"] == "expired":

                print(

                    "\nSession expired."

                )

                break

            # -----------------------------------
            # Failed
            # -----------------------------------

            failed_posts += 1

            print(

                "\nFailed:",

                result["message"]

            )

            continue

    finally:

        close_browser_session(

            session

        )
    next_index = load_post_progress()

    print(f"Total messages : {total}")
    print(f"Saved index    : {next_index}")

    remaining = max(
    0,
    total - next_index)

    print(

        "\nFinished Batch"

    )

    print(

        f"Successful : {processed}"

    )

    print(

        f"Failed     : {failed_posts}"

    )

    print(

        f"Next Index : {next_index}"

    )

    print(

        f"Remaining  : {remaining}"

    )

    return {

        "processed": processed,

        "failed": failed_posts,

        "next_index": next_index,

        "remaining": remaining

    }
# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    start_time = time.time()

    try:

        summary = post_all_messages()

        print("\n================ SUMMARY ================")

        print(
            f"Successful Posts : {summary['processed']}"
        )

        print(
            f"Failed Posts     : {summary['failed']}"
        )

        print(
            f"Next Index       : {summary['next_index']}"
        )

        print(
            f"Remaining Coins  : {summary['remaining']}"
        )

    except KeyboardInterrupt:

        print(

            "\nInterrupted by user."

        )

    except Exception as e:

        print(

            "\nFatal Error:",

            e

        )

    finally:

        elapsed = time.time() - start_time

        minutes = int(elapsed // 60)

        seconds = int(elapsed % 60)

        print(

            "\n========================================"

        )

        print(

            f"Execution Time : {minutes}m {seconds}s"

        )

        print(

            "========================================\n"

        )