"""
Plugin Manager
"""
import datetime
import json
import os
import sys
import imp
import importlib
import logging
import traceback
from types import ModuleType
import requests


from django.conf import settings


logger = logging.getLogger('ozp-center.' + str(__name__))

BASE_PLUGIN_DIRECTORY = ('%s/%s') % (os.path.realpath(os.path.join(os.path.dirname(__file__), '../')), 'plugins')


# sys.path.insert(0, BASE_DIRECTORY)
class DynamicImporterWrapper(object):
    """
    Dynamic Importer Wrapper
    """

    def _validate(self):
        if not isinstance(self.input_module, ModuleType):
            raise TypeError('Input module not of type module')
        if not hasattr(self.input_class, '__class__'):
            raise TypeError('Input class not of type class')

    def __init__(self, input_module, input_class, error_message=None):
        self.input_module = input_module
        self.input_class = input_class
        self._validate()
        self.error = False

        if error_message:
            self.error = True
            self.error_message = error_message

    def __str__(self):
        return '({0!s},{1!s},{2!s})'.format(self.input_module, self.input_class, self.error)

    def __unicode__(self):
        return u'({0!s},{1!s},{2!s})'.format(self.input_module, self.input_class, self.error)

    def __repr__(self):
        return '({0!s},{1!s},{2!s})'.format(self.input_module, self.input_class, self.error)


def dynamic_importer(name, class_name=None):
    """
    Dynamically imports modules / classes

    Usage:
    DynamicImporterWrapper(module, class) = dynamic_importer("plugins.default_access_control.main", "PluginMain")

    """
    current_module = importlib.util.find_spec(name)
    current_module_found = current_module is not None

    if not current_module_found:
        return DynamicImporterWrapper(None, None, 'Unable to locate module: {0!s}'.format(name))

    try:
        loaded_module = current_module.loader.load_module()
    except Exception as e:
        traceback.print_exc()
        return DynamicImporterWrapper(None, None, 'Error Loading module: {0!s} - Reason:{1!s}'.format(name, str(e.__traceback__)))

    if class_name:
        if getattr(loaded_module, class_name, None):
            return DynamicImporterWrapper(loaded_module, loaded_module.PluginMain)
        else:
            return DynamicImporterWrapper(loaded_module, None, 'Unable to locate Plugin Entry Point: {0!s}'.format(name))
    else:
        return DynamicImporterWrapper(loaded_module, None)


def dynamic_directory_importer(path=BASE_PLUGIN_DIRECTORY):
    """
    Used to load whole directory
    """
    output_list = []

    listing = os.listdir(path)
    for infile in listing:
        if os.path.isdir(os.path.join(path, infile)):
            if(os.path.isfile(os.path.join(path, infile, 'main.py'))):
                current_importer = dynamic_importer('plugins.{0!s}.main'.format(infile), 'PluginMain')
                output_list.append(current_importer)
    return output_list


def dynamic_mock_service_importer(path=BASE_PLUGIN_DIRECTORY):
    """
    Used to load whole directory
    """
    output_list = []

    listing = os.listdir(path)
    for infile in listing:
        if os.path.isdir(os.path.join(path, infile)):
            if(os.path.isfile(os.path.join(path, infile, 'tests', 'mock.py'))):
                current_importer = dynamic_importer('plugins.{0!s}.tests.mock'.format(infile))
                output_list.append(current_importer)
    return output_list


class PluginManager(object):
    """

    """

    def __init__(self, instances=None, path=BASE_PLUGIN_DIRECTORY):
        """
        Used to initialize plugin
        """
        self.loaded = False
        self.instances = instances
        self.path = path

    def _load(self, path=BASE_PLUGIN_DIRECTORY):
        """
        Lazy loading of plugins
        """
        if not self.instances and not self.loaded:
            self.loaded = True
            # Load plugins
            self.instances = {}

            for importer_wrapper in dynamic_directory_importer(path):
                if importer_wrapper.error:
                    logger.error('Error Loading Plugin: {0!s} - Error Message {1!s} '.format(importer_wrapper, importer_wrapper.error_message))
                else:
                    current_class_instance = importer_wrapper.input_class(settings=settings, requests=requests)
                    self.instances[current_class_instance.plugin_name] = current_class_instance
                    logger.info('Success Loading Plugin: {0!s}'.format(importer_wrapper))

    def __getattr__(self, plugin_name, path=BASE_PLUGIN_DIRECTORY):
        """
        Allows access to plugins using plugin manager instance attributes
        """
        plugin_instance = self.get_plugin_instance(plugin_name, path=path)

        if plugin_instance:
            return plugin_instance
        else:
            # Default behaviour
            raise AttributeError('Class missing method: {0!s}'.format(name))

    def load_mock_services(self, router_instance, path=BASE_PLUGIN_DIRECTORY):
        """
        Method used to load mock route from the plugins to the mock router

        if {BASE_PLUGIN_DIRECTORY}/{plugin_root_path}/test/mock.py
            load module
            check to see if it has url attr
            if has url list attr add it to the router instance
        else
            ignore directory

        Arg:
            router_instance
        """
        for importer_wrapper in dynamic_mock_service_importer(path):
            current_module = importer_wrapper.input_module
            if hasattr(current_module, 'urls'):
                # Found Urls in
                router_instance.add_urls(current_module.urls)
                logger.info('Loaded Mock Services for {0!s} '.format(current_module))

    def get_plugin_instance(self, plugin_name, path=BASE_PLUGIN_DIRECTORY):
        """
        Used to get the instance of a plugin
        """
        if not self.loaded:
            self._load()

        if self.instances.get(plugin_name):
            return self.instances.get(plugin_name)
        else:
            return None


plugin_manager_instance = PluginManager()

# Import helper for the mock services
from ozp.tests import helper

if hasattr(settings, 'ACCESS_CONTROL_PLUGIN'):
    ACCESS_CONTROL_PLUGIN = settings.ACCESS_CONTROL_PLUGIN
else:
    logger.warn('Loaded default plugin for access control')
    ACCESS_CONTROL_PLUGIN = 'default_access_control'

if hasattr(settings, 'AUTHORIZATION_PLUGIN'):
    AUTHORIZATION_PLUGIN = settings.AUTHORIZATION_PLUGIN
else:
    logger.warn('Loaded default plugin for authorization')
    AUTHORIZATION_PLUGIN = 'default_authorization'


def get_system_access_control_plugin():
    return plugin_manager_instance.get_plugin_instance(ACCESS_CONTROL_PLUGIN)


def get_system_authorization_plugin():
    return plugin_manager_instance.get_plugin_instance(AUTHORIZATION_PLUGIN)
