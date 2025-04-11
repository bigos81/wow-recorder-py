#!/usr/bin/python

from time import sleep

import datetime
import logging

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, is_running_in_ide, ASCIISpinner
from wow_recorder import Recorder
from wow.wow_control import WoWController

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
            while True:
                print('\033[18A\033[2K', end='')
                recorder.process()
                last_msg_formatted = recorder.last_message
                if len(str(last_msg_formatted)) > 93:
                    last_msg_formatted = last_msg_formatted[0:90] + '...'
                print(f"/---------------------------------------------WOW RECORDER--------------------------------------------------\\")
                print(f"| [{spinner.get_spinner()}] Time:     {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}                                                                         |")
                print(f"| OBS Studio:   {str(recorder.obs_controller.connected)} {' '*(110-19-len(str(recorder.obs_controller.connected)))}|")
                print(f"| Log file:     {recorder.wow_controller.log_file_name} {' '*(110-19-len(recorder.wow_controller.log_file_name))}|")
                print(f"| Is recording: {recorder.is_recording()} {' '*(110-19-len(str(recorder.is_recording())))}|")
                print(f"| Activity:     {str(recorder.activity)} {' '*(110-19-len(str(recorder.activity)))}|")
                print(f"| Last message: {last_msg_formatted} {' '*(110-19-len(str(last_msg_formatted)))}|")
                print(f"\\-[q to quit]------------------------------------------------------------------------------[(c) bigos 2025]-/")
                print('\033[18A\033[2K', end='')
        except Exception as e:
            print(e)
        finally:
            show_cursor()

if __name__ == "__main__":
    main()
