"""Various tricks to handle console"""
import datetime

def hide_cursor():
    """Hides Cursor"""
    print('\033[?25l', end="")

def show_cursor():
    """Enables cursor visibility in console"""
    print('\033[?25h', end="")

class ASCIISpinner:
    """Simple spinner"""
    def __init__(self):
        self.spinner_array = ['|', '/', '-', '\\', '|', '/', '-', '\\']
        self.iterator = 0
        self.last_time = datetime.datetime.now()

    def get_spinner(self):
        """Gets spinner character"""
        char = self.spinner_array[self.iterator]
        if self.iterator + 1 == len(self.spinner_array):
            self.iterator = 0
        else:
            if (datetime.datetime.now() - self.last_time).microseconds > 250000:
                self.last_time = datetime.datetime.now()
                self.iterator = self.iterator + 1
        return char

    def __str__(self):
        """ToString"""
        return f"Spinner: {self.iterator}"
