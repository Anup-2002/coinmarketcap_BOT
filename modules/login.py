from playwright.sync_api import sync_playwright


def check_login():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False
        )

        try:

            context = browser.new_context(
                storage_state="auth/state.json"
            )

            page = context.new_page()

            page.goto(
                "https://coinmarketcap.com/currencies/bitcoin/",
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(
                5000
            )

            current_url = page.url.lower()

            # -------------------------------
            # Login redirect detection
            # -------------------------------

            if (
                "/login" in current_url
                or "signin" in current_url
                or "auth" in current_url
            ):

                return {
                    "status": "expired",
                    "message": "Redirected to login page"
                }

            # -------------------------------
            # Captcha detection
            # -------------------------------

            page_text = page.locator(
                "body"
            ).inner_text().lower()

            captcha_keywords = [

                "captcha",

                "verify you are human",

                "cloudflare",

                "security challenge",

                "robot",

                "unusual traffic",

                "please verify"

            ]

            for keyword in captcha_keywords:

                if keyword in page_text:

                    return {
                        "status": "captcha",
                        "message": f"Captcha detected ({keyword})"
                    }

            # -------------------------------
            # Editor check
            # -------------------------------

            textbox = page.locator(
                '[data-test="base-editor-editable"]'
            )

            if textbox.count() == 0:

                return {
                    "status": "error",
                    "message": "Comment editor not found"
                }

            # -------------------------------
            # Post button check
            # -------------------------------

            post_button = page.locator(
                '[data-test="editor-post-button"]'
            )

            if post_button.count() == 0:

                return {
                    "status": "error",
                    "message": "Post button not found"
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
                    "message": "Session expired"
                }

            return {
                "status": "success",
                "message": "Session active"
            }

        except Exception as e:

            return {
                "status": "error",
                "message": str(e)
            }

        finally:

            browser.close()


if __name__ == "__main__":

    result = check_login()

    print(result)