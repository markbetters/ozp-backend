# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0023_auto_20170629_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='review_parent',
            field=models.ForeignKey(blank=True, null=True, to='ozpcenter.Review'),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([('review_parent', 'author', 'listing')]),
        ),
    ]
