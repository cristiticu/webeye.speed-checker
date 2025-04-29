from monitoring_events.exceptions import CurrentStatusNotFound
from monitoring_events.model import CurrentStatus, MonitoringEvent
from utils.dynamodb import dynamodb_table
import settings


class MonitoringEventsPersistence():
    def __init__(self):
        self.events = dynamodb_table(
            settings.MONITORING_EVENTS_TABLE_NAME, settings.MONITORING_EVENTS_TABLE_REGION)

    def persist(self, payload: MonitoringEvent | CurrentStatus):
        self.events.put_item(Item=payload.to_db_item())

    def get_current_status(self, u_guid: str, url: str):
        h_key = f"{u_guid}#{url}"
        s_key = f"CURRENT#{settings.AWS_REGION}"

        response = self.events.get_item(
            Key={"h_key": h_key, "s_key": s_key})
        item = response.get("Item")

        if item is None:
            raise CurrentStatusNotFound()

        return CurrentStatus.from_db_item(item)
