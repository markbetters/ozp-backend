# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0015_notification_script'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('entity_type', models.CharField(choices=[('category', 'category'), ('tag', 'tag')], db_index=True, max_length=12, default=None)),
                ('entity_id', models.IntegerField(db_index=True, default=None)),
                ('target_profile', models.ForeignKey(related_name='subscription_profiles', to='ozpcenter.Profile')),
            ],
        ),
    ]
