# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import ozpcenter.utils
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0011_recommendationsentry'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationV2',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('notification_id', models.UUIDField(editable=False, db_index=True, default=uuid.uuid4)),
                ('created_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('expires_date', models.DateTimeField()),
                ('message', models.CharField(max_length=4096)),
                ('notification_type', models.CharField(choices=[('system', 'system'), ('agency', 'agency'), ('agency_bookmark', 'agency_bookmark'), ('listing', 'listing'), ('peer', 'peer'), ('peer_bookmark', 'peer_bookmark')], db_index=True, max_length=24)),
                ('entity_id', models.IntegerField(default=0, null=True, blank=True)),
                ('email_status', models.BooleanField(default=False)),
                ('_metadata', models.CharField(null=True, blank=True, max_length=4096, db_column='metadata')),
                ('user_target', models.CharField(choices=[('all', 'all'), ('stewards', 'stewards'), ('app_steward', 'app_steward'), ('org_steward', 'org_steward'), ('user', 'user')], max_length=24)),
                ('author', models.ForeignKey(related_name='authored_notificationsv2', to='ozpcenter.Profile')),
                ('profile_target_id', models.ForeignKey(related_name='mailbox_notifications', to='ozpcenter.Profile')),
            ],
        ),
    ]
