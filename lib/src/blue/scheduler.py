import threading
import time
from pydash import is_function, is_instance_of
import schedule
import functools


class Scheduler:
    def __init__(self, task=None, cancel_on_failure=False):
        """Initializes a new Job instance.

        This constructor validates the input types, assigns the scheduling task, and
        sets up the scheduler and failure policy.

        Parameters:
            task (callable, required): The function or callable object that this job
                will execute when run by the scheduler. Must accept no arguments.
            cancel_on_failure (bool): If True, the job will be automatically
                removed from the scheduler if it raises an unhandled exception during
                execution.

        Raises:
            TypeError: If `task` is not a callable object (function).
            TypeError: If `cancel_on_failure` is not a boolean.
        """
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
        """Starts the job by scheduling its execution and beginning the main loop.

        This method takes the pre-configured job (`self.job`) and
        then starts a continuous monitoring thread to execute the scheduled tasks.

        Raises:
            TypeError: If `self.job` has not been initialized as an instance of
                `schedule.Job`.
        """
        if not is_instance_of(self.job, schedule.Job):
            raise TypeError('Object self.scheduler must be an instance of schedule.Job')
        self.scheduled = self.job.do(self.__background_job)
        self.stop_run_continuously = self.__run_continuously()

    def stop(self):
        """Stops the continuous background thread for the scheduler.

        This is achieved by calling the `set()` method on the thread termination
        event (`self.stop_run_continuously`), signaling the scheduler loop to exit
        gracefully.
        """
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
