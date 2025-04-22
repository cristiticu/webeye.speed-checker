from dotenv import load_dotenv
import os

load_dotenv('.env')

ENVIRONMENT = os.environ.get('ENVIRONMENT')
AWS_REGION = os.environ.get('AWS_REGION', '')
RESOURCE_PREFIX = "production" if ENVIRONMENT == "production" else "stage"

DYNAMODB_URL_OVERRIDE = os.environ.get('DYNAMODB_URL_OVERRIDE')
TABLE_PREFIX = os.environ.get('TABLE_PREFIX', RESOURCE_PREFIX)
MONITORING_EVENTS_TABLE_REGION = "eu-central-1"
MONITORING_EVENTS_TABLE_NAME = "webeye.monitoring-events"

BUCKET_PREFIX = os.environ.get('BUCKET_PREFIX', RESOURCE_PREFIX)
SCREENSHOTS_BUCKET_REGION = "eu-central-1"
SCREENSHOTS_BUCKET_NAME = "webeye.bucket.screenshot"
HAR_BUCKET_REGION = "eu-central-1"
HAR_BUCKET_NAME = "webeye.bucket.har"


PW_HAR_PATH = "./out/performance.har" if ENVIRONMENT == "test" else "/tmp/performance.har"
PW_SCREENSHOT_PATH = "./out/screenshot.jpg" if ENVIRONMENT == "test" else "/tmp/screenshot.jpg"

PW_CHROMIUM_ARGS = [
    "--allow-running-insecure-content",
    "--autoplay-policy=user-gesture-required",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--disable-setuid-sandbox",
    "--disable-site-isolation-trials",
    "--disable-speech-api",
    "--disable-accelerated-2d-canvas",
    "--disable-dev-shm-usage",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-client-side-phishing-detection",
    "--disable-component-update",
    "--disable-default-apps",
    "--disable-domain-reliability",
    "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-renderer-backgrounding",
    "--disable-sync",
    "--force-color-profile=srgb",
    "--hide-scrollbars",
    "--metrics-recording-only",
    "--mute-audio",
    "--no-first-run",
    "--no-zygote",
    "--no-sandbox",
    "--no-default-browser-check",
    "--no-pings",
    "--use-gl=swiftshader"
]
