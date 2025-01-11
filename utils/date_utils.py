import datetime
from cw_constants import CWConstants


def millis_to_str(time_ms: int, date_format: str = CWConstants.DEFAULT_MESSAGE_DATE_FORMAT):
    return datetime.datetime.fromtimestamp(time_ms).strftime(date_format)
