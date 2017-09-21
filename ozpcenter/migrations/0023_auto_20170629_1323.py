# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0022_profile_email_notification_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='listing_notification_flag',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subscription_notification_flag',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(default='system', max_length=24, choices=[('system', 'system'), ('agency', 'agency'), ('agency_bookmark', 'agency_bookmark'), ('listing', 'listing'), ('peer', 'peer'), ('peer_bookmark', 'peer_bookmark'), ('subscription', 'subscription')]),
        ),
    ]
