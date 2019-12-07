SPLUNK_SERVICE_BLOCK = 'splunk-services'
SPLUNK_SERVICE_NAME = 'name'
SPLUNK_SERVICE_HOST = 'host'
SPLUNK_SERVICE_PORT = 'port'
SPLUNK_SERVICE_USERNAME = 'username'
SPLUNK_SERVICE_PASSWORD = 'password'
SPLUNK_QUERY_RESPONSE = 'response'
SPLUNK_QUERY_RESULTS = 'query_results'
SPLUNK_QUERY_SERVICE = 'service'
SPLUNK_QUERY_TAG = 'tag'
SPLUNK_QUERY_DATA = 'data'
SPLUNK_QUERY_METADATA = 'metadata'
SPLUNK_MONGO_SERVICE = 'splunk_mongo_service'
SPLUNK_EXECUTOR_SERVICE = 'splunk_executor_service'
SPLUNK_REST_SERVICE = 'splunk_rest_service'


ENABLE_REST = 'enable'

USE_JWT = False

SPLUNK_QUERY_DATABASE = 'splunk_query_database'
SPLUNK_AUTH_DATABASE = 'splunk_auth_database'
SC_AUTH_DATABASE = 'sc-auth-database'
SC_QUERY_DATABASE = 'sc-query-database'

SC_USERS_COLLECTION = 'sc-users-collection'
SC_ADMINS_COLLECTION = 'sc-users-collection'
SC_QUERYS_COLLECTION = 'sc-querys-collection'

VALIDATE_SSL = 'validate_ssl'
SPLUNK_REST_BLOCK = 'splunk-rest-service'
CERT_PEM = 'cert_pem'
KEY_PEM = 'key_pem'
USERS_COLLECTION = 'users_collection'
ADMINS_COLLECTION = 'admins_collection'

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
AUTHENTICATE_ALL_REQUESTS = 'authenticate_all_requests'
USE_WSGI = 'use_wsgi'


SPLUNK_REST_USER_DEFAULTS = {
    USERNAME: UNKNOWN,
    NAME: UNKNOWN,
    EMAIL: UNKNOWN,
}

SPLUNK_REST_SERVICE_DEFAULTS = {
    HOST: '',
    PORT: 9443,
    USE_SSL: False,
    CERT_PEM: None,
    KEY_PEM: None,
    USE_JWT: False,
    USERS_COLLECTION: None,
    ADMINS_COLLECTION: None,
    USER_TOKENS: list(),
    ADMIN_TOKENS: list(),
    TOKENS: dict(),
    VALIDATE_SSL: False,
    AUTHENTICATE_ALL_REQUESTS: True,
}

SPLUNK_SERVICE_CONFIGS = [
    SPLUNK_SERVICE_NAME,
    SPLUNK_SERVICE_HOST,
    SPLUNK_SERVICE_PORT,
    SPLUNK_SERVICE_USERNAME,
    SPLUNK_SERVICE_PASSWORD,
    SPLUNK_MONGO_SERVICE,
    SPLUNK_EXECUTOR_SERVICE,
    SPLUNK_REST_SERVICE,
    SPLUNK_QUERY_DATABASE,
    SPLUNK_AUTH_DATABASE,
]

SPLUNK_QUERY_BLOCK = 'splunk-query'
SPLUNK_QUERY_NAME = 'name'
SPLUNK_QUERY_SENSITIVE = 'sensitive'
SPLUNK_QUERY_QUERY = 'query'
SPLUNK_QUERY_INSTANCES = 'instances'
SPLUNK_QUERY_TAGS = 'tags'
SPLUNK_QUERY_PARAMETER_NAMES = 'parameter_names'

LAMBDAS = 'lambdas'

