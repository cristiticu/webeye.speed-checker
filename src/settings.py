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

# S3_BUCKET = "your-bucket-name"
PW_HAR_PATH = "./out/performance.har" if ENVIRONMENT == "test" else "/tmp/performance.har"
PW_SCREENSHOT_PATH = "./out/screenshot.jpg" if ENVIRONMENT == "test" else "/tmp/screenshot.jpg"

PW_CHROMIUM_ARGS = ["--disable-gpu",
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
