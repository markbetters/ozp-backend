# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataResource',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1024)),
                ('entity', models.CharField(blank=True, max_length=1048576, null=True)),
                ('content_type', models.CharField(blank=True, max_length=1024, null=True)),
                ('username', models.CharField(max_length=128)),
                ('pattern', models.CharField(blank=True, max_length=1024, null=True)),
                ('permissions', models.CharField(blank=True, max_length=1024, null=True)),
                ('version', models.CharField(blank=True, max_length=1024, null=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='dataresource',
            unique_together=set([('username', 'key')]),
        ),
    ]
