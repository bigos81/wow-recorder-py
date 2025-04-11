#!/usr/bin/python

from time import sleep

import datetime
import logging

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, is_running_in_ide, ASCIISpinner
from wow_recorder import Recorder
from wow.wow_control import WoWController

def ellipsis(msg: str, cnt: int):
    final = msg
    if len(msg) > cnt:
        final = msg[0:cnt-3] + '...'
    return final



def main():
    #configuration
    logging.getLogger('obsws_python.baseclient.ObsClient').disabled = True
    host = 'localhost'
    port = 4455
    password = 'zbnfiosglNUQTbjJ'
    log_folder = '/home/bigos/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/'
    output_path = '/home/bigos/Capture/recorder/'
    death_delay_seconds = 3

    wow_controller = WoWController(log_folder)
    obs_controller = OBSController(host, port, password)

    recorder = Recorder(obs_controller, wow_controller, output_path, death_delay_seconds)

    if is_running_in_ide():
        while True:
            if not recorder.obs_controller.connect():
                print("Cannot connect to OBS, will retry in 10 seconds...")
                sleep(10)
                continue
            recorder.process()
            if recorder.last_message is not None:
                print(recorder.last_message)
                recorder.last_message = None
    else:
        try:
            hide_cursor()
            spinner = ASCIISpinner()
            log_name = ['L', 'O', 'G', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
            while True:
                print('\033[25A\033[2K', end='')
                recorder.process()
                print(f"                                                                       ")
                print(f"             ┓ ┏┏┓┓ ┏  ┳┓┏┓┏┓┏┓┳┓┳┓┏┓┳┓                  python powered")
                print(f"             ┃┃┃┃┃┃┃┃  ┣┫┣ ┃ ┃┃┣┫┃┃┣ ┣┫                  cross-platform")
                print(f"             ┗┻┛┗┛┗┻┛  ┛┗┗┛┗┛┗┛┛┗┻┛┗┛┛┗                web-socket based")
                print(f"--+--------------------------------------------------------------------")
                print(f"S | [{spinner.get_spinner()}] Time:     {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}")
                print(f"T | OBS Studio:   {str(recorder.obs_controller.connected)}".ljust(70))
                print(f"A | Log file:     {recorder.wow_controller.log_file_name}".ljust(70))
                print(f"T | Is recording: {recorder.is_recording()}".ljust(70))
                print(f"E | Activity:     {ellipsis(str(recorder.activity), 70)}".ljust(70))
                print(f"--+--------------------------------------------------------------------")
                # 13 lines available
                i = 0
                for msg in recorder.message_log:
                    print(f"{ellipsis(msg, 70).ljust(70)}")
                    i = i + 1
                print('\033[25A\033[2K', end='')

        except Exception as e:
            print(e)
        finally:
            show_cursor()

if __name__ == "__main__":
    main()
