"""
Parsers for declaring specific content-types
"""
from rest_framework import parsers


class DataResourceParser(parsers.JSONParser):
    media_type = 'application/vnd.ozp-iwc-data-object+json;version=2'
