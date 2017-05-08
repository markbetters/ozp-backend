# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0018_screenshot_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='group_target',
            field=models.CharField(max_length=24, default='all', choices=[('all', 'all'), ('stewards', 'stewards'), ('app_steward', 'app_steward'), ('org_steward', 'org_steward'), ('user', 'user'), ('owner', 'owner')]),
        ),
    ]
