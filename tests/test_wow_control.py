import datetime
from pathlib import Path

from src.wow.wow_control import WoWController

log_folder = 'tests/log_folder'
wc = WoWController(log_folder=log_folder)
creation_time = datetime.datetime.now()


def test_construction():
    assert wc.log_folder == log_folder
    assert wc.log_file_handle is None
    assert wc.log_file_path is None
    assert (wc.last_log_time - creation_time).total_seconds() < 1
    assert wc.new_log_file_timeout_seconds == 5
    assert wc.log_file_name is None


def test_get_current_log_path():
    log_path = wc.get_current_log_path()
    Path(log_path).touch()
    assert log_path == log_folder + '/' + 'WoWCombatLog-051825_005439.txt'

