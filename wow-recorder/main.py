#!/usr/bin/python
import sys

import datetime
import logging

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, is_running_in_ide, ASCIISpinner
from wow_recorder import Recorder
from config import RecorderConfiguration
from wow.wow_control import WoWController

def str_ellipsis(msg: str, cnt: int):
    final = msg
    if len(msg) > cnt:
        final = msg[0:cnt-4] + '...'
    return final


def main():
    logging.getLogger('obsws_python.baseclient.ObsClient').disabled = True
    conf = None

    cfg_file = 'wow_recorder_py.cfg'
    if len(sys.argv) > 1:
        cfg_file = sys.argv[1]

    # configuration
    try:
        conf = RecorderConfiguration(cfg_file)
        conf.validate_config()
    except Exception as e:
        print(f"Configuration issue: {str(e)}. Press any key to exit...")
        input()
        exit(1)

    host = conf.get_obs_host()
    port = conf.get_obs_port()
    password = conf.get_obs_password()
    log_folder = conf.get_wow_log_folder()
    output_path = conf.get_recorder_output_path()
    death_delay_seconds = conf.get_recorder_death_delay()
    linger_time = conf.get_recorder_linger_time()
    reset_time = conf.get_recorder_reset_time()

    wow_controller = WoWController(log_folder)
    obs_controller = OBSController(host, port, password)

    recorder = Recorder(obs_controller, wow_controller, output_path, death_delay_seconds, linger_time, reset_time)

    try:
        hide_cursor()
        spinner = ASCIISpinner()
        while True:
            print('\033[25A\033[2K', end='')
            recorder.process()
            print(f"                                                                       ")
            print(f"             ┓ ┏┏┓┓ ┏  ┳┓┏┓┏┓┏┓┳┓┳┓┏┓┳┓                  python powered")
            print(f"             ┃┃┃┃┃┃┃┃  ┣┫┣ ┃ ┃┃┣┫┃┃┣ ┣┫                  cross-platform")
            print(f"             ┗┻┛┗┛┗┻┛  ┛┗┗┛┗┛┗┛┛┗┻┛┗┛┛┗                web-socket based")
            print(f"--+--------------------------------------------------------------------")
            print(f"S | [{spinner.get_spinner()}] Time:     {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}")
            print(str_ellipsis(f"T | OBS Studio:   {str(recorder.obs_controller.connected)}", 70).ljust(70))
            print(str_ellipsis(f"A | Log file:     {recorder.wow_controller.log_file_name}", 70).ljust(70))
            print(str_ellipsis(f"T | Is recording: {recorder.is_recording()}", 70).ljust(70))
            print(str_ellipsis(f"E | Activity:     {str(recorder.activity)}", 70).ljust(70))
            print(f"--+--------------------------------------------------------------------")
            # 13 lines available
            i = 0
            for msg in recorder.message_log:
                print(f"{msg['time']}: {str_ellipsis(msg['msg'], 62)}".ljust(70))
                i = i + 1
            print('\033[25A\033[2K', end='')

    finally:
        show_cursor()

if __name__ == "__main__":
    main()
