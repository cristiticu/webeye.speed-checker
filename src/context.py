from downtime.persistence import DowntimePersistence
from downtime.service import DowntimeService


class ApplicationContext():
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ApplicationContext, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._downtimes_persistence = DowntimePersistence()
        self.downtimes = DowntimeService(
            self._downtimes_persistence)
