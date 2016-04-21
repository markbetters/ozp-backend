"""
Access control utilities

An access control is a marking that complies with the structure described here:
https://www.fas.org/sgp/othergov/intel/capco_reg.pdf

For example:
    SECRET//ABC//XYZ//USA or TOP SECRET or UNCLASSIFIED//FOUO

Classification Validation:
    A string is made of tokens separated by a delimiter

'SECRET//ABC//XYZ//USA'  is made of 4 tokens  [ Token(SECRET), Token(ABC), Token(XYZ), Token(USA) ]



This simple logic is this: for a user to have access:
    1. They must have a classification equal to or higher than that required
    2. They must have at least all controls that are required (in any order)
"""
import json
import logging

logger = logging.getLogger('ozp-center')


class Token(object):

    def __init__(self, short_name=None, long_name=None):
        self.short_name = short_name
        self.long_name = long_name

    def __str__(self):
        return '%s(%s)' % (self.token_type, self.long_name)

    def __repr__(self):
        return '%s(%s)' % (self.token_type, self.long_name)

    def __unicode__(self):
        return u'%s(%s)' % (self.token_type, self.long_name)


class InvalidFormatToken(Token):

    def __init__(self, **kwargs):
        super(InvalidFormatToken, self).__init__(**kwargs)
        self.token_type = 'InvalidFormatToken'

class UnknownToken(Token):

    def __init__(self, **kwargs):
        super(UnknownToken, self).__init__(**kwargs)
        self.token_type = 'UnknownToken'


class ClassificationToken(Token):

    def __init__(self, level=1, **kwargs):
        super(ClassificationToken, self).__init__(**kwargs)
        self.token_type = 'ClassificationToken'
        self.level = level


class DisseminationControlToken(Token):

    def __init__(self,  **kwargs):
        super(DisseminationControlToken, self).__init__(**kwargs)
        self.token_type = 'DisseminationControlToken'


def _convert_dict_to_token(input):
    """
    Converts Dictionary into Token
    """
    type = input.get('type')
    data = input.get('data')

    if type is None or data is None:
        return InvalidFormatToken()

    tokenTypeClass = InvalidFormatToken

    if type == 'Classification':
        tokenTypeClass = ClassificationToken
    elif type == 'DisseminationControl':
        tokenTypeClass = DisseminationControlToken
    else:
        return tokenTypeClass()

    return tokenTypeClass(**data)


tokens_list = [
    # Classification Tokens
    {'type':'Classification',
     'data':{'short_name':'U',
             'long_name':'Unclassified',
             'level': 1}
    },
    {'type':'Classification',
     'data':{'short_name':'C',
             'long_name':'Confidential',
             'level': 2}
    },
    {'type':'Classification',
     'data':{'short_name':'S',
             'long_name':'Secret',
             'level': 3}
    },
    {'type':'Classification',
     'data':{'short_name':'TS',
             'long_name':'Top Secret',
             'level': 4}
    },
    # Dissemination Control Tokens
    {'type':'DisseminationControl',
     'data':{'short_name':'FOUO',
             'long_name':'FOR OFFICIAL USE ONLY'}
    }
]

tokens = [ _convert_dict_to_token(input) for input in tokens_list]

def _split_tokens(input_marking, delimiter='//'):
    """
    This method is responsible for converting a String into Tokens
    """
    long_name_lookup = {}
    for token in tokens:
        long_name_lookup[token.long_name.upper()] = token

    short_name_lookup = {}
    for token in tokens:
        short_name_lookup[token.short_name.upper()] = token

    markings = input_marking.split(delimiter)

    output_tokens = []
    for marking in markings:
        current_token = None

        if marking.upper() in long_name_lookup:
            current_token = long_name_lookup[marking.upper()]
        else:
            if marking.upper() in short_name_lookup:
                current_token = short_name_lookup[marking.upper()]
            else:
                current_token = UnknownToken(long_name=marking)

        output_tokens.append(current_token)
    return output_tokens


def validate_marking(marking):
    """
    This function is responsible for validating a marking string

    Assume the access control is of the format:
    <CLASSIFICATION>//<CONTROL>//<CONTROL>//...

    """
    if not marking:
        return False
    tokens = _split_tokens(marking)

    if not isinstance(tokens[0], ClassificationToken):
        return False

    return True


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
