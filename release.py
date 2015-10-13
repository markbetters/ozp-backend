"""
Running this script will generate Wheels for the ozp-backend django app and its
dependencies

setuptools and wheel library must be installed in the current python
environment before running this script
"""
import argparse
import datetime
import glob
import re
import shutil
from subprocess import call

VERSION_FILE = "_version.py"
PACKAGE = 'ozp_backend'

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
        raise RuntimeError("Unable to find version string in %s." % (VERSION_FILE,))

def get_date_time():
    """
    Get current date/time string
    """
    return datetime.datetime.now().strftime('%m_%d_%Y-%H-%M')

def cleanup():
    """
    Remove build directories
    """
    shutil.rmtree("wheel", ignore_errors=True)
    shutil.rmtree("wheelhouse", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("%s.egg-info" % PACKAGE, ignore_errors=True)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', dest='version', action='store_true',
        help='Use the version number in the file output')
    parser.add_argument('--no-version', dest='version', action='store_false',
        help='Use the current date/time in the file output')
    parser.set_defaults(version=False)
    args = parser.parse_args()

    # clean up previous builds
    cleanup()

    # build wheel for ozp_backend - creates wheel in dist/
    call("python setup.py bdist_wheel", shell=True)

    # build/collect wheels for dependencies (this will put wheels in wheelhouse/)
    call("pip wheel -r requirements.txt", shell=True)

    # add our wheel to the wheelhouse
    for file in glob.glob(r'dist/*.whl'):
        shutil.copy(file, "wheelhouse")

    # tar up the wheelhouse
    if args.version:
        version = get_version()
        call("tar -czf %s-%s-wheelhouse.tar.gz wheelhouse" % (PACKAGE, version),
            shell=True)
    else:
        date = get_date_time()
        call("tar -czf %s-%s-wheelhouse.tar.gz wheelhouse" % (PACKAGE, date),
            shell=True)

    # cleanup build dirs
    cleanup()

    # to install the backend in a new python virtualenv, run
    # tar -xzf ozp_backend-<version||time>-wheelhouse.tar.gz
    # pip install --no-index --find-links=wheelhouse ozp_backend==1.0


if __name__ == "__main__":
    run()