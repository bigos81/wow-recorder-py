import pytest

from src.config import RecorderConfigurationFile


def test_config_happy_path():
    c = RecorderConfigurationFile(conf_file_path='tests/wow_recorder_py.cfg')
    c.validate_config()

    assert c.get_recorder_output_path() == '/home/bigos/Capture/recorder/'
    assert c.get_recorder_death_delay() == 3
    assert c.get_recorder_linger_time() == 5
    assert c.get_recorder_reset_time() == 30
    assert c.get_obs_port() == 4455
    assert c.get_obs_host() == 'localhost'
    assert c.get_obs_password() == 'zbnfiosglNUQTbjJ'
    assert c.get_wow_log_folder() == '/home/bigos/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/'

def test_config_not_changed():
    with pytest.raises(ValueError):
        c = RecorderConfigurationFile(conf_file_path='src/wow_recorder_py-macos-latest.cfg')
        c.validate_config()