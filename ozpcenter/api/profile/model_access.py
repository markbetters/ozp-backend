"""
Model access
"""
import logging

import django.contrib.auth

import ozpcenter.models as models
import ozpcenter.model_access as generic_model_access

# Get an instance of a logger
logger = logging.getLogger('ozp-center')

def get_self(username):
    return generic_model_access.get_profile(username)


def get_all_profiles():
    return models.Profile.objects.all()


def get_profiles_by_role(role):
    return models.Profile.objects.filter(
        user__groups__name__exact=role)


def filter_queryset_by_username_starts_with(queryset, starts_with):
    return queryset.filter(
                user__username__startswith=starts_with)


def get_all_users():
    return django.contrib.auth.models.User.objects.all()


def get_all_groups():
    return django.contrib.auth.models.Group.objects.all()
