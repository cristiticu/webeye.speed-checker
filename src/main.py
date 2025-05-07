import json
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from aws_lambda_typing.context import Context

from context import ApplicationContext
import settings

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: "Context") -> dict[str, Any]:
    u_guid = event["u_guid"]
    w_guid = event["w_guid"]
    url = event["url"]
    check_string = event["c_str"] if "c_str" in event else settings.EVENT_DEFAULT_CHECK_STRING
    accepted_status = event["accepted_status"] if "accepted_status" in event else settings.EVENT_DEFAULT_ACCEPTED_STATUS
    timeout = event["timeout"] if "timeout" in event else settings.EVENT_DEFAULT_TIMEOUT
    save_screenshot = event["screenshot"] if "screenshot" in event else False
    retention_days = event["retention_days"] if "retention_days" in event else settings.EVENT_DEFAULT_RETENTION_DAYS

    try:
        application_context.events.check_webpage(
            u_guid, w_guid, url, save_screenshot, accepted_status,
            retention_days, check_string, timeout)

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


if __name__ == "__main__":
    if settings.ENVIRONMENT == "test":
        results = application_context.events.check_webpage(
            "fb8b90bc-6015-4b46-8e6a-c2bb178d97f6", "7cc424bb-516f-45b3-8693-9f98e0c6edf7", "https://cs.ubbcluj.ro", True, ['2xx', '3xx'], 1, "<!DOCTYPE html", None)

        print(json.dumps(results["event"].to_db_item(), indent=2))
