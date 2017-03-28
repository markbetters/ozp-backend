# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0013_notification_fill_migrate'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationMailBox',
            fields=[
                ('target_profile', models.ForeignKey(related_name='mailbox_profiles', to='ozpcenter.Profile')),
                ('notification', models.ForeignKey(related_name='mailbox_notifications', to='ozpcenter.Notification')),
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('emailed_status', models.BooleanField(default=False)),
                ('read_status', models.BooleanField(default=False)),
                ('acknowledged_status', models.BooleanField(default=False)),
            ],
        ),
    ]
