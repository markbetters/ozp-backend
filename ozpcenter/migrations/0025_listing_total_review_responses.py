# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0024_auto_20170829_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='total_review_responses',
            field=models.IntegerField(default=0),
        ),
    ]
