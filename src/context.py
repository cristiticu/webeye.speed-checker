from monitoring_events.persistence import MonitoringEventsPersistence
from monitoring_events.service import MonitoringEventsService


class ApplicationContext():
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ApplicationContext, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self._monitoring_events_persistence = MonitoringEventsPersistence()
        self.events = MonitoringEventsService(
            self._monitoring_events_persistence)
