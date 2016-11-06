from __future__ import unicode_literals

from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.utils import timezone


class Writer(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=254, unique=True)
    email = models.EmailField(max_length=254)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    bio_link = models.URLField(blank=True, null=True)

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def get_full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def get_short_name(self):
        return self.get_full_name()

    def initials(self):
        return self.first_name[0] + self.last_name[0]

    def blurb_history(self):
        return self.review_set.all().order_by('-create_date')

    def last_blurb_date(self):
        # Return the date of their most recent blurb
        blurbs = self.blurb_history()
        if blurbs:
            return blurbs[0].create_date
        # No blurbs - return an old date
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

    def published_blurb_history(self):

        return self.review_set.filter(status='published').order_by('-create_date')

