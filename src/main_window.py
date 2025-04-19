"""Main window of the application"""
import tkinter as tk

from wow_recorder import Recorder

def str_ellipsis(msg: str, cnt: int):
    """Shortens the string and adds ... at the end"""
    final = msg
    if len(msg) > cnt:
        final = msg[0:cnt-4] + '...'
    return final


class RecorderMainWindow:
    """Class for window GUI"""
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
        """Updates window data based on the recorder state"""
        # fill in data
        self.wow_log_file_label.configure(text=f"WOW Log: "
                                               f"{self.recorder.wow_controller.log_file_name}")
        log_time = self.recorder.wow_controller.last_log_time.strftime('%H:%M:%S')
        self.wow_log_time_label.configure(text=f"Time: {log_time}")

        self.obs_connected_label.configure(text=f"OBS Connection: "
                                                f"{self.recorder.obs_controller.connected}")
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
        """Starts main loop of the window - this is blocking"""
        self.window.mainloop()
