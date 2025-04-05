from downtime.exceptions import CurrentStatusNotFound
from downtime.model import CurrentStatus, DowntimeEvent, DowntimePeriod
from dynamodb import dynamodb_table
import settings


class DowntimePersistence():
    def __init__(self):
        self.downtimes = dynamodb_table(
            settings.DOWNTIMES_TABLE_NAME, settings.DOWNTIMES_TABLE_REGION)

    def persist(self, payload: DowntimeEvent | CurrentStatus | DowntimePeriod):
        self.downtimes.put_item(Item=payload.to_db_item())

    def get_current_status(self, user_guid: str, url: str, type: str):
        h_key = f"{user_guid}#{url}#{type}"

        response = self.downtimes.get_item(
            Key={"h_key": h_key, "s_key": "CURRENT"})
        item = response.get("Item")

        if item is None:
            raise CurrentStatusNotFound()

        return CurrentStatus.from_db_item(item)
