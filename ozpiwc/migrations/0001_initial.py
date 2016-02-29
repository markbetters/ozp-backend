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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('key', models.CharField(max_length=1024)),
                ('entity', models.CharField(null=True, max_length=1048576, blank=True)),
                ('content_type', models.CharField(null=True, max_length=1024, blank=True)),
                ('username', models.CharField(max_length=128)),
                ('pattern', models.CharField(null=True, max_length=1024, blank=True)),
                ('permissions', models.CharField(null=True, max_length=1024, blank=True)),
                ('version', models.CharField(null=True, max_length=1024, blank=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='dataresource',
            unique_together=set([('username', 'key')]),
        ),
    ]
