import json
from typing import Any
from aws_lambda_typing.context import Context

from context import ApplicationContext
from monitoring_events.service import MonitoringEventsService
import settings

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    u_guid = event["u_guid"]
    url = event["url"]
    check_string = event["c_str"]
    fail_on_status = event["fail_status"]
    timeout = event["timeout"]

    try:
        application_context.events.check_webpage(
            u_guid, url, check_string, fail_on_status, timeout)

        return {
            "statusCode": 200,
            "body": "Completed check",
            "headers": {
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        print(e)

        return {
            "statusCode": 400,
            "body": "Bad Request. No result",
            "headers": {
                "Content-Type": "application/json"
            }
        }


TARGET_URL = "https://weather.cristit.icu"


if __name__ == "__main__":
    if settings.ENVIRONMENT == "test":
        results = MonitoringEventsService.pw_extract_metrics(
            TARGET_URL, "<!DOCTYPE html>", 15000)
        print(json.dumps(results, indent=2))
