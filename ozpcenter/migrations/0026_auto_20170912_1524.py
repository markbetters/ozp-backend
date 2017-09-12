# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ozpcenter.utils


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0025_listing_total_review_responses'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='created_date',
            field=models.DateTimeField(default=ozpcenter.utils.get_now_utc),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([]),
        ),
    ]
