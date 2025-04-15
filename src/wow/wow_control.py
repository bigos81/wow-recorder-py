import datetime
import io
import os
from os.path import isfile


class WoWController:

    def __init__(self, log_folder):
        self.log_folder = log_folder

        self.WOW_PROCESS_NAME = "WoW.exe"
        self.log_file_handle = None
        self.log_file_path = None
        self.last_log_time = datetime.datetime.now()
        self.new_log_file_timeout_seconds = 5
        self.log_file_name = None

    def get_current_log_path(self):
        last_date = 0
        current_log = None
        for file in os.listdir(self.log_folder):
            file_path = os.path.join(self.log_folder, file)
            if isfile(file_path) and str(file).startswith("WoWCombatLog-") and str(file).endswith(".txt"):
                file_date = os.path.getmtime(file_path)
                if file_date > last_date:
                    last_date = file_date
                    current_log = file_path
                    self.log_file_name = os.path.basename(current_log)

        return current_log

    def get_log_line(self):
        if self.log_file_handle is None:
            # need new file to tail
            log_path = self.get_current_log_path()
            if log_path is not None:
                # open file and rewind to end
                self.last_log_time = datetime.datetime.now()
                self.log_file_handle = open(log_path, "r")
                self.log_file_handle.seek(0, io.SEEK_END)
                self.log_file_path = log_path
            else:
                # not logging
                return ''

        line = self.log_file_handle.readline()
        if len(line) > 0:
            self.last_log_time = datetime.datetime.now()

        datedelta = datetime.datetime.now() - self.last_log_time
        if datedelta.seconds > self.new_log_file_timeout_seconds:
            new_log_file = self.get_current_log_path()
            if self.log_file_path != new_log_file:
                self.log_file_handle = None
            else:
                self.last_log_time = datetime.datetime.now()
        return line


