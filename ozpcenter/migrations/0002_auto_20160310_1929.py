# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='center_tour_flag',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='hud_tour_flag',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='webtop_tour_flag',
            field=models.BooleanField(default=True),
        ),
    ]
