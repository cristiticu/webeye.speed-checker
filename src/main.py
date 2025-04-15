import json
from typing import Any
from aws_lambda_typing.context import Context
from playwright.sync_api import sync_playwright

from context import ApplicationContext

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


# S3_BUCKET = "your-bucket-name"
HAR_PATH = "/tmp/performance.har"
SCREENSHOT_PATH = "/tmp/screenshot.png"
# HAR_PATH = "./performance.har"
TARGET_URL = "https://weather.cristit.icu"

PW_ARGS = ["--disable-gpu",
           "--no-sandbox",
           "--single-process",
           "--disable-dev-shm-usage",
           "--no-zygote",
           "--disable-setuid-sandbox",
           "--disable-accelerated-2d-canvas",
           "--disable-dev-shm-usage",
           "--no-first-run",
           "--no-default-browser-check",
           "--disable-background-networking",
           "--disable-background-timer-throttling",
           "--disable-client-side-phishing-detection",
           "--disable-component-update",
           "--disable-default-apps",
           "--disable-domain-reliability",
           "--disable-features=AudioServiceOutOfProcess",
           "--disable-hang-monitor",
           "--disable-ipc-flooding-protection",
           "--disable-popup-blocking",
           "--disable-prompt-on-repost",
           "--disable-renderer-backgrounding",
           "--disable-sync",
           "--force-color-profile=srgb",
           "--metrics-recording-only",
           "--mute-audio",
           "--no-pings",
           "--use-gl=swiftshader"
           ]


def run(url: str):
    with sync_playwright() as p:
        print("Launching Playwright")

        try:
            browser = p.chromium.launch(
                headless=True, args=PW_ARGS)
        except Exception as e:
            print("❌ Failed to launch browser:", e)
            raise

        try:
            context = browser.new_context(record_har_path=HAR_PATH)
            page = context.new_page()
        except Exception as e:
            print("❌ Failed to open page or context:", e)
            raise

        print("Launched playwright")

        # Inject JavaScript to capture core web vitals
        page.add_init_script("""
            (() => {
                window.__perfMetrics = {};
                new PerformanceObserver((entryList) => {
                    for (const entry of entryList.getEntries()) {
                        if (entry.name === 'first-contentful-paint') {
                            window.__perfMetrics.FCP = entry.startTime;
                        }
                        if (entry.entryType === 'largest-contentful-paint') {
                            window.__perfMetrics.LCP = entry.renderTime || entry.loadTime;
                        }
                    }
                }).observe({ type: 'paint', buffered: true });

                new PerformanceObserver((entryList) => {
                    const clsEntry = entryList.getEntries().pop();
                    if (clsEntry) {
                        window.__perfMetrics.CLS = clsEntry.value;
                    }
                }).observe({ type: 'layout-shift', buffered: true });
            })();
        """)

        print(f"Added observing script. Going to url {url}")

        page.goto(url, wait_until="load")
        page.wait_for_timeout(2000)

        print(f"Loaded url {url}")

        metrics = page.evaluate("""
            () => {
                const timing = performance.timing;
                const navStart = timing.navigationStart;
                const TTFB = timing.responseStart - navStart;
                return {
                    ...window.__perfMetrics,
                    TTFB,
                    loadTime: timing.loadEventEnd - navStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - navStart
                };
            }
        """)

        print("Screenshot now")
        page.screenshot(path=SCREENSHOT_PATH)

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
