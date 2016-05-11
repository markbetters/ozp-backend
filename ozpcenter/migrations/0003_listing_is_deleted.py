# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0002_auto_20160310_1929'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
