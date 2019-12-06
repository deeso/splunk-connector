import traceback
from .consts import *
from .query import SplunkQuerys, SplunkQuery, NamedSplunkQuery
from .config import Config
from .mongo_service import MongoService
from .stored_results import StoredSplunkResult
from .splunk_service import SplunkService

class SplunkServices(object):

    def __init__(self, config_file=None):
        self.services = {}
        self.splunk_querys = SplunkQuerys()
        self.parse_config(config_file=config_file)

    def get_service(self, name):
        return self.services.get(name, None)

    def get_service_names(self):
        return list(self.services.keys())

    def supports_service(self, svc):
        return svc in self.services

    @classmethod
    def from_config(cls, config_file=None):
        return cls(config_file=config_file)

    def parse_config(self, config_file=None):
        if config_file is not None:
            Config.parse_config(config_file)

        cfgs = Config.get_service_configs()
        for cfg in cfgs.values():
            svc = SplunkService(**cfg)
            self.services[getattr(svc, SPLUNK_SERVICE_NAME)] = svc

        cfgs = Config.get_query_configs()
        for cfg in cfgs.values():
            qo = self.splunk_querys.add_query(query_kargs=cfg)
            service_names = qo.instances
            if len(service_names) == 0:
                service_names = list(self.services.keys())

            for instance in service_names:
                if instance in self.services:
                    self.services[instance].add_named_splunk_query(qo)
