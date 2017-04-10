# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0016_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='recommendationsentry',
            name='recommendation_data',
            field=models.BinaryField(default=None),
        ),
        migrations.RemoveField(
            model_name='recommendationsentry',
            name='listing',
        ),
        migrations.RemoveField(
            model_name='recommendationsentry',
            name='score',
        ),
    ]
