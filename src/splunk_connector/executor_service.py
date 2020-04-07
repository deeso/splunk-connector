from threading import Timer
import traceback
import multiprocessing
from multiprocessing.pool import Pool, ApplyResult
from .standard_logger import Logger
from .config import Config
from .consts import *

def execute_splunk_job(svc_name: str, job_id: str = None, results_dict: dict = None):
    # print('splunk_service.execute_splunk_job starting: %s, %s %s' % (svc_name, job_id, traceback.format_exc()))
    try:
        from .stored_results import StoredSplunkResult
        from .connector import SplunkServices
        from .mongo_service import MongoService
    except:
        print('splunk_service.execute_splunk_job failed: %s, %s %s' % (svc_name, job_id, traceback.format_exc()))
        return job_id, None

    # print('splunk_service.execute_splunk_job loaded: %s, %s %s' % (svc_name, job_id, traceback.format_exc()))
    if job_id is None:
        return job_id, None

    self = None
    try:
        services = SplunkServices.from_config()
        self = services.get_service(svc_name)
    except:
        print('splunk_service.execute_splunk_job failed (service config not found: %s): %s'% (svc_name, traceback.format_exc()))
        return job_id, None

    self.logger.action('splunk_service.execute_splunk_job','splunk_service[%s]'%svc_name,
                       "Executing splunk queries for job_id: %s" % job_id)

    ms = MongoService.from_config(self.get_mongo_service_name())
    job_info = ms.set_job_query_start(job_id)
    query_results = results_dict if results_dict is not None else dict()

    if job_info is None:
        self.logger.error("Unable to find job_information for job_id: %s" % job_id)
        return job_id, query_results
    query_names = job_info.get_query_names()
    job_keywords = job_info.get_job_keywords()

    run_once = job_info.get_run_once()
    run_count = job_info.get_run_count()
    max_runs = job_info.get_max_runs()

    start_check = job_info.get_last_check()
    end_check = self.get_formatted_time_now()

    if start_check is None or run_count <= 0 or run_once:
        start_check = job_info.get_start_date()

    if run_count <= 0 or run_once:
        end_check = job_info.get_end_date()

    earliest = start_check
    latest = end_check
    x =  'start_check={} end_check={}'.format(start_check, end_check)
    self.logger.action('ulm-service.perform_query_cycle: performing check', SERVICE_THREAD, x)

    x = 'start_date={} end_date={}'.format(job_info.get_start_date(), job_info.get_end_date())
    self.logger.action('ulm-service.perform_query_cycle: checking value ', SERVICE_THREAD, x)

    x = 'earliest={} latest={}'.format(earliest, latest)
    self.logger.action('ulm-service.perform_query_cycle: checking value ', SERVICE_THREAD, x)

    x = 'run_once={} max_runs={} run_count={}'.format(run_once, max_runs, run_count)
    self.logger.action('ulm-service.perform_query_cycle: checking value ', SERVICE_THREAD, x)

    query_data = job_info.get_query_data().copy()
    query_data[EARLIEST] = earliest
    query_data[LATEST] = latest

    self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                       "Query parameters: %s" % str(list(query_data.keys())))

    ts = latest
    try:
        date, hour, minutes, seconds = latest.split(':')
        ts = '.'.join([date.replace('/', '-'), hour, minutes, seconds])
    except:
        self.logger.error('splunk_service.execute_splunk_job failed:' + traceback.format_exc())

    for name in query_names:
        query_results[name] = None
        self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                           "Performing splunk query '%s' for %s" % (name, job_id))
        ext = job_keywords.get(OUTPUT_MODE, 'txt')
        filename = '{}--{}--{}.{}'.format(job_id, name, ts, ext)
        ssr = None
        try:
            splunk_results = self.perform_stored_query(name, query_data=query_data, blocking=True,
                                                       export=False, job_keywords=job_keywords, filename=filename)
            ssr = StoredSplunkResult.from_splunk_result(splunk_results, job_id=job_info.get_id())
        except:
            error = 'splunk_service.execute_splunk_job failed: {}'.format(traceback.format_exc())
            ssr = StoredSplunkResult.from_error(earliest, latest, name, error, job_id)
            self.logger.error(error)

        ms.insert_stored_result(ssr)
        query_results[name] = ssr

        try:
            job_info.mongo_add_result(ms, name, ssr)
        except:
            self.logger.error('splunk_service.execute_splunk_job failed to add the query result for %s to (%s):'%(name, job_id) + traceback.format_exc())


    self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                       "completed queries, updating job %s data" % (job_id))


    self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                       "completed %s mongo update, serialized results to pass to callback" % (job_id))

    serial_query_results = {}
    try:
        serial_query_results = {k: v.serialize() if v is not None else None for k, v in query_results.items()}
    except:
        self.logger.error('splunk_service.execute_splunk_job failed to serialize results:' + traceback.format_exc())

    try:
        self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                           'updating job {} last_check to {}, was {}'.format(
                               job_id, latest, job_info.get_last_check()))
        job_info.set_last_check(latest)
        job_info.mongo_query_end(ms)
        self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                           'completed updating job {} last_check to {} is {}'.format(
                               job_id, latest, job_info.get_last_check()))
    except:
        self.logger.action('splunk_service.execute_splunk_job', 'splunk_service[%s]' % svc_name,
                           'splunk_service.execute_splunk_job failed to update job {}:\n{}'.format(
                               job_id, traceback.format_exc()))

    # print("my pid: ", multiprocessing.current_process())
    return job_id, serial_query_results

