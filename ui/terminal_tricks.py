import os

def clearscreen(numlines=100):
  """Clear the console.
numlines is an optional argument used only as a fall-back.
"""
# Thanks to Steven D'Aprano, http://www.velocityreviews.com/forums

  if os.name == "posix":
    # Unix, Linux, macOS, BSD, etc.
    os.system('clear')
  elif os.name in ("nt", "dos", "ce"):
    # DOS/Windows
    os.system('CLS')
  else:
    # Fallback for other operating systems.
    print('\n' * numlines)

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

  def get_spinner(self):
    char = self.SPINNER[self.iterator]
    if self.iterator + 1 == len(self.SPINNER):
      self.iterator = 0
    else:
      self.iterator = self.iterator + 1

    return char