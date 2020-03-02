"""
@author: Jozsef Steger
@summary: 
"""
import re
import time
import logging
import subprocess
import shlex

from django.conf import settings

logger = logging.getLogger(__name__)

def keeptrying(method, times, **kw):
    """
    @summary: run an arbitrary method with keyword arguments. In case an exception is raised during the call, 
    keep trying some more times with exponentially increasing waiting time between consecutive calls.
    @param method: the method to call
    @type method: callable
    @param times: the number of trials
    @type times: int
    @param kw: keyword arguments to pass to the method
    @returns the return value of method
    @raises the last exception if calling th method fails times many times
    """
    dt = .1
    while times > 0:
        logging.debug("executing %s" % method)
        times -= 1
        try:
            return method(**kw)
        except Exception as e:
            logging.warning("exception (%s) while executing %s [backoff and try %d more]" % (method, e, times))
            if times == 0:
                logging.error("gave up execution of %s" % method)
                raise
            time.sleep(dt)
            dt *= 2


def bash(command):
    """
    @summary: run a command as root in the hub container
    @param command: the shell command to run
    @type command: str
    """
    wrap = "bash -c \"%s\""
    logger.info(command)
    subprocess.call(shlex.split(command))

def authorize(request):
    from cbioportal.hub.models import User
    from django.http import HttpRequest
    """
    @summary: authorize a request.
    @param request: web server request
    @type request: django.http.HttpRequest
    @return: whether the user associated with the request is found in the hub db
    @rtype: bool
    """
    assert isinstance(request, HttpRequest)
    try:
        User.objects.get(username = request.user.username)
        return True
    except User.DoesNotExist:
        return False

def standardize_str(s):
    '''
    @summary: get rid of tricky characters in a string:
              1. lower the string
              2. keep english letters amd numbers
    @param s: the string to clean
    @type s: str
    @returns: rhe cleaned string
    @raises AssertionError, if not characters are left after cleaning
    '''
    s_clean = "".join(re.split(r'[^0-9a-z]*([a-z0-9]+)[^0-9a-z]*', s.lower()))
    assert len(s_clean), "No characters kept after standardization"
    return s_clean
