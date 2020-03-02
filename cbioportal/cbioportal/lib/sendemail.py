'''
@summary: send e-mails to users in the name of the administrator
@author: Jozsef Steger
'''
import logging
import time
import smtplib
from email.mime.text import MIMEText
from email.utils import formatdate

from cbioportal.settings import SETTINGS

logger = logging.getLogger(__name__)

def _send(to, subject, message):
    '''
    @summary: helper method to send a single message
    @param to: the recepient's e-mail address
    @type to: str
    @param subject: the subject of the mail
    @type subject: str
    @param message: the mail content
    @type message: str
    @returns: 0 if succeeded, 1 otherwise
    '''
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = SETTINGS.get('user').get('adminemail')
    msg['To'] = to
    msg['Date'] = formatdate(localtime = True)

    try:
        s = smtplib.SMTP(SETTINGS.get('user').get('smtpserver'))
        s.send_message(msg)
        s.quit()
        logger.info('mailto: %s [%s]' % (to, subject))
        return 0
    except Exception as e:
        logger.error('mailto: %s [%s]' % (to, subject))
        return 1

def send_new_password(user):
    '''
    @summary: send a message that a new password is generated.
    @param user: recipient
    @type user: cbioportal.user.models.User
    @returns: 0 if suceeded 0 otherwise
    '''
    subject = 'Your cbioportal account is created'
    message = """
Dear %s %s,

your new cbioportal account (%s) is created.

The login password is set %s . Please change it the first time you visit the dasboard at %s.

Best regards,
 Kooplex team
    """ % (user.first_name, user.last_name, user.username, user.password, SETTINGS.get('user').get('base_url'))

    status = _send(to = user.email, subject = subject, message = message)
    if status != 0:
        send_error_report(status, 'Error delivering pw (%s) to %s' % (user.password, user.email))
    return status

def send_error_report(status, extra = 'na'):
    '''
    @summary: send an error report to admin e-mail address
    @param status: a short description
    @type status: str
    @param extra: any additional info, default is "na"
    @type extra: str
    '''
    message = """
Instance: %s
Failure: %s
Extra: %s
    """ % (SETTINGS.get('user').get('base_url'), status, extra)
    _send(to = SETTINGS.get('user').get('adminemail'), subject = '[SMTP error]', message = message)

def send_token(user, token):
    '''
    @summary: send a new token message
    @param user: recipient
    @type user: cbioportal.user.models.User
    @param token: the secret
    @type token: str
    @returns: 0 if suceeded 0 otherwise
    '''
    subject = 'Kooplex account password reset request'
    message = """
Dear %s %s,

a cbioportal account password reset request for your account (%s) is issued.

Provide the token %s along with the new password to be set in the dashboard.

Best regards,
 Kooplex team
    """ % (user.first_name, user.last_name, user.username, token)

    status = _send(to = user.email, subject = subject, message = message)
    if status != 0:
        send_error_report(status, 'Error delivering pw request token (%s) to %s' % (token, user.email))
    return status

def send_restart_containers_mail(user, containers, reason):
    '''
    @summary: send a message that 
    @param user: recipient
    @type user: cbioportal.user.models.User
    @param container: the list of containers to be restarted
    @type token: list(cbioportal.user.models.ProjectContainer)
    @param reason: some explanation to the user
    @type reason: str
    @returns: 0 if suceeded 0 otherwise
    '''
    ctrs = ", ".join([ c.project.name if c.project.owner == user else c.project.name_with_owner for c in containers ])
    subject = 'ProjectContainer restart request'
    message = """
Dear %s %s,

please restart your containers: %s

Extra reason: %s

Best regards,
 Kooplex team
    """ % (user.first_name, user.last_name, ctrs, reason)

    status = _send(to = user.email, subject = subject, message = message)
    if status != 0:
        send_error_report(status, 'Error delivering pw request token (%s) to %s' % (token, user.email))
    return status
