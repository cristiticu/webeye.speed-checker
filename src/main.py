from typing import Any
from aws_lambda_typing.context import Context

from context import ApplicationContext

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    u_guid = event["u_guid"]
    url = event["url"]

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
