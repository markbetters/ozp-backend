"""
Create your tasks here
"""
from __future__ import absolute_import, unicode_literals
import datetime
import pytz

from celery import task
from ozpcenter import models


@task  # ignore_result=True
def add_category(category_title, category_description):
    """
    Task for creating
    from ozpcenter.shared_tasks.tasks import add_category; a = add_category.delay('4d', '90')
    """
    category = models.Category(title=category_title, description=category_description)
    category.save()
    return category.title


@task
def notification_emails():
    """
    Email Notification

    [(n.id, n.emailed_status) for n in NotificationMailBox.objects.all()]
    from ozpcenter.shared_tasks.tasks import notification_emails; notification_emails.delay()
    [(n.id, n.emailed_status) for n in NotificationMailBox.objects.all()]

    """
    profile_list =  models.Profile.objects.all()
    for current_profile in profile_list:
        # For each profile, get the mailbox
        notifications_mailbox = models.NotificationMailBox.objects.filter(target_profile=current_profile,
                                                                   notification__expires_date__gt=datetime.datetime.now(pytz.utc),
                                                                   emailed_status=False)
        notifications_mailbox_notification_list = notifications_mailbox.values_list('notification', flat=True)
        unexpired_notifications = models.Notification.objects.filter(pk__in=notifications_mailbox_notification_list)

        for unexpired_notification in unexpired_notifications:
            # Email Logic
            pass

        for record in notifications_mailbox:
            record.emailed_status = True
            record.save()
