# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0010_auto_20170109_2128'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecommendationsEntry',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('score', models.FloatField(default=0.0)),
                ('listing', models.ForeignKey(to='ozpcenter.Listing', related_name='recommendations_lisiting')),
                ('target_profile', models.ForeignKey(to='ozpcenter.Profile', related_name='recommendations_profile')),
            ],
            options={
                'verbose_name_plural': 'recommendations entries',
            },
        ),
    ]
