
from rest_framework import parsers

class DataResourceParser(parsers.JSONParser):
    """
    Parser for IWC data resources

    JSON data with specific media type
    """
    media_type = 'application/vnd.ozp-iwc-data-object-v2+json'
