import logging
import sys
import traceback

LOGGER = None

class Logger(object):
    FMT = '[%(asctime)s - %(name)s] %(message)s'
    DEFAULT_LEVEL = logging.INFO
    AUTHN_FMT = "{username} (from group:{group}) authenticated {source} at {location}: {success}"
    AUTHZ_FMT = "{principal} (using role {role}) performed {action} on {object} at {location}: {success}"
    ACTION_FMT = "{principal} performed {action} (details: {details}) at {location}"
    EXC_FMT = "exception {exc} (details: {details}) at {location}"

    def __init__(self, name, level=DEFAULT_LEVEL, fmt=FMT):
        self.name = name
        self.logger = logging.getLogger(name)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.setLevel(level)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter(fmt)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def authenticate_user(self, location, username, success=False, source='', group=None):
        msg = self.AUTHN_FMT.format(**{
            'username': username,
            'location': location,
            'success': success,
            'source': source,
            'group': group,})
        return self.info(msg)


    def authenticate_token(self, location, token_name, success=False, source='', group=None):
        msg = self.AUTHN_FMT.format(**{
            'username':token_name,
            'location':location,
            'success':success,
            'source':source,
            'group':group,
        })
        return self.info(msg)

    def authorize_user(self, location, principal, action, object_, success=False, role=None):
        msg = self.AUTHZ_FMT.format(**{
            'principal':principal,
            'action':action,
            'success':success,
            'object':object_,
            'location':location,
            'role':role,
        })
        return self.info(msg)

    def action(self, location, principal, action, details=None):
        msg = self.ACTION_FMT.format(**{
            'principal':principal,
            'action':action,
            'details':details,
            'location':location,
        })
        return self.info(msg)

    def exception(self, location, details):
        msg = self.EXC_FMT.format(**{
            'location':location,
            'details':details,
            'exc':traceback.format_exc()})
        return self.error(msg)

