import datetime
import os

def hide_cursor():
  print('\033[?25l', end="")

def show_cursor():
  print('\033[?25h', end="")

def is_running_in_ide():
  return "PYCHARM_HOSTED" in os.environ

class ASCIISpinner:
  def __init__(self):
    self.SPINNER = ['|', '/', '-', '\\', '|', '/', '-', '\\']
    self.iterator = 0
    self.last_time = datetime.datetime.now()

  def get_spinner(self):
    char = self.SPINNER[self.iterator]
    if self.iterator + 1 == len(self.SPINNER):
      self.iterator = 0
    else:
      if (datetime.datetime.now() - self.last_time).microseconds > 250000:
        self.last_time = datetime.datetime.now()
        self.iterator = self.iterator + 1

    return char