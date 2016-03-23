import django
import json_log_formatter

class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        # https://docs.python.org/2/library/logging.html#logrecord-objects
        if 'time' not in extra:
            extra['time'] = django.utils.timezone.now()
        extra['level'] = record.levelname
        extra['message'] = message
        return extra
