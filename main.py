from OBSController import OBSController
from Recorder import Recorder
from WoWController import WoWController

host = 'localhost'
port = 4455
password = 'zbnfiosglNUQTbjJ'
log_folder = '/home/bigos/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/'
output_path = '/home/bigos/Capture/recorder/'
death_delay_seconds = 3

wow_controller = WoWController(log_folder)
obs_controller = OBSController(host, port, password)

recorder = Recorder(obs_controller, wow_controller, output_path, death_delay_seconds)
recorder.start()