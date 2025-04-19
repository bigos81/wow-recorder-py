"""Parser class for wow log contents"""
import re
from dateutil import parser
from dateutil.parser import ParserError


def parse_wow_log_line(line):
    """Parses single WOW log line"""
    # remove comas from quoted strings
    for quoted in re.findall('"([^"]*)"', line):
        line = line.replace(quoted, quoted.replace(',',''))

    chunks = line.split('  ')
    if len(chunks) != 2:
        return None
    try:
        timestamp = parser.parse(chunks[0])
    except ParserError:
        return None

    event_chunks = chunks[1].split(',')
    return {"timestamp": timestamp, "type": event_chunks[0], "rest": event_chunks}
