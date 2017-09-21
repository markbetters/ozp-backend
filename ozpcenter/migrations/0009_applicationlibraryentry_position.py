# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0008_auto_20160928_1904'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationlibraryentry',
            name='position',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
