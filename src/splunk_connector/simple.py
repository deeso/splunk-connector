import time
from .consts import OUTPUT_MODE, JSON
import splunklib.client as client
from splunklib.binding import ResponseReader
from splunklib.client import Job
from splunklib.client import Service

class Query(object):

    @classmethod
    def execute(self, hostname, port, username, password,
                query, job_keywords={}, export=False) -> (Service, Job):
        svc = client.connect(
            host=hostname,
            port=port,
            username=username,
            password=password)
        job = None
        try:
            if export:
                job = svc.jobs.export(query, **job_keywords)
            else:
                jk = job_keywords.copy()
                op_mode = {OUTPUT_MODE: jk.get(OUTPUT_MODE, JSON)}
                if OUTPUT_MODE in jk:
                    del jk[OUTPUT_MODE]
                job = svc.jobs.create(query, **jk)
                job.update()
        except:
            pass
        return svc, job

    @classmethod
    def read_job(cls, job: Job, block=False, read_json=True) -> bytes:
        jk = {}
        if read_json:
            jk[OUTPUT_MODE] = JSON

        if block:
            while not job.is_done():
                job.touch()
                if job.is_done():
                    break
                time.sleep(1.0)
        rr = job.results(**jk)
        return cls.read_all(rr)

    @classmethod
    def read_all(cls, response_reader: ResponseReader) -> bytes:
        data = b''
        while not response_reader.closed:
            d = response_reader.read()
            if len(d) == 0:
                break
            data = data + d
        return data

