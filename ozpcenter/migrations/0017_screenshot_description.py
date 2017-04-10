# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0016_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='screenshot',
            name='description',
            field=models.CharField(blank=True, null=True, max_length=160),
        ),
    ]
