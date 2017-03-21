# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import ozpcenter.utils


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0011_recommendationsentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationV2',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('target_profile', models.ForeignKey(to='ozpcenter.Profile', related_name='mailbox_notifications')),
                ('notification_id', models.UUIDField(db_index=True, editable=False, default=uuid.uuid4)),
                ('created_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('expires_date', models.DateTimeField()),
                ('author_username', models.CharField(help_text='150 characters or fewer', max_length=150)),
                ('message', models.CharField(max_length=4096)),
                ('notification_type', models.CharField(max_length=24, choices=[('system', 'system'), ('agency', 'agency'), ('agency_bookmark', 'agency_bookmark'), ('listing', 'listing'), ('peer', 'peer'), ('peer_bookmark', 'peer_bookmark')])),
                ('entity_id', models.IntegerField(blank=True, null=True, default=0)),
                ('email_status', models.BooleanField(default=False)),
                ('_metadata', models.CharField(db_column='metadata', max_length=4096, null=True, blank=True)),
                ('group_target', models.CharField(max_length=24, choices=[('all', 'all'), ('stewards', 'stewards'), ('app_steward', 'app_steward'), ('org_steward', 'org_steward'), ('user', 'user')])),
            ],
        ),
    ]
