import pytest

from src.config import RecorderConfigurationFile

rc = RecorderConfigurationFile(conf_file_path='tests/wow_recorder_py.cfg')

def test_validate_config():
    rc.validate_config()

def test_get_obs_host():
    assert rc.get_obs_host() == 'localhost'

def test_get_obs_port():
    assert rc.get_obs_port() == 4455

def test_get_obs_password():
    assert rc.get_obs_password() == 'zbnfiosglNUQTbjJ'

def test_get_wow_log_folder():
    assert rc.get_wow_log_folder() == '/home/bigos/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/'

def test_get_recorder_output_path():
    assert rc.get_recorder_output_path() == '/home/bigos/Capture/recorder/'

def test_get_recorder_death_delay():
    assert rc.get_recorder_death_delay() == 3

def test_get_recorder_linger_time():
    assert rc.get_recorder_linger_time() == 5

def test_get_recorder_reset_time():
    assert rc.get_recorder_reset_time() == 30

def test_get_obs_password_not_set():
    with pytest.raises(ValueError):
        c = RecorderConfigurationFile(conf_file_path='src/wow_recorder_py-macos-latest.cfg')
        c.validate_config()