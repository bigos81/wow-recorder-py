import datetime
from time import sleep

from src.wow_recorder import Activity, ActivityType, make_file_name

name = 'Name'
key_level = 12
player_count = 5
event = 'Event happened'


def test_activity_creation():
    act = Activity(activity_type=ActivityType.M_PLUS, name=name, key_level=key_level, player_count=player_count)
    assert act.activity_type == ActivityType.M_PLUS
    assert act.name == name
    assert act.key_level == key_level
    assert act.player_count == player_count
    assert len(act.events) == 0
    assert act.success == False


def test_add_event():
    act = Activity(activity_type=ActivityType.M_PLUS, name=name, key_level=key_level, player_count=player_count)
    sleep(1)
    act.add_event(event=event, timestamp=datetime.datetime.now())
    assert len(act.events) == 1
    assert act.events[0]['time'] == '00:00:01'
    assert act.events[0]['event'] == event


def test_make_file_name():
    # M PLUS
    act = Activity(activity_type=ActivityType.M_PLUS, name=name, key_level=key_level, player_count=player_count)
    file_name = make_file_name(act)
    assert 'M_PLUS' in file_name
    assert '__' in file_name
    assert name in file_name
    assert str(key_level) in file_name
    assert '.mkv' in file_name

    # RAID wipe
    act = Activity(activity_type=ActivityType.RAID, name=name, key_level=key_level, player_count=player_count)
    file_name = make_file_name(act)
    assert 'RAID' in file_name
    assert '__' in file_name
    assert name in file_name
    assert 'wipe' in file_name
    assert '.mkv' in file_name

    # RAID wipe
    act = Activity(activity_type=ActivityType.RAID, name=name, key_level=key_level, player_count=player_count)
    act.success = True
    file_name = make_file_name(act)
    assert 'RAID' in file_name
    assert '__' in file_name
    assert name in file_name
    assert 'kill' in file_name
    assert '.mkv' in file_name

