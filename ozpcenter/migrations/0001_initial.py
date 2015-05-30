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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('icon_url', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='icon_url must be a url', code='invalid url')], max_length=2083)),
                ('short_name', models.CharField(unique=True, max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationLibraryEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('folder', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ChangeDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('field_name', models.CharField(max_length=255)),
                ('old_value', models.CharField(max_length=4000)),
                ('new_value', models.CharField(max_length=4000)),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('secure_phone', models.CharField(validators=[django.core.validators.RegexValidator(regex='\\d', message='secure_phone must be a valid phone number', code='invalid phone number')], max_length=50)),
                ('unsecure_phone', models.CharField(validators=[django.core.validators.RegexValidator(regex='\\d', message='unsecure_phone must be a valid phone number', code='invalid phone number')], max_length=50)),
                ('email', models.CharField(validators=[django.core.validators.RegexValidator(regex='\\w', message='email must be a valid address', code='invalid email')], max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('organization', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('required', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DocUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='url must be a url', code='invalid url')], max_length=2083)),
            ],
        ),
        migrations.CreateModel(
            name='Intent',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('action', models.CharField(validators=[django.core.validators.RegexValidator(regex='\\w', message='action must be a valid action', code='invalid action')], max_length=64)),
                ('type', models.CharField(validators=[django.core.validators.RegexValidator(regex='\\w', message='type must be a valid media type', code='invalid type')], max_length=129)),
                ('label', models.CharField(max_length=255)),
                ('icon', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='icon must be a url', code='invalid icon')], max_length=2083)),
            ],
        ),
        migrations.CreateModel(
            name='ItemComment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('text', models.CharField(max_length=4000)),
                ('rate', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='Listing',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=255)),
                ('approved_date', models.DateTimeField(null=True)),
                ('description', models.CharField(max_length=255)),
                ('launch_url', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='launch_url must be a url', code='invalid url')], max_length=2083)),
                ('version_name', models.CharField(max_length=255)),
                ('unique_name', models.CharField(unique=True, max_length=255)),
                ('small_icon', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='small_icon must be a url', code='invalid url')], max_length=2083)),
                ('large_icon', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='large_icon must be a url', code='invalid url')], max_length=2083)),
                ('banner_icon', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='banner_icon must be a url', code='invalid url')], max_length=2083)),
                ('large_banner_icon', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='large_banner_icon must be a url', code='invalid url')], max_length=2083)),
                ('what_is_new', models.CharField(max_length=255)),
                ('description_short', models.CharField(max_length=150)),
                ('requirements', models.CharField(max_length=1000)),
                ('approval_status', models.CharField(max_length=255)),
                ('is_enabled', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('avg_rate', models.DecimalField(max_digits=2, decimal_places=1, default=0.0)),
                ('total_votes', models.IntegerField(default=0)),
                ('total_rate5', models.IntegerField(default=0)),
                ('total_rate4', models.IntegerField(default=0)),
                ('total_rate3', models.IntegerField(default=0)),
                ('total_rate2', models.IntegerField(default=0)),
                ('total_rate1', models.IntegerField(default=0)),
                ('total_comments', models.IntegerField(default=0)),
                ('singleton', models.BooleanField(default=False)),
                ('agency', models.ForeignKey(related_name='listings', to='ozpcenter.Agency')),
            ],
        ),
        migrations.CreateModel(
            name='ListingActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('action', models.CharField(max_length=255)),
                ('activity_date', models.DateTimeField()),
                ('listing', models.ForeignKey(related_name='listing_activities', to='ozpcenter.Listing')),
            ],
        ),
        migrations.CreateModel(
            name='ListingType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=50)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=255)),
                ('display_name', models.CharField(max_length=255)),
                ('email', models.CharField(max_length=255)),
                ('bio', models.CharField(max_length=1000)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('last_login', models.DateTimeField(null=True, blank=True)),
                ('highest_role', models.IntegerField(default=1)),
                ('organizations', models.ManyToManyField(related_name='profiles', db_table='agency_profile', to='ozpcenter.Agency')),
                ('stewarded_organizations', models.ManyToManyField(related_name='stewarded_profiles', db_table='stewarded_agency_profile', to='ozpcenter.Agency', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RejectionListing',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('description', models.CharField(max_length=2000)),
                ('author', models.ForeignKey(related_name='rejection_listings', to='ozpcenter.Profile')),
                ('listing', models.ForeignKey(related_name='rejection_listings', to='ozpcenter.Listing')),
            ],
        ),
        migrations.CreateModel(
            name='Screenshot',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('small_image_url', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='small image url must be a url', code='invalid url')], max_length=2083)),
                ('large_image_url', models.CharField(validators=[django.core.validators.RegexValidator(regex='^(https|http|ftp|sftp|file)://.*$', message='large image url must be a url', code='invalid url')], max_length=2083)),
                ('listing', models.ForeignKey(related_name='screenshots', to='ozpcenter.Listing')),
            ],
        ),
        migrations.AddField(
            model_name='listingactivity',
            name='profile',
            field=models.ForeignKey(related_name='listing_activities', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='listing',
            name='appType',
            field=models.ForeignKey(related_name='listings', to='ozpcenter.ListingType'),
        ),
        migrations.AddField(
            model_name='listing',
            name='contacts',
            field=models.ManyToManyField(related_name='listings', db_table='contact_listing', to='ozpcenter.Contact'),
        ),
        migrations.AddField(
            model_name='listing',
            name='required_listings',
            field=models.ForeignKey(to='ozpcenter.Listing'),
        ),
        migrations.AddField(
            model_name='itemcomment',
            name='author',
            field=models.ForeignKey(related_name='item_comments', to='ozpcenter.Profile'),
        ),
        migrations.AddField(
            model_name='itemcomment',
            name='listing',
            field=models.ForeignKey(related_name='item_comments', to='ozpcenter.Listing'),
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
            model_name='changedetail',
            name='listing',
            field=models.ForeignKey(related_name='change_details', to='ozpcenter.Listing'),
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
    ]
