import datetime
from enum import Enum


class ActivityType(Enum):
    M_PLUS = 1
    RAID = 2


class Activity:
    def __init__(self, activity_type: ActivityType, name, player_count, key_level=0):
        self.key_level = key_level
        self.player_count = player_count
        self.name = name
        self.activity_type = activity_type
        self.start_time = datetime.datetime.now()
        self.events = []
        self.success = False

    def __str__(self):
        return str({"activity_type": self.activity_type, "player_count": self.player_count, "name": self.name, "start_time": str(self.start_time), "success": self.success, "events": len(self.events)})

    def add_event(self, timestamp: datetime.datetime, event: str):
        delta = self.start_time - timestamp
        relative_time = delta.total_seconds()
        event = {"time": relative_time, "event": event}
        self.events.append(event)
        print("Added event: {0}".format(event))

