"""
Purpose of this script: To send Emails to users that have Notifications that has not been emailed yet

Pull Request that refactored Notifications Tables to be able to do emails
https://github.com/aml-development/ozp-backend/pull/272

Steps to send out emails:
Open connection to stmp email server

Iterate all profiles
    Validate to make sure user has emailed, if not continue to next user

Development Setup:
setting.py
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_PORT = 1025

In a terminal
    python -m smtpd -n -c DebuggingServer localhost:1025
"""

import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.core import mail
from django.template import Context
from django.template import Template

from django.conf import settings


# from django.core.exceptions import ObjectDoesNotExist
from ozpcenter import models


def run():
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()

    email_batch_list = []

    print('==Notifications Email==')
    for current_profile in models.Profile.objects.filter(email_notification_flag=True).iterator():
        print('Processing Username: {}'.format(current_profile.user.username))
        current_profile_email = current_profile.user.email
        # Validate to make sure user has emailed, if not continue to next user
        if not current_profile_email:
            continue  # Skip this user, not validate email

        # Check to see if profile disabled email to be set_sender_and_entity
        # if check:
        #     continue

        # Retrieve All the Notifications for 'current_profile' that are not emailed yet
        notifications_mailbox_non_email = models.NotificationMailBox.objects.filter(target_profile=current_profile, emailed_status=False).all()
        notifications_mailbox_non_email_count = len(notifications_mailbox_non_email)

        if notifications_mailbox_non_email_count >= 1:
            # Construct messages
            template_context = Context({'non_emailed_count': notifications_mailbox_non_email_count})

            subject_line_template = Template(settings.EMAIL_SUBJECT_FIELD_TEMPLATE)
            body_template = Template(settings.EMAIL_BODY_FIELD_TEMPLATE)

            subject_line_template.render(template_context)

            current_email = mail.EmailMessage(
                subject_line_template.render(template_context),
                body_template.render(template_context),
                settings.EMAIL_FROM_FIELD,
                [current_profile_email],
            )
            current_email.content_subtype = "html"  # Main content is now text/html

            email_batch_list.append(current_email)

            print('\t{} New Notifications for username: {}'.format(notifications_mailbox_non_email_count, current_profile.user.username))
        else:
            print('\tNo New Notifications for username: {}'.format(current_profile.user.username))

        # After Sending Email to user, mark those Notifications as emailed
        for current_notification in notifications_mailbox_non_email:
            current_notification.emailed_status = True
            current_notification.save()

        if len(email_batch_list) >= 50:
            print('Starting Batch Email Send')
            connection.send_messages(email_batch_list)
            print('Finished Batch Email Send')
            email_batch_list = []

    # If there are any email to send
    if email_batch_list:
        print('Starting Batch Email Send (extra)')
        connection.send_messages(email_batch_list)
        print('Finished Batch Email Send (extra)')
        email_batch_list = []

    # The connection was already open so send_messages() doesn't close it.
    # We need to manually close the connection.
    connection.close()
