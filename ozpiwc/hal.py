"""
HAL helpers
"""
import ozpcenter.model_access as model_access

#### Constants
USER_REL = "ozp:user"
APPLICATION_REL = "ozp:application"
INTENT_REL = "ozp:intent"
SYSTEM_REL = "ozp:system"
USER_DATA_REL = "ozp:user-data"
APPLICATION_LIBRARY_REL = "ozp:application-library"


def create_base_structure(request):
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
                "href": '%s' % request.build_absolute_uri(request.path)
            }
        },
        "_embedded": {

        }
    }
    return data

def get_abs_url_for_profile(request, profile_id):
    root_url = request.build_absolute_uri('/')
    return '%siwc-api/profile/%s/' % (root_url, profile_id)
