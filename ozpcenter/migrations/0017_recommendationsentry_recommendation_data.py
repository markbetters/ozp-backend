# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def forwards(apps, schema_editor):
    if not schema_editor.connection.alias == 'default':
        return
    RecommendationsEntry = apps.get_model("ozpcenter", "RecommendationsEntry")
    RecommendationsEntry.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0016_subscription'),
    ]

    operations = [
        migrations.RunPython(forwards, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name='recommendationsentry',
            name='recommendation_data',
            field=models.BinaryField(default=None),
        ),
        migrations.RemoveField(
            model_name='recommendationsentry',
            name='listing',
        ),
        migrations.RemoveField(
            model_name='recommendationsentry',
            name='score',
        ),
    ]
