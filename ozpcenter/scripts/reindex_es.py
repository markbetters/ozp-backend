"""
Reindex data script

************************************WARNING************************************
Running this script will delete existing data in elasticsearch
************************************WARNING************************************
"""
import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from ozpcenter.api.listing.model_access_es import bulk_reindex


def run():
    """
    Reindex Data
    """
    bulk_reindex()
