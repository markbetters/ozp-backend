# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0021_screenshot_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_notification_flag',
            field=models.BooleanField(default=True),
        ),
    ]
