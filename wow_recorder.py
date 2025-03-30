import datetime
import os.path
import shutil
from enum import Enum
from time import sleep

from obs.obs_control import OBSController
from wow.wow_control import WoWController
from wow.wow_log_parser import parse_wow_log_line

# ENCOUNTER_START,2847,"Captain Dailcry",8,5,2649    encID, encName, DiffID, players
# ENCOUNTER_END,2847,"Captain Dailcry",8,5,1,131971  encID, cndName, diffID, players, success?

# 3/27/2025 20:18:45.3771  ENCOUNTER_START,2922,"Queen Ansurek",16,20,2657
# 3/27/2025 20:19:49.9681  ENCOUNTER_END,2922,"Queen Ansurek",16,20,0,64568

# 3/27/2025 20:19:21.7261  UNIT_DIED,0000000000000000,nil,0x80000000,0x80000000,Player-3713-0A9BCB2E,"Mogniania-BurningLegion-EU",0x40514,0x0,0
# 3/27/2025 20:19:17.0561  UNIT_DIED,0000000000000000,nil,0x80000000,0x80000000,Creature-0-3894-2657-19648-163366-000065A4AE,"Magus of the Dead",0x2112,0x0,0

# 3/27/2025 23:12:56.2881  CHALLENGE_MODE_END,2649,0,0,0,0.000000,0.000000
# 3/27/2025 23:12:56.4561  CHALLENGE_MODE_START,"Priory of the Sacred Flame",2649,499,10,[160,10,9]
# 3/27/2025 23:39:27.4231  CHALLENGE_MODE_END,2649,1,10,1602330,326.685974,2683.563965

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


def make_file_name(activity):
    result = 'none'
    activity_type = 'none'

    if activity.activity_type == ActivityType.M_PLUS:
        activity_type = 'M_PLUS'
        if activity.success:
            result = 'timed'
        else:
            result = 'burned'
    if activity.activity_type == ActivityType.RAID:
        activity_type = 'RAID'
        if activity.success:
            result = 'kill'
        else:
            result = 'wipe'


    return f"{activity.start_time.strftime(f'%Y-%m-%d__%H-%M-%S')}__{activity_type}__{activity.name}__{activity.name}__{result}.mkv"


class Recorder:
    def __init__(self, obs_controller: OBSController, wow_controller: WoWController, recording_target_folder: str, death_delay_seconds = 3):
        
        self.death_delay_seconds = death_delay_seconds
        self.recording_target_folder = recording_target_folder
        self.wow_controller = wow_controller
        self.obs_controller = obs_controller

        self.activity = None

    # main loop
    def start(self):
        self.obs_controller.connect()
        while True:
            log_line = self.wow_controller.get_log_line()
            if len(log_line) > 0:
                result = parse_wow_log_line(log_line)
                self.handle_wow_line(result)
            else:
                if self.activity is None:
                    # idle 1 second and try to get log event again
                    sleep(1)

    def start_activity(self, activity: Activity):
        if self.is_recording():
            print("Activity already in progress, cannot start new one")
            return

        self.activity = activity
        self.obs_controller.start_recording()
        print("Recording started {0}".format(self.activity))

    def end_activity(self, success):
        if not self.is_recording():
            print("Cannot end non-active Activity")
            return

        self.activity.success = success
        recording_path = self.obs_controller.end_recording()
        print("Recording finished {0}, OBS result {1}".format(self.activity, recording_path))
        self.handle_recording(recording_path)
        self.activity = None

    def handle_recording(self, recording_path):
        if not os.path.exists(self.recording_target_folder):
            os.makedirs(self.recording_target_folder)

        dest_file_name = make_file_name(self.activity)
        dest_file_path = os.path.join(self.recording_target_folder, dest_file_name)
        shutil.move(recording_path, dest_file_path)


        dest_event_file_path = dest_file_path.replace('.mkv', '.evt')
        f = open(dest_event_file_path, "w+")
        for e in self.activity.events:
            f.write(f"{e['time']}\t{e['event']}")
        f.close()


    def is_recording(self):
        return self.activity is not None

    def handle_wow_line(self, result):
        timestamp = result["timestamp"]
        match result["type"]:
            case 'CHALLENGE_MODE_START':
                name = str(result["rest"][1]).replace('"','')
                key_lvl = int(result["rest"][4])
                self.start_activity(Activity(ActivityType.M_PLUS, name, 5, key_lvl))
            case 'CHALLENGE_MODE_END':
                success = int(result["rest"][2]) > 0
                self.end_activity(success)
            case 'ENCOUNTER_START':
                difficulty_id = int(result["rest"][3])
                encounter_name = result["rest"][2].replace('"','')
                if difficulty_id == 16: #mythic raid
                    self.start_activity(Activity(ActivityType.RAID, encounter_name, 20))
                if difficulty_id == 8: #mythinc dungeon
                    if self.is_recording():
                        self.activity.add_event(timestamp, "Boss start: {0}".format(encounter_name))
            case 'ENCOUNTER_END':
                encounter_name = result["rest"][2].replace('"','')
                difficulty_id = int(result["rest"][3])
                success = int(result["rest"][5]) > 0
                if difficulty_id == 16: #mythic raid
                    self.end_activity(success)
                if difficulty_id == 8: #mythinc dungeon
                    if self.is_recording():
                        if success:
                            self.activity.add_event(timestamp, "Boss kill: {0}".format(encounter_name))
                        else:
                            self.activity.add_event(timestamp, "Boss wipe: {0}".format(encounter_name))
            case 'ZONE_CHANGE':
                if self.is_recording():
                    if self.activity.activity_type == ActivityType.M_PLUS:
                        # abandoned key
                        self.end_activity(False)
            case 'UNIT_DIED':
                if self.is_recording():
                    if str(result["rest"][5]).startswith("Player-"):
                        dead_player = result["rest"][6]
                        self.activity.add_event(timestamp - datetime.timedelta(seconds=self.death_delay_seconds), "Death: {0}".format(dead_player))





