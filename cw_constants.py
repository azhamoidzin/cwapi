class CWConstants:
    DEFAULT_MESSAGE_DATE_FORMAT = '%d.%m.%Y %H:%M:%S'
    "Formatting message in MessageEvent"
    DEFAULT_COMMAND_INTERVAL_MS = 1000
    "Interval between executing commands"
    DEFAULT_MESSAGE_VOLUME = 5
    "Message volume"
    DEFAULT_MOVE_INTERVAL_MS = 1000
    "Delay between executing CWMove from CWMoveSequence"
    DEFAULT_MOVE_DELTA_MS = 100
    "Resulting delay will be taken from [interval - delta, interval + delta]"
