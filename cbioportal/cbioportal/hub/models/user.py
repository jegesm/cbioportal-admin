import logging
import os
import pwgen

from django.contrib import messages
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User as DJUser
from django.db import models

from cbioportal.settings import SETTINGS

logger = logging.getLogger(__name__)

class User(DJUser):
    uid = models.IntegerField(null = True)
    gid = models.IntegerField(null = True)
    bio = models.TextField(max_length = 500, blank = True)

    def __str__(self):
        return str(self.username)

    def __lt__(self, u):
        return self.first_name < u.first_name if self.last_name == u.last_name else self.last_name < u.last_name

    def __getitem__(self, k):
        return self.__getattribute__(k)

    @property
    def displayname(self):
        return "%(first_name)s %(last_name)s" % self


    def changepassword(self, password):
        from cbioportal.lib.filesystem import write_davsecret
        from cbioportal.lib import Ldap
        self.password = password
        write_davsecret(self)
        self.save()
        Ldap().changepassword(self, password)

    def generatenewpassword(self):
        password = pwgen.pwgen(12)
        self.changepassword(self, password)
        with open(SETTINGS.get('user').get('pattern_passwordfile') % self, 'w') as f:
            f.write(self.password)
        self.changepassword(password)

    def create(self):
        from cbioportal.logic import user
        logger.debug("%s" % self)
        # set uid and gid, generate token
        last_uid = User.objects.all().aggregate(models.Max('uid'))['uid__max']
        if last_uid is None:
            self.uid = SETTINGS.get('user').get('min_userid', 1)
        else:
            self.uid = last_uid + 1
        self.gid = SETTINGS.get('ldap').get('usersgroupid', 1000)
        status = user.add(self)
        self.save()
        try:
            logger.info(("New user: %(last_name)s %(first_name)s (%(username)s with uid: %(uid)d) created. Email: %(email)s) status: " % self) + str(status))
        except:
            logger.info(("New user: %(last_name)s %(first_name)s (%(username)s with uid: %(uid)d) created. Email: %(email)s) status: " % self) + str(status))
        return status

    def remove(self):
        from cbioportal.logic import user
        logger.debug("%s" % self)
        status = user.remove(self)
        try:
            logger.info(("Deleted user: %(last_name)s %(first_name)s (%(username)s with uid: %(uid)d) created. Email: %(email)s) status: " % self))
        except:
            logger.info(("Deleted user: %(last_name)s %(first_name)s (%(username)s with uid: %(uid)d) created. Email: %(email)s) status: " % self))
#        self.delete()

