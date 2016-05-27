"""
HAL helpers
"""
import re

import ozpcenter.model_access as model_access

# Constants
USER_REL = "ozp:user"
APPLICATION_REL = "ozp:application"
INTENT_REL = "ozp:intent"
SYSTEM_REL = "ozp:system"
USER_DATA_REL = "ozp:user-data"
DATA_ITEM_REL = "ozp:data-item"
APPLICATION_ITEM_REL = "ozp:application-item"


def create_base_structure(request, type='application/json'):
    """
    Creates the initial HAL structure for a given request
    """
    root_url = request.build_absolute_uri('/')
    profile = model_access.get_profile(request.user.username)
    data = {
        "_links": {
            "curies": {
                "href": "http://ozoneplatform.org/docs/rels/{rel}",
                "name": "ozp",
                "templated": True
            },
            "self": {
                "href": '{0!s}'.format(request.build_absolute_uri(request.path)),
                "type": type
            }
        },
        "_embedded": {

        }
    }
    return data


def add_hal_structure(data, request, type='application/json'):
    """
    Adds initial HAL structure to existing dictionary
    """
    data["_links"] = {
        "curies": {
            "href": "http://ozoneplatform.org/docs/rels/{rel}",
            "name": "ozp",
            "templated": True
        },
        "self": {
            "href": '{0!s}'.format(request.build_absolute_uri(request.path)),
            "type": type
        }
    }
    data["_embedded"] = {}
    return data


def get_abs_url_for_profile(request, profile_id):
    root_url = request.build_absolute_uri('/')
    return '{0!s}iwc-api/profile/{1!s}/'.format(root_url, profile_id)


def get_abs_url_for_iwc(request):
    root_url = request.build_absolute_uri('/')
    return '{0!s}iwc-api/'.format(root_url)


def add_link_item(url, data, type='application/json'):
    if 'item' not in data['_links']:
        data['_links']['item'] = []
    new_link = {'href': url, 'type': type}
    data['_links']['item'].append(new_link)
    return data


def generate_content_type(type, version=2):
    """
    Generate the Content-Type header, including a version number

    Content-Types look like: application/vnd.ozp-iwc+json;version=1
    """
    try:
        version = re.findall(r'version=(\d+)', type)[0]
        # version number found already - just use what's there
        return type
    except IndexError:
        return '{0!s};version={1!s}'.format(type, version)


def validate_version(accept_header):
    """
    Ensure the client is requesting a valid version for this resource

    It is valid to not specify a version (the latest will be used)
    """
    # Currently, this backend only supports one version for all resources
    if not accept_header:
        return True
    accept_header = accept_header.replace(" ", "").lower()
    try:
        version = re.findall(r'version=(\d+)', accept_header)[0]
        if version != '2':
            return False
    except IndexError:
        pass

    return True
