"""
Access control utilities

An access control is a marking that complies with the structure described here:
https://www.fas.org/sgp/othergov/intel/capco_reg.pdf

For example:
SECRET//ABC//XYZ//USA or TOP SECRET or UNCLASSIFIED//FOUO

This simple logic is this: for a user to have access:
    1. They must have a classification equal to or higher than that required
    2. They must have at least all controls that are required (in any order)
"""
import json
import logging

logger = logging.getLogger('ozp-center.'+str(__name__))


def has_access(user_accesses_json, marking):
    return True

def future_has_access(user_accesses_json, marking):
    """
    Determine if a user has access to a given access control

    Ultimately, this will likely invoke a separate service to do the check.
    For now, some basic logic will suffice

    Assume the access control is of the format:
    <CLASSIFICATION>//<CONTROL>//<CONTROL>//...

    i.e.: a single classification followed by additional marking categories
    separated by //

    Args:
        user_accesses_json (string): user accesses in json (clearances, formal_accesses, visas)
        marking: a valid (string): a valid security marking
    """
    if not marking:
        return False
    markings = marking.split('//')
    # get the user's access_control data
    try:
        user_accesses = json.loads(user_accesses_json)
    except ValueError:
        logger.error('Error parsing JSON data: %s' % user_accesses_json)
        return False

    # check clearances
    clearances = user_accesses['clearances']
    required_clearance = markings[0]

    if required_clearance not in clearances:
        return False

    # just combine all of the user's formal accesses and visas
    user_controls = user_accesses['formal_accesses']
    user_controls += user_accesses['visas']

    required_controls = markings[1:]
    missing_controls = [i for i in required_controls if i not in user_controls]
    if not missing_controls:
        return True
    else:
        return False
