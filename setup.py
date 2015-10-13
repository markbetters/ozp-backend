# from distutils.core import setup
import re
from setuptools import setup

PKG = "ozp_backend"
VERSIONFILE="_version.py"
verstr = "unknown"

verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


install_requires = [
    'django-cors-headers>=1.1.0',
    'django-enumfield>=1.2.1',
    'django-extensions>=1.5.5',
    'django-extras>=0.3',
    'django-filter>=0.10.0',
    'django-rest-swagger>=0.3.2',
    'django>=1.8.2',
    'djangorestframework>=3.2.2',
    'drf-nested-routers>=0.9.0',
    'factory-boy>=2.5.2',
    'fake-factory>=0.5.1',
    'gunicorn>=19.3.0',
    'Markdown>=2.6.2',
    'Pillow>=2.9.0',
    'pytz>=2015.4',
    'pyyaml>=3.11',
    'requests>=2.7.0',
    'six>=1.9.0',
    'wheel>=0.24.0'
]

packages = ['ozp', 'ozpcenter', 'ozpiwc']
package_data = {'': ['README.md', 'static']}

setup(name=PKG,
    version=verstr,
    packages=packages,
    package_data=package_data,
    include_package_data=True,
    install_requires=install_requires
)