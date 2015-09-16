# -*- coding: utf-8 -*-
"""
model definitions for ozpiwc

"""
import logging

# import django.contrib.auth
from django.db import models

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

class Data(models.Model):
    """
    Data (data.api)
    """
    key = models.CharField(max_length=1024)
    value = models.CharField(max_length=1048576)
    # a little bit of denormalization here. Eventually this model could live
    # in a different database (perhaps an actual key-value or document store),
    # so reference the actual username here instead of a FK to the Profile or
    # User table in ozpcenter
    username = models.CharField(max_length=128)

    class Meta:
        unique_together = ('username', 'key')

    def __repr__(self):
        return '%s:%s' % (self.username, self.key)

    def __str__(self):
        return '%s:%s' % (self.username, self.key)
