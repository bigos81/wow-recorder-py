from dateutil import parser
from dateutil.parser import ParserError


def parse_wow_log_line(line):
    chunks = line.split('  ')
    if len(chunks) != 2:
        print(f"Corrupted log line: {line}")
        return None
    try:
        timestamp = parser.parse(chunks[0])
    except ParserError:
        return None

    event_chunks = chunks[1].split(',')
    return {"timestamp": timestamp, "type": event_chunks[0], "rest": event_chunks}
