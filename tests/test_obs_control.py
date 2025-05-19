import pytest
from charset_normalizer.cli.normalizer import cli_detect
from unittest.mock import Mock, MagicMock
from websocket import WebSocketException

from src.obs.obs_control import OBSController

host = 'host'
password = 'pass'
port = 1234
c = OBSController(host, port, password)


def test_obscontroller_construction():
    assert c is not None
    assert host == c.host
    assert password == c.passwd
    assert port == c.port


def test_connect():
    with pytest.raises(WebSocketException):
        c.connect()


def test_get_record_status_error():
    c.connected = False
    with pytest.raises(RuntimeError):
        c.get_record_status()


def test_get_record_status_pass():
    c.connected = True
    client_mock = Mock()
    c.obs_client = client_mock
    c.get_record_status()
    client_mock.get_record_status.assert_called()


def test_start_recording_error():
    c.connected = False
    with pytest.raises(RuntimeError):
        c.start_recording()


def test_start_recording_pass():
    c.connected = True
    client_mock = Mock()
    c.obs_client = client_mock
    c.start_recording()
    client_mock.start_record.assert_called()


def test_end_recording_error():
    c.connected = False
    with pytest.raises(RuntimeError):
        c.end_recording()


def test_end_recording_pass():
    c.connected = True
    client_mock = Mock()
    c.obs_client = client_mock
    c.end_recording()
    client_mock.stop_record.assert_called()


def test_disconnect():
    c.connected = True
    client_mock = Mock()
    c.obs_client = client_mock
    c.disconnect()
    client_mock.disconnect.assert_called()
    assert c.connected == False

def test_disconnect_on_disconnected():
    c.connected = False
    client_mock = Mock()
    c.obs_client = client_mock
    c.disconnect()
    client_mock.disconnect.assert_not_called()
    assert c.connected == False