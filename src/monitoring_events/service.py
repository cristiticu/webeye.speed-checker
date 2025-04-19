import os
from datetime import datetime, timezone
from typing import Mapping
from playwright.sync_api import sync_playwright, Error
from uuid import UUID
from monitoring_events.exceptions import CurrentStatusNotFound
from monitoring_events.model import CurrentStatus, MonitoringEvent
from monitoring_events.persistence import MonitoringEventsPersistence
import settings


class MonitoringEventsService():
    def __init__(self, persistence: MonitoringEventsPersistence):
        self._events = persistence

    @classmethod
    def pw_extract_metrics(cls, url: str, check_string: str | None = None, timeout: float | None = None):
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=settings.PW_CHROMIUM_ARGS
            )
            context = browser.new_context(record_har_path=settings.PW_HAR_PATH)
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

                context.close()
                browser.close()

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

            page.screenshot(path=settings.PW_SCREENSHOT_PATH,
                            type="jpeg", quality=50)

            print("Created screenshot")

            context.close()
            browser.close()

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
        new_downtime_s_at = current.downtime_s_at

        if (current.status == "unknown" or current.status == "up") and event.status == "down":
            new_downtime_s_at = datetime.now(timezone.utc)
        if (current.status == "unknown" or current.status == "down") and event.status == "up":
            new_downtime_s_at = None

            # new_downtime = DowntimePeriod(
            #     u_guid=current.u_guid,
            #     url=current.url,
            #     s_at=current.downtime_s_at or datetime.now(timezone.utc),
            #     r_at=datetime.now(timezone.utc)
            # )
            # self._downtimes.persist(new_downtime)

        patched_status = CurrentStatus.model_validate({
            **current.model_dump(exclude_none=True),
            "status": new_status,
            "error": new_error,
            "downtime_s_at": new_downtime_s_at
        })

        self._events.persist(patched_status)
        return patched_status

    def check_webpage(self, u_guid: str, url: str, check_string: str | None = None, fail_on_status: list[str] = [], timeout: float | None = None):
        current = self.get_current_status_or_create(u_guid, url)

        extracted_metrics = self.pw_extract_metrics(url, check_string, timeout)

        status = "up"
        error = None

        if "error" in extracted_metrics:
            status = "down"
            error = extracted_metrics["error"]

        if check_string and not extracted_metrics["contains_check_string"]:
            status = "down"
            error = "Check string not found"

        if extracted_metrics["response_status"] in fail_on_status:
            status = "down"
            error = "Bad response status"

        event = MonitoringEvent(
            u_guid=UUID(u_guid),
            url=url,
            region=settings.AWS_REGION,
            status=status,
            results=extracted_metrics if status == "up" else None,
            error=error,
            c_at=datetime.now(timezone.utc)
        )

        self._events.persist(event)
        new_status = self.update_current_status(event, current)

        return {
            "current": new_status,
            "event": event
        }
