from pymongo import MongoClient
from umongo import Instance
from umongo import Document, EmbeddedDocument
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker, Session
from .standard_logger import Logger
from .consts import *


def patch_umongo_meta(odm_cls, **kargs):
    meta = getattr(odm_cls, META)
    if meta is None:
        return False
    connection = kargs.get(CONNECTION, None)
    database = kargs.get(DATABASE, None)
    collection = kargs.get(COLLECTION, None)

    instance = Instance(connection[database])
    if connection is not None and \
        isinstance(connection, MongoClient) and \
        database is not None and \
        collection is not None:
        col = connection[database][collection]
        setattr(odm_cls, META, col)

    if connection is not None and \
        isinstance(connection, MongoClient) and \
        database is not None:
        instance = instance.register(odm_cls)
        setattr(odm_cls, META, instance)
    return True


def patch_sqlalchemy_meta(sqla_cls, **kargs):
    table = getattr(sqla_cls, TABLE__)
    if table is None:
        return False
    tablename = kargs.get(TABLE, None)
    if table is not None:
        setattr(table, NAME, tablename)
        setattr(table, FULLNAME, tablename)
        setattr(table, DESCRIPTION, tablename)
    return True


class BaseSqla(declarative_base()):
    ENGINE = None
    NAME = 'BaseSqla'
    LOGGER = Logger(NAME)

    @classmethod
    def set_internal_state(cls, **kargs):
        patch_sqlalchemy_meta(cls, **kargs)
        cls.ENGINE = kargs.get(ENGINE, None)

    @classmethod
    def get_meta(cls):
        return cls.__table__.Meta

    @classmethod
    def get_session(cls) -> Session:
        if getattr(cls, ENGINE, None) is not None:
            return sessionmaker(cls.ENGINE)
        return None

    def perform_commit(self):
        session = None
        committed = False
        try:
            session = self.get_session()
            if session is None:
                raise Exception("Failed to create a valid session")
            session.add(self)
            session.commit()
            session.close()
            committed = True
        except:
            self.LOGGER.error("Failed to commit {}".format(self))
        finally:
            if session is not None:
                session.close()
        return committed


class BaseDocument(Document):
    ENGINE = None
    NAME = 'BaseDocument'
    LOGGER = Logger(NAME)

    @classmethod
    def set_internal_state(cls, **kargs):
        patch_umongo_meta(cls, **kargs)
        cls.ENGINE = kargs.get(ENGINE, None)

    @classmethod
    def get_instance(cls):
        return cls.Meta.instance

    @classmethod
    def get_collection(cls):
        return cls.Meta.collection

    @classmethod
    def get_meta(cls):
        return cls.Meta

    def perform_commit(self):
        committed = False
        try:
            self.commit()
            committed = True
        except:
            self.LOGGER.error("Failed to commit {}".format(self))
        return committed

    class Meta:
        collection = None
        instance = None


class BaseEmbeddedDocument(EmbeddedDocument):
    ENGINE = None
    NAME = 'BaseEmbeddedDocument'
    LOGGER = Logger(NAME)

    @classmethod
    def set_internal_state(cls, **kargs):
        patch_umongo_meta(cls, **kargs)
        cls.ENGINE = kargs.get(ENGINE, None)

    @classmethod
    def get_instance(cls):
        return cls.Meta.instance

    @classmethod
    def get_collection(cls):
        return cls.Meta.collection

    @classmethod
    def get_meta(cls):
        return cls.Meta

    def perform_commit(self):
        committed = False
        try:
            self.commit()
            committed = True
        except:
            self.LOGGER.error("Failed to commit {}".format(self))
        return committed

    class Meta:
        collection = None
        instance = None


