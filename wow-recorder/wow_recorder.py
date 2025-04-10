import datetime
import os.path
import shutil
import time
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
        return str({"Type": self.activity_type, "Start": str(self.start_time), "Event count": len(self.events)})

    def add_event(self, timestamp: datetime.datetime, event: str):
        delta = timestamp - self.start_time
        total_minute, second = divmod(delta.seconds, 60)
        hour, minute = divmod(total_minute, 60)
        relative_time = f"{hour:02}:{minute:02}:{second:02}"
        event = {"time": relative_time, "event": event}
        self.events.append(event)


def make_file_name(activity):
    result = 'none'
    activity_type = 'none'

    if activity.activity_type == ActivityType.M_PLUS:
        activity_type = 'M_PLUS'
        duration = (datetime.datetime.now() - activity.start_time).total_seconds() / 60
        result = f"{int(duration)}_min"
    if activity.activity_type == ActivityType.RAID:
        activity_type = 'RAID'
        if activity.success:
            result = 'kill'
        else:
            result = 'wipe'


    return f"{activity.start_time.strftime(f'%Y-%m-%d__%H-%M-%S')}__{activity_type}__{activity.name}__{result}.mkv".replace(' ', '_')


def get_file_extension(dest_file_name):
    chunks = dest_file_name.split('.')
    if len(chunks) > 1:
        return chunks[-1]
    return ''

class Recorder:
    def __init__(self, obs_controller: OBSController, wow_controller: WoWController, recording_target_folder: str, death_delay_seconds = 3, linger_time_seconds = 5):
        
        self.message_log = []
        self.message_log_len = 10
        self.linger_time_seconds = linger_time_seconds
        self.death_delay_seconds = death_delay_seconds
        self.recording_target_folder = recording_target_folder
        self.wow_controller = wow_controller
        self.obs_controller = obs_controller

        self.activity = None

    def process(self):
        if not self.obs_controller.connected:
            if not self.obs_controller.connect():
                self.add_message("Cannot connect to OBS, waiting 3 seconds to retry...")
                sleep(3)
            else:
                self.add_message("Connection to OBS successful")

        log_line = self.wow_controller.get_log_line()
        if len(log_line) > 0:
            # self.last_message = log_line
            result = parse_wow_log_line(log_line)
            if result is not None:
                self.handle_wow_line(result)
        else:
            if self.activity is None:
                # idle 1 second and try to get log event again
                sleep(0)


    # main loop
    def start(self):
        self.obs_controller.connect()
        while True:
            self.process()

    def start_activity(self, activity: Activity):
        if self.is_recording():
            self.add_message("Activity already in progress, cannot start new one")
            return

        self.activity = activity
        self.obs_controller.start_recording()
        self.add_message("Recording started {0}".format(self.activity))

    def end_activity(self, success):
        if not self.is_recording():
            self.add_message("Cannot end non-active Activity")
            return
        self.activity.success = success

        if self.linger_time_seconds > 0:
            self.add_message(f"Lingering recording time by {self.linger_time_seconds} seconds...")
            time.sleep(self.linger_time_seconds)

        recording_path = self.obs_controller.end_recording()
        self.add_message("Recording finished: {0}".format(recording_path))
        self.handle_recording(recording_path)
        self.activity = None

    def handle_recording(self, recording_path):
        if (datetime.datetime.now() - self.activity.start_time).total_seconds() < 30:
            #boss reset
            os.remove(recording_path)
            return
        if not os.path.exists(self.recording_target_folder):
            os.makedirs(self.recording_target_folder)

        dated_dest_folder = os.path.join(self.recording_target_folder, datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(dated_dest_folder):
            os.makedirs(dated_dest_folder)

        dest_file_name = make_file_name(self.activity)
        dest_file_path = os.path.join(dated_dest_folder, dest_file_name)
        shutil.move(recording_path, dest_file_path)

        file_extension = get_file_extension(dest_file_name)
        dest_event_file_path = dest_file_path.replace(file_extension, '.evt')
        f = open(dest_event_file_path, "w+")
        for e in self.activity.events:
            f.write(f"{e['time']}\t{e['event']}\n")
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
                        dead_player = result["rest"][6].replace('"','')
                        self.activity.add_event(timestamp - datetime.timedelta(seconds=self.death_delay_seconds), "Death: {0}".format(dead_player))

    def add_message(self, message):
        if len(self.message_log) == self.message_log_len:
            self.message_log.pop(0)
        self.message_log.append({"time": datetime.datetime.now().strftime('%H:%M:%S'), "msg": message})
