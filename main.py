import sys
from time import sleep

import datetime

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, is_running_in_ide, ASCIISpinner
from wow_recorder import Recorder
from wow.wow_control import WoWController

#configureation
host = 'localhost'
port = 4455
password = 'zbnfiosglNUQTbjJ'
log_folder = '/home/bigos/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/'
output_path = '/home/bigos/Capture/recorder/'
death_delay_seconds = 3

wow_controller = WoWController(log_folder)
obs_controller = OBSController(host, port, password)

recorder = Recorder(obs_controller, wow_controller, output_path, death_delay_seconds)
recorder.obs_controller.connect()

if is_running_in_ide():
    while True:
        recorder.process()
        if recorder.last_message is not None:
            print(recorder.last_message)
            recorder.last_message = None
else:
    try:
        hide_cursor()
        spinner = ASCIISpinner()
        while True:
            recorder.process()
            print(f"[{spinner.get_spinner()}] WOW RECORDER - PYTHON EDITION (c) bigos 2025")
            print(f"Time: {datetime.datetime.now()}")
            print(f"Log file: {recorder.wow_controller.log_file_name}")
            print(f"Is recording: {recorder.is_recording()}")
            print(f"Activity: {str(recorder.activity)}")
            print(f"Last message: {recorder.last_message}")
            print('\033[6A\033[2K', end='')
            sleep(0.25)
    finally:
        show_cursor()