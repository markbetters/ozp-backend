# -*- coding: utf-8 -*-
"""
model definitions for ozpiwc

"""
import logging

# import django.contrib.auth
from django.db import models

# Get an instance of a logger
logger = logging.getLogger('ozp-iwc.'+str(__name__))

class DataResource(models.Model):
    """
    Data resource (data.api)
    """
    key = models.CharField(max_length=1024)
    entity = models.CharField(max_length=1048576, blank=True, null=True)
    content_type = models.CharField(max_length=1024, blank=True, null=True)
    # a little bit of denormalization here. Eventually this model could live
    # in a different database (perhaps an actual key-value or document store),
    # so reference the actual username here instead of a FK to the Profile or
    # User table in ozpcenter
    username = models.CharField(max_length=128)

    pattern = models.CharField(max_length=1024, blank=True, null=True)
    permissions = models.CharField(max_length=1024, blank=True, null=True)
    version = models.CharField(max_length=1024, blank=True, null=True)


    class Meta:
        unique_together = ('username', 'key')

    def __repr__(self):
        return '%s:%s' % (self.username, self.key)

    def __str__(self):
        return '%s:%s' % (self.username, self.key)
