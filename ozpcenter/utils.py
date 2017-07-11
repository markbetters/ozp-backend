"""
Utility functions
"""
import datetime
import pytz
import re

from django.template import Context
from django.template import Template


def make_keysafe(key):
    """
    given an input string, make it lower case and remove all non alpha-numeric
    characters so that it will be safe to use as a cache keyname

    TODO: check for max length (250 chars by default for memcached)
    """
    return re.sub(r'[^a-zA-Z0-9_."`-]+', '', key).lower()


def find_between(s, start, end):
    """
    Return a string between two other strings
    """
    return (s.split(start))[1].split(end)[0]


def get_now_utc():
    """
    Return current datetime in UTC

    Format: YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ]
    """
    return datetime.datetime.now(pytz.utc)


def render_template_string(template_string, context_dict):
    """
    Render Django Template

    Args:
        template_string(str): Template String
        context_dict(dict): Context Variable Dictionary
    """
    template_context = Context(context_dict)
    template = Template(template_string)
    return template.render(template_context)
