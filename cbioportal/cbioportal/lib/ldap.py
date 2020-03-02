import ldap3
import logging

from cbioportal.settings import SETTINGS

logger = logging.getLogger(__name__)

class LdapException(Exception):
    pass

class Ldap:
    host = SETTINGS.get('ldap').get('host')
    port = SETTINGS.get('ldap').get('port')
    base_dn = SETTINGS.get('ldap').get('base_dn')
    bind_dn = SETTINGS.get('ldap').get('bind_dn')
    bind_pw = SETTINGS.get('ldap').get('bind_password')

    def __init__(self):
        logger.debug("init")
        server = ldap3.Server(host = self.host, port = self.port)
        self.connection = ldap3.Connection(server, self.bind_dn, self.bind_pw)
        success = self.connection.bind()
        if not success:
            logger.error("Cannot bind to ldap server, host: %s ; bind: %s; base: %s"%(self.host,self.bind_dn, self.base_dn))
            raise LdapException("Cannot bind to ldap server")

    def get_user(self, user):
        filter_expression = '(&(objectClass=posixAccount)(uid=%s))' % user.username
        search_base = 'ou=users,%s' % self.base_dn
        self.connection.search(
            search_base = self.base_dn,
            search_filter = filter_expression,
            search_scope = ldap3.SUBTREE,
            attributes = ldap3.ALL_ATTRIBUTES)
        entries = self.connection.response
        if not entries or len(entries) == 0:
            raise LdapException('no such user')
        return entries

    def modify_user_entries(self, oldentries, newentries):
        assert oldentries[0]['dn'] == newentries[0]['dn']
        dn = newentries[0]['dn']
        changes = {}
        for key, value in newentries[0]['attributes'].items():
            if oldentries[0]['attributes'][key] != value:
                changes[key] = [(ldap3.MODIFY_REPLACE, value)]
        logger.debug("%s" % changes.keys())
        if not self.connection.modify(dn, changes):
            raise LdapException(self.connection.last_error)

    def changepassword(self, user, newpassword, oldpassword = None):
        logger.debug('changepassword %s' % user)
        if oldpassword is not None:
            self.validate_user(user.username, oldpassword)
        oldentries = self.get_user(user)
        newentries = self.get_user(user)
        newentries[0]['attributes']['userPassword'] = [ newpassword ]
        self.modify_user_entries(oldentries, newentries)

    def is_validpassword(self, user, password):
        try:
            entries = self.get_user(user)
            return entries[0]['attributes']['userPassword'][0].decode() == password
        except:
            # user record may be missing
            return False        

    def userdn(self, user):
        return 'uid=%s,ou=users,%s' % (user.username, self.base_dn)

    def adduser(self, user):
        logging.debug('add %s' % user)
        dn = self.userdn(user)
        object_class = [
            'top',
            'simpleSecurityObject',
            'organizationalPerson',
            'person',
            'inetOrgPerson',
            'posixAccount',
            'shadowAccount',
        ]
        attributes = {
            'cn': user.username,
            'uid': user.username,
            'uidNumber': user.uid,
            'gidNumber': user.gid,
            'homeDirectory': '/home/%s' % user.username,
            'sn': user.last_name,
            'displayName': '%s %s' % (user.first_name, user.last_name),
            'givenName': user.first_name,
            'loginShell': '/bin/bash',
            'mail': user.email,
            'shadowExpire': -1,
            'shadowFlag': 0,
            'shadowLastChange': 10877,
            'shadowMax': 999999,
            'shadowMin': 8,
            'shadowWarning': 7,
            'userPassword': user.password
        }
        success = self.connection.add(dn, object_class, attributes)
        if not success:
            raise LdapException(self.connection.result['description'])

    def removeuser(self, user):
        logging.debug('remove %s' % user)
        dn = self.userdn(user)
        if not self.connection.delete(dn):
            raise LdapException(self.connection.result['description'])

