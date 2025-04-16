import os
import json
from typing import Any
from aws_lambda_typing.context import Context
from playwright.sync_api import sync_playwright

from context import ApplicationContext
import settings

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    u_guid = event["u_guid"]
    url = event["url"]

    run(url)

    try:
        application_context.events.check_webpage(u_guid, url)

        return {
            "statusCode": 200,
            "body": "Completed check",
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception:
        return {
            "statusCode": 400,
            "body": "Bad Request. No result",
            "headers": {
                "Content-Type": "application/json"
            }
        }


TARGET_URL = "https://requestmetrics.com/web-performance/measure-web-performance/"


def run(url: str):
    with sync_playwright() as p:
        print("Launching Playwright")

        try:
            browser = p.chromium.launch(
                headless=True, args=settings.PW_CHROMIUM_ARGS)
        except Exception as e:
            print("❌ Failed to launch browser:", e)
            raise

        try:
            context = browser.new_context(record_har_path=settings.PW_HAR_PATH)
            page = context.new_page()
        except Exception as e:
            print("❌ Failed to open page or context:", e)
            raise

        print("Launched playwright")

        dirname = os.path.dirname(__file__)

        # Inject JavaScript to capture core web vitals
        page.add_init_script(
            path=os.path.join(dirname, "monitoring_events/scripts/initialization.js"))

        print(f"Added observing script. Going to url {url}")

        page.goto(url, wait_until="load")
        page.wait_for_timeout(3000)

        print(f"Loaded url {url}")

        # metrics = page.evaluate(exports.METRIC_EVALUATION)
        metrics = page.evaluate("window.__pwMetrics")

        print("Screenshot now")
        page.screenshot(path=settings.PW_SCREENSHOT_PATH)

        print("Screenshot success")
        context.close()
        browser.close()

        print("Extracted Metrics:")
        print(json.dumps(metrics, indent=2))

        # Upload HAR to S3
        # s3 = boto3.client("s3")
        # with open(HAR_PATH, "rb") as f:
        #     s3.upload_fileobj(f, S3_BUCKET, "har/example.har")

        return metrics


# run(TARGET_URL)
