# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
from django.conf import settings
import ozpcenter.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('short_name', models.CharField(unique=True, max_length=32)),
            ],
            options={
                'verbose_name_plural': 'agencies',
            },
        ),
        migrations.CreateModel(
            name='ApplicationLibraryEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('folder', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'application library entries',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=255, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='ChangeDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('field_name', models.CharField(max_length=255)),
                ('old_value', models.CharField(max_length=4000, blank=True, null=True)),
                ('new_value', models.CharField(max_length=4000, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('secure_phone', models.CharField(max_length=50, blank=True, validators=[django.core.validators.RegexValidator(regex='\\d', code='invalid phone number', message='secure_phone must be a valid phone number')], null=True)),
                ('unsecure_phone', models.CharField(max_length=50, blank=True, validators=[django.core.validators.RegexValidator(regex='\\d', code='invalid phone number', message='unsecure_phone must be a valid phone number')], null=True)),
                ('email', models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(regex='\\w', code='invalid email', message='email must be a valid address')])),
                ('name', models.CharField(max_length=100)),
                ('organization', models.CharField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('required', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DocUrl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=2083, validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', code='invalid url', message='url must be a url')])),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('uuid', models.CharField(unique=True, max_length=36)),
                ('security_marking', models.CharField(max_length=1024)),
                ('file_extension', models.CharField(default='png', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='ImageType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=64, choices=[('small_icon', 'small_icon'), ('large_icon', 'large_icon'), ('banner_icon', 'banner_icon'), ('large_banner_icon', 'large_banner_icon'), ('small_screenshot', 'small_screenshot'), ('large_screenshot', 'large_screenshot')])),
                ('max_size_bytes', models.IntegerField(default=1048576)),
                ('max_width', models.IntegerField(default=2048)),
                ('max_height', models.IntegerField(default=2048)),
                ('min_width', models.IntegerField(default=16)),
                ('min_height', models.IntegerField(default=16)),
            ],
        ),
        migrations.CreateModel(
            name='Intent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('action', models.CharField(max_length=64, validators=[django.core.validators.RegexValidator(regex='\\w', code='invalid action', message='action must be a valid action')])),
                ('media_type', models.CharField(max_length=129, validators=[django.core.validators.RegexValidator(regex='\\w', code='invalid type', message='type must be a valid media type')])),
                ('label', models.CharField(max_length=255)),
                ('icon', models.ForeignKey(related_name='intent', to='ozpcenter.Image')),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('edited_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('description', models.CharField(max_length=8192, blank=True, null=True)),
                ('launch_url', models.CharField(max_length=2083, blank=True, validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', code='invalid url', message='launch_url must be a url')], null=True)),
                ('version_name', models.CharField(max_length=255, blank=True, null=True)),
                ('unique_name', models.CharField(unique=True, max_length=255, blank=True, null=True)),
                ('what_is_new', models.CharField(max_length=255, blank=True, null=True)),
                ('description_short', models.CharField(max_length=150, blank=True, null=True)),
                ('requirements', models.CharField(max_length=1000, blank=True, null=True)),
                ('approval_status', models.CharField(default='IN_PROGRESS', max_length=255, choices=[('IN_PROGRESS', 'IN_PROGRESS'), ('PENDING', 'PENDING'), ('APPROVED_ORG', 'APPROVED_ORG'), ('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED')])),
                ('is_enabled', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('avg_rate', models.FloatField(default=0.0)),
                ('total_votes', models.IntegerField(default=0)),
                ('total_rate5', models.IntegerField(default=0)),
                ('total_rate4', models.IntegerField(default=0)),
                ('total_rate3', models.IntegerField(default=0)),
                ('total_rate2', models.IntegerField(default=0)),
                ('total_rate1', models.IntegerField(default=0)),
                ('total_reviews', models.IntegerField(default=0)),
                ('iframe_compatible', models.BooleanField(default=True)),
                ('security_marking', models.CharField(max_length=1024, blank=True, null=True)),
                ('is_private', models.BooleanField(default=False)),
                ('agency', models.ForeignKey(related_name='listings', to='ozpcenter.Agency')),
                ('banner_icon', models.ForeignKey(related_name='listing_banner_icon', blank=True, to='ozpcenter.Image', null=True)),
                ('categories', models.ManyToManyField(db_table='category_listing', related_name='listings', to='ozpcenter.Category')),
                ('contacts', models.ManyToManyField(db_table='contact_listing', related_name='listings', to='ozpcenter.Contact')),
            ],
        ),
        migrations.CreateModel(
            name='ListingActivity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('action', models.CharField(max_length=128, choices=[('CREATED', 'CREATED'), ('MODIFIED', 'MODIFIED'), ('SUBMITTED', 'SUBMITTED'), ('APPROVED_ORG', 'APPROVED_ORG'), ('APPROVED', 'APPROVED'), ('REJECTED', 'REJECTED'), ('ENABLED', 'ENABLED'), ('DISABLED', 'DISABLED'), ('REVIEW_EDITED', 'REVIEW_EDITED'), ('REVIEW_DELETED', 'REVIEW_DELETED')])),
                ('activity_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('description', models.CharField(max_length=2000, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'listing activities',
            },
        ),
        migrations.CreateModel(
            name='ListingType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('message', models.CharField(max_length=4096)),
                ('expires_date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('display_name', models.CharField(max_length=255)),
                ('bio', models.CharField(max_length=1000, blank=True)),
                ('is_new_user', models.BooleanField(default=True)),
                ('dn', models.CharField(unique=True, max_length=1000)),
                ('issuer_dn', models.CharField(max_length=1000, blank=True, null=True)),
                ('auth_expires', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('access_control', models.CharField(max_length=16384)),
                ('organizations', models.ManyToManyField(db_table='agency_profile', related_name='profiles', to='ozpcenter.Agency')),
                ('stewarded_organizations', models.ManyToManyField(db_table='stewarded_agency_profile', blank=True, related_name='stewarded_profiles', to='ozpcenter.Agency')),
                ('user', models.OneToOneField(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('text', models.CharField(max_length=4000, blank=True, null=True)),
                ('rate', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('edited_date', models.DateTimeField(default=ozpcenter.utils.get_now_utc)),
                ('author', models.ForeignKey(related_name='reviews', to='ozpcenter.Profile')),
                ('listing', models.ForeignKey(related_name='reviews', to='ozpcenter.Listing')),
            ],
        ),
        migrations.CreateModel(
            name='Screenshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('large_image', models.ForeignKey(related_name='screenshot_large', to='ozpcenter.Image')),
                ('listing', models.ForeignKey(related_name='screenshots', to='ozpcenter.Listing')),
                ('small_image', models.ForeignKey(related_name='screenshot_small', to='ozpcenter.Image')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=16)),
            ],
        ),
        migrations.AddField(
            model_name='notification',
            name='author',
            field=models.ForeignKey(related_name='authored_notifications', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='notification',
            name='dismissed_by',
            field=models.ManyToManyField(db_table='notification_profile', related_name='dismissed_notifications', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='notification',
            name='listing',
            field=models.ForeignKey(related_name='notifications', blank=True, to='ozpcenter.Listing', null=True),
        ),
        migrations.AddField(
            model_name='listingactivity',
            name='author',
            field=models.ForeignKey(related_name='listing_activities', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='listingactivity',
            name='change_details',
            field=models.ManyToManyField(db_table='listing_activity_change_detail', related_name='listing_activity', to='ozpcenter.ChangeDetail'),
        ),
        migrations.AddField(
            model_name='listingactivity',
            name='listing',
            field=models.ForeignKey(related_name='listing_activities', to='ozpcenter.Listing'),
        ),
        migrations.AddField(
            model_name='listing',
            name='current_rejection',
            field=models.OneToOneField(related_name='+', blank=True, to='ozpcenter.ListingActivity', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='intents',
            field=models.ManyToManyField(db_table='intent_listing', related_name='listings', to='ozpcenter.Intent'),
        ),
        migrations.AddField(
            model_name='listing',
            name='large_banner_icon',
            field=models.ForeignKey(related_name='listing_large_banner_icon', blank=True, to='ozpcenter.Image', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='large_icon',
            field=models.ForeignKey(related_name='listing_large_icon', blank=True, to='ozpcenter.Image', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='last_activity',
            field=models.OneToOneField(related_name='+', blank=True, to='ozpcenter.ListingActivity', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='listing_type',
            field=models.ForeignKey(related_name='listings', blank=True, to='ozpcenter.ListingType', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='owners',
            field=models.ManyToManyField(db_table='profile_listing', related_name='owned_listings', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='listing',
            name='required_listings',
            field=models.ForeignKey(blank=True, to='ozpcenter.Listing', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='small_icon',
            field=models.ForeignKey(related_name='listing_small_icon', blank=True, to='ozpcenter.Image', null=True),
        ),
        migrations.AddField(
            model_name='listing',
            name='tags',
            field=models.ManyToManyField(db_table='tag_listing', related_name='listings', to='ozpcenter.Tag'),
        ),
        migrations.AddField(
            model_name='image',
            name='image_type',
            field=models.ForeignKey(related_name='images', to='ozpcenter.ImageType'),
        ),
        migrations.AddField(
            model_name='docurl',
            name='listing',
            field=models.ForeignKey(related_name='doc_urls', to='ozpcenter.Listing'),
        ),
        migrations.AddField(
            model_name='contact',
            name='contact_type',
            field=models.ForeignKey(related_name='contacts', to='ozpcenter.ContactType'),
        ),
        migrations.AddField(
            model_name='applicationlibraryentry',
            name='listing',
            field=models.ForeignKey(related_name='application_library_entries', to='ozpcenter.Listing'),
        ),
        migrations.AddField(
            model_name='applicationlibraryentry',
            name='owner',
            field=models.ForeignKey(related_name='application_library_entries', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='agency',
            name='icon',
            field=models.ForeignKey(related_name='agency', blank=True, to='ozpcenter.Image', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set([('author', 'listing')]),
        ),
    ]
