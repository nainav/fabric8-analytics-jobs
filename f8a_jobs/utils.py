#!/usr/bin/env python3
import logging
from datetime import timedelta
from apscheduler.schedulers.base import STATE_RUNNING, STATE_STOPPED
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from f8a_jobs.handlers.error import ErrorHandler

logger = logging.getLogger(__name__)


def get_service_state_str(scheduler):
    """Get string representation of service state/scheduler"""
    if scheduler.state == STATE_RUNNING:
        return 'running'
    elif scheduler.state == STATE_STOPPED:
        return 'stopped'
    else:
        return 'paused'


def get_job_state_str(job):
    """Get string representation of a job"""
    if not hasattr(job, 'next_run_time'):
        # based on apscheduler sources
        return 'pending'
    elif job.next_run_time is None:
        return 'paused'
    else:
        return 'active'


def is_failed_job(job):
    """
    :param job: job to check
    :return: True if the given job is an error handler job
    """
    return is_failed_job_handler_name(job.args[0])


def is_failed_job_handler_name(handler_name):
    """
    :param handler_name: job handler name
    :return: True if job handler is an error handler
    """
    return handler_name == ErrorHandler.__name__


def job2raw_dict(job):
    """Return a dictionary for the given job that is JSON serializable"""
    result = {
        'job_id': job.id,
        'handler': job.args[0],
        'kwargs': job.kwargs,
        'state': get_job_state_str(job),
    }

    if isinstance(job.trigger, DateTrigger):
        result['when'] = str(job.trigger.run_date)
        result['periodically'] = False
    elif isinstance(job.trigger, IntervalTrigger):
        result['when'] = str(job.trigger.start_date)
        result['periodically'] = str(timedelta(seconds=job.trigger.interval_length))

    if hasattr(job, 'misfire_grace_time') and job.misfire_grace_time is not None:
        result['misfire_grace_time'] = str(timedelta(seconds=job.misfire_grace_time))

    return result
