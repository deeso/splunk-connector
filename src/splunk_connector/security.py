from .consts import *
from .mongo_service import MongoService

class Auth(object):

    DEFAULT_VALUES = {
        ACCESS_CONTROL_COLLECTION: ACCESS_CONTROL,
        MANAGED_BY: MANAGED_BY,
        ACCESS_CONTROL_USERS: ACCESS_CONTROL_USERS,
        ACCESS_CONTROL_GROUPS: ACCESS_CONTROL_GROUPS,
        ACCESS_CONTROL_TOKENS: ACCESS_CONTROL_TOKENS,
        ADMIN_COLLECTION: ADMINS,
        ADMIN_USERS: ADMIN_USERS,
        ADMIN_GROUPS: ADMIN_GROUPS,
        ADMIN_TOKENS: ADMIN_TOKENS,
        ALLOWED_TOKENS_COLLECTION: ALLOWED_TOKENS,

    }

    def __init__(self, **kargs):
        for k, v in self.DEFAULT_VALUES.items():
            setattr(self, k, kargs.get(k, v))

    def username_allowed(self, username):
        conn, db = self.get_conn_database()
        doc = db[self.get_access_control_collection()].find_one({})
        try:
            if username in doc[self.get_access_control_users()]:
                return True
            return False
        except:
            return False
        finally:
            self.close_connection(conn)

    def groups_allowed(self, groups):
        conn, db = self.get_conn_database()
        doc = db[self.get_access_control_collection()].find_one({})
        r = False
        if len(groups) > 0:
            for g in groups:
                if g in doc[self.get_access_control_groups()]:
                    r = True
                    break
        self.close_connection(conn)
        return r

    def manager_allowed(self, manager=None):
        conn, db = self.get_conn_database()
        doc = db[self.get_access_control_collection()].find_one({})
        r = False
        if manager is not None and manager in doc[self.get_access_control_managed_by()]:
            r = True
        self.close_connection(conn)
        return r

    def user_allowed(self, username, groups=None, manager=None):
        groups = [] if groups is None else groups
        if self.username_allowed(username):
            return True
        if self.groups_allowed(groups):
            return True
        if self.manager_allowed(manager):
            return True
        return False

    def find_token(self, token_name, token_value):
        conn, db = self.get_conn_database()
        doc = db[self.get_allowed_tokens_collection()].find_one({TOKEN_NAME: token_name, TOKEN_VALUE: token_value})
        self.close_connection(conn)
        return doc

    def token_allowed(self, token_name, token_value):
        doc = self.find_token(token_name, token_value)
        if doc is None:
            return False
        return True

    def token_owner(self, token_name, token_value):
        doc = self.find_token(token_name, token_value)
        if doc is None:
            return None
        return doc.get(TOKEN_USERNAME, None)

    def is_admin(self, username, groups=None):
        groups = [] if groups is None else groups
        conn, db = self.get_conn_database()
        doc = db[self.get_admin_collection()].find_one({})
        r = False
        if username in doc[self.get_admin_users()]:
            r = True
        elif len(groups) > 0:
            for g in groups:
                if g in doc[self.get_admin_groups()]:
                    r = True
                    break
        self.close_connection(conn)
        return r

    def is_admin_token(self, token_name):
        conn, db = self.get_conn_database()
        doc = db[self.get_admin_collection()].find_one({})
        r = False
        if token_name in doc[self.get_admin_tokens()]:
            r = True
        self.close_connection(conn)
        return r

    def get_conn_database(self):
        ms = MongoService.from_config()
        return ms.get_conn_database(db_name=self.get_acl_dbname())

    def close_connection(self, conn):
        MongoService.close_connection(conn)

    def get_acl_dbname(self):
        return getattr(self, ACCESS_CONTROL_DBNAME)

    def get_access_control_collection(self):
        return getattr(self, ACCESS_CONTROL_COLLECTION)

    def get_access_control_users(self):
        return getattr(self, ACCESS_CONTROL_USERS)

    def get_access_control_groups(self):
        return getattr(self, ACCESS_CONTROL_GROUPS)

    def get_access_control_managed_by(self):
        return getattr(self, ACCESS_CONTROL_MANAGED_BY)

    def get_allowed_tokens(self):
        return getattr(self, ALLOWED_TOKENS)

    def get_allowed_tokens_collection(self):
        return getattr(self, ALLOWED_TOKENS_COLLECTION)

    def get_admin_collection(self):
        return getattr(self, ADMIN_COLLECTION)

    def get_admin_tokens(self):
        return getattr(self, ADMIN_TOKENS)

    def get_admin_users(self):
        return getattr(self, ADMIN_USERS)

    def get_admin_groups(self):
        return getattr(self, ADMIN_GROUPS)
