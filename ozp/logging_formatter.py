"""
Logger Formatter
"""
from datetime import datetime
import django
import logging
import json
import os
import socket
import traceback
import platform

BUILTIN_ATTRS = {
    'args',
    'asctime',
    'created',
    'exc_info',
    'exc_text',
    'filename',
    'funcName',
    'levelname',
    'levelno',
    'lineno',
    'module',
    'msecs',
    'message',
    'msg',
    'name',
    'pathname',
    'process',
    'processName',
    'relativeCreated',
    'stack_info',
    'thread',
    'threadName',
}


class FailProofJSONEncoder(json.JSONEncoder):
    """Uses object's representation for unsupported types."""

    def default(self, o):  # pylint: disable=E0202
        # E0202 ignored in favor of compliance with documentation:
        # https://docs.python.org/2/library/json.html#json.JSONEncoder.default
        """Return object's repr when not JSON serializable."""
        try:
            return repr(o)
        except Exception:  # pylint: disable=W0703
            return super(FailProofJSONEncoder, self).default(o)


def format_backtrace(trace):
    """Create a formatted dictionary from a traceback object."""
    backtrace = []
    for filename, line, func, _ in traceback.extract_tb(trace):
        desc = {'file': filename,
                'line': line,
                'function': func,
                'text': _}
        backtrace.append(desc)
    return backtrace


def is_exc_info_tuple(exc_info):
    """Determine whether 'exc_info' is an exc_info tuple.
    Note: exc_info tuple means a tuple of exception related values
    as returned by sys.exc_info().
    """
    try:
        errtype, value, tback = exc_info
        if all([x is None for x in exc_info]):
            return True
        elif all((isinstance(errtype, type),
                  isinstance(value, Exception),
                  hasattr(tback, 'tb_frame'),
                  hasattr(tback, 'tb_lineno'),
                  hasattr(tback, 'tb_next'))):
            return True
    except (TypeError, ValueError):
        pass
    return False


class JSONFormatter(logging.Formatter):
    """JSON log formatter.
    Usage example::
        import logging
        import json_log_formatter
        json_handler = logging.FileHandler(filename='/var/log/my-log.json')
        json_handler.setFormatter(json_log_formatter.JSONFormatter())
        logger = logging.getLogger('my_json')
        logger.addHandler(json_handler)
        logger.info('Sign up', extra={'referral_code': '52d6ce'})
    The log file will contain the following log record (inline)::
        {
            "message": "Sign up",
            "time": "2015-09-01T06:06:26.524448",
            "referral_code": "52d6ce"
        }
    """
    json_lib = json

    def format(self, record):
        error_dict = None

        if record.exc_info and is_exc_info_tuple(record.exc_info):
            errtype, value, tback = record.exc_info

            error_dict = {}
            error_dict['backtrace'] = format_backtrace(tback)

            error_type = errtype.__name__
            if error_type == 'Http404':
                error_dict['type'] = 'NotFound'
            else:
                error_dict['type'] = error_type

            if str(value):
                error_dict['message'] = str(value)
            else:
                lines = traceback.format_exception(*record.exc_info)

                lines = '\n'.join(lines).split('\n')
                lines = [line.strip() for line in lines if line]
                lines = [line for line in lines if str(line).lower() != 'none']

                if lines:
                    error_dict['message'] = lines[-1]

        message = record.getMessage()

        extra = self.extra_from_record(record)
        json_record = self.json_record(message, extra, record, error_dict)
        mutated_record = self.mutate_json_record(json_record)
        # Backwards compatibility: Functions that overwrite this but don't
        # return a new value will return None because they modified the
        # argument passed in.
        if mutated_record is None:
            mutated_record = json_record
        return self.json_lib.dumps(mutated_record, cls=FailProofJSONEncoder,
                                   sort_keys=True)

    def extra_from_record(self, record):
        """Returns `extra` dict you passed to logger.
        The `extra` keyword argument is used to populate the `__dict__` of
        the `LogRecord`.
        """
        return {
            attr_name: record.__dict__[attr_name]
            for attr_name in record.__dict__
            if attr_name not in BUILTIN_ATTRS
        }

    def json_record(self, message, extra, record, error_dict):
        """Prepares a JSON payload which will be logged.
        Override this method to change JSON log format.
        :param message: Log message, e.g., `logger.info(msg='Sign up')`.
        :param extra: Dictionary that was passed as `extra` param
            `logger.info('Sign up', extra={'referral_code': '52d6ce'})`.
        :param record: `LogRecord` we got from `JSONFormatter.format()`.
        :return: Dictionary which will be passed to JSON lib.
        """
        extra['message'] = message
        if 'time' not in extra:
            extra['time'] = datetime.utcnow()
        return extra

    def mutate_json_record(self, json_record):
        """Override it to convert fields of `json_record` to needed types.
        Default implementation converts `datetime` to string in ISO8601 format.
        """
        for attr_name in json_record:
            attr = json_record[attr_name]
            if isinstance(attr, datetime):
                json_record[attr_name] = attr.isoformat()
        return json_record


class CustomisedJSONFormatter(JSONFormatter):

    def json_record(self, message, extra, record, error_dict):
        """ https://docs.python.org/2/library/logging.html#logrecord-objects """

        if 'time' not in extra:
            extra['time'] = django.utils.timezone.now()

        extra['os'] = platform.platform()
        extra['language'] = 'Python {}'.format(platform.python_version())
        extra['app_id'] = 'ozp-backend'
        extra['app_version'] = os.environ['OZP_BACKEND_VERSION']
        extra['environment'] = (os.getenv('OZP_ENVIRONMENT') or 'dev')
        extra['hostname'] = socket.gethostname()
        extra['process_id'] = record.process

        extra['levelname'] = record.levelname
        extra['message'] = message
        extra['logger'] = record.name

        extra['backtrace'] = []
        extra['type'] = 'record'

        if error_dict:
            extra['message'] = error_dict['message']
            extra['backtrace'] = error_dict['backtrace']
            extra['type'] = error_dict['type']

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