SPLUNK_QUERY_CONFIGS = [
    SPLUNK_QUERY_SENSITIVE,
    SPLUNK_QUERY_QUERY,
    SPLUNK_QUERY_INSTANCES,
    SPLUNK_QUERY_PARAMETER_NAMES,
    LAMBDAS,
]
SPLUNK_JOB_KEYWORDS = "job_keywords"
SPLUNK_QUERYS = 'splunk_querys'
BLOCKING = 'blocking'
EARLIEST_TIME = "earliest_time"
LATEST_TIME = "latest_time"
NOW = "now"
OUTPUT_MODE = "output_mode"
SEARCH_MODE = "search_mode"
NORMAL = "normal"

CONTACT = "contact"
CONTACTS = "contacts"
INVESTIGATORS = "investigators"
DESCRIPTION = "description"
START_DATE = "start_date"
END_DATE = "end_date"
SERVICES = "services"
USER_LIST = "user_list"
GIR_CASE = "gir_case"
EVERY_N_MINUTES = 'every_n_minutes'
DEFAULT_NHOURS_VALUE = 24 * 60 #
DEFAULT_NMINUTES_VALUE = 60
END_MONITORING = 'end_monitoring'
INITIATOR = 'initiator'


SUCCESS = 'success'
STATUS = 'status'
PENDING = 'pending'
RUNNING = 'running'
FAILED = 'failed'
COMPLETE = 'complete'
INIT = 'init'

HAS_RESULTS = 'has_results'
RESULTS = 'results'
LAST_CHECK = 'last_check'
ID = '_id'
SPLUNK_QUERY_RUNNING = 'splunk_query_running'

PURGE_AFTER_MINUTES_VALUE = 60*12 # 12 hours
JOB_ID = 'job_id'
STORED_RESULT_ID = 'stored_result_id'

FILENAME = 'filename'
BUFFERED_CONTENT = 'buffered_content'
EARLIEST = 'earliest'
LATEST = 'latest'
SPLUNK_QUERY = 'splunk_query'
SPLUNK_THREAD = 'splunk_thread'
SERVICE_THREAD = 'service-thread'

USE_SSL = 'use_ssl'
CERT_PEM = 'cert_pem'
KEY_PEM = 'key_pem'
USE_UWSGI = 'use_uwsgi'
PURGE_AFTER_HOURS = 'purge_after_hours'
DATA_KEY = 'data_key'
RESULTS_ENC = 'results_encrypted'
RESULT_DATA = 'result_data'
RESULTS_SHA256 = 'results_hash'

JSON = 'json'
CSV = 'csv'
XML = 'xml'
ALLOWED_SPLUNK_QUERY_RESULTS_FORMAT_VALUES = [JSON, CSV, XML]
SPLUNK_QUERY_RESULTS_FORMAT = 'results_format'
SPLUNK_QUERY_RESULTS_FORMAT_VALUE = JSON

DATA = 'data'
DATA_HASH = 'data_hash'
CIPHER = 'cipher'


SPLUNK_QUERY_NAMES = 'query_names'
TIME_FMT = '%m/%d/%Y:%H:%M:%S'

ADMIN_BLOCK = 'admin'
ADMIN_TOKENS = 'tokens'
ADMIN_USERS = 'users'
ADMIN_GROUPS = 'groups'

ADMIN_USERS_CONFIGS = [
    ADMIN_TOKENS,
    ADMIN_USERS,
    ADMIN_GROUPS
]

ACCESS_CONTROL_BLOCK = 'access-control'

MANAGED_BY = 'managed_by'
USERS = 'users'
TOKENS = 'tokens'
GROUPS = 'groups'

ACCESS_CONTROL_CONFIGS = [
    MANAGED_BY,
    USERS,
    TOKENS,
    GROUPS,
]

ALLOWED_TOKENS_BLOCK = 'allowed-tokens'
TOKEN_NAME = 'token_name'
TOKEN_VALUE = 'token_value'
TOKEN_DESCRIPTION = 'token_description'
TOKEN_USERNAME = 'token_username'
TOKEN_ACCOUNT_TYPE = 'token_account_type'
TOKEN_EMAIL = 'token_email'

