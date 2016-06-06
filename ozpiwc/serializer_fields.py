import json

from rest_framework import serializers


class JsonField(serializers.Field):
    """
    A field with a JSON value
    """
    default_error_messages = {
        'invalid_json': 'Invalid JSON object',
        'other': 'Other error: {err}'
    }

    def to_representation(self, obj):
        if isinstance(obj, str):
            return obj
        return json.dumps(obj)

    def to_internal_value(self, data):
        try:
            if isinstance(data, str):
                return data
            else:
                return json.dumps(data)
        except ValueError:
            self.fail('invalid_json')
        except Exception as e:
            self.fail('other', err=str(e))
