"""Class controlling OBS Studio via web socket"""
import datetime
import os.path
import shutil
import time
from enum import Enum
from time import sleep

from obs.obs_control import OBSController
from wow.wow_control import WoWController
from wow.wow_log_parser import parse_wow_log_line


class ActivityType(Enum):
    """Type of activity"""
    M_PLUS = 1
    RAID = 2


class Activity:
    """Represents activity that the recorder is recording"""
    def __init__(self, activity_type: ActivityType, name, player_count, key_level=0):
        self.key_level = key_level
        self.player_count = player_count
        self.name = name
        self.activity_type = activity_type
        self.start_time = datetime.datetime.now()
        self.events = list[dict[str, str]]()
        self.success = False

    def __str__(self):
        """ToString"""
        return f"{str(self.activity_type)}, {self.name} ({len(self.events)})"

    def add_event(self, timestamp: datetime.datetime, event: str):
        """Adds event to activity"""
        delta = timestamp - self.start_time
        total_minute, second = divmod(delta.seconds, 60)
        hour, minute = divmod(total_minute, 60)
        relative_time = f"{hour:02}:{minute:02}:{second:02}"
        event_to_add = {"time": relative_time, "event": event}
        self.events.append(event_to_add)


def make_file_name(activity):
    """Creates file name appropriate for given activity"""
    result = 'none'
    activity_type = 'none'

    if activity.activity_type == ActivityType.M_PLUS:
        activity_type = 'M_PLUS'
        duration = (datetime.datetime.now() - activity.start_time).total_seconds() / 60
        result = f"{activity.key_level}__{int(duration)}_min"
    if activity.activity_type == ActivityType.RAID:
        activity_type = 'RAID'
        if activity.success:
            result = 'kill'
        else:
            result = 'wipe'


    return (f"{activity.start_time.strftime('%Y-%m-%d__%H-%M-%S')}__{activity_type}"
            f"__{activity.name}__{result}.mkv").replace(' ', '_')


def get_file_extension(dest_file_name):
    """Gets file extension from path"""
    chunks = dest_file_name.split('.')
    if len(chunks) > 1:
        return chunks[-1]
    return ''

class RecorderConfiguration:
    """Configuration class containing various recorder settings"""
    def __init__(self, recording_target_folder: str, death_delay_seconds = 3,
                 linger_time_seconds = 5, boss_reset = 30):
        self.boss_reset = boss_reset
        self.linger_time_seconds = linger_time_seconds
        self.death_delay_seconds = death_delay_seconds
        self.recording_target_folder = recording_target_folder

    def is_valid(self):
        """Validates configuration to be usable or not"""
        return True

    def __str__(self):
        return (f"reset: {self.boss_reset}; linger: {self.linger_time_seconds}; "
                f"delay: {self.death_delay_seconds}; target: {self.recording_target_folder}")


class Recorder:
    """Main WoW Recorder class processing the data from wow controller and steering
    obs with obs controller classes"""
    def __init__(self, obs_controller: OBSController, wow_controller: WoWController,
                 configuration: RecorderConfiguration):
        self.configuration = configuration
        self.message_log = list[dict[str, str]]()
        self.message_log_len = 10
        self.wow_controller = wow_controller
        self.obs_controller = obs_controller

        self.activity = None

    def get_activity(self) -> Activity:
        if self.activity is not None:
            return self.activity
        raise ValueError("Activity not set")

    def process(self):
        """Performs single pass of processing, should be run in infinite loop"""
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


    def start_activity(self, activity: Activity):
        """Starts Activity"""
        if self.is_recording():
            self.add_message("Activity already in progress, cannot start new one")
            return

        self.activity = activity # type: ignore
        self.obs_controller.start_recording()
        self.add_message(f"Recording started {self.activity}")

    def end_activity(self, success):
        """Ends activity with given success result"""
        if not self.is_recording():
            self.add_message("Cannot end non-active Activity")
            return
        self.activity.success = success

        if self.configuration.linger_time_seconds > 0:
            self.add_message(f"Lingering recording time by "
                             f"{self.configuration.linger_time_seconds} seconds...")
            time.sleep(self.configuration.linger_time_seconds)

        recording_path = self.obs_controller.end_recording()
        self.add_message(f"Recording finished: {recording_path}")
        self.handle_recording(recording_path)
        self.activity = None

    def handle_recording(self, recording_path):
        """Handles recording file after Activity is finished"""
        recording_duration = (datetime.datetime.now() - self.activity.start_time).total_seconds()
        if recording_duration < self.configuration.boss_reset:
            self.add_message(f"Recording is only {recording_duration} seconds long, assuming reset")
            os.remove(recording_path)
            return

        if not os.path.exists(self.configuration.recording_target_folder):
            os.makedirs(self.configuration.recording_target_folder)

        dated_dest_folder = os.path.join(self.configuration.recording_target_folder,
                                         datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(dated_dest_folder):
            os.makedirs(dated_dest_folder)

        dest_file_name = make_file_name(self.activity)
        dest_file_path = os.path.join(dated_dest_folder, dest_file_name)
        shutil.move(recording_path, dest_file_path)

        file_extension = get_file_extension(dest_file_name)
        dest_event_file_path = dest_file_path.replace(file_extension, '.evt')
        with open(dest_event_file_path, "w+", encoding='UTF-8') as f:
            for e in self.activity.events:
                f.write(f"{e['time']}\t{e['event']}\n")


    def is_recording(self):
        """Indicates whether a recording is being performed"""
        return self.activity is not None

    def handle_wow_line(self, result) -> None:
        """Handles WOW log line, preformatted via wow parser"""
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
                        self.get_activity().add_event(timestamp, f"Boss start: {encounter_name}")
            case 'ENCOUNTER_END':
                encounter_name = result["rest"][2].replace('"','')
                difficulty_id = int(result["rest"][3])
                success = int(result["rest"][5]) > 0
                if difficulty_id == 16: #mythic raid
                    self.end_activity(success)
                if difficulty_id == 8: #mythinc dungeon
                    if self.is_recording():
                        if success:
                            self.get_activity().add_event(timestamp,
                                                    f"Boss kill: {encounter_name}")
                        else:
                            self.get_activity().add_event(timestamp,
                                                    f"Boss wipe: {encounter_name}")
            case 'ZONE_CHANGE':
                if self.is_recording():
                    if self.get_activity().activity_type == ActivityType.M_PLUS:
                        # abandoned key
                        self.end_activity(False)
            case 'UNIT_DIED':
                if self.is_recording():
                    if str(result["rest"][5]).startswith("Player-"):
                        dead_player = result["rest"][6].replace('"','')
                        self.get_activity().add_event(timestamp -
                                                datetime.timedelta(
                                                    seconds=self.configuration.death_delay_seconds),
                                                f"Death: {dead_player}")

    def add_message(self, message: str) -> None:
        """Adds message to the message log, if message log is full, removes
        oldest message and adds a new one at the end"""
        if len(self.message_log) == self.message_log_len:
            self.message_log.pop(0)
        self.message_log.append({"time": datetime.datetime.now().strftime('%H:%M:%S'),
                                 "msg": message})
