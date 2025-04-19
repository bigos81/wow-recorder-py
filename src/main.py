"""Main entry point of application"""
#!/usr/bin/python
import sys
import threading

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

class RecorderMainWindow:
    def __init__(self, recorder: Recorder):
        self.recorder = recorder

        self.window = tk.Tk()
        self.window.title("WOW Recorder PY")

        self.window.resizable(False, False)

        self.obs_label_frame = tk.LabelFrame(self.window, text='OBS', background='grey')
        self.obs_label_frame.grid(row=0, column=0, sticky="wens")

        self.obs_connected_label = tk.Label(self.obs_label_frame, anchor="nw")
        self.obs_connected_label.pack(fill='x')

        self.obs_recording_label = tk.Label(self.obs_label_frame, anchor="nw")
        self.obs_recording_label.pack(fill='x')

        self.wow_label_frame = tk.LabelFrame(self.window, text='WOW', background='grey')
        self.wow_label_frame.grid(row=0, column=1, sticky="wens")

        self.wow_log_file_label = tk.Label(self.wow_label_frame, anchor='nw')
        self.wow_log_file_label.pack(fill='x')

        self.wow_log_time_label = tk.Label(self.wow_label_frame, anchor='nw')
        self.wow_log_time_label.pack(fill='x')

        self.activity_label_frame = tk.LabelFrame(self.window, text="ACTIVITY")
        self.activity_label_frame.grid(row=1, column=0, columnspan=2, sticky='wens')

        self.activity_label = tk.Label(self.activity_label_frame, justify='center')
        self.activity_label.pack(fill='x')

        self.log_label_frame = tk.LabelFrame(self.window, text="LOG", height=10)
        self.log_label_frame.grid(row=2, column=0, columnspan=2, sticky='wen')

        self.log_label = tk.Label(self.log_label_frame, anchor='nw', justify='left', height=10)
        self.log_label.pack(fill='x')

        self.window.after(1, self.update_data)

    def update_data(self) -> None:
        # fill in data
        self.wow_log_file_label.configure(text=f"WOW Log: {self.recorder.wow_controller.log_file_name}")
        self.wow_log_time_label.configure(text=f"Time: {self.recorder.wow_controller.last_log_time.strftime('%H:%M:%S')}")

        self.obs_connected_label.configure(text=f"OBS Connection: {self.recorder.obs_controller.connected}")
        self.obs_recording_label.configure(text=f"Recording: {self.recorder.is_recording()}")

        self.activity_label.configure(text=f"{str(self.recorder.activity)}")

        all_str = ''
        for msg in self.recorder.message_log:
            all_str = all_str + str_ellipsis(f"{msg['time']}: {msg['msg']}\n", 100)
        self.log_label.configure(text=all_str[:-1])

        # style the containers
        if self.recorder.obs_controller.connected:
            self.obs_label_frame.configure(background='lime green')
            self.obs_connected_label.configure(background='lime green')
            self.obs_recording_label.configure(background='lime green')
        else:
            self.obs_label_frame.configure(background='red')
            self.obs_connected_label.configure(background='red')
            self.obs_recording_label.configure(background='red')

        if self.recorder.wow_controller.log_file_name is None:
            self.wow_label_frame.configure(background='red')
            self.wow_log_file_label.configure(background='red')
            self.wow_log_time_label.configure(background='red')
        else:
            self.wow_label_frame.configure(background='lime green')
            self.wow_log_file_label.configure(background='lime green')
            self.wow_log_time_label.configure(background='lime green')

        if self.recorder.activity is None:
            self.activity_label_frame.configure(background='gray')
            self.activity_label.configure(background='gray')
        else:
            self.activity_label_frame.configure(background='lime green')
            self.activity_label.configure(background='lime green')

        self.window.after(250, self.update_data)

    def main_loop(self):
        self.window.mainloop()


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

    wow_controller = WoWController(conf.get_wow_log_folder())
    obs_controller = OBSController(conf.get_obs_host(),
                                   conf.get_obs_port(),
                                   conf.get_obs_password())

    recorder = Recorder(obs_controller, wow_controller,
                        RecorderConfiguration(conf.get_recorder_output_path(),
                                              conf.get_recorder_death_delay(),
                                              conf.get_recorder_linger_time(),
                                              conf.get_recorder_reset_time()))

    t = threading.Thread(target=recorder.start)
    try:
        t.start()
        window = RecorderMainWindow(recorder)
        window.main_loop()
    finally:
        recorder.kill()
        t.join(timeout=2)


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
