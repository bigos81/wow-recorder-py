from dateutil import parser

def parse_wow_log_line(line):
    chunks = line.split(' ')
    timestamp = parser.parse(chunks[0] + ' ' + chunks[1])

    event_chunks = line.split('  ')[1].split(',')
    return {"timestamp": timestamp, "type": event_chunks[0], "rest": event_chunks}

