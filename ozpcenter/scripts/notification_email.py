import os
import sys

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from django.core import mail

# from django.core.exceptions import ObjectDoesNotExist
# from ozpcenter import models


def run():
    connection = mail.get_connection()
    # Manually open the connection
    connection.open()

    # Construct an email message that uses the connection
    email1 = mail.EmailMessage(
        'Hello',
        'Body goes here',
        'from@example.com',
        ['to1@example.com'],
        connection=connection,
    )
    email1.send()  # Send the email

    # Construct two more messages
    email2 = mail.EmailMessage(
        'Hello',
        'Body goes here',
        'from@example.com',
        ['to2@example.com'],
    )
    email3 = mail.EmailMessage(
        'Hello',
        'Body goes here',
        'from@example.com',
        ['to3@example.com'],
    )

    # Send the two emails in a single call -
    connection.send_messages([email2, email3])
    # The connection was already open so send_messages() doesn't close it.
    # We need to manually close the connection.
    connection.close()
