"""OBS Controller using web socket"""
import obsws_python as obs
from obsws_python import ReqClient


class OBSController:
    """Object for controlling OBS Studio via web socket"""


    def __init__(self, host: str, port: int, passwd: str):
        self.connected = False
        self.obs_client = None
        self.host = host
        self.port = port
        self.passwd = passwd


    def connect(self) -> bool:
        """Connects to OBS"""
        try:
            # it's the only way to ignore the type assignment, as the contractor of ReqClient
            # throws exception :(
            self.obs_client = (
                ReqClient(host=self.host, port=self.port, passwd=self.passwd)) # type: ignore
            self.connected = True
            return True
        except ConnectionRefusedError:
            return False


    def disconnect(self):
        """Disconnects from OSB"""
        if self.connected:
            self.obs_client.disconnect()
            self.connected = False

    def get_record_status(self):
        """Indicates whether recording is happening"""
        if not self.connected:
            raise RuntimeError("OBS not connected...")

        return self.obs_client.get_record_status()

    def start_recording(self):
        """Starts recording"""
        if not self.connected:
            raise RuntimeError("OBS not connected...")

        return self.obs_client.start_record()

    def end_recording(self):
        """Ends recording in OBS"""
        if not self.connected:
            raise RuntimeError("OBS not connected...")

        result = self.obs_client.stop_record()
        return result.output_path
