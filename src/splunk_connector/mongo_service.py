from .standard_logger import Logger
from .consts import *
import ssl
from pymongo import MongoClient
from .config import Config
from datetime import datetime, timedelta
from .job_info import ScheduledJobInfo
from .stored_results import StoredSplunkResult
from .results import SplunkResult
import traceback

import docker

class MongoService(object):
    DEFAULT_VALUES = {
        MONGO_NAME: SPLUNK_MONGO_SERVICE,
        MONGO_HOST: '127.0.0.1',
        MONGO_PORT: 27017,
        MONGO_DB: MONGO_SERVICE_BLOCK,
        MONGO_USERNAME: None,
        MONGO_PASSWORD: None,
        JOBS_COLLECTION: JOBS_COLLECTION_VALUE,
        QUERY_RESULTS_COLLECTION: QUERY_RESULTS_COLLECTION_VALUE,
        USE_SSL: True,
        USE_MONGO_ACL:False,
        MONGO_DOCKER_NET: MONGO_DOCKER_NET_VALUE,
        MONGO_DOCKER_SUBNET: MONGO_DOCKER_SUBNET_VALUE,
        MONGO_DOCKER_GATEWAY: MONGO_DOCKER_GATEWAY_VALUE,
        MONGO_DOCKER_PORT: MONGO_DOCKER_PORT_VALUE,
        MONGO_DOCKER_DETACH: MONGO_DOCKER_DETACH_VALUE,
        MONGO_DOCKER_USERNAME: MONGO_DOCKER_USERNAME_VALUE,
        MONGO_DOCKER_PASSWORD: MONGO_DOCKER_PASSWORD_VALUE,
        MONGO_DOCKER_NAME: MONGO_DOCKER_NAME_VALUE,
        MONGO_DOCKER_ENVIRONMENT: MONGO_DOCKER_ENVIRONMENT_VALUE,
        MONGO_DOCKER_PORTS: MONGO_DOCKER_PORTS_VALUE,
        MONGO_DOCKER_IMAGE: MONGO_DOCKER_IMAGE_VALUE,
        MONGO_DOCKER_IP: MONGO_DOCKER_IP_VALUE,
        MONGO_ENCRYPT_DATA: False,
        MONGO_DATA_KEY: None,
    }

    def __init__(self, **kwargs):
        if kwargs.get(MONGO_DATA_KEY, None) is not None:
            kwargs[MONGO_ENCRYPT_DATA] = True
            StoredSplunkResult.set_data_key(kwargs[MONGO_DATA_KEY])
        elif kwargs.get(MONGO_ENCRYPT_DATA, False):
            kwargs[MONGO_ENCRYPT_DATA] = True
            StoredSplunkResult.set_data_key(use_random=True)
        else:
            kwargs[MONGO_ENCRYPT_DATA] = False
            StoredSplunkResult.set_data_key()

        self.docker_kargs = {}

        self.init_keys = set()

        for k, v in kwargs.items():
            setattr(self, k, v)
            self.init_keys.add(k)

        for k, v in self.DEFAULT_VALUES.items():
            if k not in kwargs:
                setattr(self, k, v)
            else:
                setattr(self, k, kwargs.get(k))

        self.logger = Logger(self.get_mongo_name())

    def get_docker_net(self):
        return getattr(self, MONGO_DOCKER_NET, MONGO_DOCKER_NET_VALUE)

    def get_docker_subnet(self):
        return getattr(self, MONGO_DOCKER_SUBNET, MONGO_DOCKER_SUBNET_VALUE)

    def get_docker_gateway(self):
        return getattr(self, MONGO_DOCKER_GATEWAY, MONGO_DOCKER_GATEWAY_VALUE)

    def get_docker_port(self):
        return getattr(self, MONGO_DOCKER_PORT, MONGO_DOCKER_PORT_VALUE)

    def get_docker_detach(self):
        return getattr(self, MONGO_DOCKER_DETACH, MONGO_DOCKER_DETACH_VALUE)

    def get_docker_image(self):
        return getattr(self, MONGO_DOCKER_IMAGE, MONGO_DOCKER_IMAGE_VALUE)

    def get_docker_ip(self):
        return getattr(self, MONGO_DOCKER_IP, MONGO_DOCKER_IP_VALUE)

    def configure_docker(self, **kargs):
        self.docker_kargs = {}
        self.docker_kargs[MONGO_DOCKER_NET] = kargs.get(MONGO_DOCKER_NET, self.get_docker_net())
        self.docker_kargs[MONGO_DOCKER_SUBNET] = kargs.get(MONGO_DOCKER_SUBNET, self.get_docker_subnet())
        self.docker_kargs[MONGO_DOCKER_GATEWAY] = kargs.get(MONGO_DOCKER_GATEWAY, self.get_docker_gateway())
        self.docker_kargs[MONGO_DOCKER_PORT] = kargs.get(MONGO_DOCKER_PORT, self.get_docker_port())
        self.docker_kargs[MONGO_DOCKER_DETACH] = kargs.get(MONGO_DOCKER_DETACH, self.get_docker_detach())
        self.docker_kargs[MONGO_DOCKER_USERNAME] = self.get_mongo_username()
        self.docker_kargs[MONGO_DOCKER_PASSWORD] = self.get_mongo_password()
        self.docker_kargs[MONGO_DOCKER_NAME] = self.get_mongo_name()
        self.docker_kargs[MONGO_DOCKER_IMAGE] = kargs.get(MONGO_DOCKER_IMAGE, self.get_docker_image())
        self.docker_kargs[MONGO_DOCKER_IP] = kargs.get(MONGO_DOCKER_IP, self.get_docker_ip())

        if MONGO_DOCKER_PORTS not in kargs:
            self.docker_kargs[MONGO_DOCKER_PORTS] = {
                # "%s/tcp" % str(self.docker_kargs[MONGO_DOCKER_PORT]): [27017],
                "%s/tcp" % str(27017): [self.docker_kargs[MONGO_DOCKER_PORT]],
            }
        else:
            self.docker_kargs[MONGO_DOCKER_PORTS] = kargs[MONGO_DOCKER_PORTS]

        if MONGO_DOCKER_ENVIRONMENT not in kargs:
            self.docker_kargs[MONGO_DOCKER_ENVIRONMENT] = {
                MONGO_INITDB_ROOT_USERNAME: self.docker_kargs.get(MONGO_DOCKER_USERNAME, MONGO_DOCKER_USERNAME_VALUE),
                MONGO_INITDB_ROOT_PASSWORD: self.docker_kargs.get(MONGO_DOCKER_PASSWORD, MONGO_DOCKER_PASSWORD_VALUE),
            }
        else:
            self.docker_kargs[MONGO_DOCKER_ENVIRONMENT] = kargs[MONGO_DOCKER_ENVIRONMENT]

    def start_docker(self):
        client = docker.from_env()
        try:

            ipam_pool = docker.types.IPAMPool(subnet=self.docker_kargs[MONGO_DOCKER_SUBNET],
                                              gateway=self.docker_kargs[MONGO_DOCKER_GATEWAY])
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

            self.logger.debug('creating the docker network for %s' % self.docker_kargs[MONGO_DOCKER_NET])
            network = client.networks.create(
                self.docker_kargs[MONGO_DOCKER_NET],
                driver="bridge",
                ipam=ipam_config)
        except:
            pass

        self.logger.debug('creating the docker container for %s' % self.docker_kargs[MONGO_DOCKER_NAME])
        container = client.containers.run(self.docker_kargs[MONGO_DOCKER_IMAGE],
                                          name=self.docker_kargs[MONGO_DOCKER_NAME],
                                          ports=self.docker_kargs[MONGO_DOCKER_PORTS],
                                          environment=self.docker_kargs[MONGO_DOCKER_ENVIRONMENT],
                                          detach=self.docker_kargs[MONGO_DOCKER_DETACH], )
        self.logger.debug('connecting the docker container %s to network: %s' % (
            self.docker_kargs[MONGO_DOCKER_NAME],
            self.docker_kargs[MONGO_DOCKER_NET]))

        net = client.networks.get(self.docker_kargs[MONGO_DOCKER_NET])
        net.connect(container, ipv4_address=self.docker_kargs[MONGO_DOCKER_IP])
        client.close()

        try:
            self.get_conn_database()
            return True
        except:
            raise

    def stop_docker(self):
        client = docker.from_env()
        container = client.containers.get(self.docker_kargs[MONGO_DOCKER_NAME])
        network = client.networks.get(self.docker_kargs[MONGO_DOCKER_NET])
        if container is not None:
            try:
                container.kill()
            except:
                pass
            try:
                container.remove()
            except:
                pass

        if network is not None:
            try:
                network.remove()
            except:
                pass
        client.close()

    def refresh_docker(self):
        try:
            self.stop_docker()
        except:
            pass
        self.start_docker()

    @classmethod
    def from_config(cls, name=None):
        mongo_cdict = None
        if name is None:
            mongo_service_cdict = Config.get_value(MONGO_SERVICE_BLOCK)
            if mongo_service_cdict is None:
                raise Exception("No valid mongo service configurations found")
            if len(mongo_service_cdict):
                mongo_cdict = list(mongo_service_cdict.values())[0]
        else:
            mongo_cdict = Config.get_mongo_service(name)

        if mongo_cdict is None or len(mongo_cdict) == 0:
            raise Exception("No valid mongo service configurations found")

        kwargs = {}
        for k, v in cls.DEFAULT_VALUES.items():
            if k not in mongo_cdict:
                kwargs[k] = v
            else:
                kwargs[k] = mongo_cdict.get(k)
        return cls(**kwargs)

    def get_connection(self, ssl_cert_reqs=ssl.CERT_NONE):
        # TODO SSL connection validation
        return MongoClient(host=self.get_mongo_host(),
                           port=self.get_mongo_port(),
                           username=self.get_mongo_username(),
                           password=self.get_mongo_password(),
                           ssl=self.get_use_ssl(),
                           ssl_cert_reqs=ssl_cert_reqs)

    def get_conn_database(self, ssl_cert_reqs=ssl.CERT_NONE, db_name=None):
        db_name = db_name if db_name is not None else self.get_mongo_db()
        conn = self.get_connection(ssl_cert_reqs)
        db = conn[db_name]
        return conn, db

    def job_status(self, job_id):
        conn, db = self.get_conn_database()
        doc = db[self.get_jobs_collection()].find_one({'_id': job_id})
        r = None
        if doc is not None:
            job = ScheduledJobInfo(**doc)
            r = job.get_status()
        self.close_connection(conn)
        return r

    def splunk_query_running(self, job_id):
        conn, db = self.get_conn_database()
        doc = db[self.get_jobs_collection()].find_one({'_id': job_id})
        r = None
        if doc is not None:
            job = ScheduledJobInfo(**doc)
            r = job.is_query_running()
        self.close_connection(conn)
        return r

    def jobs_with_results(self):
        results = []
        docs = self.get_all()
        # conn, db = self.get_conn_database()
        # cur = db[self.get_jobs_collection()].find({})
        for doc in docs:
            job = ScheduledJobInfo(salt=doc.get(JOB_ID, None), **doc)
            if job.has_results():
                results.append(job)
        return results

    def job_has_results(self, job_id):
        # conn, db = self.get_conn_database()
        # doc = db[self.get_jobs_collection()].find_one({'_id': job_id})
        doc = self.get_one(ID, job_id)
        r = None
        if doc is not None:
            job = ScheduledJobInfo(**doc)
            r = job.get_results()
        # self.close_connection(conn)
        return r

    def clear_job_results(self, job_id, services):
        # conn, db = self.get_conn_database()
        # doc = db[self.get_jobs_collection()].find_one({'_id': job_id})
        doc = self.get_one(ID, job_id)
        r = False
        if doc is not None:
            job = ScheduledJobInfo(**doc)
            job.clear_results(services)
            job.mongo_update(self, fields=[RESULTS])
            r = True
        # self.close_connection(conn)
        return r

    def set_job_results(self, job_id, query_name, results):
        # conn, db = self.get_conn_database()
        # doc = db[self.get_jobs_collection()].find_one({'_id': job_id})
        doc = self.get_one(ID, job_id)
        r = False
        if doc is not None:
            job_info = ScheduledJobInfo(**doc)
            job_results = job_info.get_results()
            job_results[query_name] = {HAS_RESULTS: True, RESULTS: results, SPLUNK_QUERY_RUNNING: False}
            job_info.mongo_update(self, fields=[RESULTS])
            r = True
        # self.close_connection(conn)
        return r

    def get_one(self, key, value):
        key_values = {key: value}
        conn, db = self.get_conn_database()
        doc = db[self.get_jobs_collection()].find_one(key_values)
        self.close_connection(conn)
        return doc

    def get_all(self):
        return self.get_all_by_key(key_values=dict())

    def get_all_by_key(self, key=None, value=None, key_values=None):
        key_values = {} if key_values is None else key_values
        if key is not None:
            key_values[key] = value
        conn = None
        try:
            conn, db = self.get_conn_database()
            cur = db[self.get_jobs_collection()].find(key_values)
            return [i for i in cur]
        except:
            self.logger.error(traceback.format_exc())
        finally:
            if conn is not None:
                self.close_connection(conn)
        return None

    def job_get_results(self, job_id: str):
        doc = self.get_one(ID, job_id)
        r = None
        if doc is not None:
            job = ScheduledJobInfo(**doc)
            r = job.get_results()
            job.clear_results()
            job.mongo_update(self, field=RESULTS)
        return r

    def job_past_results(self, job_id: str):
        return self.get_stored_result_for_job_id(job_id)

    def start_pending_jobs(self):
        cnt = 0
        docs = self.get_all_by_key(STATUS, PENDING)
        if docs is None:
            return -1
        for doc in docs:
            job = ScheduledJobInfo(**doc)
            self.logger.debug("Changing {} status from {} to {}".format(job.get_id(), PENDING, RUNNING))
            setattr(job, STATUS, RUNNING)
            job.mongo_update(self, field=STATUS)
            cnt += 1
        return cnt

    def set_job_query_start(self, job_id: str) -> ScheduledJobInfo:
        job_info = self.get_job_info(job_id)
        if job_info is None:
            return None
        job_info.mongo_query_start(self)
        return job_info

    def set_job_query_done(self, job_id: str) -> ScheduledJobInfo:
        job_info = self.get_job_info(job_id)
        if job_info is None:
            return None
        job_info.mongo_query_end(self)
        return job_info

    def load_completed_jobs(self):
        self.mark_jobs_complete()
        docs = self.get_all_by_key(STATUS, COMPLETE)
        if docs is None:
            return None
        jobs = []
        if docs is None:
            return jobs
        for doc in docs:
            job = ScheduledJobInfo(**doc)
            jobs.append(job)
        return jobs

    def mark_jobs_complete(self):
        docs = self.get_all_by_key(STATUS, RUNNING)
        if docs is None:
            return None

        ctime = datetime.utcnow()
        cnt = 0
        for doc in docs:
            job = ScheduledJobInfo(**doc)
            if job.is_expired(ctime):
                setattr(job, STATUS, COMPLETE)
                job.mongo_update(self, field=STATUS)
                cnt += 1
                continue
        return cnt

    def jobs_ready_for_query(self):
        docs = self.get_all_by_key(STATUS, RUNNING)
        job_ids = []
        if docs is None:
            return job_ids
        ctime = datetime.utcnow()
        for doc in docs:
            if doc[SPLUNK_QUERY_RUNNING]:
                continue
            job = ScheduledJobInfo(**doc)
            if job.ready_for_query(ctime):
                job_ids.append(job.get_id())
                setattr(job, SPLUNK_QUERY_RUNNING, True)
                job.mongo_update(self)
        return job_ids

    @classmethod
    def close_connection(cls, conn):
        try:
            conn.close()
        except:
            pass

    def test_connection(self):
        r = False
        mc, _ = self.get_conn_database()
        try:
            _ = mc.list_database_names()
            r = True
        except:
            pass
        finally:
            self.close_connection(mc)
        return r

    def load_all_jobs(self):
        # results = self.get_jobs_docs_iterable()
        jobs = [ScheduledJobInfo(salt=doc.get(JOB_ID, None), **doc) for doc in self.get_all()]
        return jobs

    def load_all_query_results(self):
        return self.get_stored_results()

    def get_jobs_docs_iterable(self, key_values=None):
        return self.get_all_by_key(key_values=key_values)

    def get_query_results_doc_iterable(self, key_values=None):
        key_values = {} if key_values is None else key_values
        conn, db = self.get_conn_database()
        cur = db[self.get_query_results_collection()].find(key_values)
        results = []
        if cur is not None:
            results = [i for i in cur]

        self.close_connection(conn)
        return results

    def purge_jobs(self, purge_after=PURGE_AFTER_HOURS):
        self.mark_jobs_complete()
        docs = self.get_all_by_key(STATUS, COMPLETE)
        ctime = datetime.utcnow()
        cnt = 0
        for doc in docs:
            job = ScheduledJobInfo(**doc)
            if job.needs_purge(ctime, purge_after):
                cnt += 1
                self.purge_stored_results_for_job(job.get_id())
                job.mongo_delete(self)

        return cnt

    def delete_all_jobs(self):
        jobs = []
        docs = self.get_all()
        for doc in docs:
            job = ScheduledJobInfo(salt=doc.get(JOB_ID, None), **doc)
            job.mongo_delete(self)
            jobs.append(job)
        return jobs

    def delete_all_results(self):
        results = self.load_all_query_results()
        for result in results:
            result.mongo_delete(self)
        return results

    def get_job_info(self, job_id: str) -> ScheduledJobInfo:
        doc = self.get_one(ID, job_id)
        if doc is not None:
            return ScheduledJobInfo(salt=job_id, **doc)
        return None

    def insert_job(self, job_info: ScheduledJobInfo):
        conn, db = self.get_conn_database()
        r = job_info.mongo_update(self)
        self.close_connection(conn)
        return r is not None

    def insert_splunk_result(self, splunk_result: SplunkResult, job_id=None, salt=None):
        stored_result = StoredSplunkResult.from_splunk_result(splunk_result, job_id=job_id, salt=salt)
        return self.insert_stored_result(stored_result)

    def insert_stored_result(self, stored_result: StoredSplunkResult):
        conn, db = self.get_conn_database()
        r = stored_result.mongo_insert(self)
        self.close_connection(conn)
        return r is not None

    def get_stored_result_for_job_id(self, job_id):
        conn, db = self.get_conn_database()
        stored_results = StoredSplunkResult.mongo_load_all(self, job_id=job_id)
        self.close_connection(conn)
        return stored_results

    def get_stored_results(self):
        conn, db = self.get_conn_database()
        r = StoredSplunkResult.mongo_load_all(self)
        self.close_connection(conn)
        return r

    def get_stored_result(self, oid):
        conn, db = self.get_conn_database()
        r = StoredSplunkResult.mongo_load(self, oid)
        self.close_connection(conn)
        return r

    def update_job(self, job_info: ScheduledJobInfo, field=None, fields=None):
        fields = [] if fields is None else fields
        conn, db = self.get_conn_database()
        r = job_info.mongo_update(self, field=field, fields=fields)
        self.close_connection(conn)
        return r is not None

    def purge_stored_results_for_job(self, job_id):
        stored_results = self.get_stored_result_for_job_id(job_id)
        conn, db = self.get_conn_database()
        for sr in stored_results:
            sr.mongo_delete(db, self.get_query_results_collection())
        self.close_connection(conn)
        return stored_results

    def purge_stored_results(self, oid=None):
        if oid is None:
            stored_results = self.get_stored_results()
            for sr in stored_results:
                sr.mongo_delete(self)
            return stored_results
        else:
            sr = self.get_stored_result(oid)
            if sr is not None:
                sr.mongo_delete(self)
            return sr

    def get_jobs_collection(self):
        return getattr(self, JOBS_COLLECTION)

    def get_query_results_collection(self):
        return getattr(self, QUERY_RESULTS_COLLECTION)

    def get_mongo_name(self):
        return getattr(self, MONGO_NAME)

    def get_mongo_db(self):
        return getattr(self, MONGO_DB)

    def get_mongo_host(self):
        return getattr(self, MONGO_HOST)

    def get_mongo_port(self):
        return getattr(self, MONGO_PORT)

    def get_mongo_username(self):
        return getattr(self, MONGO_USERNAME)

    def get_mongo_password(self):
        return getattr(self, MONGO_PASSWORD)

    def get_use_ssl(self):
        return getattr(self, USE_SSL)

