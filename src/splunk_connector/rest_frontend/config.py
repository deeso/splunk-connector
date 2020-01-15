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
            cls.parse_rest_service(toml_data)
        except:
            raise

    @classmethod
    def parse_rest_service(cls, toml_data):
        sr_block = toml_data.get(REST_SERVICE_BLOCK)
        sr_block = {} if sr_block  is None else sr_block
        if len(sr_block ) == 0:
            return

        rest_service = {}
        for k, v in REST_SERVICE_CONFIGS.items():
            rest_service[k] = sr_block.get(k, v)

        cls.CONFIG[REST_SERVICE_BLOCK] = rest_service

    @classmethod
    def get(cls):
        return cls.CONFIG

    @classmethod
    def set_value(cls, key, value):
        cls.CONFIG[key] = value

    @classmethod
    def get_value(cls, key):
        return cls.CONFIG.get(key, None)
