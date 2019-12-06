from .consts import *

class SplunkResult(object):
    DEFAULT_KWARGS = {
        SPLUNK_QUERY_NAME: lambda: None,
        SPLUNK_QUERY_SENSITIVE: lambda: None,
        SPLUNK_QUERY_QUERY: lambda: None,
        SPLUNK_QUERY_TAGS: lambda: None,
        SPLUNK_QUERY_SERVICE: lambda: None,
        SPLUNK_QUERY_RESPONSE: lambda: None,
        # SPLUNK_QUERY_RUNNING: lambda: False,
        DATA: lambda: None,
        FILENAME: lambda: None,
        EARLIEST: lambda: None,
        LATEST: lambda: None,
    }

    SERIAL_IGNORE = [
        SPLUNK_QUERY_RESPONSE,
        SPLUNK_QUERY_SERVICE
    ]

    def __init__(self, **kwargs):
        if SPLUNK_QUERY_RESULTS in kwargs and not DATA in kwargs:
            kwargs[DATA] = kwargs[SPLUNK_QUERY_RESULTS]

        for k, dfn in self.DEFAULT_KWARGS.items():
            v = dfn() if k not in kwargs else kwargs[k]
            if k in self.DEFAULT_KWARGS:
                setattr(self, k, v)

    def serialize(self):
        return {k: getattr(self, k) for k in self.DEFAULT_KWARGS if k not in self.SERIAL_IGNORE}


    def get_name(self):
        return getattr(self, SPLUNK_QUERY_NAME, None)

    def set_name(self, value=None):
        setattr(self, SPLUNK_QUERY_NAME, value)

    def get_sensitive(self):
        return getattr(self, SPLUNK_QUERY_SENSITIVE, None)

    def set_sensitive(self, value=None):
        setattr(self, SPLUNK_QUERY_SENSITIVE, value)

    def get_query(self):
        return getattr(self, SPLUNK_QUERY_QUERY, None)

    def set_query(self, value=None):
        setattr(self, SPLUNK_QUERY_QUERY, value)

    def get_tags(self):
        return getattr(self, SPLUNK_QUERY_TAGS, None)

    def set_tags(self, value=None):
        setattr(self, SPLUNK_QUERY_TAGS, value)

    def get_svc(self):
        return getattr(self, SPLUNK_QUERY_SERVICE, None)

    def set_svc(self, value=None):
        setattr(self, SPLUNK_QUERY_SERVICE, value)

    def get_response(self):
        return getattr(self, SPLUNK_QUERY_RESPONSE, None)

    def set_response(self, value=None):
        setattr(self, SPLUNK_QUERY_RESPONSE, value)

    def get_data(self):
        return getattr(self, DATA, None)

    def set_data(self, value=None):
        setattr(self, DATA, value)

    def get_filename(self):
        return getattr(self, FILENAME, None)

    def set_filename(self, value=None):
        setattr(self, FILENAME, value)

    def get_buffered_content(self):
        return getattr(self, BUFFERED_CONTENT, None)

    def set_buffered_content(self, value=None):
        setattr(self, BUFFERED_CONTENT, value)

    def get_earliest(self):
        return getattr(self, EARLIEST, None)

    def set_earliest(self, value=None):
        setattr(self, EARLIEST, value)

    def get_latest(self):
        return getattr(self, LATEST, None)

    def set_latest(self, value=None):
        setattr(self, LATEST, value)

    def get_splunk_query_running(self):
        getattr(self, SPLUNK_QUERY_RUNNING, False)

    def set_splunk_query_running(self, v=False):
        setattr(self, SPLUNK_QUERY_RUNNING, v)


class SplunkResults(object):

    def __init__(self, name, results=[]):
        self.results = {}
        for result in results:
            if isinstance(result, SplunkResult):
                self.add_result(result)
            elif isinstance(result, dict):
                self.add_result(SplunkResult(**result))

    @classmethod
    def from_json_results(cls, name, json_results):
        results = [SplunkResult(**result) for result in json_results]
        return cls(name, results=results)

    def add_result(self, result: SplunkResult):
        earliest = result.get_earliest()
        self.results[earliest] = result

    def get_results(self):
        return list(self.results.values())

    def serialize(self):
        return [i.serialize() for i in self.results.values()]