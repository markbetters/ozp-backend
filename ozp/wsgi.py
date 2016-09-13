"""
WSGI config for ozp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import re

from django.core.wsgi import get_wsgi_application

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VERSION_FILE = os.path.join(BASE_DIR, '_version.py')


def get_version():
    """
    Get the version number from VERSION_FILE
    """
    verstrline = open(VERSION_FILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
        return verstr
    else:
        raise RuntimeError(
            "Unable to find version string in {0!s}.".format(VERSION_FILE))


# TODO: Find a better way to get version
os.environ['OZP_BACKEND_VERSION'] = get_version()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ozp.settings')

application = get_wsgi_application()
