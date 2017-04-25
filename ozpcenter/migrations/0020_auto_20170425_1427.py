# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0019_screenshot_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='screenshot',
            name='order',
            field=models.IntegerField(),
        ),
    ]
