"""
Running this script will generate Wheels for the ozp-backend django app and its
dependencies

setuptools, wheel, and django libraries must be installed in the current python
environment before running this script

NOTE: It's not yet clear whether we want to install a Wheel for the ozp_backend
application itself, or if it will be better to install wheels for all of the
dependencies, then use the source of ozp_backend for running the app.

Installing ozp_backend as a wheel will place it in <python_env>/lib/Python3.4.3/site-packages/,
which might not be as convenient as running from source.

After running this script, the application can be deployed "from source"
by doing:

tar -xzf <release tarball>
pip install --no-index --find-links=release/wheelhouse -r requirements.txt
gunicorn ozp.wsgi ... (from the release directory referencing the local ozp package)

Alternatively, the wheel for the application can be installed in the python
env and the source is no longer needed:

tar -xzf <release tarball>
pip install --no-index --find-links=release/wheelhouse ozp_backend==1.0
gunicorn ozp.wsgi ... (ozp.wsgi is installed in site-packages, so it can be run
    from anywhere)

One problem with the latter method is that it will only include the python
packages (no static files, test data, etc). Theoretically we should be able
to modify setup.py and specify those things in data_files, but that has not
yet worked out
"""
import argparse
import datetime
import glob
import os
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
        raise RuntimeError(
            "Unable to find version string in {0!s}.".format(VERSION_FILE))


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
    shutil.rmtree("release", ignore_errors=True)
    shutil.rmtree("{0!s}.egg-info".format(PACKAGE), ignore_errors=True)


def create_release_dir():
    """
    Creates a directory for the release and moves files there
    """
    os.mkdir("release")
    shutil.copytree("wheelhouse", "release/wheelhouse")
    shutil.copytree("ozp", "release/ozp")
    shutil.copytree("ozpcenter", "release/ozpcenter")
    shutil.copytree("ozpiwc", "release/ozpiwc")
    shutil.copytree("static", "release/static")
    shutil.copytree("plugins", "release/plugins")
    shutil.copytree("plugins_util", "release/plugins_util")
    shutil.copy("_version.py", "release")
    shutil.copy("manage.py", "release")
    shutil.copy("README.md", "release")
    shutil.copy("requirements.txt", "release")
    shutil.copy("Makefile", "release")


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

    # collect static files
    call("mkdir -p static", shell=True)
    call("python manage.py collectstatic --noinput", shell=True)
    # make directory for wheelhouse
    call("mkdir -p wheelhouse", shell=True)

    # build wheel for ozp_backend - creates wheel in dist/
    call("python setup.py bdist_wheel", shell=True)

    # build/collect wheels for dependencies (this will put wheels in
    # wheelhouse/)
    call("pip wheel -r requirements.txt --wheel-dir wheelhouse", shell=True)

    call("cp wheelhouse/msgpack_python-0.4.7-cp34-cp34m-manylinux1_x86_64.whl wheelhouse/msgpack_python-0.4.7-cp34-cp34m-linux_x86_64.whl", shell=True)
    # add our wheel to the wheelhouse
    for file in glob.glob(r'dist/*.whl'):
        shutil.copy(file, "wheelhouse")

    # create release directory including the wheelhouse (dependencies) and the
    # relevant source for ozp_backend
    create_release_dir()

    # tar everything up
    if args.version:
        version = get_version()
        call("tar -czf {0!s}-{1!s}.tar.gz release".format('backend', version),
             shell=True)
    else:
        date = get_date_time()
        call("tar -czf {0!s}-{1!s}.tar.gz release".format('backend', date),
             shell=True)

    # cleanup build dirs
    cleanup()


if __name__ == "__main__":
    run()
