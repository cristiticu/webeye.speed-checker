import requests
import time
from datetime import datetime, timezone
from typing import Mapping
from uuid import UUID
from monitoring_events.exceptions import CurrentStatusNotFound
from monitoring_events.model import CurrentStatus, DowntimeEvent
from monitoring_events.persistence import MonitoringEventsPersistence
import settings


class MonitoringEventsService():
    def __init__(self, persistence: MonitoringEventsPersistence):
        self._events = persistence

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

    def update_current_status(self, event: DowntimeEvent, current: CurrentStatus):
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
            "downtime_s_at": new_downtime_s_at
        })

        self._events.persist(patched_status)
        return patched_status

    def check_webpage(self, u_guid: str, url: str):
        current = self.get_current_status_or_create(u_guid, url)

        response = self.get_http_response(url)

        event = DowntimeEvent(
            u_guid=UUID(u_guid),
            url=url,
            region=settings.AWS_REGION,
            status=response["status"],
            r_time=response["response_time"] if "response_time" in response else None,
            error=response["error"] if "error" in response else None,
            c_at=datetime.now(timezone.utc)
        )

        self._events.persist(event)
        new_status = self.update_current_status(event, current)

        return {
            "current": new_status,
            "event": event
        }
