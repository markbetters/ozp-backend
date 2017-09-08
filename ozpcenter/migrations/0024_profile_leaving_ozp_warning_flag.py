# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0023_auto_20170629_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='leaving_ozp_warning_flag',
            field=models.BooleanField(default=False),
        ),
    ]
