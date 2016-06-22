import django
import json_log_formatter


class CustomisedJSONFormatter(json_log_formatter.JSONFormatter):

    def json_record(self, message, extra, record):
        # https://docs.python.org/2/library/logging.html#logrecord-objects
        if 'time' not in extra:
            extra['time'] = django.utils.timezone.now()
        extra['level'] = record.levelname
        extra['message'] = message
        extra['logger'] = record.name

        # Django Request
        request = extra.get('request')
        if request:
            extra['user'] = request.user.username
            del extra['request']
        else:
            extra['user'] = 'system'

        user = extra.get('user')
        if user and not request:
            extra['user'] = user

        if 'method' in extra:
            method = extra['method']
            delete_method_key = True
            if method:
                delete_method_key = False
            if delete_method_key:
                del extra['method']

        return extra
