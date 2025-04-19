"""Main entry point of application"""
#!/usr/bin/python
import sys
import threading

import tkinter.messagebox as mbox

import logging

from obs.obs_control import OBSController
from src.ui.main_window import RecorderMainWindow
from wow_recorder import RecorderConfiguration, Recorder
from config import RecorderConfigurationFile
from wow.wow_control import WoWController

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



if __name__ == "__main__":
    main_gui()
