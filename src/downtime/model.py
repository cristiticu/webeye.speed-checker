from datetime import datetime
from typing import Mapping
from pydantic import UUID4, BaseModel


class DowntimePeriod(BaseModel):
    user_guid: UUID4
    url: str
    check_type: str
    added_at: datetime
    resolved_at: datetime

    def to_db_item(self):
        h_key = f"{self.user_guid}#{self.url}#{self.check_type}"
        s_key = f"DOWNTIME#{self.added_at.isoformat().replace("+00:00", "Z")}"

        return {
            "metatype": "downtime",
            "h_key": h_key,
            "s_key": s_key,
            "resolved_at": self.resolved_at.isoformat().replace("+00:00", "Z")
        }

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")
        split_s_key = item["s_key"].split("#")

        item_payload = {
            **item,
            "user_guid": split_h_key[0],
            "url": split_h_key[1],
            "check_type": split_h_key[2],
            "added_at": split_s_key[1]
        }

        return DowntimePeriod.model_validate(item_payload)


class DowntimeEvent(BaseModel):
    user_guid: UUID4
    url: str
    check_type: str
    status: str
    region: str
    response_time: int | None = None
    error: str | None = None
    added_at: datetime

    def to_db_item(self):
        h_key = f"{self.user_guid}#{self.url}#{self.check_type}"
        s_key = f"EVENT#{self.added_at.isoformat().replace("+00:00", "Z")}"

        return {
            "metatype": "event",
            "h_key": h_key,
            "s_key": s_key,
            "status": self.status,
            "region": self.region,
            "response_time": self.response_time,
            "error": self.error,
        }

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")
        split_s_key = item["s_key"].split("#")

        item_payload = {
            **item,
            "user_guid": split_h_key[0],
            "url": split_h_key[1],
            "check_type": split_h_key[2],
            "added_at": split_s_key[1]
        }

        return DowntimeEvent.model_validate(item_payload)


class CurrentStatus(BaseModel):
    user_guid: UUID4
    url: str
    check_type: str
    last_checked_from: str
    status: str
    added_at: datetime | None = None

    def to_db_item(self):
        h_key = f"{self.user_guid}#{self.url}#{self.check_type}"

        return {
            "metatype": "current",
            "h_key": h_key,
            "s_key": "CURRENT",
            "last_checked_from": self.last_checked_from,
            "added_at": self.added_at.isoformat().replace("+00:00", "Z") if self.added_at else None,
            "status": self.status
        }

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")

        item_payload = {
            **item,
            "user_guid": split_h_key[0],
            "url": split_h_key[1],
            "check_type": split_h_key[2],
        }

        return CurrentStatus.model_validate(item_payload)
