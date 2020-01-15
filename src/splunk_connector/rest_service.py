from .config import Config
from .consts import *
from .standard_logger import Logger
from quart import Quart
from .mongo_service import MongoService



# from https://www.anserinae.net/using-python-decorators-for-authentication.html
async def check_admin_token(fn):
    def deco(self, *args, **kwargs):
        rv = {}
        token = args[0]
        if self.auth_token(token) and \
                self.is_token_admin(token):
            rv['code'] = 200
            rv['payload'] = fn(*args, **kwargs)
        else:
            rv['code'] = 401
        return rv
    return deco

async def check_token(fn):
    def deco(self, *args, **kwargs):
        rv = {}
        token = args[0]
        if self.is_token_admin(token):
            rv['code'] = 200
            rv['payload'] = fn(*args, **kwargs)
        else:
            rv['code'] = 401
        return rv
    return deco

class RestService(object):
    DEFAULT_VALUES = SPLUNK_REST_SERVICE_DEFAULTS
    NAME = SPLUNK_REST_BLOCK

    def __init__(self, **kwargs):
        self.init_keys = set()

        for k, v in kwargs.items():
            setattr(self, k, v)
            self.init_keys.add(k)

        for k, v in self.DEFAULT_VALUES.items():
            if k not in kwargs:
                setattr(self, k, v)
            else:
                setattr(self, k, kwargs.get(k))

        self.logger = Logger(self.NAME)

        self.app = Quart(self.NAME)
        self.pages = []

        self.splunk_service = None

    def set_splunk_service(self, splunk_service):
        self.splunk_service = splunk_service

    @classmethod
    def from_config(cls):
        cdict = Config.get_value(SPLUNK_REST_BLOCK)
        if cdict is None:
            cdict = {}

        kwargs = {}
        for k, v in cls.DEFAULT_VALUES.items():
            kwargs[k] = cdict.get(k, v)
        return cls(**kwargs)

    def run(self, debug=False):
        self.start()
        ssl_context = None
        if self.get_key_pem() is not None and \
                self.get_cert_pem() is not None:
            ssl_context = (self.get_cert_pem(), self.get_key_pem())

        if self.get_use_uwsgi():
            return self.app.run(port=self.get_listening_port(),
                                host=self.get_listening_host(),
                                debug=debug,
                                ssl_context=ssl_context)
        return self.app.run(port=self.get_listening_port(),
                            host=self.get_listening_host(),
                            debug=debug,
                            ssl_context=ssl_context)

    def get_query_names(self):
        conn, db = MongoService.from_config().get_connection()

        MongoService.close_connection(conn)

    def has_page(self, page):
        if page is not None:
            return page.name in set([i.name for i in self.pages])
        return False

    def get_json(self, the_request):
        try:
            return the_request.json()
        except:
            return None

    def add_page(self, page):
        self.pages.append(page)
        page.update_app(self.app)

    def get_listening_host(self):
        return getattr(self, HOST)

    def get_listening_port(self):
        return getattr(self, PORT)

    def get_validate_ssl(self):
        return getattr(self, VALIDATE_SSL)

    def get_use_mongo_acl(self):
        return getattr(self, USE_MONGO_ACL)

    def get_authenticate_all_requests(self):
        return getattr(self, AUTHENTICATE_ALL_REQUESTS)

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

    def get_use_jwt(self):
        return getattr(self, USE_JWT)

    def get_users_collection(self):
        return getattr(self, USERS_COLLECTION)

    def get_admins_collection(self):
        return getattr(self, ADMINS_COLLECTION)

    def get_user_tokens(self):
        return getattr(self, USER_TOKENS)

    def get_admin_tokens(self):
        return getattr(self, ADMIN_TOKENS)

    def get_tokens(self):
        return getattr(self, TOKENS)

    #TODO Rest Functinos to implement
    # from https://www.anserinae.net/using-python-decorators-for-authentication.html


    async def auth_user(self, **karg):
        pass

    async def is_user_admin(self, **karg):
        pass

    async def auth_token(self, **karg):
        pass

    async def is_token_admin(self, **karg):
        pass

    # TODO query managemnt
    @check_token
    async def handle_get_queries(self):
        # TODO get a list of all valid querys
        pass

    @check_token
    async def handle_get_query(self):
        # TODO get serialized version of query
        pass

    @check_token
    async def handle_put_query(self):
        # TODO update query in mongo
        pass

    @check_token
    async def handle_post_query(self):
        # TODO add a new query in mongo
        pass

    @check_token
    async def handle_delete_query(self):
        # TODO delete a query in mongo
        pass

    @check_token
    async def handle_get_query_test(self):
        # TODO populate query with test endpoint
        pass

    @check_token
    async def handle_get_query_execute(self):
        # TODO execute query with test endpoint
        pass


    #TODO Admin Management

    @check_admin_token
    async def handle_post_admin(self):
        #TODO add a new admin user
        pass

    @check_admin_token
    async def handle_get_admin(self):
        #TODO get admin user
        pass

    @check_admin_token
    async def handle_put_admin(self):
        #TODO update admin user
        pass

    @check_admin_token
    async def handle_delete_admin(self):
        #TODO get admin user
        pass

    @check_admin_token
    async def handle_put_admin_token(self):
        #TODO update admin user, generate a token
        pass

    @check_admin_token
    async def handle_delete_admin_token(self):
        #TODO update admin user, delete a token
        pass

    # TODO user management
    async def handle_get_user_token(self):
        # TODO get user user tokens
        pass

    @check_admin_token
    async def handle_post_user(self):
        # TODO add a new user user
        pass

    @check_admin_token
    async def handle_get_user(self):
        # TODO get user user
        pass

    @check_admin_token
    async def handle_put_user(self):
        # TODO update user user
        pass

    @check_admin_token
    async def handle_delete_user(self):
        # TODO get user user
        pass

    @check_token
    async def handle_put_user_token(self):
        # TODO update user user, generate a token
        pass

    @check_token
    async def handle_delete_user_token(self):
        # TODO update user user, delete a token
        pass

    # TODO export/import items
    @check_admin_token
    async def handle_export_user(self):
        # TODO get JSON export of users
        pass

    @check_admin_token
    async def handle_export_admin(self):
        # TODO get JSON export of admins
        pass

    @check_token
    async def handle_export_queries(self):
        # TODO get JSON export of queries
        pass

    @check_admin_token
    async def handle_import_user(self):
        # TODO get JSON export of users
        pass

    @check_admin_token
    async def handle_import_admin(self):
        # TODO get JSON import of admins
        pass

    @check_admin_token
    async def handle_import_queries(self):
        # TODO get JSON import of queries
        pass