ALLOWED_TOKENS = 'allowed_tokens'
TOKEN_CONFIGS = [
    TOKEN_NAME,
    TOKEN_VALUE,
    TOKEN_DESCRIPTION,
    TOKEN_USERNAME,
    TOKEN_ACCOUNT_TYPE,
    TOKEN_EMAIL
]

MONGO_SERVICE_BLOCK = 'mongo-services'
MONGO_HOST = 'mongo_host'
MONGO_PORT = 'mongo_port'
MONGO_DB = 'mongo_db'
MONGO_USERNAME = 'mongo_username'
MONGO_PASSWORD = 'mongo_password'
MONGO_NAME = 'mongo_name'

ACCESS_CONTROL_COLLECTION = 'access_control_collection'
ACCESS_CONTROL_DBNAME = 'access_control_database'

ACCESS_CONTROL = 'access_control'
ACCESS_CONTROL_MANAGED_BY = 'access_control_managed_by'
ACCESS_CONTROL_USERS = 'access_control_users'
ACCESS_CONTROL_GROUPS = 'access_control_groups'
ACCESS_CONTROL_TOKENS = 'access_control_tokens'

ADMINS = 'admins'
ADMIN_COLLECTION = 'admin_collection'
ADMIN_USERS = 'admin_users'
ADMIN_GROUPS = 'admin_groups'
ADMIN_TOKENS = 'admin_tokens'

ALLOWED_TOKENS_COLLECTION = 'allowed_tokens_collection'
JOBS_COLLECTION = 'jobs_collection'
QUERY_RESULTS_COLLECTION = 'jobs_query_results'
QUERY_RESULTS_COLLECTION_VALUE = 'query_results'

USE_MONGO_ACL = 'use_mongo_acl'
JOBS_COLLECTION_VALUE = 'jobs'
MONGO_ENCRYPT_DATA = 'encrypt_data'
MONGO_DATA_KEY = 'data_key'


# LDAP SEARCH
RAW_QUERY = 'raw_query'
SEARCH_BASE = 'search_base'
ATTRIBUTES = 'attributes'
SEARCH_FILTER = 'search_filter'
CREDENTIALS = 'auth'

# AUTHENTICATE
USERNAME = 'username'
PASSWORD = 'password'

SPLUNK_QUERY_JOB = 'job'

MONGO_DOCKER_NET = 'mongo_docker_net'
MONGO_DOCKER_SUBNET = 'mongo_docker_subnet'
MONGO_DOCKER_GATEWAY = 'mongo_docker_gateway'
MONGO_DOCKER_PORT = 'mongo_docker_port'
MONGO_DOCKER_DETACH = 'mongo_docker_detach'
MONGO_DOCKER_USERNAME = 'mongo_docker_username'
MONGO_DOCKER_PASSWORD = 'mongo_docker_password'
MONGO_DOCKER_NAME = 'mongo_docker_name'
MONGO_DOCKER_ENVIRONMENT = 'mongo_docker_environment'
MONGO_DOCKER_PORTS = 'mongo_docker_ports'
MONGO_DOCKER_IMAGE = 'mongo_docker_image'
MONGO_DOCKER_IP = 'mongo_docker_ip'


MONGO_CONFIGS = [
    MONGO_DATA_KEY,
    MONGO_ENCRYPT_DATA,
    MONGO_NAME,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB,
    MONGO_PASSWORD,
    MONGO_USERNAME,
    USE_MONGO_ACL,
    ACCESS_CONTROL_COLLECTION,
    ACCESS_CONTROL_MANAGED_BY,
    ACCESS_CONTROL_USERS,
    ACCESS_CONTROL_GROUPS,
    ACCESS_CONTROL_TOKENS,
    ADMIN_COLLECTION,
    ADMIN_USERS,
    ADMIN_GROUPS,
    ADMIN_TOKENS,
    ALLOWED_TOKENS_COLLECTION,
    JOBS_COLLECTION,
    USE_SSL,
    MONGO_DOCKER_NET,
    MONGO_DOCKER_SUBNET,
    MONGO_DOCKER_GATEWAY,
    MONGO_DOCKER_PORT,
    MONGO_DOCKER_DETACH,
    MONGO_DOCKER_USERNAME,
    MONGO_DOCKER_PASSWORD,
    MONGO_DOCKER_NAME,
    MONGO_DOCKER_ENVIRONMENT,
    MONGO_DOCKER_PORTS,
    MONGO_DOCKER_IMAGE,
    MONGO_DOCKER_IP,
]

