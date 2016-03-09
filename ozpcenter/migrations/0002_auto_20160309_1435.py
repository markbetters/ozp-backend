# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='is_new_user',
            new_name='center_tour_flag',
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
