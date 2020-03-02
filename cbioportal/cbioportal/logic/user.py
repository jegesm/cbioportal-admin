import logging
import re
import pwgen

from cbioportal.settings import SETTINGS
from cbioportal.lib import Ldap
from cbioportal.lib.sendemail import send_new_password, send_token
from cbioportal.hub.models import User

logger = logging.getLogger(__name__)

def generatenewpassword(user):
    # generate password
    user.password = pwgen.pwgen(12)
    fname = SETTINGS.get('user').get('pattern_passwordfile')%user
    with open(fname, 'w') as f:
        f.write(user.password)

def add(user):
    """
    @summary: create a new user
              1. generate a password
              2. create an ldap entry
    @param user: a new user to add to the system
    @type user: cbioportal.hub.models.User
    @returns: { 'status_code': int, 'messages': list(str) }
              status_code:
              - flag: 0x000001: wrong characters in username or username or email already in use
              - flag: 0x000010: ldap failure
              - flag: 0x000100: filesystem failure
              - flag: 0x100000: fstab update error
    """
    logger.debug('call %s' % user)
    # check
    wrong_characters = "".join( re.split('[a-z0-9]+', user.username) )
    if wrong_characters != "":
        msg = "Username contains blacklisted characters: %s" % wrong_characters
        logger.error(msg)
        return { 'status_code': 0x00001, 'messages': [ msg ] }
    try:
        User.objects.get(username = user.username)
        msg = "Username already exists: %s" % user
        logger.error(msg)
        return { 'status_code': 0x00001, 'messages': [ msg ] }
    except User.DoesNotExist:
        pass
    try:
        User.objects.get(email = user.email)
        msg = "Email is already registered: %s" % user
        logger.error(msg)
        return { 'status_code': 0x00001, 'messages': [ msg ] }
    except User.DoesNotExist:
        pass

    status = 0
    messages = []
    generatenewpassword(user)
    # create new ldap entry
    try:
        Ldap().adduser(user)
    except Exception as e:
        msg = "Failed to create ldap entry for %s (%s)" % (user, e)
        logger.error(msg)
        messages.append(msg)
        status |= 0x000010
    # create home filesystem save dav secret
    return { 'status_code': status, 'messages': messages }

def remove(user):
    """
    @summary: remove a user
              1. delete ldap entry
              2. garbage collect home directory structure
              3. remove a gitlab account
              4. update fstab in impersonator container
    @param user: the user to be removed from the system
    @type user: cbioportal.hub.models.User
    @returns: { 'status_code': int, 'messages': list(str) }
              status_code:
              - flag: 0x0001: ldap failure
              - flag: 0x0010: filesystem failure
              - flag: 0x0100: gitlab removeuser failure
              - flag: 0x1000: fstab update error
    """
    logger.debug('call %s' % user)
    status = 0
    # remove ldap entry
    try:
        Ldap().removeuser(user)
    except Exception as e:
        logger.error("Failed to remove ldap entry for %s (%s)" % (user, e))
        status |= 0x0001
    return status
