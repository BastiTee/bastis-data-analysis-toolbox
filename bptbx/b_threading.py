r"""This module contains tools for multi-threading operations."""

import multiprocessing
from random import randrange
from threading import Thread
from time import sleep

from bptbx import b_legacy
Queue = b_legacy.b_queue()


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            self.tasks.task_done()


class ThreadPool:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """Add a task to the queue"""
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

    def is_empty(self):
        return self.tasks.empty()


def get_cpus():
    """This method obtains the number of available cpus"""

    return multiprocessing.cpu_count()


def sleep_job():
    """This method is used for testing and runs a random sleep
    between 1-5 seconds"""

    timespan = randrange(1, 6)
    print('Sleeping for {0} seconds'.format(timespan))
    sleep(timespan)
