"""
Utility functions
"""
import re
import sys

def make_keysafe(key):
    """
    given an input string, make it lower case and remove all non alpha-numeric
    characters so that it will be safe to use as a cache keyname

    TODO: check for max length (250 chars by default for memcached)
    """
    return re.sub(r'\W+', '', key).lower()