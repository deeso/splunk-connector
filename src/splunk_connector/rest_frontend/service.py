from .config import Config
from .consts import *
from .standard_logger import Logger
from quart_openapi import Pint
from .db import DBSettings, ODMMapper, ORMMapper
import importlib
import traceback
import asyncio
from multiprocessing import Process
from hypercorn.config import Config as HyperConfig
from hypercorn.asyncio import serve
from sqlalchemy.engine import create_engine
from .models import patch_umongo_meta, patch_sqlalchemy_meta
from sqlalchemy.ext.declarative import declarative_base

class RestService(object):
    DEFAULT_VALUES = REST_SERVICE_CONFIGS
    NAME = REST_SERVICE_BLOCK

    def __init__(self, **kwargs):
        self.init_keys = set()

        for k, v in kwargs.items():        # TODO figure out how to distinguish between Models in Mongo and Postgres
            setattr(self, k, v)
            self.init_keys.add(k)

        for k, v in self.DEFAULT_VALUES.items():
            if k not in kwargs:
                setattr(self, k, v)
            else:
                setattr(self, k, kwargs.get(k))

        self.logger = Logger(self.NAME)

        self.app = Pint(self.NAME)
        self.app.config.update(DBSettings.get_mongo_config(**kwargs))
        self.app.config.update(DBSettings.get_sqlalchemy_config(**kwargs))


        self.orm_mappings = {}
        self.odm_mappings = {}
        self.default_mongo_settings = {}
        self.default_sqlalchemy_settings = {}

        self.default_mongo_engine = None
        self.default_sqla_engine = None

        self.views = []
        if isinstance(kwargs.get(VIEWS, list()), list):
            for v in kwargs.get(VIEWS, list()):
                self.import_add_view(v)

        if self.get_using_mongo():
            self.default_mongo_settings = DBSettings.get_mongoclient_kargs(**kwargs)
            self.default_mongo_settings[TLS_INSECURE] = True
            if self.default_mongo_settings.get(SSL_KEYFILE, None) is None:
                self.default_mongo_settings[SSL_KEYFILE] = self.get_key_pem()
            if self.default_mongo_settings.get(SSL_CERTFILE, None) is None:
                self.default_mongo_settings[SSL_KEYFILE] = self.get_cert_pem()



        if self.get_using_postgres():
            self.default_sqlalchemy_settings = DBSettings.get_sqlalchemy_config(**kwargs)
            uri = self.pgc.get(SQLALCHEMY_DATABASE_URI)
            self.default_sqla_engine = create_engine(uri)

            for name, kargs in self.get_sqlalchemy_orms():
                classname = kargs.get(ORM_CLASS, None)
                tablename = kargs.get(TABLE, None)

                if classname is None or tablename is None:
                    continue
                self.import_add_orms(classname, tablename)



        self.load_odm_configurations(self.get_odms())
        self.load_orm_configurations(self.get_orms())
        self.bg_thread = None

    def load_odm_configurations(self, odm_configs):
        for name, configs in odm_configs.items():
            odm = ODMMapper(name, default_engine_settings=self.default_mongo_settings, **configs)
            self.odm_mappings[name] = odm

        # TODO finalize mappings

    def load_orm_configurations(self, orm_configs):
        for name, configs in orm_configs.items():
            odm = ODMMapper(name, default_engine_settings=self.default_sqlalchemy_settings, **configs)
            self.odm_mappings[name] = odm

        self.Base = declarative_base()


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
            self.logger.exception(msg)
            return None

        try:
            python_class = getattr(mi, cn, None)
        except:
            msg = "{} is not a valid Python class in {}: \n{}".format(cn, mn, traceback.format_exc())
            self.logger.exception(msg)
            return None
        return python_class

    def import_add_view(self, fq_python_class_view: str) -> bool:
        '''
        Import a module and load the class for a provided view
        :param view: Python module in dot'ted notation, e.g. `foo.views.ViewX`
        :return: bool
        '''
        self.logger.debug("Adding view ({}) to rest-service".format(fq_python_class_view))
        blah = fq_python_class_view.split('.')
        if len(blah) <= 1:
            raise Exception("Expecting a python_module.Class got {}".format(fq_python_class_view))

        python_class = self.load_class(fq_python_class_view)
        if python_class is not None:
            self.views.append(python_class)
            python_class.bind_application(self.app)
            self.logger.debug("Finished adding view ({}) to rest-service".format(fq_python_class_view))
            return True

        self.logger.debug("Failed tp add view ({}) to rest-service".format(fq_python_class_view))
        return False

    def import_add_odms(self, fq_python_class_odm: str, database_name, collection_name) -> bool:
        '''
        Import a module and load the class for a provided view
        :param view: Python module in dot'ted notation, e.g. `foo.views.ViewX`
        :return: bool
        '''
        self.logger.debug("Adding view ({}) to rest-service".format(fq_python_class_odm))

        python_class = self.load_class(fq_python_class_odm)

        if python_class is not None and self.default_mongo_engine is not None:
            kargs = {ODM_DATABASE: database_name,
                     ODM_COLLECTION: collection_name,
                     ODM_CONNECTION: self.default_mongo_engine
                     }
            r = patch_umongo_meta(python_class, **kargs)
            self.logger.debug("Finished adding view ({}) to rest-service".format(fq_python_class_odm))
            return r

        self.logger.debug("Failed tp add view ({}) to rest-service".format(fq_python_class_odm))
        return False

    def import_add_orms(self, fq_python_class_orm: str, table_name) -> bool:
        '''
        Import a module and load the class for a provided view
        :param view: Python module in dot'ted notation, e.g. `foo.views.ViewX`
        :return: bool
        '''
        self.logger.debug("Adding view ({}) to rest-service".format(fq_python_class_orm))

        python_class = self.load_class(fq_python_class_orm)

        if python_class is not None and self.default_sqla_engine is not None:
            kargs = {ORM_TABLE: table_name, }
            r = patch_sqlalchemy_meta(python_class, **kargs)
            self.logger.debug("Finished adding view ({}) to rest-service".format(fq_python_class_orm))
            return r

        self.logger.debug("Failed tp add view ({}) to rest-service".format(fq_python_class_orm))
        return False

    def add_odm(self, database_name, collection_name, odm_class):
        if self.mongddb_client is None:
            return False

        kargs = {'mongo_database': database_name,
                  'mongo_collection': collection_name,
                  'mongo_connection': self.mongddb_client
                  }
        patch_umongo_meta(odm_class, **kargs)
        return True

    @classmethod
    def from_config(cls):

        cdict = Config.get_value(REST_SERVICE_BLOCK)
        if cdict is None:
            cdict = {}

        kwargs = {}
        for k, v in cls.DEFAULT_VALUES.items():
            kwargs[k] = cdict.get(k, v)
        return cls(**kwargs)

    def run(self, debug=False):
        ssl_context = None
        self.logger.debug("Preparing to start rest-service")
        self.logger.info("Starting the application {}:{} using ssl? {}".format(self.get_listening_host(),
                                                                               self.get_listening_port(),
                                                                               ssl_context is None))
        # Created a separate process so that the application will run in the background
        # this lets me manage it from a distance if need be
        self.bg_thread = Process(target=self.start_app, args=(debug,))
        self.bg_thread.start()
        return True

    def start_app(self, debug):
        ssl_context = None
        self.logger.debug("Preparing to start rest-service")
        if self.get_use_ssl() and self.get_key_pem() is not None and \
                self.get_cert_pem() is not None:
            self.logger.debug("Preparing ssl_context with cert:{} and key:{}".format(self.get_cert_pem(),
                                                                                     self.get_key_pem()))
            ssl_context = (self.get_cert_pem(), self.get_key_pem())
        self.logger.info("Starting the application {}:{} using ssl? {}".format(self.get_listening_host(),
                                                                               self.get_listening_port(),
                                                                               ssl_context is None))

        # looked at the hypercorn and quart Python project to figure out
        # how to start the application separately, without going through
        # the Quart.app.run APIs
        self.app.debug = debug
        config = HyperConfig()
        config.debug = debug
        config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
        config.accesslog = self.logger.logger
        config.bind = ["{host}:{port}".format(**{'host':self.get_listening_host(),
                                                 'port':self.get_listening_port()})]
        config.certfile = self.get_cert_pem() if self.get_use_ssl() else None
        config.keyfile = self.get_key_pem() if self.get_use_ssl() else None

        config.errorlog = config.accesslog
        config.use_reloader = True
        scheme = "https" if config.ssl_enabled else "http"

        self.logger.info("Running on {}://{} (CTRL + C to quit)".format(scheme, config.bind[0]))
        loop = asyncio.get_event_loop()
        if loop is not None:
            loop.set_debug(debug or False)
            loop.run_until_complete(serve(self.app, config))
        else:
            asyncio.run(serve(self.app, config), debug=config.debug)


    def stop(self):
        if self.bg_thread is not None:
            self.bg_thread.terminate()
            self.bg_thread.join()

    def has_view(self, view):
        if view is not None:
            return view.name in set([i.name for i in self.views])
        return False

    def get_json(self, the_request):
        try:
            return the_request.json()
        except:
            return None

    def add_view(self, view):
        self.views.append(view)
        view.bind_application(self.app)

    def get_using_postgres(self):
        return getattr(self, USING_SQLALCHEMY, False)

    def get_using_mongo(self):
        return getattr(self, USING_MONGO, False)

    def get_listening_host(self):
        return getattr(self, HOST)

    def get_listening_port(self):
        return getattr(self, PORT)

    def get_validate_ssl(self):
        return getattr(self, VALIDATE_SSL)

    def get_cert_pem(self):
        return getattr(self, CERT_PEM)

    def get_key_pem(self):
        return getattr(self, KEY_PEM)

    def get_use_uwsgi(self):
        return getattr(self, USE_UWSGI)

    def get_host(self):
        return getattr(self, HOST)

    def get_port(self):
        return getattr(self, PORT)

    def get_use_ssl(self):
        return getattr(self, USE_SSL)

    def get_mongo_odms(self):
        return getattr(self, MONGO_ODMS, {})

    def get_sqlalchemy_orms(self):
        return getattr(self, SQLALCHEMY_ORMS, {})

    def get_heartbeat(self, *args, **kargs):
        raise Exception("Not implemented")
