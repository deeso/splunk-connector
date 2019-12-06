import time
import traceback
from .consts import *
import splunklib.client as splunklib_client
from splunklib.binding import ResponseReader as SplunklibResponseReader
from splunklib.client import Job as SplunkJob
from .query import SplunkQuerys, SplunkQuery, NamedSplunkQuery
from .config import Config
from .mongo_service import MongoService
from .executor_service import ExecutorService, execute_splunk_job
from datetime import datetime, timedelta
from .stored_results import StoredSplunkResult
from .results import SplunkResult
from .standard_logger import Logger
from .simple import Query





class SplunkService(object):

    DEFAULT_VALUES = {
        SPLUNK_SERVICE_HOST: '127.0.0.1',
        SPLUNK_SERVICE_PORT: 8000,
        SPLUNK_SERVICE_NAME: None,
        SPLUNK_SERVICE_USERNAME: None,
        SPLUNK_SERVICE_PASSWORD: None,
        SPLUNK_QUERYS: None,
        SPLUNK_MONGO_SERVICE: None,
        MONGO_ENCRYPT_DATA: False,
        SPLUNK_EXECUTOR_SERVICE: None,
    }


    EXPORTS_DEFAULTS = {
        LATEST_TIME: NOW,
        OUTPUT_MODE: JSON,
        SEARCH_MODE: NORMAL,
    }

    def __init__(self, **kargs):

        self.mongo_service = None
        self.executor_service = None

        self.init_keys = set()
        self.unknown_keys = set()
        for k, v in kargs.items():
            if k not in self.DEFAULT_VALUES:
                self.unknown_keys.add(k)
            self.init_keys.add(k)
            setattr(self, k, v)

        for k, v in self.DEFAULT_VALUES.items():
            if not hasattr(self, k):
                setattr(self, k, v)
            self.init_keys.add(k)

        if self.splunk_querys is None:
            self.splunk_querys = {}

        self.logger = Logger('splunk-service-'+self.get_splunk_service_name())
        self.mongo_service = None
        if SPLUNK_MONGO_SERVICE in kargs and \
           isinstance(kargs.get(SPLUNK_MONGO_SERVICE), str):
            self.mongo_service = MongoService.from_config(name=self.get_mongo_service_name())

        self.using_mongo_docker = False
        self.executor_service = None
        self.default_poll_task = self.poll_mongo_for_jobid
        self.default_executor_func = execute_splunk_job
        self.default_callback_func = None
        self.default_error_callback_func = None
        if SPLUNK_EXECUTOR_SERVICE in kargs and \
           isinstance(kargs.get(SPLUNK_EXECUTOR_SERVICE), str):
            self.executor_service = ExecutorService.from_config(name=self.get_executor_service_name())
            self.executor_service.set_poll_task(self.default_poll_task)
            self.executor_service.set_start_polling_with_service(True)
        elif SPLUNK_EXECUTOR_SERVICE in kargs and \
                isinstance(kargs.get(SPLUNK_EXECUTOR_SERVICE), ExecutorService):
            self.executor_service = kargs.get(SPLUNK_EXECUTOR_SERVICE)
        else:
            raise Exception("No executor service provided")

    def is_using_docker(self):
        return self.using_mongo_docker

    def start(self, with_docker=False, reset_docker=False, with_polling=True):
        self.executor_service.start(with_polling=with_polling)
        ms = self.get_mongo_service()
        # if with_docker:
        #     ms.configure_docker()
        #
        # if with_docker and reset_docker:
        #     self.using_mongo_docker = True
        #     ms.refresh_docker()
        # elif with_docker and not ms.test_connection():
        #     self.using_mongo_docker  = True
        #     ms.refresh_docker()
        return ms.test_connection()

    def stop(self, kill_docker=False, join_executor=False):
        ms = self.get_mongo_service()
        if kill_docker and \
                self.using_mongo_docker and \
                ms.test_connection():
            ms.stop_docker()
        self.executor_service.stop(join=join_executor)
        return

    def get_splunk_service_name(self):
        return getattr(self, SPLUNK_SERVICE_NAME)

    def update_executor_poll_task(self, func: callable):
        self.default_poll_task = func
        self.executor_service.set_poll_task(self.default_poll_task)

    def update_executor_poll_time(self, poll_time: int):
        self.executor_service.set_poll_time(poll_time)

    def update_executor_function(self, func: callable):
        self.default_executor_func = func

    def update_executor_callback_function(self, func: callable):
        self.default_callback_func = func

    def update_executor_error_callback_func(self, func: callable):
        self.default_error_callback_func = func

    def get_mongo_service(self):
        return self.mongo_service

    def get_mongo_service_name(self):
        return getattr(self, SPLUNK_MONGO_SERVICE, None)

    def set_mongo_service_name(self, name):
        setattr(self, SPLUNK_MONGO_SERVICE, name)
        self.mongo_service = MongoService.from_config(name=name)

    def get_executor_service(self):
        return self.executor_service

    def get_executor_service_name(self):
        return getattr(self, SPLUNK_EXECUTOR_SERVICE, None)

    def set_executor_service_name(self, name):
        setattr(self, SPLUNK_EXECUTOR_SERVICE, name)
        self.mongo_service = ExecutorService.from_config(name=name)

    def get_formatted_time_now(self):
        return datetime.utcnow().strftime('%m/%d/%Y:%H:%M:%S')

    @classmethod
    def from_config(cls, name=None):
        splunk_config = None
        if name is None:
            service_dict = Config.get_service_configs()
            if not isinstance(service_dict, dict) or len(service_dict) == 0:
                raise Exception("No splunk configurations were found")
            splunk_config = list(service_dict.values())[0]
        else:
            splunk_config = Config.get_splunk_service(name)

        if not isinstance(splunk_config, dict) or len(splunk_config) == 0:
            raise Exception("No splunk configurations were found")

        kargs = {k: v for k, v in splunk_config.items() if k in cls.DEFAULT_VALUES}
        ss = cls(**kargs)
        query_cnt = 0
        anon_name = 'query-{}'
        queries = cls.querys_from_config(ss.get_splunk_service_name())
        for qo in queries:
            if qo.get_splunk_query_name() is None:
                qo.set_name(anon_name.format(str(query_cnt)))

            if isinstance(qo, NamedSplunkQuery):
                ss.add_named_splunk_query(qo)
            else:
                ss.add_splunk_query(qo.get_splunk_query_name(), qo)
        return ss

    @classmethod
    def querys_from_config(cls, name=None):
        queries = []
        cfgs = Config.get_query_configs()
        for cfg in cfgs.values():
            qo = SplunkQuery(**cfg)
            service_names = qo.get_instances()

            if name is None:
                queries.append(qo)
            elif len(service_names) == 0:
                queries.append(qo)
            elif qo.get_splunk_query_name() is None:
                queries.append(qo)
            elif qo.get_splunk_query_name() == name:
                queries.append(qo)
        return queries

    def validate(self):
        if getattr(self, SPLUNK_SERVICE_PASSWORD, None) is None or \
                getattr(self, SPLUNK_SERVICE_USERNAME, None) is None:
            raise Exception("Username and password must be set for splunk service")

    def get_splunk_service(self):
        return splunklib_client.connect(
            host=self.get_splunk_host(),
            port=self.get_splunk_port(),
            username=self.get_splunk_username(),
            password=self.get_splunk_password())

    def set_splunk_host(self, host):
        setattr(self, SPLUNK_SERVICE_HOST, host)

    def get_splunk_host(self):
        return getattr(self, SPLUNK_SERVICE_HOST)

    def set_splunk_port(self, port):
        setattr(self, SPLUNK_SERVICE_PORT, port)

    def get_splunk_port(self):
        return getattr(self, SPLUNK_SERVICE_PORT)

    def set_splunk_username(self, username):
        setattr(self, SPLUNK_SERVICE_USERNAME, username)

    def get_splunk_username(self):
        return getattr(self, SPLUNK_SERVICE_USERNAME)

    def set_splunk_password(self, password):
        setattr(self, SPLUNK_SERVICE_PASSWORD, password)

    def get_splunk_password(self):
        return getattr(self, SPLUNK_SERVICE_PASSWORD)

    def perform_stored_query_by_tags(self, tags, query_data={}, job_keywords={}, export=False):
        named_querys = {}
        for tag in sorted(tags):
            querys = [i for i in self.get_querys().values() if tag in i.get(SPLUNK_QUERY_TAGS, [])]
            for nq in querys:
                if nq.name in named_querys:
                    continue
                query = nq.build(**query_data)
                svc, rsp = None, None
                try:
                    svc, rsp = self.start_query(query, job_keywords=job_keywords, export=export)
                except:
                    pass
                named_querys[nq.name] = {'query': query, 'tags':tags, 'service':svc, 'response':rsp}
        return named_querys

    def perform_stored_query_by_tag(self, tag, query_data={}, job_keywords={}, export=False):
        return self.perform_stored_query_by_tags([tag,],
                                                 query_data=query_data,
                                                 job_keywords=job_keywords,
                                                 export=export)

    def get_querys(self) -> dict:
        return getattr(self, SPLUNK_QUERYS, {})

    def get_named_query(self, name) -> NamedSplunkQuery:
        querys = self.get_querys()
        return querys.get(name, None)

    def perform_stored_query(self, name, query_data={}, job_keywords={}, export=False, blocking=False, filename=None) -> SplunkResult:
        results = {FILENAME: filename}
        named_query = self.get_named_query(name)
        if named_query is None:
            raise Exception("Stored query is missing parameters")

        self.logger.action('perform_stored_query', None, 'building query and results dictionary')
        query = named_query.build(**query_data)
        results[SPLUNK_QUERY_SENSITIVE] = getattr(named_query, SPLUNK_QUERY_SENSITIVE, False)
        results[SPLUNK_QUERY_NAME] = name
        results[SPLUNK_QUERY_TAGS] = named_query.get_tags()
        results[SPLUNK_QUERY_QUERY] = query
        self.logger.action('perform_stored_query', None, 'performing query')
        sq = self.start_query(query, job_keywords=job_keywords, export=export, blocking=blocking)
        results.update(sq)
        if EARLIEST in query_data:
            results[EARLIEST] = query_data[EARLIEST]
        else:
            results[EARLIEST] = datetime.utcnow().strftime(TIME_FMT)

        if LATEST in query_data:
            results[LATEST] = query_data[LATEST]
        else:
            results[LATEST] = datetime.utcnow().strftime(TIME_FMT)

        self.logger.action('perform_stored_query', None, 'returning results')
        splunk_results = SplunkResult(**results)
        return splunk_results

    def start_query(self, query, job_keywords={}, export=False, blocking=False):
        results = {}

        self.logger.action('start_query', None, 'query started')
        svc, job = Query.execute(self.get_splunk_host(), self.get_splunk_port(),
                                 self.get_splunk_username(), self.get_splunk_password(),
                                 query, job_keywords=job_keywords, export=export)

        results[SPLUNK_QUERY_SERVICE] = svc
        rr = None

        if not isinstance(job, SplunkJob):
            rr = job
            job = None
        else:
            jk = {OUTPUT_MODE: job_keywords.get(OUTPUT_MODE, JSON)}
            while not job.is_done():
                job.touch()
                if job.is_done():
                    break
                time.sleep(1.0)
                pass
            rr = job.results(**jk)


        results[SPLUNK_QUERY_JOB] = job
        results[SPLUNK_QUERY_RESPONSE] = rr

        if blocking and isinstance(rr,  SplunklibResponseReader):
            self.logger.action('start_query', None, 'blocking on exported query')
            rr = results[SPLUNK_QUERY_RESPONSE]
            results[SPLUNK_QUERY_RESULTS] = Query.read_all(rr)
            self.logger.action('start_query', None, 'blocking completed, results recieved')
        elif blocking:
            self.logger.action('start_query', None, 'blocking on non-exported query')
            jk = {OUTPUT_MODE: job_keywords.get(OUTPUT_MODE, JSON)}
            rr = job.results(**jk)
            while not job.is_done():
                job.touch()
                pass
            results[SPLUNK_QUERY_RESULTS] = Query.read_all(rr)
            self.logger.action('start_query', None, 'blocking completed on non-exported query, results recieved')
        else:
            while not job.is_ready():
                job.touch()
                pass
            rr = job.results(**jk)
            results[SPLUNK_QUERY_RESPONSE] = rr

        self.logger.action('start_query', None, 'returning results dictionary')
        return results

    def read_all(self, rsp):
        data = b''
        while not rsp.closed:
            d = rsp.read()
            if len(d) == 0:
                break
            data = data + d
        return data

    def add_splunk_query(self, name, splunk_query: SplunkQuery):
        self.splunk_querys[name] = splunk_query

    def add_named_splunk_query(self, named_splunk_query: NamedSplunkQuery):
        self.splunk_querys[named_splunk_query.name] = named_splunk_query

    def get_splunk_query(self, name: str = None) -> SplunkQuery:
        if name is None and len(self.splunk_querys) > 0:
            return list(self.splunk_querys)[0]
        elif name in self.splunk_querys:
            return self.splunk_querys[name]
        raise Exception("No splunk querys available or invalid name")

    def poll_mongo_for_jobid(self, *args, **kargs):
        results = []
        self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, "In poll_mongo_for_jobid")
        ms = self.get_mongo_service()
        try:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, "Marking jobs complete from poll_mongo_for_jobid")
            ms.mark_jobs_complete()
        except:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, traceback.format_exc())

        try:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, "Starting pending jobs from poll_mongo_for_jobid")
            ms.start_pending_jobs()
        except:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, traceback.format_exc())

        job_ids = []
        try:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, "Query for jobs ready to run from poll_mongo_for_jobid")
            job_ids = ms.jobs_ready_for_query()
        except:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, traceback.format_exc())

        results = []
        try:
            self.logger.action("poll_mongo_for_jobid", SERVICE_THREAD, "Executing jobs ready to run from poll_mongo_for_jobid")
            for job_id in job_ids:
                func = self.default_executor_func
                callback = self.default_callback_func
                error_callback = self.default_error_callback_func
                jargs = [ ]
                # TODO fix this hack, should use default initial args
                if func == execute_splunk_job:
                    jargs = [self.get_splunk_service_name()]
                jkargs = {JOB_ID: job_id}
                r = ExecutorService.build_executor_results(func, jargs, jkargs,
                                                           callback=callback,
                                                           error_callback=error_callback)
                results.append(r)
        except:
            self.logger.action("poll_mongo_for_jobid", None, traceback.format_exc())
        return results

    def is_alive(self):
        return self.get_executor_service().is_running()

    def is_running(self):
        return self.is_alive()
