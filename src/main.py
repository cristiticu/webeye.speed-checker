import json
from typing import Any
from aws_lambda_typing.context import Context

from context import ApplicationContext
import settings

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    u_guid = event["u_guid"]
    url = event["url"]
    check_string = event["c_str"] if "c_str" in event else None
    fail_on_status = event["fail_status"] if "fail_status" in event else []
    timeout = event["timeout"] if "timeout" in event else None
    save_screenshot = event["screenshot"] if "screenshot" in event else False

    try:
        application_context.events.check_webpage(
            u_guid, url, save_screenshot, check_string, fail_on_status, timeout)

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


TARGET_URL = "https://www.cs.ubbcluj.ro"


if __name__ == "__main__":
    if settings.ENVIRONMENT == "test":
        results = application_context.events.check_webpage("fb8b90bc-6015-4b46-8e6a-c2bb178d97f6",
                                                           TARGET_URL, True, "<!DOCTYPE html", [400, 500, 404], None)

        print(json.dumps(results["event"].to_db_item(), indent=2))
