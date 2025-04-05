from typing import Any
from aws_lambda_typing.context import Context

from context import ApplicationContext

application_context = ApplicationContext()


def lambda_handler(event: dict[str, Any], context: Context) -> dict[str, Any]:
    user_guid = event["user_guid"]
    url = event["url"]
    check_type = event["check_type"]

    result = None

    if check_type == "http":
        result = application_context.downtimes.run_http_uptime(user_guid, url)

    if result != None:
        return {
            "statusCode": 200,
            "body": "Completed check",
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 400,
            "body": "Bad Request. No result",
            "headers": {
                "Content-Type": "application/json"
            }
        }
