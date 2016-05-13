# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ozpcenter', '0003_listing_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='approval_status',
            field=models.CharField(choices=[('IN_PROGRESS', 'IN_PROGRESS'), ('PENDING', 'PENDING'), ('APPROVED_ORG', 'APPROVED_ORG'), ('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED'), ('DELETED', 'DELETED')], default='IN_PROGRESS', max_length=255),
        ),
        migrations.AlterField(
            model_name='listingactivity',
            name='action',
            field=models.CharField(choices=[('CREATED', 'CREATED'), ('MODIFIED', 'MODIFIED'), ('SUBMITTED', 'SUBMITTED'), ('APPROVED_ORG', 'APPROVED_ORG'), ('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED'), ('ENABLED', 'ENABLED'), ('DISABLED', 'DISABLED'), ('DELETED', 'DELETED'), ('REVIEW_EDITED', 'REVIEW_EDITED'), ('REVIEW_DELETED', 'REVIEW_DELETED')], max_length=128),
        ),
    ]
