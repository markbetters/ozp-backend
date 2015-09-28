"""
Model access
"""
import json
import logging

import ozpiwc.models as models
import ozpiwc.errors as errors

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_data_resource(username, key):
    return models.DataResource.objects.filter(
                key=key, username=username).first()

def set_data(username, key, request_data):
    required_fields = ['entity']
    for i in required_fields:
        if i not in request_data:
            raise errors.InvalidInput('missing required field %s' % i)

    # value = json.dumps(request_data)
    entity = request_data['entity']
    content_type = request_data.get('content_type', None)

    logger.debug('Saving data resource with key %s, value %s, username %s' % (key, value, username))
    data = models.DataResource(username=username, key=key, value=value,
        content_type=content_type)
    data.save()
    return {'key': key, 'value': value, 'username': username,
        'content_type': content_type}


def get_data(username, key):
    logger.debug('looking for key %s' % key)
    try:
        data = models.DataResource.objects.get(username=username, key=key)
        value = {'version': data.value.version, 'entity': data.value.entity,
            'pattern': data.value.pattern, 'permissions': data.value.permissions,
            'collection': data.value.collection}
        return {'key': data.key, 'value': value, 'username': username,
        'content_type': data.content_type}

    except models.DataResource.DoesNotExist:
        return None

def get_all_data(username):
    return models.DataResource.objects.filter(username=username)

def get_all_keys(username):
    return models.DataResource.objects.filter(username=username).only('key')