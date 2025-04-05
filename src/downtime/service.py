import requests
import time
from datetime import datetime, timezone
from typing import Mapping
from uuid import UUID
from downtime.exceptions import CurrentStatusNotFound
from downtime.model import CurrentStatus, DowntimeEvent, DowntimePeriod
from downtime.persistence import DowntimePersistence
import settings


class DowntimeService():
    def __init__(self, persistence: DowntimePersistence):
        self._downtimes = persistence

    def get_http_response(self, url: str) -> Mapping:
        with requests.Session() as session:
            session.max_redirects = 20

            try:
                start_time = time.time_ns() // 1_000_000
                response = session.head(url, timeout=10, allow_redirects=True)
                response_time = time.time_ns() // 1_000_000 - start_time

                if response.status_code >= 200 and response.status_code < 300:
                    return {
                        'status': 'up',
                        'response_time': response_time,
                        'status_code': response.status_code
                    }
                else:
                    if response.status_code >= 300 and response.status_code < 400:
                        error = "Too many redirects"
                    else:
                        error = "HTTP/S Error"

                    return {
                        'status': 'down',
                        'response_time': response_time,
                        'error': error,
                        'status_code': response.status_code
                    }
            except requests.RequestException as e:
                return {
                    "status": "down",
                    "error": str(e)
                }

    def get_current_status_or_create(self, user_guid: str, url: str, type: str):
        try:
            status = self._downtimes.get_current_status(user_guid, url, type)
        except CurrentStatusNotFound:
            status = CurrentStatus(
                user_guid=UUID(user_guid),
                url=url,
                check_type=type,
                last_checked_from="none",
                status="unknown")
            self._downtimes.persist(status)

        return status

    def update_current_status(self, event: DowntimeEvent, current: CurrentStatus):
        new_status = current.status
        new_added_at = current.added_at

        if (current.status == "unknown" or current.status == "up") and event.status == "down":
            new_status = "down"
            new_added_at = datetime.now(timezone.utc)
        if current.status == "unknown" and event.status == "up":
            new_status = "up"
            new_added_at = None
        if current.status == "down" and event.status == "up":
            new_status = "up"
            new_added_at = None

            new_downtime = DowntimePeriod(
                user_guid=current.user_guid,
                url=current.url,
                check_type=current.check_type,
                added_at=current.added_at or datetime.now(timezone.utc),
                resolved_at=datetime.now(timezone.utc)
            )
            self._downtimes.persist(new_downtime)

        patched_status = CurrentStatus.model_validate({
            **current.model_dump(exclude_none=True),
            "status": new_status,
            "added_at": new_added_at,
            "last_checked_from": settings.AWS_REGION
        })

        self._downtimes.persist(patched_status)
        return patched_status

    def run_http_uptime(self, user_guid: str, url: str):
        current = self.get_current_status_or_create(user_guid, url, "http")

        response = self.get_http_response(url)

        event = DowntimeEvent(
            user_guid=UUID(user_guid),
            url=url,
            check_type="http",
            status=response["status"],
            region=settings.AWS_REGION,
            response_time=response["response_time"] if "response_time" in response else None,
            error=response["error"] if "error" in response else None,
            added_at=datetime.now(timezone.utc)
        )

        self._downtimes.persist(event)
        new_status = self.update_current_status(event, current)

        return {
            "current": new_status,
            "event": event
        }