MONGO_DOCKER_NET_VALUE = "mongo-jobinfo-net"
MONGO_DOCKER_SUBNET_VALUE = "1.20.1.0/24"
MONGO_DOCKER_GATEWAY_VALUE = "1.20.1.254"
MONGO_DOCKER_PORT_VALUE = 29017
MONGO_DOCKER_DETACH_VALUE = True
MONGO_DOCKER_USERNAME_VALUE = 'mongo_test_user'
MONGO_DOCKER_PASSWORD_VALUE = 'itsasekritssssh1234'
MONGO_DOCKER_NAME_VALUE = 'splunk-mongo-service'
MONGO_INITDB_ROOT_USERNAME = 'MONGO_INITDB_ROOT_USERNAME'
MONGO_INITDB_ROOT_PASSWORD = 'MONGO_INITDB_ROOT_PASSWORD'
MONGO_DOCKER_ENVIRONMENT_VALUE = {
    MONGO_INITDB_ROOT_USERNAME: MONGO_DOCKER_USERNAME_VALUE,
    MONGO_INITDB_ROOT_PASSWORD: MONGO_DOCKER_PASSWORD_VALUE,
}
MONGO_TCP_PORT = "27017/tcp"
MONGO_DOCKER_PORTS_VALUE = {
    MONGO_TCP_PORT : [MONGO_DOCKER_PORT_VALUE],
}
MONGO_DOCKER_IMAGE_VALUE = 'mongo:latest'
MONGO_DOCKER_IP_VALUE = '1.20.1.3'


EXECUTOR_SERVICE_BLOCK = 'executor-services'
EXECUTOR_NUM_PROCS = 'executor_num_procs'
EXECUTOR_NAME = 'executor_name'
EXECUTOR_POLL_TIME = 'executor_poll_time'
EXECUTOR_POLL_TASK = 'executor_poll_task'
EXECUTOR_START_POLLING_WITH_SVC = 'executor_start_polling_with_service'
EXECUTOR_SERVICE_START = 'executor_service_start'
EXECUTOR_POLL_ARGS = 'executor_poll_args'
EXECUTOR_POLL_KARGS = 'executor_poll_kargs'
EXECUTOR_MAX_ITERATIONS = 'executor_max_iterations'

EXECUTOR_JOB_FUNC = "executor_job_func"
EXECUTOR_JOB_CALLBACK = "executor_job_callback"
EXECUTOR_JOB_ERROR_CALLBACK = "executor_job_error_callback"
EXECUTOR_JOB_ARGS = "executor_job_args"
EXECUTOR_JOB_KARGS = "executor_job_kargs"
ERROR = 'error'
CC_JOB_LIST = 'cc_job_list'

EXECUTOR_CONFIGS = [
    EXECUTOR_NAME,
    EXECUTOR_NUM_PROCS,
    EXECUTOR_MAX_ITERATIONS,
    EXECUTOR_POLL_TIME,
    EXECUTOR_START_POLLING_WITH_SVC,
    EXECUTOR_SERVICE_START,
]

FN_NAME = 'name'
FN_CODE = 'code'
FN_CALLABLE = 'callable'

SPLUNK_QUERY_TOML_BLOCK = """
[splunk-query.{name}]
    name = '{name}'
    sensitive = {sensitive}
    tags = {tags}
    query = '''{query_fmt}'''
    parameter_names = {parameter_names}
    {lambdas_block}
"""

SPLUNK_QUERY_TOML_LAMBDAS_BLOCK = """
[splunk-query.{name}.lambdas]
    {lambdas}
"""

RUN_ONCE = 'run_once'
MAX_RUNS = 'max_runs'
RUN_COUNT = 'run_count'