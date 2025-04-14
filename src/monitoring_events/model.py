from datetime import datetime
from typing import Mapping
from pydantic import UUID4, BaseModel


class DowntimePeriod(BaseModel):
    u_guid: UUID4
    url: str
    region: str
    s_at: datetime
    r_at: datetime

    def to_db_item(self):
        h_key = f"{self.u_guid}#{self.url}"
        s_key = f"DOWNTIME#{self.s_at.isoformat().replace("+00:00", "Z")}"

        return {
            "h_key": h_key,
            "s_key": s_key,
            "r_at": self.r_at.isoformat().replace("+00:00", "Z")
        }


class DowntimeEvent(BaseModel):
    u_guid: UUID4
    url: str
    region: str
    status: str
    r_time: int | None = None
    error: str | None = None
    c_at: datetime

    def to_db_item(self):
        h_key = f"{self.u_guid}#{self.url}"
        s_key = f"EVENT#{self.c_at.isoformat().replace("+00:00", "Z")}"

        return {
            "h_key": h_key,
            "s_key": s_key,
            "status": self.status,
            "region": self.region,
            "r_time": self.r_time,
            "error": self.error,
        }


class CurrentStatus(BaseModel):
    u_guid: UUID4
    url: str
    region: str
    status: str
    downtime_s_at: datetime | None = None

    def to_db_item(self):
        h_key = f"{self.u_guid}#{self.url}"
        s_key = f"CURRENT#{self.region}"

        return {
            "h_key": h_key,
            "s_key": s_key,
            "status": self.status,
            "downtime_s_at": self.downtime_s_at.isoformat().replace("+00:00", "Z") if self.downtime_s_at else None,
        }

    @classmethod
    def from_db_item(cls, item: Mapping):
        split_h_key = item["h_key"].split("#")
        split_s_key = item["s_key"].split("#")

        item_payload = {
            **item,
            "u_guid": split_h_key[0],
            "url": split_h_key[1],
            "region": split_s_key[1]
        }

        return CurrentStatus.model_validate(item_payload)
