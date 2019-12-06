from .config import Config
from .consts import *
from .standard_logger import Logger


class SplunkQueryCallable(object):
    REQUIRED_VALUES = [
        FN_NAME,
        FN_CODE,
    ]

    def __init__(self, **kargs):

        for k in self.REQUIRED_VALUES:
            if k not in kargs:
                raise Exception("Missing %s from keyword arguments"%k)

        for k, v in kargs.items():
            setattr(self, k, v)

        setattr(self, FN_CALLABLE, eval(self.get_code()))

        if not callable(self.get_callable()):
            raise Exception("Provided code provided for %s is not a function or callable" % self.get_name())

    def __call__(self, *args, **kwargs):
        fn = self.get_callable()
        return fn(*args, **kwargs)

    def get_code(self) -> str:
        return getattr(self, FN_CODE)

    def get_name(self) -> str:
        return getattr(self, FN_NAME)

    def get_callable(self) -> callable:
        return getattr(self, FN_CALLABLE)

    def get_toml_kargs(self):
        return {'name': self.get_name(), 'code': self.get_code()}

    def to_toml(self):
        return """{name} = '''{code}'''""".format(**self.get_toml_kargs())

class SplunkQuery(object):

    DEFAULT_VALUES = {
        SPLUNK_QUERY_NAME: lambda : None,
        SPLUNK_QUERY_QUERY: lambda : None,
        SPLUNK_QUERY_SENSITIVE: lambda: None,
        SPLUNK_QUERY_INSTANCES: lambda : list(),
        SPLUNK_QUERY_TAGS: lambda : list(),
        SPLUNK_QUERY_PARAMETER_NAMES: lambda : list(),
        LAMBDAS: lambda : dict(),
        OUTPUT_MODE: lambda : None,
    }

    def validate(self):
        if not hasattr(self, SPLUNK_QUERY_QUERY) or getattr(self, SPLUNK_QUERY_QUERY, None) is None:
            raise Exception("Query needs a query")
        return True

    def __init__(self, **kargs):
        self.init_keys = set()
        self.unknown_keys = set()

        for k, v in kargs.items():
            if k not in self.DEFAULT_VALUES:
                self.unknown_keys.add(k)
            self.init_keys.add(k)
            setattr(self, k, v)

        for k, v in self.DEFAULT_VALUES.items():
            if not hasattr(self, k):
                self.init_keys.add(k)
                setattr(self, k, v())

        if LAMBDAS in kargs:
            splunk_callables = {}
            for spc_kargs in kargs.get(LAMBDAS, list()):
                sqc = SplunkQueryCallable(**spc_kargs)
                splunk_callables[sqc.get_name()] = sqc
            setattr(self, LAMBDAS, splunk_callables)

        self.validate()
        self.logger = Logger('splunk-query-'+self.get_splunk_query_name())

    def build(self, **parameters):
        # self.logger.action('build', self.get_splunk_query_name(),
        #                    'building query with paramters %s'%str(list(parameters.keys())))
        my_params = self.get_parameter_names()

        vparameters = [i for i in parameters.keys() if i in my_params]
        missing_parameters = [i for i in my_params if not i in parameters]
        if len(missing_parameters) > 0:
            raise Exception('Required parameters missing: {}'.format(", ".join(missing_parameters)))
        query_parameters = self.build_parameter_dict(values=parameters)
        return self.get_splunk_query_format().format(**query_parameters)

    def get_parameter_lambdas(self):
        return getattr(self, LAMBDAS, dict())

    def get_parameter_callable(self, k) -> callable:
        lambdas = self.get_parameter_lambdas()
        if k in lambdas:
            return lambdas[k].get_callable()
        return None

    def get_tags(self):
        return getattr(self, SPLUNK_QUERY_TAGS, list())

    def get_splunk_query_name(self):
        return getattr(self, SPLUNK_QUERY_NAME, '')

    def get_splunk_query_sensitive(self):
        return getattr(self, SPLUNK_QUERY_SENSITIVE, False)

    def get_splunk_query_format(self):
        return getattr(self, SPLUNK_QUERY_QUERY)

    def get_parameter_names(self):
        return getattr(self, SPLUNK_QUERY_PARAMETER_NAMES, list())

    def build_parameter_dict(self, values={}):
        parameter_dict = {}
        for parameter_name in self.get_parameter_names():
            if parameter_name in values:
                v = values[parameter_name]
                lambda_fn = self.get_parameter_callable(parameter_name)
                nv = v
                if lambda_fn is not None:
                    nv = lambda_fn(v)
                parameter_dict[parameter_name] = nv
        return parameter_dict

    def add_splunk_query_callable(self, spc: SplunkQueryCallable):
        self.get_parameter_lambdas()[spc.get_name()] = spc

    def get_lambdas_block(self):
        if len(self.get_parameter_lambdas()) == 0:
            return ''
        toml_kargs = {
            'name': self.get_splunk_query_name(),
            'lambdas': '\n'.join([i.serialize() for i in self.get_parameter_lambdas().values()])
        }
        return SPLUNK_QUERY_TOML_LAMBDAS_BLOCK.format(**toml_kargs)

    def get_toml_kargs(self):
        return {'name': self.get_splunk_query_name(),
                'sensitive': str(self.get_splunk_query_sensitive()).lower(),
                'tags': self.get_tags(),
                'query_fmt': self.get_splunk_query_format(),
                'parameter_names': self.get_parameter_names(),
                'lambdas_block': self.get_lambdas_block()
                }

    def to_toml(self):
        return SPLUNK_QUERY_TOML_BLOCK.format(**self.get_toml_kargs())

    def get_instances(self):
        return getattr(self, SPLUNK_QUERY_INSTANCES)

    def set_name(self, name):
        setattr(self, SPLUNK_QUERY_NAME, name)


class NamedSplunkQuery(SplunkQuery):

    def validate(self):
        if not hasattr(self, SPLUNK_QUERY_NAME) or getattr(self, SPLUNK_QUERY_NAME, None) is None:
            raise Exception("Query needs a name")
        if not hasattr(self, SPLUNK_QUERY_QUERY) or getattr(self, SPLUNK_QUERY_QUERY, None) is None:
            raise Exception("Query needs a query")
        return True

    def __init__(self, **kargs):
        super(NamedSplunkQuery, self).__init__(**kargs)


class SplunkQuerys(object):
    def __init__(self):
        self.querys = {}

    def get_formatted_query(self, name, **parameters):
        query = self.get_query(name)
        if query is None:
            raise Exception("Invalid query name provided")
        return query.format(**parameters)

    def get_query(self, name):
        return self.querys.get(name)

    def add_query(self, query_obj=None, query_kargs={}):
        if query_obj is None:
            query_obj = SplunkQuery(**query_kargs)

        query_obj.validate()
        self.querys[query_obj.name] = query_obj
        return query_obj

    def remove_query(self, name):
        if name in self.querys:
            del self.querys[name]
            return True
        return False

    def find_instance_querys(self, instance_name):
        querys = []

        for q in self.querys.items():
            if instance_name in getattr(q, SPLUNK_QUERY_INSTANCES, []):
                querys.append(q)
        return querys

    @classmethod
    def init_from_config(cls):
        query_dict = Config.get_value(SPLUNK_QUERY_BLOCK, {})
        sqs = SplunkQuerys()

        for sqk in query_dict.items():
            sqs.add_query(sqk)
        return sqs
