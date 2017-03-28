# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0011_recommendationsentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='group_target',
            field=models.CharField(default='all', choices=[('all', 'all'), ('stewards', 'stewards'), ('app_steward', 'app_steward'), ('org_steward', 'org_steward'), ('user', 'user')], max_length=24),
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(default='system', choices=[('system', 'system'), ('agency', 'agency'), ('agency_bookmark', 'agency_bookmark'), ('listing', 'listing'), ('peer', 'peer'), ('peer_bookmark', 'peer_bookmark')], max_length=24),
        ),
        migrations.AddField(
            model_name='notification',
            name='entity_id',
            field=models.IntegerField(blank=True, db_index=True, null=True, default=None),
        )
    ]
