"""Main entry point of application"""
#!/usr/bin/python
import sys

import tkinter as tk
import tkinter.messagebox as mbox

import datetime
import logging

from obs.obs_control import OBSController
from ui.terminal_tricks import hide_cursor, show_cursor, ASCIISpinner
from wow_recorder import Recorder, RecorderConfiguration
from config import RecorderConfigurationFile
from wow.wow_control import WoWController


def str_ellipsis(msg: str, cnt: int):
    """Shortens the string and adds ... at the end"""
    final = msg
    if len(msg) > cnt:
        final = msg[0:cnt-4] + '...'
    return final


def main_gui():
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
        mbox.showerror(title="Configuration error!", message=str(e))
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
                        RecorderConfiguration(output_path, death_delay_seconds,
                                              linger_time, reset_time))
    window = tk.Tk()
    window.title("WOW Recorder PY")

    window.resizable(False, False)

    obs_label_frame = tk.LabelFrame(window, text='OBS', background='grey')
    obs_label_frame.grid(row=0, column=0, sticky="wens")

    obs_connected_label = tk.Label(obs_label_frame, anchor="nw")
    obs_connected_label.pack(fill='x')

    obs_recording_label = tk.Label(obs_label_frame, anchor="nw")
    obs_recording_label.pack(fill='x')

    wow_label_frame = tk.LabelFrame(window, text='WOW', background='grey')
    wow_label_frame.grid(row=0, column=1, sticky="wens")

    wow_log_file_label = tk.Label(wow_label_frame, anchor='nw')
    wow_log_file_label.pack(fill='x')

    wow_log_time_label = tk.Label(wow_label_frame, anchor='nw')
    wow_log_time_label.pack(fill='x')

    activity_label_frame = tk.LabelFrame(window, text="ACTIVITY")
    activity_label_frame.grid(row=1, column=0, columnspan=2, sticky='wens')

    activity_label = tk.Label(activity_label_frame, justify='center')
    activity_label.pack(fill='x')

    log_label_frame = tk.LabelFrame(window, text="LOG")
    log_label_frame.grid(row=2, column=0, columnspan=2, sticky='wen')

    log_label = tk.Label(log_label_frame, text='log?', anchor='w', justify='left')
    log_label.pack(fill='x')

    while True:
        recorder.process()

        # fill in data
        wow_log_file_label.configure(text=f"WOW Log: {recorder.wow_controller.log_file_name}")
        wow_log_time_label.configure(text=f"Time: {recorder.wow_controller.last_log_time}")

        obs_connected_label.configure(text=f"OBS Connection: {recorder.obs_controller.connected}")
        obs_recording_label.configure(text=f"Recording: {recorder.is_recording()}")

        activity_label.configure(text=f"{str(recorder.activity)}")

        all_str = ''
        for msg in recorder.message_log:
            all_str = all_str + str_ellipsis(f"{msg['time']}: {msg['msg']}\n", 100)
        log_label.configure(text=all_str[:-1])


        # style the containers
        if recorder.obs_controller.connected:
            obs_label_frame.configure(background='lime green')
            obs_connected_label.configure(background='lime green')
            obs_recording_label.configure(background='lime green')
        else:
            obs_label_frame.configure(background='red')
            obs_connected_label.configure(background='red')
            obs_recording_label.configure(background='red')

        if recorder.wow_controller.log_file_name is None:
            wow_label_frame.configure(background='red')
            wow_log_file_label.configure(background='red')
            wow_log_time_label.configure(background='red')
        else:
            wow_label_frame.configure(background='lime green')
            wow_log_file_label.configure(background='lime green')
            wow_log_time_label.configure(background='lime green')

        if recorder.activity is None:
            activity_label_frame.configure(background='gray')
            activity_label.configure(background='gray')
        else:
            activity_label_frame.configure(background='lime green')
            activity_label.configure(background='lime green')

        # update window
        window.update()

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
                        RecorderConfiguration(output_path, death_delay_seconds,
                                              linger_time, reset_time))

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
    main_gui()
    # main()
