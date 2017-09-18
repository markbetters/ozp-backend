# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0026_auto_20170912_1524'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='requirements',
            new_name='usage_requirements',
        ),
        migrations.AddField(
            model_name='listing',
            name='system_requirements',
            field=models.CharField(max_length=1000, blank=True, null=True),
        ),
    ]
