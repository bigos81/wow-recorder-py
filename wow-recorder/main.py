"""Main entry point of application"""
#!/usr/bin/python
import sys

import datetime
import logging

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, ASCIISpinner
from wow_recorder import Recorder, RecorderConfiguration
from config import RecorderConfigurationFile
from wow.wow_control import WoWController


def str_ellipsis(msg: str, cnt: int):
    """Shortens the string and ass ... at the end"""
    final = msg
    if len(msg) > cnt:
        final = msg[0:cnt-4] + '...'
    return final


def main():
    """Main app function"""
    logging.getLogger('obsws_python.baseclient.ObsClient').disabled = True
    conf = None

    cfg_file = 'wow_recorder_py.cfg'
    if len(sys.argv) > 1:
        cfg_file = sys.argv[1]

    # configuration
    try:
        conf = RecorderConfigurationFile(cfg_file)
        conf.validate_config()
    except Exception as e:
        print(f"Configuration issue: {str(e)}. Press any key to exit...")
        input()
        sys.exit(1)

    output_path = conf.get_recorder_output_path()
    death_delay_seconds = conf.get_recorder_death_delay()
    linger_time = conf.get_recorder_linger_time()
    reset_time = conf.get_recorder_reset_time()


    wow_controller = WoWController(conf.get_wow_log_folder())
    obs_controller = OBSController(conf.get_obs_host(),
                                   conf.get_obs_port(),
                                   conf.get_obs_password())

    recorder = Recorder(obs_controller, wow_controller,
                        RecorderConfiguration(output_path, death_delay_seconds, linger_time, reset_time))

    try:
        hide_cursor()
        spinner = ASCIISpinner()
        while True:
            print('\033[25A\033[2K', end='')
            recorder.process()
            print("                                                                       ")
            print("             ┓ ┏┏┓┓ ┏  ┳┓┏┓┏┓┏┓┳┓┳┓┏┓┳┓                  python powered")
            print("             ┃┃┃┃┃┃┃┃  ┣┫┣ ┃ ┃┃┣┫┃┃┣ ┣┫                  cross-platform")
            print("             ┗┻┛┗┛┗┻┛  ┛┗┗┛┗┛┗┛┛┗┻┛┗┛┛┗                web-socket based")
            print("--+--------------------------------------------------------------------")
            print(f"S | [{spinner.get_spinner()}] Time:     "
                  f"{datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
            print(str_ellipsis(f"T | OBS Studio:   "
                               f"{str(recorder.obs_controller.connected)}", 70).ljust(70))
            print(str_ellipsis(f"A | Log file:     "
                               f"{recorder.wow_controller.log_file_name}", 70).ljust(70))
            print(str_ellipsis(f"T | Is recording: "
                               f"{recorder.is_recording()}", 70).ljust(70))
            print(str_ellipsis(f"E | Activity:     "
                               f"{str(recorder.activity)}", 70).ljust(70))
            print("--+--------------------------------------------------------------------")
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
