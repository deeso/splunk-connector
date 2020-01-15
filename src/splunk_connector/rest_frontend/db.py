import traceback
import importlib
from .consts import *
import urllib.parse
from .standard_logger import Logger
from pymongo import MongoClient
from sqlalchemy import create_engine


class DBSettings(object):

    @classmethod
    def get_mongoclient_kargs(cls, **kargs):
        config = {}
        for k, nk in MAP_MONGO_TO_APP.items():
            v = kargs.get(k, '')
            config[nk] = v
        return config

    @classmethod
    def get_mongo_config(cls, **kargs):
        settings = {}
        for k, nk in MAP_MONGO_TO_SETTINGS.items():
            v = kargs.get(k, '')
            if v is None:
                v = ''
            settings[nk] = v
        return settings

    @classmethod
    def get_sqlalchemy_config(cls, **kargs):
        config = {}
        for k, nk in MAP_SQLALCHEMY_TO_APP.items():
            v = kargs.get(k, '')
            if v is None:
                v = ''
            config[nk] = v

        if config.get(PASSWORD, None) is not None:
            config[PASSWORD] = urllib.parse.quote_plus(config[PASSWORD])
        config[DIALECT_DRIVER] = SQLALCHEMY_DIALECT
        uri = DB_URI_FMT.format(**config)
        return {SQLALCHEMY_DATABASE_URI: uri}

class DefaultMapper(object):
    NAME = 'DefaultMapper'
    LOGGER = Logger(NAME)
    DEFAULT_SETTINGS = {}
    ENGINE_SETTINGS_MAP = {}

    def __init__(self, name, rest_service, **kwargs):
        self.name = name
        self.rest_service = rest_service
        self.resource_klass = None
        self.controller_klass = None
        self.odm_klass = None

        for k, v in self.DEFAULT_SETTINGS.items():
            setattr(self, k, kwargs.get(k, v))

        self.resource_klass = None
        self.controller_klass = None
        self.om_klass = None
        if getattr(self, CLASS, None) is not None:
            self.om_klass = self.load_class(getattr(self, CLASS))

        if getattr(self, RESOURCE, None) is not None:
            self.resource_klass = self.load_class(getattr(self, RESOURCE))

        if getattr(self, CONTROLLER, None) is not None:
            self.controller_klass = self.load_class(getattr(self, CONTROLLER))

    def patch_om_klass(self):
        raise Exception("Not implemented")

    def patch_controller_klass(self):
        raise Exception("Not implemented")

    def patch_resource_klass(self):
        raise Exception("Not implemented")

    def create_engine_settings(self):
        settings = {}
        default_settings = self.get_default_engine_settings()
        for k, v in self.ENGINE_SETTINGS_MAP.items():
            if not hasattr(self, k) and k in default_settings:
                settings[v] = default_settings.get(k)
            else:
                settings[v] = getattr(self, k, None)
        return settings

    def create_engine(self):
        raise Exception("Not implemented")

    @classmethod
    def load_class(self, classname):
        blah = classname.split('.')
        if len(blah) <= 1:
            raise Exception("Expecting a python_module.Class got {}".format(classname))

        mn = '.'.join(blah[:-1])
        cn = blah[-1]
        mi = None
        python_class = None

        try:
            mi = importlib.import_module(mn)
        except:
            msg = "{} is not a valid Python module: \n{}".format(mn, traceback.format_exc())
            self.LOGGER.exception(msg)
            return None

        try:
            python_class = getattr(mi, cn, None)
        except:
            msg = "{} is not a valid Python class in {}: \n{}".format(cn, mn, traceback.format_exc())
            self.LOGGER.exception(msg)
            return None
        return python_class

    def get_default_engine_settings(self):
        return getattr(self, DEFAULT_ENGINE_SETTINGS, None)

    def can_create_uri(self, settings):
        return all([k in settings for k in REQUIRED_DB_URI_FMT_KEYS])

class ODMMapper(DefaultMapper):
    NAME = 'ODMMapper'
    LOGGER = Logger(NAME)
    ENGINE_SETTINGS = {}
    def __init__(self, name, rest_service, **kargs):
        super(ODMMapper, self).__init__(name, rest_service, **kargs)

        self.uri = None


        self.patch_om_klass()
        self.patch_resource_klass()
        self.patch_controller_klass()

        self.engine = self.create_engine()

    def create_engine(self):
        settings = self.create_engine_settings()
        return MongoClient(**settings)


class ORMMapper(DefaultMapper):
    NAME = 'ORMMapper'
    LOGGER = Logger(NAME)
    ENGINE_SETTINGS = {}
    def __init__(self, name, rest_service, **kargs):
        super(ORMMapper, self).__init__(name, rest_service, **kargs)

        self.uri = None
        self.patch_om_klass()
        self.patch_resource_klass()
        self.patch_controller_klass()

        self.engine = self.create_engine()

    def create_engine(self):
        settings = self.create_engine_settings()
        return MongoClient(**settings)
