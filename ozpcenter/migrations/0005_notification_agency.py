# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0004_auto_20160511_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='agency',
            field=models.ForeignKey(blank=True, related_name='agency_notifications', null=True, to='ozpcenter.Agency'),
        ),
    ]
