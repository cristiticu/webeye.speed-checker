import gzip
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from playwright.sync_api import sync_playwright, Error
from uuid import UUID

from monitoring_events.exceptions import CurrentStatusNotFound
from monitoring_events.model import CurrentStatus, MonitoringEvent
from monitoring_events.persistence import MonitoringEventsPersistence
import settings
from utils.bucket import s3_bucket


class MonitoringEventsService():
    def __init__(self, persistence: MonitoringEventsPersistence):
        self._events = persistence
        self._screenshots = s3_bucket(
            settings.SCREENSHOTS_BUCKET_NAME, settings.SCREENSHOTS_BUCKET_REGION)
        self._hars = s3_bucket(settings.HAR_BUCKET_NAME,
                               settings.HAR_BUCKET_REGION)

    def pw_extract_metrics(self, u_guid: str, w_guid: str, url: str, save_screenshot: bool, check_string: str | None = None, timeout: float | None = None):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=settings.PW_CHROMIUM_ARGS
            )
            context = browser.new_context(
                record_har_path=settings.PW_HAR_PATH, record_har_content="omit", record_har_omit_content=True)
            page = context.new_page()

            print("Launched playwright")

            dirname = os.path.dirname(__file__)

            page.add_init_script(
                path=os.path.join(dirname, "scripts/initialization.js"))

            print(f"Added observing script. Going to url {url}")

            response = None
            try:
                response = page.goto(url, wait_until="load", timeout=timeout)
            except Error as e:
                print(e.message)

                print("Closing context")
                context.close()

                print("Closing pages")
                pages = context.pages
                for page in pages:
                    page.close()

                return {
                    "error": e.message.splitlines()[0].replace("Page.goto: ", "")
                }

            contains_check_string = False
            if response and check_string:
                body = response.body().decode("utf-8")

                if check_string in body:
                    contains_check_string = True
                    print("Check string present")

            page.wait_for_timeout(3000)

            metrics = page.evaluate("window.__pwMetrics")
            metrics["contains_check_string"] = contains_check_string
            metrics["response_status"] = response.status if response else None

            print("Extracted metrics")

            if save_screenshot:
                screenshot_bytes = page.screenshot(path=settings.PW_SCREENSHOT_PATH,
                                                   type="jpeg", quality=40)
                self._screenshots.put_object(
                    Key=f"{u_guid}/{w_guid}.jpg", Body=screenshot_bytes, ContentType="image/jpeg")

                print("Created screenshot")

            print("Closing context")
            context.close()

            print("Closing pages")
            pages = context.pages
            for page in pages:
                page.close()

            print("Returning metrics")
            return metrics

    def get_current_status_or_create(self, u_guid: str, url: str):
        try:
            status = self._events.get_current_status(u_guid, url)
        except CurrentStatusNotFound:
            status = CurrentStatus(
                u_guid=UUID(u_guid),
                url=url,
                region=settings.AWS_REGION,
                status="unknown")
            self._events.persist(status)

        return status

    def update_current_status(self, event: MonitoringEvent, current: CurrentStatus):
        new_error = event.error
        new_status = event.status

        patched_status = CurrentStatus.model_validate({
            **current.model_dump(exclude_none=True),
            "status": new_status,
            "error": new_error,
            "m_at": event.c_at
        })

        self._events.persist(patched_status)

        return patched_status

    def export_har_to_s3(self, u_guid: str, w_guid: str, event: MonitoringEvent):
        with open(settings.PW_HAR_PATH, "r", encoding="utf-8") as raw_json:
            har_data = json.load(raw_json)

        har_data["log"]["creator"]["name"] = "Webeye, using Playwright"

        with gzip.open(settings.PW_HAR_PATH, "wt", encoding="utf-8") as gz_file:
            json.dump(har_data, gz_file, separators=(",", ":"))

        self._hars.upload_file(
            settings.PW_HAR_PATH,
            Key=f"{u_guid}/{w_guid}/{settings.AWS_REGION}/{event.c_at.isoformat().replace("+00:00", "Z")}.har.json.gz",
            ExtraArgs={"ContentType": "application/json",
                       "ContentEncoding": "gzip"}
        )

    def check_webpage(self, u_guid: str, w_guid: str, url: str, save_screenshot: bool, accepted_status: list[str], retention_days: int, check_string: str | None = None, timeout: float | None = None):
        current = self.get_current_status_or_create(u_guid, url)

        extracted_metrics: Any = self.pw_extract_metrics(
            u_guid,
            w_guid,
            url,
            save_screenshot,
            check_string,
            timeout)

        print(extracted_metrics)

        status = "up"
        error = None
        accepted_status_code_prefixes = [
            int(status[0]) for status in accepted_status]

        if "error" in extracted_metrics:
            status = "down"
            error = extracted_metrics["error"]

        elif check_string and not extracted_metrics["contains_check_string"]:
            status = "down"
            error = "Check string not found"

        elif extracted_metrics["response_status"] and not ((extracted_metrics["response_status"] / 100) in accepted_status_code_prefixes):
            status = "down"
            error = f"Bad response status code: {extracted_metrics["response_status"]}"

        event = MonitoringEvent(
            u_guid=UUID(u_guid),
            url=url,
            region=settings.AWS_REGION,
            status=status,
            results=extracted_metrics if status == "up" else None,
            error=error,
            ttl=int((datetime.now() + timedelta(days=retention_days)).timestamp()),
            c_at=datetime.now(timezone.utc),
        )

        print("Event:", event)

        self._events.persist(event)
        new_status = self.update_current_status(event, current)

        if event.status == "up":
            self.export_har_to_s3(u_guid, w_guid, event)

        return {
            "current": new_status,
            "event": event
        }
