from tabulate import tabulate
from .consts import *
import toml
import os


class Config(object):

    CONFIG = {}

    @classmethod
    def check_raise(cls, block_name, key, value):
        if value is None:
            raise Exception("'%s':'%s' requires a value"%(block_name, key))

    @classmethod
    def parse_config(cls, config_file):
        if not os.path.exists(config_file):
            raise Exception("Unable to parse {}: does not exist".format(config_file))
        return cls.parse_string(open(config_file).read())

    @classmethod
    def parse_string(cls, config_string):
        try:
            toml_data = toml.loads(config_string)

            cls.parse_splunk_instances(toml_data)
            cls.parse_splunk_querys(toml_data)
            cls.parse_mongo_service(toml_data)
            cls.parse_executor_service(toml_data)

            if USE_MONGO_ACL not in cls.CONFIG[MONGO_SERVICE_BLOCK]:
                cls.CONFIG[USE_MONGO_ACL] = False

        except:
            raise

    @classmethod
    def parse_splunk_instances(cls, toml_data):
        blocks = toml_data.get(SPLUNK_SERVICE_BLOCK)
        blocks = {} if blocks is None else blocks
        if len(blocks) == 0:
            return

        svc = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        for name, block in blocks.items():
            c = {}
            for k in SPLUNK_SERVICE_CONFIGS:
                c[k] = block.get(k)
                if k == SPLUNK_SERVICE_NAME and \
                    (c[k] is None or len(c[k]) == 0):
                    c[k] = name
            svc[c[SPLUNK_SERVICE_NAME]] = c
        cls.CONFIG[SPLUNK_SERVICE_BLOCK] = svc

    @classmethod
    def parse_splunk_querys(cls, toml_data):
        blocks = toml_data.get(SPLUNK_QUERY_BLOCK)
        blocks = {} if blocks is None else blocks
        if len(blocks) == 0:
            return

        svc = cls.CONFIG.get(SPLUNK_QUERY_BLOCK, {})
        for name, block in blocks.items():
            c = {SPLUNK_QUERY_NAME:name}
            for k in SPLUNK_QUERY_CONFIGS:
                c[k] = block.get(k)
                if k == LAMBDAS:
                    c[k] = cls.parse_splunk_query_lambdas(block.get(k))
                if k == SPLUNK_QUERY_SENSITIVE and c[k] is None:
                    c[k] = False
                elif k == SPLUNK_QUERY_INSTANCES and c[k] is None:
                    c[k] = []
                elif k == SPLUNK_QUERY_INSTANCES and isinstance(c[k], str):
                    c[k] = [c[k]]
                elif k == SPLUNK_QUERY_NAME and \
                    (c[k] is None or len(c[k]) == 0):
                    c[k] = name


            svc[c[SPLUNK_QUERY_NAME]] = c
        cls.CONFIG[SPLUNK_QUERY_BLOCK] = svc

    @classmethod
    def parse_splunk_query_lambdas(cls, lambdas_dict):
        lambdas = []
        for k, code in lambdas_dict.items():
            lambda_info = {'name': k, 'code': code}
            lambdas.append(lambda_info)
        return lambdas

    @classmethod
    def get_service_config(cls, name):
        cfg = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        return cfg.get(name, {})

    @classmethod
    def set_services_username(cls, username):
        cfg = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        for name in cfg:
            cls.set_service_username(name, username)

    @classmethod
    def set_services_password(cls, password):
        cfg = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        for name in cfg:
            cls.set_service_password(name, password)

    @classmethod
    def set_service_username(cls, name, username):
        cfg = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        svc = cfg.get(name, None)
        if svc is None:
            return False
        svc[SPLUNK_SERVICE_USERNAME] = username
        return True

    @classmethod
    def set_service_password(cls, name, password):
        cfg = cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})
        svc = cfg.get(name, None)
        if svc is None:
            return False
        svc[SPLUNK_SERVICE_PASSWORD] = password
        return True

    @classmethod
    def get_service_configs(cls):
        return cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {})

    @classmethod
    def get_query_config(cls, name):
        cfg = cls.CONFIG.get(SPLUNK_QUERY_BLOCK, {})
        return cfg.get(name, {})

    @classmethod
    def get_query_configs(cls):
        return cls.CONFIG.get(SPLUNK_QUERY_BLOCK, {})

    @classmethod
    def get(cls):
        return cls.CONFIG

    @classmethod
    def set_value(cls, key, value):
        cls.CONFIG[key] = value

    @classmethod
    def get_value(cls, key):
        return cls.CONFIG.get(key, None)

    @classmethod
    def print_config(cls):
        headers = ['Key', 'Value']
        # url = "%s://%s:%s"%(Config.get_value(PROTO), Config.get_value(HOST), Config.get_value(PORT))
        items = []

        table = str(tabulate(items, headers=headers))
        print(table+'\n\n\n')

    @classmethod
    def print(cls):
        headers = ['Key', 'Value']
        items = []

        # items.append(['username', str(Config.get_value('username'))])
        # items.append(['password set?', Config.get_value('password') is not None])

        table = str(tabulate(items, headers=headers))
        print(table+'\n\n\n')

    @classmethod
    def parse_mongo_service(cls, toml_data):
        cls.CONFIG[MONGO_SERVICE_BLOCK] = {}
        block = toml_data.get(MONGO_SERVICE_BLOCK)
        block = {} if block is None else block
        if len(block) == 0:
            return

        mongo = {}
        for name, ms_block in block.items():
            mongo_service = {}
            for k in MONGO_CONFIGS:
                if k in ms_block:
                    mongo_service[k] = ms_block.get(k)

            if MONGO_NAME in mongo_service:
                name = mongo_service[MONGO_NAME]
            else:
                mongo_service[MONGO_NAME] = name
            mongo[name] = mongo_service


        cls.CONFIG[MONGO_SERVICE_BLOCK] = mongo

    @classmethod
    def get_mongo_service(cls, name):
        return cls.CONFIG.get(MONGO_SERVICE_BLOCK, {}).get(name, {})

    @classmethod
    def get_splunk_service(cls, name):
        return cls.CONFIG.get(SPLUNK_SERVICE_BLOCK, {}).get(name, {})

    @classmethod
    def parse_admin_users(cls, toml_data):
        block = toml_data.get(ADMIN_BLOCK)
        block = {} if block is None else block
        if len(block) == 0:
            return

        admin_users = {}
        for k in ADMIN_USERS_CONFIGS:
            cls.check_raise(ADMIN_BLOCK, k, block.get(k))
            admin_users[k] = block.get(k)
            if not isinstance(admin_users[k], list):
                raise Exception("'%s':'%s' requires a list" % (ADMIN_BLOCK, k))

        cls.CONFIG[ADMIN_BLOCK] = admin_users

    @classmethod
    def parse_access_control(cls, toml_data):
        block = toml_data.get(ACCESS_CONTROL_BLOCK)
        block = {} if block is None else block
        if len(block) == 0:
            return
        acl = {}
        for k in ACCESS_CONTROL_CONFIGS:
            cls.check_raise(ACCESS_CONTROL_BLOCK, k, block.get(k))
            acl[k] = block.get(k)
            if not isinstance(acl[k], list):
                raise ("'%s':'%s' requires a list" % (ACCESS_CONTROL_BLOCK, k))

        cls.CONFIG[ACCESS_CONTROL_BLOCK] = acl

    @classmethod
    def parse_allowed_tokens(cls, toml_data):
        block = toml_data.get(ALLOWED_TOKENS_BLOCK)
        block = {} if block is None else block
        if len(block) == 0:
            return

        tokens = {}
        for name, token_block in block.items():
            token = {}

            for k in TOKEN_CONFIGS:
                cls.check_raise(ALLOWED_TOKENS_BLOCK, k, token_block.get(k))
                token[k] = token_block.get(k, '')

            if TOKEN_NAME not in token:
                token[TOKEN_NAME] = name
            else:
                name = token[TOKEN_NAME]

            if TOKEN_VALUE not in token or \
                len(token[TOKEN_VALUE]) == 0:
                continue

            tokens[name] = token

        cls.CONFIG[ALLOWED_TOKENS] = tokens

    @classmethod
    def user_allowed(cls, username, groups=[], manager=''):
        acl = cls.CONFIG.get(ACCESS_CONTROL_BLOCK)
        agroups = acl.get(GROUPS,[])
        ausers = acl.get(USERS, [])
        amanagers = acl.get(MANAGED_BY, [])
        if username in ausers:
            return True
        elif manager in amanagers:
            return True
        return len(set(groups) & set(agroups)) > 0

    @classmethod
    def token_allowed(cls, token_name, token_value):
        token_infos = cls.CONFIG.get(ALLOWED_TOKENS, {}).values()
        for ti in token_infos:
            if ti[TOKEN_NAME] == token_name and ti[TOKEN_VALUE] == token_value:
                return True
        return False

    @classmethod
    def token_owner(cls, token_name, token_value):
        token_infos = cls.CONFIG.get(ALLOWED_TOKENS, {}).values()
        for ti in token_infos:
            if ti[TOKEN_NAME] == token_name and ti[TOKEN_VALUE] == token_value:
                return ti.get(TOKEN_USERNAME, None)
        return None

    @classmethod
    def username_allowed(cls, username):
        acl = cls.CONFIG.get(ACCESS_CONTROL_BLOCK, {})
        ausers = acl.get(USERS, [])
        if username in ausers:
            return True
        return False

    @classmethod
    def groups_allowed(cls, groups):
        acl = cls.CONFIG.get(ACCESS_CONTROL_BLOCK, {})
        agroups = acl.get(GROUPS,[])
        if len(groups) > 0:
            for g in groups:
                if g in agroups:
                    return g
        return None

    @classmethod
    def manager_allowed(cls, manager=None):
        acl = cls.CONFIG.get(ACCESS_CONTROL_BLOCK, {})
        amanagers = acl.get(MANAGED_BY, [])
        if manager in amanagers:
            return True
        return False

    @classmethod
    def parse_executor_service(cls, toml_data):
        cls.CONFIG[EXECUTOR_SERVICE_BLOCK] = {}
        block = toml_data.get(EXECUTOR_SERVICE_BLOCK)
        block = {} if block is None else block
        if len(block) == 0:
            return

        executor = {}
        for name, ms_block in block.items():
            executor_service = {}
            for k in EXECUTOR_CONFIGS:
                if k in ms_block:
                    executor_service[k] = ms_block.get(k)

            if EXECUTOR_NAME in executor_service:
                name = executor_service[EXECUTOR_NAME]
            else:
                executor_service[EXECUTOR_NAME] = name
            executor[name] = executor_service


        cls.CONFIG[EXECUTOR_SERVICE_BLOCK] = executor

    @classmethod
    def get_executor_service(cls, name):
        return cls.CONFIG.get(EXECUTOR_SERVICE_BLOCK, {}).get(name, {})
