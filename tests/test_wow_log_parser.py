import dateutil.parser

from src.wow.wow_log_parser import parse_wow_log_line

example_correct_line = '5/18/2025 01:26:01.6292  SPELL_AURA_APPLIED,Player-3713-0AA99976,"Bigospriest-BurningLegion-EU",0x511,0x0,Player-3713-0AA99976,"Bigospriest-BurningLegion-EU",0x511,0x0,372014,"Visage",0x8,BUFF'
example_correct_line_quotes = '5/18/2025 01:26:01.6292  SPELL_AURA_APPLIED,Player-3713-0AA99976,"Bigospriest-BurningLegion-EU",0x511,0x0,Player-3713-0AA99976,"Bigospriest-BurningLegion-EU",0x511,0x0,372014,"Visage,dauniak",0x8,BUFF'
example_corrupted_line = '5/18/2025 01:26:01.6'
example_corrupted_date_line = '5/18/202a5 01:26:01.634  asdd,assa,asdsad'


def test_parse_wow_log_line_happy():
    result = parse_wow_log_line(example_correct_line)
    ts = result['timestamp']
    event = result['type']
    chunks = result['rest']
    assert ts == dateutil.parser.parse('5/18/2025 01:26:01.6292')
    assert 'SPELL_AURA_APPLIED' == event
    assert len(chunks) == 13

def test_parse_wow_log_line_happy_with_quotes():
    result = parse_wow_log_line(example_correct_line_quotes)
    ts = result['timestamp']
    event = result['type']
    chunks = result['rest']
    assert ts == dateutil.parser.parse('5/18/2025 01:26:01.6292')
    assert 'SPELL_AURA_APPLIED' == event
    assert len(chunks) == 13

def test_parse_wow_log_line_corrupted():
    result = parse_wow_log_line(example_corrupted_line)
    assert result is None

def test_parse_wow_log_line_corrupted_date():
    result = parse_wow_log_line(example_corrupted_date_line)
    assert result is None


