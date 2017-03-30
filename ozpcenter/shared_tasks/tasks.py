# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import task
from ozpcenter import models


@task(ignore_result=True)
def add_category(category_title, category_description):
    category = models.Category(title=category_title, description=category_description)
    category.save()
    return category.title
