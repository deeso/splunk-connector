import uuid
from datetime import datetime, timedelta
from .consts import *
import random
import string
from .stored_results import StoredSplunkResult
# from .mongo_service import MongoService

RANDOM_KEY = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(440))



class ScheduledJobInfo(object):

    REQUIRED_META_DATA_KEYS = {
        JOB_ID,
        DESCRIPTION,
        START_DATE,
        END_DATE,
        EVERY_N_MINUTES,
        STATUS,
        RESULTS,
        SPLUNK_QUERY_NAMES,
        SPLUNK_QUERY_DATA,
        SPLUNK_QUERY_METADATA,
        SPLUNK_JOB_KEYWORDS,
        SPLUNK_QUERY_RUNNING,
        SPLUNK_QUERY_RESULTS_FORMAT,
        LAST_CHECK,
        # EARLIEST,
        # LATEST,
        CC_JOB_LIST,
        RUN_ONCE,
        MAX_RUNS,
        RUN_COUNT,
    }

    DEFAULT_JOB_KEYWORDS = {
        OUTPUT_MODE: JSON,
    }

    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4()).lower()

    @classmethod
    def from_keywords(cls, job_id=None, description='', status=INIT,
                      start_date=None, end_date=None,
                      every_n_minutes=DEFAULT_NMINUTES_VALUE, cc_job_list=None,
                      latest=None, earliest=None, run_once=False,
                      run_count=0, max_runs=-1,**kargs):
        job_id = cls.generate_id() if job_id is None else job_id
        start_date = start_date if start_date is not None else (datetime.utcnow()).strftime(TIME_FMT)
        end_date = end_date if end_date is not None else (datetime.utcnow() +
                                                          timedelta(hours=DEFAULT_NHOURS_VALUE)).strftime(TIME_FMT)

        skargs = {}
        skargs[JOB_ID] = job_id
        skargs[DESCRIPTION] = description
        skargs[START_DATE] = start_date
        skargs[END_DATE] = end_date
        skargs[EVERY_N_MINUTES] = every_n_minutes
        skargs[STATUS] = status
        skargs[RESULTS] = kargs.get(RESULTS, {})
        skargs[SPLUNK_QUERY_NAMES] = kargs.get(SPLUNK_QUERY_NAMES, [])
        skargs[SPLUNK_QUERY_DATA] = kargs.get(SPLUNK_QUERY_DATA, {})
        skargs[SPLUNK_QUERY_METADATA] = kargs.get(SPLUNK_QUERY_METADATA, {})
        skargs[SPLUNK_JOB_KEYWORDS] = kargs.get(SPLUNK_JOB_KEYWORDS, {})
        skargs[LAST_CHECK] = kargs.get(LAST_CHECK, None)
        skargs[SPLUNK_QUERY_RESULTS_FORMAT] = kargs.get(SPLUNK_QUERY_RESULTS_FORMAT, SPLUNK_QUERY_RESULTS_FORMAT_VALUE)
        skargs[CC_JOB_LIST] = cc_job_list
        skargs[EARLIEST] = earliest
        skargs[LATEST] = latest
        skargs[MAX_RUNS] = max_runs
        skargs[RUN_ONCE] = run_once or max_runs == 1
        skargs[RUN_COUNT] = 0
        return ScheduledJobInfo(**skargs)

    @classmethod
    def default_results_dict(cls):
        return StoredSplunkResult.default_results_dict()

    @classmethod
    def set_data_key(cls, key=None):
        StoredSplunkResult.set_data_key(key)

    @classmethod
    def encrypt(cls, salt, data):
        return StoredSplunkResult.encrypt(salt, data)

    @classmethod
    def get_data_hash(cls, data):
        return StoredSplunkResult.get_data_hash(data)

    @classmethod
    def decrypt(cls, salt, cipher, data_hash=None):
        return StoredSplunkResult.decrypt(salt, cipher, data_hash=data_hash)

    def __init__(self, salt=None, decrypt_results=True, **kargs):
        self.salt = salt

        if kargs.get(CC_JOB_LIST, None) is None:
            kargs[CC_JOB_LIST] = []
        if kargs.get(LAST_CHECK, None) is None:
            kargs[LAST_CHECK] = (datetime.utcnow()+timedelta(weeks=-1)).strftime(TIME_FMT)
        if SPLUNK_QUERY_RUNNING not in kargs:
            kargs[SPLUNK_QUERY_RUNNING] = False
        if STATUS not in kargs:
            kargs[STATUS] = INIT

        if SPLUNK_JOB_KEYWORDS not in kargs:
            kargs[SPLUNK_JOB_KEYWORDS] = self.DEFAULT_JOB_KEYWORDS.copy()

        if ID not in kargs and JOB_ID not in kargs:
            kargs[JOB_ID] = str(uuid.uuid4()).lower()
        elif kargs.get(ID, None) is None and kargs.get(JOB_ID, None) is None:
            kargs[JOB_ID] = str(uuid.uuid4()).lower()

        if kargs.get(ID, None) is None:
            kargs[ID] = kargs[JOB_ID]
        elif kargs.get(JOB_ID, None) is None:
            kargs[JOB_ID] = kargs[ID]

        setattr(self, SPLUNK_QUERY_NAMES, kargs.get(SPLUNK_QUERY_NAMES, []))
        if RESULTS not in kargs:
            kargs[RESULTS] = {}

        for k in self.REQUIRED_META_DATA_KEYS:
            if k not in kargs:
                raise Exception("Missing required key: %s" % k)
            setattr(self, k, kargs.get(k))
        # load or create base results

        if len(kargs.get(RESULTS, {})) == 0:
            results = self.build_default_results(salt=self.salt)
            self.add_results(results)
        else:
            self.add_results_json(kargs.get(RESULTS, {}), salt=self.salt, decrypt=True)

        if self.get_end_date() is None:
            self.set_end_date(days=10)

        last_check = kargs.get(LAST_CHECK, None)
        self.set_last_check(last_check)

    def start_job(self):
        if self.get_status() == INIT:
            self.set_status(PENDING)
            return True
        return False



    def set_end_date(self, dt=None, days=0):
        dt = dt if dt is not None else (datetime.utcnow()+timedelta(days=days)).strftime(TIME_FMT)
        return setattr(self, END_DATE, dt)

    def build_default_results(self, salt=None):
        results = {}
        for svc in self.get_query_names():
            results[svc] = StoredSplunkResult.default_results(salt=self.salt)
        return results

    def get_data(self):
        return getattr(self, SPLUNK_QUERY_DATA, None)

    def get_query_names(self):
        return getattr(self, SPLUNK_QUERY_NAMES, [])
    
    def get_id(self):
        return getattr(self, JOB_ID)

    def get_results(self):
        return getattr(self, RESULTS, {})

    def get_period(self):
        return getattr(self, EVERY_N_MINUTES)

    def get_status(self):
        return getattr(self, STATUS)

    def set_status(self, status=PENDING):
        setattr(self, STATUS, status)

    def set_pending(self):
        return self.set_status(PENDING)

    def set_running(self):
        return self.set_status(RUNNING)

    def set_complete(self):
        return self.set_status(COMPLETE)

    def set_failed(self):
        return self.set_status(FAILED)

    def get_query_running(self):
        return getattr(self, SPLUNK_QUERY_RUNNING)

    def set_query_running(self, v):
        return setattr(self, SPLUNK_QUERY_RUNNING, v)

    def get_end_date(self):
        return getattr(self, END_DATE)

    def get_start_date(self):
        return getattr(self, START_DATE)

    def get_poll_interval(self):
        return getattr(self, EVERY_N_MINUTES)

    def get_last_check(self):
        return getattr(self, LAST_CHECK)

    def get_query_data(self):
        return getattr(self, SPLUNK_QUERY_DATA)

    def get_cc_list(self):
        return getattr(self, CC_JOB_LIST)

    def set_cc_list(self, cc_job_list):
        setattr(self, CC_JOB_LIST, cc_job_list)

    def set_job_keywords(self, job_keywords=None):
        job_keywords = self.DEFAULT_JOB_KEYWORDS.copy() if job_keywords is None else job_keywords
        job_keywords[OUTPUT_MODE] = self.get_results_format()
        setattr(self, SPLUNK_JOB_KEYWORDS, job_keywords)

    def get_job_keywords(self):
        job_kw = getattr(self, SPLUNK_JOB_KEYWORDS, None)
        if job_kw is None or len(job_kw) == 0:
            self.set_job_keywords()
            return getattr(self, SPLUNK_JOB_KEYWORDS)
        job_kw[OUTPUT_MODE] = self.get_results_format()
        return job_kw

    def set_last_check(self, dt=None):
        if isinstance(dt, str):
            try:
                datetime.strptime(dt,  TIME_FMT)
            except:
                dt = (datetime.utcnow()).strftime(TIME_FMT)
        elif dt is None:
            dt = (datetime.utcnow()).strftime(TIME_FMT)
        return setattr(self, LAST_CHECK, dt)

    def decrypt_results(self, results=None, reset_invalid=True):
        my_results = self.get_results()
        results = my_results.copy() if results is None else results
        for svc in results.keys():
            entry = my_results[svc]
            verification = entry.verify(self.get_id())
            if not verification and reset_invalid:
                entry.reset()
            elif not verification:
                raise Exception("Results for %s failed validation check" % svc)
            entry.decrypt_cipher(in_place=True)
            results[svc] = entry
        return results

    def encrypt_results(self, results=None):
        my_results = self.get_results()
        results = my_results.copy() if results is None else results
        for svc in results.keys():
            entry = results[svc]
            entry.encrypt_data(inplace=True)
            results[svc] = entry
        return results

    def reset_invalid_results(self):
        results = self.get_results()
        reset = False
        for svc in results:
            entry = results[svc]
            if not entry.verify(self.get_id()):
                reset = True
        return reset

    def verify_results(self, reset_invalidated=False):
        if not hasattr(self, RESULTS) or not isinstance(self.get_results(), dict):
            return False
        results = self.get_results()
        default_results = self.build_default_results()
        reset = False
        for svc in results:
            entry = results[svc]
            verification = entry.verify(self.get_id())
            if not verification and reset_invalidated:
                results[svc] = entry.reset()
                reset = True
            elif not verification:
                return False
        return not reset

    def is_expired(self, ctime=None):
        # if self.is_query_running():
        #     return False
        ctime = datetime.utcnow() if ctime is None else ctime
        lctime = datetime.strptime(self.get_last_check(), TIME_FMT)
        etime = datetime.strptime(self.get_end_date(), TIME_FMT)
        has_run = self.get_run_count() > 0

        if (lctime + timedelta(minutes=self.get_period())) < etime:
            return False
        if etime < ctime and has_run:
            return True
        return False

    def ready_for_query(self, ctime=None):
        ctime = datetime.utcnow() if ctime is None else ctime
        lctime = datetime.strptime(self.get_last_check(), TIME_FMT)
        is_ready = ctime > (lctime + timedelta(minutes=self.get_period()))

        if is_ready:
            self.set_query_running(True)
            self.set_running()
            return True
        return False

    def needs_purge(self, ctime=None, purge_after=PURGE_AFTER_MINUTES_VALUE):
        if not self.get_status() == COMPLETE:
            return False
        ctime = datetime.utcnow() if ctime is None else ctime
        lctime = datetime.strptime(self.get_last_check(), TIME_FMT)
        if ctime < (lctime + timedelta(minutes=purge_after)):
            return True
        return False

    def get_query_results(self, services=None, only_has_results=True):
        results = []
        if services is None or len(services) == 0:
            services = [i for i in self.get_query_names()]

        my_results = self.get_results()
        for svc in services:
            r = my_results[svc]
            if only_has_results and r[HAS_RESULTS]:
                results.append(r.copy())
            elif not only_has_results:
                results.append(r.copy())

        return results

    def add_results(self, results=None):
        results = dict() if results is None else results
        for name, entry in results.items():
            self.add_result(name, entry)

    def add_result_json(self, name, result_json, salt=None, decrypt=False):
        entry = StoredSplunkResult(salt=salt, **result_json)
        if decrypt:
            entry.decrypt_data(in_place=decrypt)
        return self.add_result(name, entry)

    def add_results_json(self, results_json=None, salt=None, decrypt=False):
        results_json = dict() if results_json is None else results_json
        for name, result_json in results_json.items():
            self.add_result_json(name, result_json, salt=salt, decrypt=decrypt)

    def mongo_add_result(self, mongo_service, name, results: StoredSplunkResult):
        if self.add_result(name, results):
            return self.mongo_update(mongo_service, field=RESULTS)
        return None

    def add_result(self, name, results: StoredSplunkResult):
        if results.has_plain_text():
            my_results = self.get_results()
            my_results[name] = results
            # print("Adding: {} {}".format(results.get_id(), results.serialize()))
            return True
        return False

    def is_query_running(self):
        a = any([r.get_splunk_query_running() for r in self.get_results().values()])
        self.set_query_running(a)
        return a

    def has_results(self):
        my_results = self.get_results()
        return any([r.get_has_results() for r in my_results.values()])

    def clear_results(self, services=None):
        results = []
        if services is None or len(services) == 0:
            services = [i for i in self.get_query_names()]

        my_results = self.get_results()
        for svc in services:
            my_results[svc][RESULTS] = None
            my_results[svc][HAS_RESULTS] = False
        return results

    def start_query(self, lctime=None, service=None, services=None):
        services = [] if services is None else services
        lctime = datetime.utcnow() if lctime is None else lctime
        ts = lctime.strftime(TIME_FMT)
        r = [i for i in services]
        if service not in r:
            r.append(service)

        if len(r) == 0:
            r = [i for i in self.get_query_names()]

        self.set_last_check(ts)
        self.set_query_running(True)
        my_results = self.get_results()
        for svc in r:
            my_results[svc][SPLUNK_QUERY_RUNNING] = True

    def serialize(self):
        r = {k: getattr(self, k, None) for k in self.REQUIRED_META_DATA_KEYS}
        r[RESULTS] = {k: e.serialize() for k, e in self.get_results().items()}
        r[ID] = r[JOB_ID]
        return r

    def serialize_store(self):
        r = self.serialize()
        r[RESULTS] = {k: e.serialize_store() for k, e in self.get_results().items()}
        return r

    def mongo_update_status(self, mongo_service, status=PENDING):
        if status != RUNNING and self.is_expired(datetime.utcnow()):
            self.set_status(COMPLETE)
        else:
            self.set_status(status)
        return self.mongo_update(mongo_service, field=STATUS)

    def mongo_query_start(self, mongo_service):
        self.set_status(RUNNING)
        self.set_query_running(True)
        return self.mongo_update(mongo_service, fields=[STATUS, SPLUNK_QUERY_RUNNING])

    def mongo_query_end(self, mongo_service, last_check=None):
        if last_check is not None:
            self.set_last_check(last_check)
        if self.is_expired(datetime.utcnow()):
            self.set_status(COMPLETE)
        else:
            self.set_status(PENDING)
        self.set_query_running(False)
        return self.mongo_update(mongo_service, fields=[STATUS, SPLUNK_QUERY_RUNNING, LAST_CHECK])

    def mongo_update_result_format(self, mongo_service, format=JSON):
        format = format if format in ALLOWED_SPLUNK_QUERY_RESULTS_FORMAT_VALUES else SPLUNK_QUERY_RESULTS_FORMAT_VALUE
        self.set_results_format(format)
        return self.mongo_update(mongo_service, field=SPLUNK_QUERY_RESULTS_FORMAT)

    def mongo_start_job(self, mongo_service):
        if self.start_job():
            return self.mongo_update(mongo_service, field=STATUS) is not None
        return False

    def mongo_update_lastcheck(self, mongo_service, last_check):
        self.set_last_check(last_check)
        return self.mongo_update(mongo_service, field=LAST_CHECK)

    def mongo_update(self, mongo_service, field=None, fields=None):
        fields = list() if fields is None else fields
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_jobs_collection()

        fields = [] if fields is None else fields
        doc = db[collection_name].find_one({'_id': self.get_id()})
        if doc is None:
            r = db[collection_name].insert_one(self.serialize_store())
            conn.close()
            return r

        r = [i for i in fields]
        if field is not None:
            r.append(field)

        if len(r) == 0:
            r = self.REQUIRED_META_DATA_KEYS

        data = self.serialize_store()
        updates = {k: data[k] for k in r}
        r = db[collection_name].update_one({'_id': self.get_id()}, {'$set': updates})
        conn.close()
        return r

    def mongo_store(self, mongo_service):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_jobs_collection()
        r = db[collection_name].update_one({'_id': self.get_id()}, {'$set': self.serialize_store()})
        conn.close()
        return r

    def mongo_insert(self, mongo_service):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_jobs_collection()
        r = db[collection_name].insert_one(self.serialize_store())
        conn.close()
        return r

    def mongo_delete(self, mongo_service):
        conn, db = mongo_service.get_conn_database()
        collection_name = mongo_service.get_jobs_collection()
        r = db[collection_name].delete_one({'_id': self.get_id()})
        conn.close()
        return r

    def get_meta_data(self):
        return getattr(self, SPLUNK_QUERY_METADATA, {})

    def set_meta_data(self, meta_data):
        return setattr(self, SPLUNK_QUERY_METADATA, meta_data)

    def get_results_format(self):
        return getattr(self, SPLUNK_QUERY_RESULTS_FORMAT)

    def set_results_format(self, value=JSON):
        setattr(self, SPLUNK_QUERY_RESULTS_FORMAT, value)

    def get_earliest(self):
        return getattr(self, EARLIEST)

    def get_latest(self):
        return getattr(self, LATEST)

    def get_run_once(self):
        return getattr(self, RUN_ONCE, False)

    def get_run_count(self):
        return getattr(self, RUN_COUNT, 0)

    def get_max_runs(self):
        return getattr(self, MAX_RUNS, -1)

    def inc_run_count(self):
        setattr(self, RUN_COUNT, self.get_run_count()+1)