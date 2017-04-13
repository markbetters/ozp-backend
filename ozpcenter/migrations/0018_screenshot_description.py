# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0017_recommendationsentry_recommendation_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='screenshot',
            name='description',
            field=models.CharField(null=True, blank=True, max_length=160),
        ),
    ]
