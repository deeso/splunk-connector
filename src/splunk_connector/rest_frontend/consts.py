PATTERNS = 'patterns'
USER_TOKENS = 'user_tokens'
ADMIN_TOKENS = 'admin_tokens'
TOKEN_VALUE = 'token_value'
USERNAME = 'username'
NAME = 'name'
EMAIL = 'email'
TOKENS = 'tokens'
UNKNOWN = 'unknown'
HOST = 'host'
PORT = 'port'
USE_SSL = 'use_ssl'
USE_WSGI = 'use_wsgi'
VALIDATE_SSL = 'validate_ssl'
USE_UWSGI = 'use_uwsgi'
CERT_PEM = 'cert_pem'
KEY_PEM = 'key_pem'

USER = 'user'
PASSWORD = 'password'
DB = 'db'
DATABASE = 'database'
COLLECTION = 'collection'
TABLE = 'table'

USING_SQLALCHEMY = 'using_postgres'
SQLALCHEMY_HOST = 'sqlalchemy_host'
SQLALCHEMY_PORT = 'sqlalchemy_port'
SQLALCHEMY_USER = 'sqlalchemy_user'
SQLALCHEMY_PASS = 'sqlalchemy_password'
SQLALCHEMY_USE_SSL = 'sqlalchemy_use_ssl'
SQLALCHEMY_DB = 'sqlalchemy_db'
SQLALCHEMY_ORMS = 'sqlalchemy_orms'
TLS_INSECURE = 'tlsInsecure'
SSL_KEYFILE = 'ssl_keyfile'
SSL_CERTFILE = 'ssl_certfile'
DEFAULT_ENGINE_SETTINGS = 'default_engine_settings'

ODMS = 'odms'
ORMS = 'orms'

ORM_CLASS = 'odm_class'
ODM_CLASS = 'odm_class'
CLASS = 'class'
CONTROLLER = 'controller'
RESOURCE = 'resource'

# ORM_CLASS = 'orm_class'
# HOST = 'host'
# PORT = 'port'
# USE_SSL = 'use_ssl'
# USERNAME = 'username'
# PASSWORD = 'password'
CERT = 'cert'
KEY = 'key'
CONNECTION = 'connection'
dialect = 'dialect'

USING_MONGO = 'using_mongo'
MONGO_HOST = 'mongo_host'
MONGO_PORT = 'mongo_port'
MONGO_USER = 'mongo_user'
MONGO_PASS = 'mongo_password'
MONGO_USE_SSL = 'mongo_use_ssl'
MONGO_DB = 'mongo_db'
MONGO_ODMS = 'mongo_odms'
MONGO_CONNECTION = 'mongo_connection'
MONGO_DATABASE = 'mongo_database'
MONGO_COLLECTION = 'mongo_collection'

VIEWS = 'views'

META = 'Meta'
TABLE__ = '__table__'
FULLNAME = 'fullname'
DESCRIPTION = 'description'
ENGINE = 'engine'

REST_SERVICE_BLOCK = 'rest-service'

REST_SERVICE_CONFIGS = {
    USE_SSL: False,
    USE_UWSGI: False,
    HOST: '127.0.0.1',
    PORT: 8000,
    VALIDATE_SSL: False,
    CERT_PEM: None,
    KEY_PEM: None,

    VIEWS: list(),

    # Mongo related
    USING_MONGO: False,
    MONGO_HOST: None,
    MONGO_PORT: None,
    MONGO_USER: None,
    MONGO_PASS: None,
    MONGO_USE_SSL: False,
    MONGO_DB: None,
    MONGO_ODMS: list(),
    ODMS: {},


    # Postgres related
    USING_SQLALCHEMY: False,
    SQLALCHEMY_HOST: None,
    SQLALCHEMY_PORT: None,
    SQLALCHEMY_USER: None,
    SQLALCHEMY_PASS: None,
    SQLALCHEMY_USE_SSL: False,
    SQLALCHEMY_DB: None,
    ORMS: {},
    PATTERNS: None,
}

MONGODB_SETTINGS = 'MONGODB_SETTINGS'
MONGODB_HOST = 'MONGODB_HOST'
MONGODB_PORT = 'MONGODB_PORT'
MONGODB_USER = 'MONGODB_USERNAME'
MONGODB_PASS = 'MONGODB_PASSWORD'
MONGODB_DB = 'MONGODB_DB'

MAP_MONGO_TO_APP = {
    MONGO_HOST: HOST,
    MONGO_PORT: PORT,
    MONGO_USER: USERNAME,
    MONGO_PASS: PASSWORD,
    # MONGO_DB: DB,
}

MAP_MONGO_TO_SETTINGS = {
    MONGO_HOST: MONGODB_HOST,
    MONGO_PORT: MONGODB_PORT,
    MONGO_USER: MONGODB_USER,
    MONGO_PASS: MONGODB_PASS,
    MONGO_DB: MONGODB_DB,
}

SQLALCHEMYDB_SETTINGS = 'SQLALCHEMYDB_SETTINGS'
MAP_SQLALCHEMY_TO_APP = {
    SQLALCHEMY_HOST: HOST,
    SQLALCHEMY_PORT: PORT,
    SQLALCHEMY_USER: USERNAME,
    SQLALCHEMY_PASS: PASSWORD,
    SQLALCHEMY_DB: DATABASE,
}

DIALECT_DRIVER = 'dialect_driver'
SQLALCHEMY_DIALECT = 'postgresql+psycopg2'
MONGODB_DIALECT = 'mongodb'
SQLALCHEMY_DATABASE_URI ='SQLALCHEMY_DATABASE_URI'

REQUIRED_DB_URI_FMT_KEYS = [DIALECT_DRIVER, USERNAME, PASSWORD, HOST, PORT]
DB_URI_FMT = '{dialect_driver}://{username}:{password}@{host}:{port}/{database}'
DB_URI_NO_DB_FMT = '{dialect_driver}://{username}:{password}@{host}:{port}'



ODM_DATABASE = 'odm_database'
ODM_COLLECTION = 'odm_collection'
ODM_CONNECTION = 'odm_connection'

ORM_DATABASE = 'orm_database'
ORM_COLLECTION = 'orm_collection'
ORM_CONNECTION = 'orm_connection'
ORM_TABLE = 'orm_table'
