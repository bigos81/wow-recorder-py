"""Configuration file module"""
import configparser

class RecorderConfigurationFile:
    """Class representing configuration access object"""

    def __init__(self, conf_file_path = 'wow_recorder_py.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read(conf_file_path)

    def validate_config(self):
        """Validates whether all values can be read from configuration file"""
        self.get_recorder_reset_time()
        self.get_recorder_linger_time()
        self.get_recorder_death_delay()
        self.get_obs_host()
        self.get_obs_port()
        self.get_obs_password()
        self.get_recorder_output_path()
        self.get_wow_log_folder()


    def get_obs_host(self):
        """Gets OBS Studio host"""
        return self.config['OBS']['host']

    def get_obs_port(self):
        """Gets OBS Studio port"""
        return int(self.config['OBS']['port'])

    def get_obs_password(self):
        """Gets OBS Studio password"""
        value = self.config['OBS']['password']
        if 'CHANGE_ME!' == value:
            raise ValueError('Configuration file not valid, '
                            'password for OBS not set (is default value)')
        return value

    def get_wow_log_folder(self):
        """Gets World of Warcraft log folder"""
        return self.config['WOW']['log_folder']

    def get_recorder_output_path(self):
        """Gets application output folder where to store the output video files"""
        return self.config['RECORDER']['output_path']

    def get_recorder_death_delay(self):
        """Gets delay added to death event in seconds"""
        return int(self.config['RECORDER']['death_delay'])

    def get_recorder_linger_time(self):
        """Gets how much seconds to still record after Activity ends"""
        return int(self.config['RECORDER']['linger_time'])

    def get_recorder_reset_time(self):
        """Gets how short of a recording is too short"""
        return int(self.config['RECORDER']['reset_time'])
