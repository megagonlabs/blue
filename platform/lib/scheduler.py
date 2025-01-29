import threading
import time
from pydash import is_function, is_instance_of
import schedule
import functools


class Scheduler:
    def __init__(self, task=None, cancel_on_failure=False):
        if not is_function(task):
            raise TypeError('Object task must be callable')
        if not is_instance_of(cancel_on_failure, bool):
            raise TypeError('Object cancel_on_failure must be an instance of bool')
        self.task = task
        self.scheduler = schedule.Scheduler()
        self.cancel_on_failure = cancel_on_failure
        self.set_job()

    def set_job(self):
        self.job = self.scheduler.every(2).seconds

    def start(self):
        if not is_instance_of(self.job, schedule.Job):
            raise TypeError('Object self.scheduler must be an instance of schedule.Job')
        self.scheduled = self.job.do(self.__background_job)
        self.stop_run_continuously = self.__run_continuously()

    def stop(self):
        self.stop_run_continuously.set()

    def __run_continuously(self):
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    if self.scheduled.should_run:
                        self.scheduled.run()
                    time.sleep(1)

        continuous_thread = ScheduleThread()
        continuous_thread.daemon = True
        continuous_thread.start()
        return cease_continuous_run

    def catch_exceptions(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback

                print(traceback.format_exc())
                if args[0].cancel_on_failure:
                    return schedule.CancelJob

        return wrapper

    @catch_exceptions
    def __background_job(self):
        self.task()
