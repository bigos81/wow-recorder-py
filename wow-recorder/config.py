import configparser


class RecorderConfiguration:

    def __init__(self, conf_file_path = 'wow_recorder_py.cfg'):
        self.config = configparser.ConfigParser()
        self.config.read(conf_file_path)

    def validate_config(self):
        self.get_recorder_reset_time()
        self.get_recorder_linger_time()
        self.get_recorder_death_delay()
        self.get_obs_host()
        self.get_obs_port()
        self.get_obs_password()
        self.get_recorder_output_path()
        self.get_wow_log_folder()


    def get_obs_host(self):
        return self.config['OBS']['host']

    def get_obs_port(self):
        return int(self.config['OBS']['port'])

    def get_obs_password(self):
        value = self.config['OBS']['password']
        if 'CHANGE_ME!' == value:
            raise Exception('Configuration file not valid, password for OBS not set (is default value)')
        return value

    def get_wow_log_folder(self):
        return self.config['WOW']['log_folder']

    def get_recorder_output_path(self):
        return self.config['RECORDER']['output_path']

    def get_recorder_death_delay(self):
        return int(self.config['RECORDER']['death_delay'])

    def get_recorder_linger_time(self):
        return int(self.config['RECORDER']['linger_time'])

    def get_recorder_reset_time(self):
        return int(self.config['RECORDER']['reset_time'])