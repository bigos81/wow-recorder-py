import obsws_python as obs
import psutil


class OBSController:

    def __init__(self, host, port, password):
        self.OBS_PROCESS_NAME = 'obs'
        self.connected = False
        self.obs_client = None
        self.host = host
        self.port = port
        self.password = password

    def is_running(self):
        for process in psutil.process_iter():
            if self.OBS_PROCESS_NAME == process.name():
                return True
        return False

    def connect(self):
        self.obs_client = obs.ReqClient(host=self.host, port=self.port, password=self.password)
        self.connected = True

    def disconnect(self):
        if self.connected:
            self.obs_client.disconnect()
            self.connected = False

    def get_record_status(self):
        if not self.connected:
            raise Exception("OBS not connected...")

        return self.obs_client.get_record_status()

    def start_recording(self):
        if not self.connected:
            raise Exception("OBS not connected...")

        return self.obs_client.start_record()

    def end_recording(self):
        if not self.connected:
            raise Exception("OBS not connected...")

        result = self.obs_client.stop_record()
        return result.output_path
