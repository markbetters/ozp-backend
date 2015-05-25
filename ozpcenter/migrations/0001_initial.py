# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('icon_url', models.CharField(max_length=2083, validators=[django.core.validators.RegexValidator(code='invalid url', message='icon_url must be a url', regex='^(https|http|ftp|sftp|file)://.*$')])),
                ('short_name', models.CharField(unique=True, max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('approved_date', models.DateTimeField(null=True)),
                ('agency', models.ForeignKey(to='ozpcenter.Agency')),
            ],
        ),
    ]