class ExecutorService(object):

    DEFAULT_VALUES = {
        EXECUTOR_NAME: lambda: SPLUNK_EXECUTOR_SERVICE,
        EXECUTOR_NUM_PROCS: lambda: 4,
        EXECUTOR_POLL_TIME: lambda: 10,
        EXECUTOR_POLL_TASK: lambda: None,
        EXECUTOR_POLL_ARGS: lambda: list(),
        EXECUTOR_POLL_KARGS: lambda: dict(),
        EXECUTOR_START_POLLING_WITH_SVC: lambda: False,
        EXECUTOR_SERVICE_START: lambda: False,
        EXECUTOR_MAX_ITERATIONS: lambda: 0,
    }

    def __init__(self, **kargs):
        self.pool = None
        self.accepting_tasks = False
        self.polling = False
        self.polling_timer_thread = None

        self.iterations = 0

        for k, v in kargs.items():
            if k in self.DEFAULT_VALUES and v is not None:
                setattr(self, k, v)
            elif k in self.DEFAULT_VALUES:
                fn = self.DEFAULT_VALUES[k]
                setattr(self, k, fn())

        for k, fn in self.DEFAULT_VALUES.items():
            if k not in kargs:
                setattr(self, k, fn())
        self.logger = Logger("executor-service-%s" % str(self.get_name()))
        if self.get_service_start():
            self.start()

    def get_num_procs(self) -> int:
        return getattr(self, EXECUTOR_NUM_PROCS)

    def set_num_procs(self, num_procs: int):
        return setattr(self, EXECUTOR_NUM_PROCS, num_procs)

    def get_max_iterations(self) -> int:
        return getattr(self, EXECUTOR_MAX_ITERATIONS)

    def set_max_iterations(self, max_iterations: int):
        return setattr(self, EXECUTOR_MAX_ITERATIONS, max_iterations)

    def get_name(self) -> str:
        return getattr(self, EXECUTOR_NAME)

    def set_name(self, name: str):
        return setattr(self, EXECUTOR_NAME, name)

    def get_poll_args(self) -> list:
        return getattr(self, EXECUTOR_POLL_ARGS)

    def set_poll_args(self, poll_args: list):
        return setattr(self, EXECUTOR_NAME, poll_args)

    def get_poll_kargs(self) -> dict:
        return getattr(self, EXECUTOR_POLL_KARGS)

    def set_poll_kargs(self, poll_kargs: dict):
        return setattr(self, EXECUTOR_NAME, poll_kargs)

    def get_poll_time(self) -> int:
        return getattr(self, EXECUTOR_POLL_TIME)

    def set_poll_time(self, poll_time: int):
        return setattr(self, EXECUTOR_POLL_TIME, poll_time)

    def get_poll_task(self) -> callable:
        return getattr(self, EXECUTOR_POLL_TASK)

    def set_poll_task(self, poll_task: callable):
        return setattr(self, EXECUTOR_POLL_TASK, poll_task)

    def get_start_polling_with_service(self) -> bool:
        return getattr(self, EXECUTOR_START_POLLING_WITH_SVC)

    def set_start_polling_with_service(self, start_polling: bool):
        setattr(self, EXECUTOR_START_POLLING_WITH_SVC, start_polling)

    def get_service_start(self) -> bool:
        return getattr(self, EXECUTOR_SERVICE_START)


    @classmethod
    def from_config(cls, name=None, **kwargs):
        executor_cdict = None
        if name is None:
            executor_service_cdict = Config.get_value(EXECUTOR_SERVICE_BLOCK)
            if executor_service_cdict  is None:
                raise Exception("No valid executor service configurations found")
            if len(executor_service_cdict):
                executor_cdict = list(executor_service_cdict.values())[0]
        else:
            executor_cdict = Config.get_executor_service(name)

        if executor_cdict is None or len(executor_cdict) == 0:
            raise Exception("No valid executor service configurations found")

        skwargs = {}
        for k, v in cls.DEFAULT_VALUES.items():
            if k in kwargs:
                skwargs[k] = kwargs[k]
            elif k in executor_cdict:
                skwargs[k] = executor_cdict.get(k)
            else:
                skwargs[k] = v()
        return cls(**skwargs)

    def poll_task(self):
        '''
        Execute the supplied task with keywords and arguments,
        and then upon performing the poll_task take the results and submit
        them as a job to the ExecutorService

        The results returned from the supplied poll_task should be a list of dictionaries containing
        the following keys and typed data:
        {
            "executor_job_func": callable,
            "executor_job_callback": callable,
            "executor_job_error_callback": callable,
            "executor_job_args": list,
            "executor_job_kargs": dict,
        }

        returns a Timer Thread (None, current, or newly scheduled) and whether or not a new Timer Thread was scheduled
        :return: Timer, bool
        '''
        self.iterations += 1
        self.logger.action('executor-poll_task', None, 'checking and preparing poll task')
        poll_task = self.get_poll_task()
        if not self.polling:
            return self.polling_timer_thread, False
        elif poll_task is None:
            return self.polling_timer_thread, False

        self.logger.action('executor-poll_task', None, 'executing poll_task')
        args = self.get_poll_args()
        kargs = self.get_poll_kargs()
        args = [] if args is None else args
        kargs = {} if kargs is None else kargs
        results = poll_task(*args, **kargs)
        self.logger.action('executor-poll_task', None, '%s found %d results' % (poll_task.__name__, len(results)))
        for result in results:
            func: callable = result.get(EXECUTOR_JOB_FUNC, None)
            callback: callable = result.get(EXECUTOR_JOB_CALLBACK, None)
            error_callback: callable = result.get(EXECUTOR_JOB_ERROR_CALLBACK, None)
            jargs: list = result.get(EXECUTOR_JOB_ARGS, list())
            jkargs: dict = result.get(EXECUTOR_JOB_KARGS, dict())
            self.submit_job(func, jargs, jkargs, callback=callback, error_callback=error_callback)

        self.polling_timer_thread = None
        if self.polling and not self.is_iterations_completed():
            return self.schedule_next_polling_timer()
        return self.polling_timer_thread, False

    def is_iterations_completed(self):
        '''
        Check to see if the execution service has completed the number of required iterations

        :return: bool if we exceeded the number of poll iterations and max number of iterations is not zero
        '''
        mi = self.get_max_iterations()
        if mi == 0 or self.iterations < mi:
            return False
        self.polling = False
        return True


    def schedule_next_polling_timer(self) -> (Timer, bool):
        '''
        Schedule a timer thread to execute a Executor.poll_task after Executor.get_poll_time() secconds

        if Executor.polling is False, polling thread is not rescheduled
        :return: Timer, bool Timer is None if not polling or previous thread
        '''
        if not self.polling:
            return None, False

        if not self.cancel_polling_timer():
            return self.polling_timer_thread, False

        poll_time = float(self.get_poll_time())
        x = 'scheduling next task, current poll iteration: %.01fs' % poll_time
        self.logger.action('executor-schedule_next_polling_timer', None, x)
        self.polling_timer_thread = Timer(poll_time, self.poll_task)
        self.polling_timer_thread.start()
        return self.polling_timer_thread, True

    def start_polling_timer(self):
        '''
        Start the continuous iterations of timer thread to execute a Executor.poll_task after
        Executor.get_poll_time() secconds

        if Executor.polling is False, polling thread is not rescheduled
        :return: Timer, bool Timer is None if not polling or previous thread
        :return:
        '''
        if self.polling:
            return self.polling
        poll_time = self.get_poll_time()
        x = 'starting the polling timer: %.01fs' % poll_time
        self.logger.action('executor-schedule_next_polling_timer', None, x)

        self.iterations = 0
        self.polling = True
        self.schedule_next_polling_timer()

    def cancel_polling_timer(self):
        if self.polling_timer_thread is None or \
                not isinstance(self.polling_timer_thread, Timer):
            self.polling_timer_thread = None
            return True

        self.polling_timer_thread.cancel()
        return not self.polling_timer_thread.is_alive() and \
               self.polling_timer_thread.finished.is_set()

    def stop_polling_timer(self):
        self.polling = False
        return self.cancel_polling_timer()

    def start_service(self, with_polling=False):
        return self.start(with_polling=with_polling)

    def stop_service(self):
        return self.stop()

    def start(self, with_polling=False):
        '''
        start the executor process pool
        :return:
        '''
        if self.pool is not None:
            self.stop()

        if with_polling or self.get_start_polling_with_service():
            self.start_polling_timer()
        self.logger.action('executor-start', None, 'starting the service')
        self.accepting_tasks = True
        self.pool = Pool(processes=self.get_num_procs())
        self.logger.action('executor-start', None, 'starting the service completed')

    def stop(self, join=True):
        '''
        stop the process pool.  if join is true, join all processes first, otherwise terminate
        :return:
        '''
        self.logger.action('executor-stop', None, 'stopping the service')
        self.accepting_tasks = False

        self.polling = False
        self.stop_polling_timer()

        if join:
            self.join_terminate()
        else:
            self.terminate()
        self.pool = None

    def submit_job(self, func:callable, args:list, kargs:dict,
                   callback:callable=None, error_callback:callable=None) -> ApplyResult:
        '''

        :param func: callable, function to call
        :param callback: callable to handle completion
        :param error_callback: callable to handle errors
        :param args: tuple of arguments for function
        :param kwargs: keyword arguments for function
        :return: ApplyResult, if callback not specified then the ApplyResult can be used to get the results if
                 the task can not be run, None is returned
        '''
        # callback = callback if self.callback is None else callback
        name = None if callback is None else callback.__name__
        if not self.accepting_tasks:
            self.logger.action('executor-submit_job', None, 'declined to accept a job, no longer accepting')
            return None
        try:
            self.logger.action('executor-submit_job', None,
                               'accepting a job (%s) with %d args and %d kwargs with a callback: %s'
                               % (func.__name__, len(args), len(kargs), name))
            return self.pool.apply_async(func, tuple(args), kargs, callback=callback, error_callback=error_callback)
        except:
            self.logger.action('executor-submit_job', None, 'failed to accept a job')
            return None

    def terminate(self):
        '''
        terminate the process pool
        :return:
        '''
        self.stop_polling_timer()
        if self.pool is None:
            self.logger.action('executor-terminate', None, 'no pool being used')
            return
        self.logger.action('executor-terminate', None, 'terminating and closing pool down')
        self.pool.close()
        self.pool.terminate()
        self.pool = None

    def join_terminate(self):
        '''
        join and then terminate the process pool
        :return:
        '''
        self.stop_polling_timer()
        self.accepting_tasks = False
        self.logger.action('executor-join_terminate', None, 'ending job acceptance and koining pool')
        try:
            self.pool.join()
        except:
            pass
        self.terminate()

    def is_running(self):
        return self.polling

    def is_alive(self):
        if self.polling_timer_thread is not None and self.polling_timer_thread.is_alive():
            return False
        if self.pool is not None and self.pool.is_alive():
            return False
        return True

    @classmethod
    def build_executor_results(cls, func: callable, jargs:list, jkargs:dict, callback: callable = None, error_callback: callable = None):
        result_params = {}
        result_params[EXECUTOR_JOB_FUNC] = func
        result_params[EXECUTOR_JOB_CALLBACK] = callback
        result_params[EXECUTOR_JOB_ERROR_CALLBACK] = error_callback
        result_params[EXECUTOR_JOB_ARGS] = jargs
        result_params[EXECUTOR_JOB_KARGS] = jkargs
        return result_params