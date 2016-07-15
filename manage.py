#!/usr/bin/env python
import os
import sys
import _version

if __name__ == "__main__":
    os.environ['OZP_BACKEND_VERSION'] = _version.__version__  # TODO: Find a better way to get version
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozp.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
