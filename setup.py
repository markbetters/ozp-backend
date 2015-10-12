# from distutils.core import setup
from setuptools import setup

setup(name='ozp-backend',
    version='1.0',
    packages=['ozp', 'ozpcenter', 'ozpiwc'],
    package_data={'': ['README.md', 'static']},
    include_package_data=True,
    install_requires=[
        'django-cors-headers==1.1.0',
        'django-enumfield==1.2.1',
        'django-extensions==1.5.5',
        'django-extras==0.3',
        'django-filter==0.10.0',
        'django-rest-swagger==0.3.2',
        'django==1.8.2',
        'djangorestframework==3.2.2',
        'drf-nested-routers==0.9.0',
        'factory-boy==2.5.2',
        'fake-factory==0.5.1',
        'gunicorn==19.3.0',
        'Markdown==2.6.2',
        'Pillow==2.9.0',
        'pytz==2015.4',
        'pyyaml==3.11',
        'requests==2.7.0',
        'six==1.9.0',
        'wheel==0.24.0'
    ]
)