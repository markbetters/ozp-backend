#!/usr/bin/env bash

# Useful for development ONLY, this script will:
# 	* wipe the existing database
#	* wipe all existing migrations
#	* create a fresh database with new migrations
#	* load sample data
#	* start up the django dev server on port 8000

export DJANGO_SETTINGS_MODULE=ozpv3.settings

rm db.sqlite3
rm -r ozpcenter/migrations/*
python manage.py makemigrations ozpcenter
python manage.py migrate
# load sample data (uses runscript from django-extensions package)
echo 'Loading sample data...'
python manage.py runscript sample_data_generator
python manage.py runserver
